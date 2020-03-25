#!/usr/bin/python
# -*- coding: utf-8 -*-

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


def InitDatabase(connection):
  connection.executescript("""
DROP TABLE IF EXISTS Results;
CREATE TABLE Results(
  result_id INTEGER PRIMARY KEY,
  result TEXT NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS ResultIndex ON Results(result);

DROP TABLE IF EXISTS Parties;
CREATE TABLE Parties(
  party_id INTEGER PRIMARY KEY,
  party TEXT NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS PartyIndex ON Parties(party);

DROP TABLE IF EXISTS Deputies;
CREATE TABLE Deputies(
  deputy_id INTEGER PRIMARY KEY,
  deputy TEXT NOT NULL,
  party_id INTEGER NOT NULL REFERENCES Parties(party_id));
CREATE UNIQUE INDEX DeputyIndex ON Deputies(deputy);

DROP TABLE IF EXISTS Votings;
CREATE TABLE Votings(
  voting_id INTEGER PRIMARY KEY,
  voting TEXT NOT NULL);
CREATE UNIQUE INDEX VotingIndex ON Votings(voting);

DROP TABLE IF EXISTS VotingResults;
CREATE TABLE VotingResults(
  id INTEGER PRIMARY KEY,
  voting_id INTEGER NOT NULL REFERENCES Votings(voting_id),
  deputy_id INTEGER NOT NULL REFERENCES Deputies(deputy_id),
  result_id INTEGER NOT NULL REFERENCES Results(result_id));

  PRAGMA foreign_keys = ON;
""")


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


def Insert(table, column, value, cursor):
  cursor.execute(
      """INSERT OR IGNORE INTO %s(%s) VALUES (?)""" %
      (table, column), (value,))
  if cursor.rowcount:
    return cursor.lastrowid
  return cursor.execute(
      """SELECT %s_id FROM %s WHERE %s = ?""" %
      (column, table, column), (value,)).fetchone()[0]


def SaveRecord(voting, deputy, party, result, cursor):
  voting_id = Insert('Votings', 'voting', voting, cursor)
  result_id = Insert('Results', 'result', result, cursor)
  party_id = Insert('Parties', 'party', party, cursor)
  cursor.execute(
      """INSERT OR IGNORE INTO Deputies(deputy, party_id) VALUES (?, ?)""",
      (deputy, party_id))
  if cursor.rowcount:
    deputy_id = cursor.lastrowid
  else:
    deputy_id = cursor.execute(
       """SELECT deputy_id FROM Deputies WHERE deputy = ?""",
       (deputy,)).fetchone()[0]
    cursor.execute(
        """UPDATE Deputies SET party_id = ? WHERE deputy_id = ?""",
        (party_id, deputy_id))
  cursor.execute(
      """INSERT INTO VotingResults(voting_id, deputy_id, result_id)
         VALUES (?, ?, ?)""", (voting_id, deputy_id, result_id))


def Process(filename, connection):
  sys.stderr.write('Processing file %s\n' % filename)
  cursor = connection.cursor()
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
        SaveRecord(filename, name, party, result, cursor)
      else:
        name = CleanUp(line)
  connection.commit()
  if party is None:
    sys.stderr.write('File %s is in a different format\n' % filename)
    return
  if num_votes not in (460, 459, 458, 457, 454, 452, 444):
    sys.stderr.write(
        'Bad number of votes in file %s: %d\n' % (filename, num_votes))
    sys.exit(1)


def main():
  connection = sqlite3.connect('sejm.sqlite')
  InitDatabase(connection)
  votings = glob.glob('data/glos_*_*.html')
  votings.sort(key=NaturalSort)
  for filename in votings:
    Process(filename, connection)
  connection.close()


if __name__ == '__main__':
  main()
