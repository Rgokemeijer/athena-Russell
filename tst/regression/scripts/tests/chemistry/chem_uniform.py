#regression test for equilibrium chemistry and temperature in uniform density 
#and radiation field.
#compare to know solution.

# Modules
import logging
import numpy as np                             # standard Python module for numerics
import sys                                     # standard Python module to change path
import scripts.utils.athena as athena          # utilities for running Athena++
import scripts.utils.comparison as comparison  # more utilities explicitly for testing
sys.path.insert(0, '../../vis/python')         # insert path to Python read scripts
import athena_read                             # utilities for reading Athena++ data
import os
logger = logging.getLogger('athena' + __name__[7:])  # set logger name based on module

def prepare(**kwargs):
  athena.configure(
      prob='uniform_chem',
      chemistry='gow16', 
      radiation='const',
      cxx = 'g++',
      cvode_path=os.environ['CVODE_PATH']
      )
  athena.make()

def run(**kwargs):
  arguments = [ 
          'problem/G0=1e-6',
          'chemistry/maxsteps=100000',
          'chemistry/reltol=1e-6',
          'mesh/nx1=4',
          'mesh/nx2=4',
          'mesh/nx3=4'
          ]
  athena.run('chemistry/athinput.uniform_chem', arguments)

def analyze():
  err_control = 1e-6
  gam1 = 1.666666666666667 - 1.
  _,_,_,data_ref = athena_read.vtk('data/chem_uniform_G1e-6.vtk')
  _,_,_,data_new = athena_read.vtk('bin/uniform_chem.block0.out1.00010.vtk')
  species = ["He+", "OHx", "CHx", "CO", "C+", "HCO+", "H2", "H+", "H3+", "H2+", 
             "O+", "Si+"]
  ns = len(species)
  err_all = np.zeros(ns+1)
  for i in xrange(ns):
    s = species[i]
    xs_ref = data_ref[s]
    xs_new = data_new["r"+s]
    err_all[i] = (abs(xs_ref - xs_new) / abs(xs_ref) ).max()
  E_ref = data_ref["E"]
  E_new = data_new["press"]/gam1
  err_all[ns] = (abs(E_ref - E_new) / abs(E_ref) ).max()
  err_max = err_all.max()
  if err_max < err_control:
    return True
  else:
    print "err_max", err_max
    return False
