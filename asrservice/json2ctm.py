import os
import sys
import json

# convert json file to CTM file

# in: json file (utf8, first argument on command line)
# out: ctm, tab separated (utf8, STDOUT)

ifn = sys.argv[1] # json file

f = open(ifn)
# returns JSON object as a dictionary
data = json.load(f)
f.close()
 
# no clear idea how to fill in the following fields
audiofile = 'audiofile'
channelID = 0

# write out CTM
for s in data['segments']:
  for s2 in s['words']:
    print(audiofile, end='\t')
    print(channelID, end='\t')
    print(s2['start'], end='\t')
    print(s2['end'], end='\t')
    print(s2['text'], end='\t')
    print(s2['confidence'], end='')
    print()
  print() # next utterance
