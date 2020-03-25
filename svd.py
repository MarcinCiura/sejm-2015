#!/usr/bin/python

import sqlite3
import sys

import numpy

NUMERIC_RESULTS = {
    'AYE': +1,
    'NAY': -1,
    'ABSTAIN': 0,
    'ABSENT': 0,
}


def Insert(item, collection):
  if item in collection[0]:
    return collection[0][item]
  length = len(collection[1])
  collection[0][item] = length
  collection[1].append(item)
  return length


def main():
  connection = sqlite3.connect('sejm.sqlite')
  num_columns = connection.execute(
      """SELECT COUNT(*) FROM Deputies""").fetchone()[0]
  num_rows = connection.execute(
      """SELECT COUNT(*) FROM Votings""").fetchone()[0]
  R = numpy.zeros((num_rows, num_columns), dtype=numpy.float64)
  deputies = [{}, []]
  votings = [{}, []]
  deputy_party = {}
  i = 0
  for deputy, party, voting, result in connection.execute(
      """SELECT deputy, party, voting, result
         FROM VotingResults
         JOIN Deputies USING(deputy_id)
         JOIN Parties USING(party_id)
         JOIN Votings USING(voting_id)
         JOIN Results USING(result_id)"""):
    numeric_deputy = Insert(deputy, deputies)
    numeric_voting = Insert(voting, votings)
    numeric_result = NUMERIC_RESULTS[result]
    deputy_party[numeric_deputy] = party
    R[numeric_voting, numeric_deputy] = numeric_result
    i += 1
    if i % 10000 == 0:
      sys.stderr.write('Read %d rows\r' % i)
  connection.close()
  M = R.sum(axis=1) / numpy.fabs(R).sum(axis=1)
  MT = M[:, numpy.newaxis]
  Rcentred = numpy.where(R != 0, R - MT, 0)
  U, S, VT = numpy.linalg.svd(Rcentred, full_matrices=False)
  numpy.savez_compressed('sejm', U=U, R=Rcentred)
  with open('info.py', 'w') as info:
    info.write('deputies = %r\n' % deputies[1])
    info.write('parties = %r\n' % deputy_party)
    info.write('votings=%r\n' % votings[1])


if __name__ == '__main__':
  main()
