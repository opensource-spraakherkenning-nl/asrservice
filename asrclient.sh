#!/bin/sh

die()  {
    echo "$@"
    exit 2
}

usage() {
    printf 'Usage: %s [-U url] [-u username] [-p password] [-l language] [wav-files...]\n' "$0" >&2
    exit 2
}

command -v curl > /dev/null || die "missing dependency: curl (please install via your package manager)"
command -v jq > /dev/null || die "missing dependency: jq (please install via your package manager)"
command -v uuidgen > /dev/null || die "missing dependency: uuidgen (please install via your package manager)"

username=
password=
URL=
language=en

while getopts 'hu:p:U:l:' opt; do
    case $opt in
        U) URL=$OPTARG ;;
        u) username=$OPTARG ;;
        p) password=$OPTARG ;;
        l) language=$OPTARG ;;
        h) usage ;;
        \?) usage ;;
        :) usage ;;
    esac
done

die_with_cleanup() {
    message="$*"
    if [ -n "$username" ] && [ -n "$password" ]; then
        set -- --fail-with-body --header "Accept: application/json" --basic --user "$username:$password"
    else
        set -- --fail-with-body --header "Accept: application/json"
    fi
    echo "Cleanup after failure...">&2
    curl -sS -X DELETE "$@" --header "Accept: application/json" "$URL/$language/$project" || echo "Cleanup failed">&2
    die "$message"
}

shift "$((OPTIND - 1))"
files=$(find "$@")
if [ -n "$username" ] && [ -n "$password" ]; then
    set -- --http1.1 --fail-with-body --header "Accept: application/json" --basic --user "$username:$password"
else
    set -- --http1.1 --fail-with-body --header "Accept: application/json"
fi

if [ "$#" -eq 0 ]; then
    die "No files specified"
fi

if [ -z "$URL" ]; then
    die "No URL specified"
fi


#Random project name
project=$(uuidgen)

#create a project
echo "Creating project $project">&2
curl -sS -X PUT "$@" "$URL/$language/$project" || die "Failed to create project"

#shellcheck disable=SC2086
for f in $files; do
    #upload files
    echo "Uploading $f">&2
    curl -vS -X PUT "$@" --header "Content-Type: audio/wav" "$URL/$language/$project/inputwav/$(basename "$f")" --data-binary "@$f" || die_with_cleanup "Failed to upload file $f"
done

#start project
curl -sS -X POST "$@" --form "diarization=1" "$URL/$language/$project"

#poll project at regular intervals until it is marked as done
response=
while true; do
    echo "Polling...">&2
    response=$(curl -sS -X GET "$@" "$URL/$language/$project") || die_with_cleanup "Failed to poll project"
    stage=$(echo "$response" | jq -r '.stage')
    echo " Status is $stage ...">&2
    message=$(echo "$response" | jq -r ".data.message")
    echo " $message" >&2
    if [ "$stage" = "Done" ]; then
        break
    fi
    sleep 1
done

success=$(echo "$response" | jq -r ".data.success")
case "$success" in
    0|false)
        message=$(echo "$response" | jq -r ".data.message")
        die_with_cleanup "Project failed with error: $message ..."
        ;;
esac

#retrieve output files
output_files=$(echo "$response" | jq -r ".data.output_files[].name")
for f in $output_files; do
    echo "Downloading $f ...">&2
    curl -sS -X GET "$@" "$URL/$language/$project/output/$f" || die_with_cleanup "Failed to download file $f"
done

#delete project
echo "Deleting project ...">&2
curl -sS -X DELETE "$@" --header "Accept: application/json" "$URL/$language/$project" || echo "Cleanup failed">&2
