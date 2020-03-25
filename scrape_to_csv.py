#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import glob
import re
import sqlite3
import sys


FILENAME_RE = re.compile(r'glos_([0-9]+)_([0-9]+)\.html$')
PARTY_RE = re.compile(
    r'<b>([A-Za-z.]+)(?: |&#160;)\([0-9]+\)&#160;</b><br/>\n$')
RESULT_RE = re.compile(r'(za|pr\.|ws\.|ng\.)&#160;<br/>\n$')

RESULTS = {
    'za': 'AYE',
    'pr.': 'NAY',
    'ws.': 'ABSTAIN',
    'ng.': 'ABSENT',
}


def NaturalSort(filename):
  match = FILENAME_RE.search(filename)
  return (int(match.group(1)), int(match.group(2)))


def CleanUp(line):
  if not line.endswith('&#160;<br/>\n'):
    return None
  name = line[:-12].replace('&#160;', ' ').replace('  ', ' ').decode('utf-8')
  return {
      u'KAMIŃSKI MARIUSZ S. ARKADIUSZA': u'KAMIŃSKI MARIUSZ',
      u'KAMIŃSKI MARIUSZ S. LESŁAWA': u'KAMIŃSKI MARIUSZ ANTONI',
      u'TRYBUŚ ALEKSANDRA': u'TRYBUŚ-CIEŚLAR ALEKSANDRA',
  }.get(name, name)


def SaveRecord(voting, deputy, party, result, writer):
  writer.writerow(
      [voting[10:-5], deputy.encode('utf-8'), party.encode('utf-8'), result])


def Process(filename, writer):
  sys.stderr.write('Processing file %s\n' % filename)
  with open(filename) as voting:
    party = None
    num_votes = 0
    name = None
    lines = voting.readlines()
    for line in lines:
      match = PARTY_RE.search(line)
      if match:
        party = match.group(1)
      if party is None:
        continue
      match = RESULT_RE.match(line)
      if match:
        assert name is not None
        result = RESULTS[match.group(1)]
        num_votes += 1
        SaveRecord(filename, name, party, result, writer)
      else:
        name = CleanUp(line)
  if party is None:
    sys.stderr.write('File %s is in a different format\n' % filename)
    return
  if num_votes not in (460, 459, 458, 457, 454, 452, 444):
    sys.stderr.write(
        'Bad number of votes in file %s: %d\n' % (filename, num_votes))
    sys.exit(1)


def main():
  votings = glob.glob('data/glos_*_*.html')
  votings.sort(key=NaturalSort)
  with open('sejm.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    for filename in votings:
      Process(filename, writer)


if __name__ == '__main__':
  main()
