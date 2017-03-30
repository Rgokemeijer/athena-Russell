
//========================================================================================
// Copyright(C) 2014 James M. Stone <jmstone@princeton.edu> and other code contributors
// Licensed under the 3-clause BSD License, see LICENSE file for details
//========================================================================================

// C/C++ headers
#include <iostream>
#include <cmath>

// Athena++ headers
#include "../gravity.hpp"
#include "../../athena.hpp"
#include "../../athena_arrays.hpp"
#include "../../parameter_input.hpp"
#include "../../coordinates/coordinates.hpp"
#include "../../mesh/mesh.hpp"
#include "../../hydro/hydro.hpp"
#include "../../fft/athena_fft.hpp"

//----------------------------------------------------------------------------------------
//! \fn  void Gravity::Initialize
//  \brief Initialize FFT gravity solver

void Gravity::Initialize(ParameterInput *pin)
{
  MeshBlock *pmb=pmy_block;
  AthenaFFT *pfft=pmb->pfft;

  pfft->fplan = pfft->QuickCreatePlan(AthenaFFTForward,pfft->in);
  pfft->bplan = pfft->QuickCreatePlan(AthenaFFTBackward,pfft->in);
}

//----------------------------------------------------------------------------------------
//! \fn  void Gravity::Solver
//  \brief Calculate potential from density using FFT

void Gravity::Solver(const AthenaArray<Real> &u)
{
  MeshBlock *pmb=pmy_block;
  AthenaFFT *pfft=pmb->pfft;
  Coordinates *pcoord = pmb->pcoord;
  Mesh *pm=pmy_block->pmy_mesh;

  int is = pmb->is; int js = pmb->js; int ks = pmb->ks;
  int ie = pmb->ie; int je = pmb->je; int ke = pmb->ke;
  Real dx1=pcoord->dx1v(is);
  Real dx2=pcoord->dx2v(js);
  Real dx3=pcoord->dx3v(ks);
  Real dx1sq = SQR(dx1), dx2sq = SQR(dx2), dx3sq = SQR(dx3);

  Real pcoeff;
// Copy phi to phi_old
  for(int k=ks; k<=ke; ++k){
    for(int j=js; j<=je; ++j){
      for(int i=is; i<=ie; ++i){
        phi_old(k,j,i) = phi(k,j,i);
      }
    }
  }

// Fill the work array

  for(int k=ks; k<=ke; ++k){
    for(int j=js; j<=je; ++j){
      for(int i=is; i<=ie; ++i){
        long int idx=pfft->GetIndex(i-is,j-js,k-ks,pfft->f_in);
        pfft->in[idx][0] = (u(IDN,k,j,i) - grav_mean_rho);
        pfft->in[idx][1] = 0.0;
      }
    }
  }

  pfft->Execute(pfft->fplan);

// Multiply kernel coefficient

  for(int k=0; k<pfft->knx[2]; k++){
    for(int j=0; j<pfft->knx[1]; j++){
      for(int i=0; i<pfft->knx[0]; i++){
        long int gidx = pfft->GetGlobalIndex(i,j,k); 
        if(gidx == 0){
          pcoeff = 0.0;
        } else { 
          pcoeff = ((2.0*std::cos((i+pfft->kdisp[0])*pfft->dkx[0])-2.0)/dx1sq);
          if(pfft->dim_ > 1)
            pcoeff += ((2.0*std::cos((j+pfft->kdisp[1])*pfft->dkx[1])-2.0)/dx2sq);
          if(pfft->dim_ > 2)
            pcoeff += ((2.0*std::cos((k+pfft->kdisp[2])*pfft->dkx[2])-2.0)/dx3sq);
          pcoeff = 1.0/pcoeff;
        }
        long int idx_in=pfft->GetIndex(i,j,k,pfft->b_in);
        long int idx_out=pfft->GetIndex(i,j,k,pfft->f_out);
        pfft->in[idx_in][0] = pfft->out[idx_out][0]*pcoeff;
        pfft->in[idx_in][1] = pfft->out[idx_out][1]*pcoeff;
      }
    }
  }
  
  pfft->Execute(pfft->bplan);

// Return phi

  for(int k=ks; k<=ke; ++k){
    for(int j=js; j<=je; ++j){
      for(int i=is; i<=ie; ++i){
        long int idx=pfft->GetIndex(i-is,j-js,k-ks,pfft->b_out);
        phi(k,j,i) = four_pi_G * pfft->out[idx][0]/pfft->gcnt;
      }
    }
  }

  CalculateGravityFlux(phi,pmb->phydro->flux);
}