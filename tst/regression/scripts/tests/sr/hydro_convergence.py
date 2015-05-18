# Test script for relativistic hydro convergence

# Modules
import numpy as np
import math
import scripts.utils.athena as athena
import scripts.utils.comparison as comparison

# Parameters
wave_flags = range(5)
res_low = 64
res_high = 512
cutoff = 1.8
amp = 1.0e-6
gamma_adi = 4.0/3.0
rho = 4.0
pgas = 1.0
vx = 0.1
vy = 0.3
vz = -0.05

# Prepare Athena++
def prepare():
  athena.configure('s',
      prob='linear_wave_rel',
      coord='cartesian',
      flux='hllc')
  athena.make()

# Run Athena++
def run():
  wavespeeds = wavespeeds_hydro()
  for wave_flag in wave_flags:
    time = 1.0 / abs(wavespeeds[wave_flag])
    arguments = [
        'job/problem_id=sr_hydro_wave_{0}_low'.format(wave_flag),
        'mesh/nx1=' + repr(res_low),
        'time/tlim=' + repr(time),
        'output1/dt=' + repr(time),
        'fluid/gamma=' + repr(gamma_adi),
        'problem/rho=' + repr(rho), 'problem/pgas=' + repr(pgas),
        'problem/vx=' + repr(vx), 'problem/vy=' + repr(vy), 'problem/vz=' + repr(vz),
        'problem/wave_flag=' + repr(wave_flag), 'problem/amp=' + repr(amp)]
    athena.run('hydro_sr/athinput.linear_wave', arguments)
    arguments[0] = 'job/problem_id=sr_hydro_wave_{0}_high'.format(wave_flag)
    arguments[1] = 'mesh/nx1=' + repr(res_high)
    athena.run('hydro_sr/athinput.linear_wave', arguments)

# Analyze outputs
def analyze():

  # Specify tab file columns
  headings = ('x', 'rho', 'pgas', 'vx', 'vy', 'vz')

  # Check that convergence is attained for each wave
  for wave_flag in wave_flags:

    # Read low and high resolution initial and final states
    prim_initial_low = athena.read_tab(
        'bin/sr_hydro_wave_{0}_low.block0.out1.00000.tab'.format(wave_flag),
        headings=headings, dimensions=1)
    prim_initial_high = athena.read_tab(
        'bin/sr_hydro_wave_{0}_high.block0.out1.00000.tab'.format(wave_flag),
        headings=headings, dimensions=1)
    prim_final_low = athena.read_tab(
        'bin/sr_hydro_wave_{0}_low.block0.out1.00001.tab'.format(wave_flag),
        headings=headings, dimensions=1)
    prim_final_high = athena.read_tab(
        'bin/sr_hydro_wave_{0}_high.block0.out1.00001.tab'.format(wave_flag),
        headings=headings, dimensions=1)

    # Calculate overall errors for low and high resolution runs
    epsilons_low = []
    epsilons_high = []
    for quantity in headings[1:]:
      qi = prim_initial_low[quantity][0,0,:]
      qf = prim_final_low[quantity][0,0,:]
      epsilons_low.append(math.fsum(abs(qf-qi)) / res_low)
      qi = prim_initial_high[quantity][0,0,:]
      qf = prim_final_high[quantity][0,0,:]
      epsilons_high.append(math.fsum(abs(qf-qi)) / res_high)
    epsilons_low = np.array(epsilons_low)
    epsilons_high = np.array(epsilons_high)
    epsilon_low = (math.fsum(epsilons_low**2) / len(epsilons_low))**0.5 / amp
    epsilon_high = (math.fsum(epsilons_high**2) / len(epsilons_high))**0.5 / amp

    # Test fails if convergence is not at least that specified by cutoff
    if epsilon_high / epsilon_low > (float(res_low) / float(res_high))**cutoff:
      return False

  # All waves must have converged
  return True

# Hydro wavespeed calculator
def wavespeeds_hydro():

  # Handle simple entropy case
  wavespeeds = np.empty(5)
  wavespeeds[1] = vx
  wavespeeds[2] = vx
  wavespeeds[3] = vx

  # Calculate useful quantities
  gamma_adi_red = gamma_adi / (gamma_adi - 1.0)
  v_sq = vx**2 + vy**2 + vz**2
  gamma_lor_sq = 1.0 / (1.0 - v_sq)
  gamma_x_sq = 1.0 / (1.0 - vx**2)
  wgas = rho + gamma_adi_red * pgas
  cs_sq = gamma_adi * pgas / wgas
  cs = cs_sq**0.5
  delta = gamma_lor_sq * (1.0 - cs_sq) + cs_sq

  # Calculate sound speeds
  wavespeeds[0] = vx - 1.0/delta \
      * (vx * cs_sq + cs * (gamma_lor_sq/gamma_x_sq*(1.0-cs_sq) + cs_sq)**0.5)
  wavespeeds[4] = vx - 1.0/delta \
      * (vx * cs_sq - cs * (gamma_lor_sq/gamma_x_sq*(1.0-cs_sq) + cs_sq)**0.5)
  return wavespeeds
