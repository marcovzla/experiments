import re
import sys

with open(sys.argv[1]) as f:
    for line in f:
        match = re.search(r'[OX]$', line)
        if match:
            print match.group()
        else:
            print
