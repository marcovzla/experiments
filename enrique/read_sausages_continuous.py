#!/usr/bin/env python
# coding: utf-8

from __future__ import division

import os
import re
from glob import glob
from operator import mul
from itertools import product
import numpy as np
from nltk.probability import DictionaryProbDist, entropy
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, StrictGlobalSequenceAligner



class Example(object):
    SPECIAL_TOKENS = ('<s>', '</s>', '*DELETE*')

    def __init__(self, ref, hyp, fname):
        self.dataset = os.path.basename(os.path.dirname(os.path.dirname(fname)))
        self.name = os.path.splitext(os.path.basename(fname))[0]
        self.ref_log = ref
        self.hyp_log = hyp
        self.sausage = parse_sausage(fname)

    def description(self):
        s = 'dataset: %s\n' % self.dataset
        s += 'name: %s\n' % self.name
        s += 'ref: %s\n' % self.ref()
        hyp = self.best_hyp()
        s += 'hyp: %s\n' % hyp
        s += 'hyp score: %s\n' % self.score_hyp(hyp)
        s += 'correct: %s\n' % self.correct()
        s += 'labels: %s\n' % self.get_labels()
        return s

    def ref(self):
        """returns ref as an array of tokens"""
        # remove * and make all lowercase
        return re.sub(r'\*+', '', self.ref_log).lower().split()

    def best_hyp(self):
        """returns the best hyp for the sausage"""
        return [dist.max() for dist in self.sausage]

    def all_hyps(self):
        """generate all possible hyps in any order"""
        return product(*[dist.samples() for dist in self.sausage])

    def score_hyp(self, hyp):
        """returns score for hyp"""
        # multiply posterior probability for each token in hyp
        return reduce(mul, [dist.prob(tok) for dist,tok in zip(self.sausage, hyp)])

    def nbest(self, n=None):
        """returns nbest hyps sorted by score in descending order"""
        scored_hyps = [(self.score_hyp(hyp), hyp) for hyp in self.all_hyps()]
        scored_hyps = sorted(scored_hyps, reverse=True)
        # you can get the n-best only, but we always score them all
        return scored_hyps[:n] if n is not None else scored_hyps

    def clean_hyp(self, hyp):
        """remove tokens that aren't words"""
        return filter(lambda tok: tok not in self.SPECIAL_TOKENS, hyp)

    def correct(self):
        """did the asr system got this right?"""
        return self.ref() == self.clean_hyp(self.best_hyp())

    def num_slots(self):
        return len(self.sausage)

    def get_labels(self):
        """label each slot in the sausage (O=correct X=incorrect)"""
        if self.correct():
            # everything is correct
            return ['O'] * self.num_slots()

        # align the ref and the best hyp
        a = Sequence(self.ref())
        b = Sequence(self.best_hyp())
        v = Vocabulary()
        aEncoded = v.encodeSequence(a)
        bEncoded = v.encodeSequence(b)
        scoring = SimpleScoring(2, -1)
        aligner = StrictGlobalSequenceAligner(scoring, -2)
        score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)
        alignment = v.decodeSequenceAlignment(encodeds[0])

        # get labels according to alignment
        labels = []
        for a,b in zip(alignment.first, alignment.second):
            if a == b or a == '-' and b == '*DELETE*':
                labels.append('O')
            else:
                labels.append('X')
        return labels

    def get_features(self):
        """get sausage features as a list of dicts"""
        features = []
        for i,slot in enumerate(self.sausage):
            feats = {}
            best = slot.max()
            probs = [slot.prob(s) for s in slot.samples()]
            # length of the sausage
            feats['sausage_length'] = len(self.sausage)
            # position of this slot in the sausage
            feats['slot_position'] = i
            # mean of slot arc posteriors
            feats['slot_mean'] = np.mean(probs)
            # standard deviation of slot arc posteriors
            feats['slot_stdev'] = np.std(probs)
            # entropy of slot arc posteriors
            feats['slot_entropy'] = entropy(slot)
            # highest posterior in slot
            feats['slot_highest'] = slot.prob(best)
            # length of highest posterior word in slot
            feats['slot_best_length'] = 0 if best == '*DELETE*' else len(best)
            # 1 if highest posterior arc is *DELETE*
            feats['delete'] = int(best == '*DELETE*')
            features.append(feats)
        return features



