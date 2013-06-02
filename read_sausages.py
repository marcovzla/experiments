#!/usr/bin/env python
# coding: utf-8

# code to read ASR sausages

from __future__ import division

import os, sys

datapath = sys.argv[1]

with open('refs.txt','w') as refs, open('hyps.txt', 'w') as hyps:
    for dirpath, dirnames, filenames in os.walk(datapath):
        if 'log.txt' not in filenames:
            continue
        with open(os.path.join(dirpath, 'log.txt')) as f:
            for line in f:
                if line.startswith('HYP: '):
                    hyps.write(line[5:])
                elif line.startswith('REF: '):
                    refs.write(line[5:])
