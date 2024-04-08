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
 
channelID = 0

# write out CTM
for s in data['segments']:
  for s2 in s['words']:
    print(os.path.basename(ifn).replace(".json",""), end='\t')
    print(channelID, end='\t')
    print(s2['start'], end='\t')
    print(round(s2['end'] - s2['start'],3), end='\t')
    print(s2['word'], end='\t')
    print(s2['score'])
  print() # next utterance
