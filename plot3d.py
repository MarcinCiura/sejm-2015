#!/usr/bin/python

import sys

import info
from matplotlib import animation
from matplotlib import patches
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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

NUM_FRAMES = 20


def Plot(nframe):
  sys.stderr.write('Drawing frame %d\r' % nframe)
  plt.clf()
  ax = fig.add_subplot(111, projection='3d')
  for i, (x, y, z) in enumerate(deputies):
    color = PARTY_COLOR[info.parties[i]]
    ax.scatter(x, y, z, c=color, marker='o', s=20, linewidths=0.5)
#    ax.scatter(x, z, c=color, marker='o', zdir='y', zs=+50, s=5, linewidths=0)
#    ax.scatter(y, z, c=color, marker='o', zdir='x', zs=-70, s=5, linewidths=0)
#    ax.scatter(x, y, c=color, marker='o', zdir='z', zs=-30, s=5, linewidths=0)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_zlabel('z')
  ax.set_xlim(-70, +60)
  ax.set_ylim(-20, +50)
  ax.set_zlim(-30, +40)
  if nframe <= NUM_FRAMES:
    azim = -50 + nframe * 1.0
  else:
    azim = -50 + (2 * NUM_FRAMES - nframe) * 1.0
  ax.view_init(elev=30, azim=azim)
  plt.figlegend(legend_handles, PARTIES, 'upper right', fontsize=8)


def main():
  with numpy.load('sejm.npz') as sejm:
    R = sejm['R']
    U = sejm['U']
  UU = U[:, :3].transpose()
  global deputies
  deputies = UU.dot(R).transpose()
  global fig, legend_handles
  fig = plt.figure(figsize=(6.4, 4.8))
  legend_handles = [
      patches.Circle((0.5, 0.5), color=PARTY_COLOR[x]) for x in PARTIES]
  anim = animation.FuncAnimation(fig, Plot, frames=2 * NUM_FRAMES)
  anim.save('sejm3d.gif', writer='imagemagick', fps=12.5)


if __name__ == '__main__':
  main()
