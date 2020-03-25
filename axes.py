#!/usr/bin/python

import pprint

import info
import numpy


def main():
  with numpy.load('sejm.npz') as sejm:
    U = sejm['U']
  UU = U.transpose()
  for i in xrange(3):
    values = []
    for j in xrange(len(UU[i])):
      values.append((UU[i][j], info.votings[j]))
    values.sort()
    print 'Axis %d' % i
    pprint.pprint(values[:5])
    pprint.pprint(values[-1:-6:-1])


if __name__ == '__main__':
  main()
