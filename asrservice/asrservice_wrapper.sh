#!/usr/bin/env sh

#you can use this function as-is to handle errors
die() {
    echo "ERROR: $*">&2
    echo "Failed: $*">> "$STATUSFILE"
    exit 1
}

validate() {
    if ! echo "$1" | grep -qe '^[a-zA-Z0-9_\.-]*$'; then
        die "invalid value passed"
    fi
}

#This script will be called by CLAM and will run with the current working directory set to the specified project directory
SCRIPTDIR=$(dirname "$0")

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

if [ -n "$HF_TOKEN" ]; then
    validate "$HF_TOKEN"
    EXTRAPARAMS="--hf_token $HF_TOKEN"
    echo "HF_TOKEN: Present" >&2
else
    EXTRAPARAMS=""
    echo "HF_TOKEN: Missing" >&2
fi
GPU=0
while getopts "l:m:ds:S:g" opt "$@"; do
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
        validate "$OPTARG"
        EXTRAPARAMS="$EXTRAPARAMS --min_speakers $OPTARG"
        ;;
    S)
        validate "$OPTARG"
        EXTRAPARAMS="$EXTRAPARAMS --max_speakers $OPTARG"
        ;;
    g)
        echo "Enabling GPU">&2
        GPU=1
        ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

[ "$GPU" = "0" ] && EXTRAPARAMS="$EXTRAPARAMS --device cpu --compute_type int8"
[ -n "$LANGUAGE" ] || die "No language set"
[ -n "$MODEL" ] || die "No model set"

echo "Processing files" | tee -a "$STATUSFILE"
whisperx --model "$MODEL" --language "$LANGUAGE" $EXTRAPARAMS "$INPUTDIRECTORY/"* || die "ASR system failed"
for f in *.json; do
    base=$(basename "$f")
    if [ "$base" != "*.json" ]; then
        python3 "$SCRIPTDIR/json2ctm.py" "$f" > "$OUTPUTDIRECTORY/${base%.json}.ctm"
    fi
done
mv ./*.txt "$OUTPUTDIRECTORY/"
mv ./*.srt "$OUTPUTDIRECTORY/"
mv ./*.vtt "$OUTPUTDIRECTORY/"
mv ./*.json "$OUTPUTDIRECTORY/"
mv ./*.tsv "$OUTPUTDIRECTORY/"
mv ./*.aud "$OUTPUTDIRECTORY/"

echo "Done." >> "$STATUSFILE"
