#!/usr/bin/env python
# coding: utf-8

# The Switchboard Corpus in NXT
# http://groups.inf.ed.ac.uk/switchboard/

from __future__ import division

import os
import re
from lxml import etree
import numpy as np
import pandas as pd
from nltk.tree import Tree



# set the path to the switchboard corpus
CORPUS_PATH = '/home/marco/research_data/nxt_switchboard_ann'
DATADIR = os.path.join(CORPUS_PATH, 'xml')

# dialog agents
AGENTS = ('A', 'B')

# namespace
NS = '{http://nite.sourceforge.net/}'



def get_dialog_ids():
    """returns a list with all available dialog names"""
    fname = os.path.join(DATADIR, 'corpus-resources', 'dialogues.xml')
    tree = etree.parse(fname)
    return [e.attrib['swbdid'] for e in tree.iterfind('dialogue')]



def get_dialogs():
    """returns dataframe with all dialogs data"""
    return pd.concat([get_dialog(id) for id in get_dialog_ids()])



def get_topics():
    """return each dialog topic"""
    fname = os.path.join(DATADIR, 'corpus-resources', 'dialogues.xml')
    dialogs = etree.parse(fname).getroot()
    fname = os.path.join(DATADIR, 'corpus-resources', 'topics.xml')
    topics = etree.parse(fname).getroot()
    results = {}
    for e in dialogs.iterchildren():
        dialog_id = e.attrib['swbdid']
        ptr = e.xpath('nite:pointer[@role="topic"]',
                      namespaces=dialogs.nsmap)[0]
        topic_id = re.search(r'\((.+)\)$', ptr.attrib['href']).group(1)
        topic = topics.xpath('topic[@nite:id="%s"]' % topic_id,
                             namespaces=topics.nsmap)[0]
        results[dialog_id] = topic.attrib['abstract']
    return results



# get topics
TOPICS = get_topics()

def get_dialog(dialog_id):
    """returns dataframe with dialog data"""
    terms = get_terminals_for_dialog(dialog_id)
    dialog_acts = get_dialacts_for_dialog(dialog_id)
    dialog = terms.merge(dialog_acts, 'left')
    dialog['dialog_id'] = dialog_id
    dialog['topic'] = TOPICS[dialog_id]
    return dialog



def get_terminals_for_dialog(dialog_id, agent=None):
    """returns a dataframe with the terminals data"""

    if not agent:
        # concatenate all agents terminals
        # and sort them by sentence_id and term_id
        tt = [get_terminals_for_dialog(dialog_id, a) for a in AGENTS]
        df = pd.concat(tt, ignore_index=True)
        return df.sort(('sentence_id','terminal_id')).reset_index(drop=True)

    terminals = []
    fname = os.path.join(DATADIR, 'terminals',
                         'sw%s.%s.terminals.xml' % (dialog_id, agent))
    tree = etree.parse(fname)

    # collect terminals for a specific dialog and agent
    for e in tree.getroot().iterchildren():
        tag = e.tag
        sid, tid = parse_term_id(e.attrib[NS+'id'])
        term = dict(sentence_id=sid, terminal_id=tid, tag=tag, agent=agent)
        if tag in ('sil','punc','trace'):
            term['orth'] = e.text or np.nan
            term['pos'] = np.nan
        else:
            term['orth'] = e.attrib['orth']
            term['pos'] = e.attrib['pos']
        terminals.append(term)

    return pd.DataFrame(terminals)



def get_dialacts_for_dialog(dialog_id, agent=None):
    """returns a dataframe with dialog acts"""

    if not agent:
        # return dial acts for dialog (all agents)
        dd = [get_dialacts_for_dialog(dialog_id, a) for a in AGENTS]
        df = pd.concat(dd, ignore_index=True)
        df = df.sort(('dialog_act_id','terminal_id'))
        return df.reset_index(drop=True)

    fname = os.path.join(DATADIR, 'dialAct',
                         'sw%s.%s.dialAct.xml' % (dialog_id, agent))
    tree = etree.parse(fname)
    dial_acts = []

    # collect dialog acts for dialog and agent
    for e in tree.getroot().iterchildren():
        nite = e.attrib['niteType']
        swbd = e.attrib['swbdType']
        daid = int(e.attrib[NS+'id'][2:])
        for child in e.iterchildren():
            term_id = re.search(r's\d+_\d+', child.attrib['href']).group()
            sid, tid = parse_term_id(term_id)
            da = dict(sentence_id=sid, terminal_id=tid, nite_type=nite,
                      swbd_type=swbd, dialog_act_id=daid)
            dial_acts.append(da)

    return pd.DataFrame(dial_acts)



def parse_term_id(s):
    """returns sentence and terminal id
    from a string of the form `s##_##`"""
    sid, tid = s[1:].split('_')
    return int(sid), int(tid)






if __name__ == '__main__':
    print 'reading data ...'
    dialogs = get_dialogs()
    print 'writing data ...'
    dialogs.to_csv('swbd.csv', index=False)
    print 'wrote swbd.csv'