def parse_sausage(fname):
    """gets the filename of a sausage and returns a list of probability distributions"""
    sausage = []
    with open(fname) as f:
        for line in f:
            if line.startswith('align'):
                # align a w1 p1 w2 p2 ...
                # split line and ignore first two tokens
                bits = line.split()[2:]
                dist = DictionaryProbDist({w:float(p) for w,p in zip(bits[::2],bits[1::2])})
                sausage.append(dist)

    # remove sentence boundaries
    assert sausage[0].samples() == ['<s>']
    assert sausage[-1].samples() == ['</s>']
    sausage = sausage[1:-1]

    return sausage



def parse_log(fname):
    refs = []
    hyps = []
    filenames = []
    dirname = os.path.dirname(fname)
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if line.startswith('FILENAME:'):
                # get filename of wav file
                basename = os.path.basename(line[10:])
                # replace extension
                basename = os.path.splitext(basename)[0] + '.sausage'
                # get absolute path
                filenames.append(os.path.join(dirname, 'sausages', basename))
            elif line.startswith('REF:'):
                refs.append(line[5:])
            elif line.startswith('HYP:'):
                hyps.append(line[5:])
    return refs, hyps, filenames



def get_examples(fname):
    examples = []
    refs, hyps, filenames = parse_log(fname)
    for ref, hyp, sausage_file in zip(refs, hyps, filenames):
        examples.append(Example(ref, hyp, sausage_file))
    return examples



def train_test_split(data, test_size=0.3):
    np.random.shuffle(data)
    split = int(len(data) * (1-test_size))
    return data[:split], data[split:]



# def quantize(vals, bins=10):
#     minval = min(vals)
#     maxval = max(vals)
#     step = (maxval-minval) / bins
#     return np.arange(bins) * step + minval

# def best_bin(val, bins):
#     retval = None
#     for b in bins:
#         if b > val:
#             break
#         retval = b
#     return '%.2f' % retval


def create_corpus(fname, examples):
    features = [e.get_features() for e in examples]
    labels = [e.get_labels() for e in examples]

    qq = {}
    qq['slot_mean'] = [f['slot_mean'] for feats in features for f in feats] #quantize([f['slot_mean'] for feats in features for f in feats])
    qq['slot_stdev'] = [f['slot_stdev'] for feats in features for f in feats] #quantize([f['slot_stdev'] for feats in features for f in feats])
    qq['sausage_length'] = [f['sausage_length'] for feats in features for f in feats] #quantize([f['sausage_length'] for feats in features for f in feats])
    qq['slot_entropy'] = [f['slot_entropy'] for feats in features for f in feats] #quantize([f['slot_entropy'] for feats in features for f in feats])
    qq['slot_highest'] = [f['slot_highest'] for feats in features for f in feats] #quantize([f['slot_highest'] for feats in features for f in feats])

    with open(fname, 'w') as f:
        for e in examples:
            for feats, label in zip(e.get_features(), e.get_labels()):
                line = ''
                for k in sorted(feats):
                    line += '%s=%s ' % (k, feats[k])
                line += label
                line += '\n'
                f.write(line)
            f.write('\n')



if __name__ == '__main__':
    examples = []
    for fname in glob('output_sausages/*/log.txt'):
        examples += get_examples(fname)
    # for e in examples:
    #     labels = e.get_labels()
    #     Os = sum(1 for l in labels if l == 'O')
    #     Xs = sum(1 for l in labels if l == 'X')
    #     if Os < Xs:
    #         print e.description()
    train, test = train_test_split(examples)
    create_corpus('train.txt', train)
    create_corpus('test.txt', test)
