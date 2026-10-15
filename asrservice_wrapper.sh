#!/bin/sh

diarize=0
minspeakers=0
maxspeakers=0
charalign=0
outputdir=

while getopts "dcmMpo:" opt; do
    case $opt in
        d) diarize=1 ;;
        c) charalign=1 ;;
        o) outputdir=$OPTARG ;;
        m) minspeakers=$OPTARG ;;
        M) maxspeakers=$OPTARG ;;
        p) port=$OPTARG ;;
        :) printf 'Option -%s requires an argument\n' "$OPTARG" >&2;
           exit 2 ;;
        *) printf 'Invalid option %s' "$OPT" >&2; exit 2 ;;
    esac
done
shift "$((OPTIND - 1))"

if [ -z "$port" ]; then
    echo "ERROR: Missing port">&2
fi
if [ -z "$outputdir" ]  || [ ! -d "$outputdir" ]; then
    echo "ERROR: Outputdir not provided or does not exist">&2
    exit 2
fi

for f in "$@"; do
    f="$(realpath "$f")"
    printf "%s\t%s\t%s\t%s\t%s\t%s"  "$f" "$diarize" "$minspeakers" "$maxspeakers" "$charalign" "$outputdir" | socat -t 2 - "tcp:localhost:$port" >&2
done
