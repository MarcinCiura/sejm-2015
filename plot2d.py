#!/usr/bin/python

import collections
import re
import sys

import info
from matplotlib import animation
from matplotlib import patches
from matplotlib import pyplot as plt
import numpy


PARTY_COLOR = {
    'PO': '#FCA241',
    'PiS': '#073A76',
    'SLD': '#E2001A',
    'PSL': '#1BB100',
    'RP': '#D06700',
    'ZP': '#6ACECB',
    'KPSP': '#BBBBBB',
    'TR': '#BBBBBB',
    'niez.': '#BBBBBB',
}

PARTIES = ['PO', 'PiS', 'SLD', 'PSL', 'RP', 'ZP', 'niez.']

name_translation = {}


def FillNameTranslation():
  names = collections.defaultdict(list)
  for name in info.deputies:
    if name.startswith('VAN DER COGHEN'):
      surname = 'van der Coghen'
    else:
      surname1 = []
      split = re.split(r'([ -])', name)
      for i, n in enumerate(split):
        if n == u' ':
          first = ''.join([x[0] for x in split[i:] if x != u' '])
          break
        surname1.append(n.capitalize())
      surname = ''.join(surname1)
    name_translation[name] = [surname, first]
    names[surname].append(name)
  for surname in names:
    if len(names[surname]) == 1:
      del name_translation[names[surname][0]][1:]


def PlotXY():
  plt.clf()
  ax = fig.add_subplot(111)
  for i, (x, y, z) in enumerate(deputies):
    color = PARTY_COLOR[info.parties[i]]
    ax.scatter(x, y, c=color, marker='o', s=5, linewidths=0)
    deputy = ' '.join(name_translation[info.deputies[i]])
    plt.annotate(deputy, xy=(x, y), fontsize=6, color=color)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_xlim(-70, +60)
  ax.set_ylim(-20, +50)
  plt.figlegend(legend_handles, PARTIES, 'upper right', fontsize=8)

def PlotXZ():
  plt.clf()
  ax = fig.add_subplot(111)
  for i, (x, y, z) in enumerate(deputies):
    color = PARTY_COLOR[info.parties[i]]
    ax.scatter(x, z, c=color, marker='o', s=5, linewidths=0)
    deputy = ' '.join(name_translation[info.deputies[i]])
    plt.annotate(deputy, xy=(x, z), fontsize=6, color=color)
  ax.set_xlabel('x')
  ax.set_ylabel('z')
  ax.set_xlim(-70, +60)
  ax.set_ylim(-30, +40)
  plt.figlegend(legend_handles, PARTIES, 'upper right', fontsize=8)

def PlotYZ():
  plt.clf()
  ax = fig.add_subplot(111)
  for i, (x, y, z) in enumerate(deputies):
    color = PARTY_COLOR[info.parties[i]]
    ax.scatter(y, z, c=color, marker='o', s=5, linewidths=0)
    deputy = ' '.join(name_translation[info.deputies[i]])
    plt.annotate(deputy, xy=(y, z), fontsize=6, color=color)
  ax.set_xlabel('y')
  ax.set_ylabel('z')
  ax.set_xlim(-20, +50)
  ax.set_ylim(-30, +40)
  plt.figlegend(legend_handles, PARTIES, 'upper right', fontsize=8)


def main():
  FillNameTranslation()
  with numpy.load('sejm.npz') as sejm:
    R = sejm['R']
    U = sejm['U']
  UU = U[:, :3].transpose()
  global deputies
  deputies = UU.dot(R).transpose()
  global fig, legend_handles
  fig = plt.figure(figsize=(16, 12))
  legend_handles = [
      patches.Circle((0.5, 0.5), color=PARTY_COLOR[x]) for x in PARTIES]
  PlotXY()
  plt.savefig('sejm-xy.png')
  PlotXZ()
  plt.savefig('sejm-xz.png')
  PlotYZ()
  plt.savefig('sejm-yz.png')


if __name__ == '__main__':
  main()
