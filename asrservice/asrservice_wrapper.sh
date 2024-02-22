#!/usr/bin/env sh

#you can use this function as-is to handle errors
die() {
    echo "ERROR: $*">&2
    echo "Failed: $*">> "$STATUSFILE"
    exit 1
}

#This script will be called by CLAM and will run with the current working directory set to the specified project directory


#this script takes three arguments from CLAM: $STATUSFILE $INPUTDIRECTORY $OUTPUTDIRECTORY. (as configured at COMMAND= in the service configuration file)
STATUSFILE=$1
INPUTDIRECTORY=$2
OUTPUTDIRECTORY=$3
shift 3

# If $PARAMETERS was passed via COMMAND= in the service configuration file;
# the remainder of the arguments in $@ are now custom parameters for which you either need to do your own parsing, or you pass them directly to your application

#Output a status message to the status file that users will see in the interface
echo "Starting..." >> "$STATUSFILE"

#Example parameter parsing using getopt:

if [ -n "$HF_TOKEN" ] ; then
    EXTRAPARAMS="--hf_token \"$HF_TOKEN\""
else
    EXTRAPARAMS=""
fi
while getopts "l:m:ds:S:" opt "$@"; do
  case $opt in
    l)
        LANGUAGE=$OPTARG;
        ;;
    m)
        MODEL=$OPTARG;
        ;;
    d)
        EXTRAPARAMS="$EXTRAPARAMS --diarize"
        ;;
    s)
        EXTRAPARAMS="$EXTRAPARAMS --min_speakers \"$OPTARG\""
        ;;
    S)
        EXTRAPARAMS="$EXTRAPARAMS --max_speakers \"$OPTARG\""
        ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

[ -n "$LANGUAGE" ] || die "No language set"
[ -n "$MODEL" ] || die "No model set"

echo "Processing files" | tee -a "$STATUSFILE"
whisperx --model "$MODEL" --language "$LANGUAGE" --compute_type int8 $EXTRAPARAMS "$INPUTDIRECTORY/"* || die "ASR system failed"
mv ./*.txt "$OUTPUTDIRECTORY/"
mv ./*.srt "$OUTPUTDIRECTORY/"
mv ./*.vtt "$OUTPUTDIRECTORY/"
mv ./*.json "$OUTPUTDIRECTORY/"
mv ./*.tsv "$OUTPUTDIRECTORY/"
mv ./*.aud "$OUTPUTDIRECTORY/"

echo "Done." >> "$STATUSFILE"
