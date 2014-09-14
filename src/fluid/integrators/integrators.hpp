#ifndef INTEGRATORS_HPP
#define INTEGRATORS_HPP
//======================================================================================
/* Athena++ astrophysical MHD code
 * Copyright (C) 2014 James M. Stone  <jmstone@princeton.edu>
 * See LICENSE file for full public license information.
 *====================================================================================*/
/*! \file integrators.hpp
 *  \brief defines FluidIntegrator implements data and functions to integrate fluid
 *====================================================================================*/

// Athena headers
#include "../../athena.hpp"         // Real
#include "../../athena_arrays.hpp"  // AthenaArray

class MeshBlock;
class Fluid;

//! \class FluidIntegrator
//  \brief member functions implement various integration algorithms for the fluid

class FluidIntegrator {
public:
  FluidIntegrator(Fluid *pf);
  ~FluidIntegrator();

  Fluid *pmy_fluid;  // ptr to Fluid containing this FluidIntegrator

  void Predict(MeshBlock *pmb);
  void Correct(MeshBlock *pmb);

  void RiemannSolver(const int k, const int j, const int il, const int iu,
    const int ivx, const int ivy, const int ivz,
    AthenaArray<Real> *pwl, AthenaArray<Real> *pwr, AthenaArray<Real> *pflx);

  void ReconstructionFuncX1(const int k, const int j, const int il, const int iu, 
    AthenaArray<Real> &w, AthenaArray<Real> *pwl, AthenaArray<Real> *pwr);

  void ReconstructionFuncX2(const int k, const int j, const int il, const int iu, 
    AthenaArray<Real> &w, AthenaArray<Real> *pwl, AthenaArray<Real> *pwr);

  void ReconstructionFuncX3(const int k, const int j, const int il, const int iu, 
    AthenaArray<Real> &w, AthenaArray<Real> *pwl, AthenaArray<Real> *pwr);

private:
// scratch space used in integrator
  AthenaArray<Real> wl_, wr_, flx_, src_; 
  AthenaArray<Real> face_area_, cell_volume_;
};
#endif
