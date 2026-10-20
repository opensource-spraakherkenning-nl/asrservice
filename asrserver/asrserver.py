import sys
import socket
import signal
import os
import threading
import json
import whisperx
import traceback
from whisperx.diarize import DiarizationPipeline
from whisperx.utils import ResultWriter, SubtitlesWriter, WriteJSON, WriteSRT, WriteTSV, WriteTXT, WriteVTT

"""
This is a simple TCP background server that loads and holds the background model, accepts multiple clients,
and transcribes texts as requested. Input/output data does not flow over the socket but directly to the filesystem.
The socket only provides the command and control interface. The server is not meant to be served publicly but is only
used as a background service via CLAM, hence the hardcoded binding to localhost.
"""

model_id = sys.argv[1] #e.g: large-v2
device = sys.argv[2] #e.g: cuda
compute_type = sys.argv[3] #e.g: float16 (change to int8 if low on gpu mem or on cpu, at loss of accuracy)
port = sys.argv[4]
language_code = sys.argv[5]


output_options = {"max_line_width": 1000, "max_line_count": 9000000, "highlight_words": False}

batch_size = 16
terminate = threading.Event()

def shutdown(signalnum, _):
    global terminate
    print(f"Shutting down, received signal {signalnum}", file=sys.stderr)
    terminate.set()

def json2ctm(inputfile: str, outputfile: str):
    channelID = 0
    with open(outputfile,'w',encoding='utf-8') as f_out:
        with open(inputfile,'r',encoding='utf-8') as f:
            data = json.load(f)

        inputfile_base = os.path.basename(inputfile).replace(".json","")
        for s in data['segments']:
          for s2 in s['words']:
            print(inputfile_base, end='\t', file=f_out)
            if 'speaker' in s2:
                print(s2['speaker'], end='\t', file=f_out)
            else:
                print(channelID, end='\t', file=f_out)
            print(s2['start'], end='\t', file=f_out)
            print(round(s2['end'] - s2['start'],3), end='\t', file=f_out)
            print(s2['word'], end='\t', file=f_out)
            print(s2['score'], file=f_out)
          print(file=f_out) # next utterance

def process(filename: str, diarize: bool, min_speakers: int, max_speakers: int, return_char_alignments: bool, outputdir: str) -> bool:
    """Main processing function, uses globally loaded model state"""
    if filename.find('..') != -1 or not os.path.exists(filename):
        return False
    audio = whisperx.load_audio(filename)
    result = model.transcribe(audio, batch_size=batch_size)
    result = whisperx.align(result["segments"], alignmodel, metadata, audio, device, return_char_alignments=return_char_alignments)
    if diarize:
        if min_speakers < max_speakers:
            diarize_segments = diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)
        else:
            diarize_segments = diarize_model(audio)
        result = whisperx.assign_word_speakers(diarize_segments, result)

    if not 'language' in result:
        result['language'] = language_code

    outputfile = os.path.join(outputdir, os.path.splitext(os.path.basename(filename))[0])
    with open(outputfile + ".txt",'w',encoding='utf-8') as f:
        WriteTXT(ResultWriter).write_result(result, file=f, options=output_options)
    with open(outputfile + ".srt", 'w',encoding='utf-8') as f:
        WriteSRT(SubtitlesWriter).write_result(result, file=f, options=output_options)
    with open(outputfile + ".vtt", 'w',encoding='utf-8') as f:
        WriteVTT(SubtitlesWriter).write_result(result, file=f, options=output_options)
    with open(outputfile + ".tsv", 'w',encoding='utf-8') as f:
        WriteTSV(ResultWriter).write_result(result, file=f, options=output_options)
    with open(outputfile + ".json", 'w',encoding='utf-8') as f:
        WriteJSON(ResultWriter).write_result(result, file=f, options=output_options)
    json2ctm(outputfile + ".json", outputfile+ ".ctm")
    return True

def client_handler(conn):
    """Handle incoming client connections"""
    conn.settimeout(2)
    try:
        with conn:
            while not terminate.is_set():
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    filename, diarize, minspeakers,maxspeakers, return_char_alignments, outputdir = str(data,'utf-8').strip().split("\t")
                except:
                    conn.sendall(b"ERROR: Expected tab-separated fields: filename, diarize (0 or 1), minspeakers, maxspeakers, return_char_alignments (0 or 1), outputdir\n")
                    continue
                try:
                    conn.sendall(b"Processing " + os.path.basename(filename).encode('utf-8') + b" ...\n")
                    if process(filename, diarize == "1", int(minspeakers), int(maxspeakers), return_char_alignments == "1", outputdir):
                        conn.sendall(b"Finished " + os.path.basename(filename).encode('utf-8') + b"\n")
                    else:
                        conn.sendall(b"ERROR: Invalid file or file not found\n")
                except Exception as e:
                    traceback.print_exc()
                    conn.sendall(f"ERROR: {e}".encode('utf-8') + b"\n")
                #important, send EOF and close connection, client may only send one instruction per connection
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                return
    except OSError as e:
        print(f"Client connection ended: {e}", file=sys.stderr)

def main():
    global model, diarize_model, alignmodel, metadata, terminate

    # Catch signals, we must be able to terminate gracefully on request for CLAM
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Load models
    model = whisperx.load_model(model_id, device, compute_type=compute_type, language=language_code, download_root="model/")
    if not os.path.exists("model"):
        os.mkdir("model")
    alignmodel, metadata = whisperx.load_align_model(language_code=language_code, device=device, model_dir="model/")
    HF_TOKEN=os.environ.get("HF_TOKEN",None)
    if HF_TOKEN:
        diarize_model = DiarizationPipeline(token=HF_TOKEN, device=device)
    else:
        diarize_model = DiarizationPipeline(device=device)

    print("READY",file=sys.stderr);

    # Start the server, allow multiple clients
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", int(port)))
        server.listen()
        server.settimeout(0.5) #timeout needed so we can catch signals and shutdown if needed

        threads = []

        while not terminate.is_set():
            try:
                conn, _ = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            thread = threading.Thread(target=client_handler, args=(conn,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join(timeout=4)
