//! no_std FSOT scalar — frozen constants from FSOT-2.1-Lean rust kernel.
//! T2 = 0 on the POC kernel (same as verification/rust/fsot_scalar_kernel).

#![allow(dead_code)]

use libm::{cos, exp, log, sin, sqrt};

pub const K: f64 = 0.4202216641606967;
pub const ALPHA: f64 = 0.0008082937414140405;
pub const PSI_CON: f64 = 0.6321205588285577;
pub const ETA_EFF: f64 = 0.46694220692425986;
pub const BETA: f64 = 2.620866911333223e-17;
pub const C_EFF: f64 = 0.9577022026205613;
pub const A_BLEED: f64 = 1.046973630587551;
pub const B_IN: f64 = 0.7879407922764435;
pub const A_IN: f64 = 1.6668538450045731;
pub const CHAOS: f64 = -0.33102418261048183;
pub const P_NEW: f64 = 0.30030227667037146;
pub const C_FACTOR: f64 = 0.28760015181918397;
pub const POOF: f64 = 0.1534822148944508;
pub const THETA_S: f64 = 0.29089654054517305;
pub const SUCTION: f64 = 0.14703398542810284;
pub const P_VAR: f64 = 0.9579871226722757;
pub const COLLAPSE_THRESHOLD: f64 = C_EFF * P_VAR;

/// Electromagnetism domain from vendor/fsot_compute.py §5.
pub const EM_D_EFF: f64 = 9.0;
pub const EM_DELTA_PSI: f64 = 0.7;
pub const EM_OBSERVED: bool = true;
pub const EM_HITS: f64 = 0.0;

const GAMMA_EULER: f64 = 0.5772156649;
const PHI: f64 = 1.6180339887;
const PI: f64 = core::f64::consts::PI;

pub fn compute_fsot_scalar(d_eff: f64, delta_psi: f64, observed: bool, recent_hits: f64) -> f64 {
    let n = 1.0_f64;
    let p = 1.0_f64;
    let d = d_eff.max(1.0);
    let dp = delta_psi;
    let hits = recent_hits;

    let growth = exp(ALPHA * (1.0 - hits / n) * GAMMA_EULER / PHI);
    let base = (n * p / sqrt(d))
        * cos((PSI_CON + dp) / ETA_EFF)
        * exp(-ALPHA * hits / n + 1.0 + B_IN * dp)
        * (1.0 + growth * C_EFF);
    let mut t1 = base * (1.0 + P_NEW * log(d / 25.0));
    if observed {
        t1 *= exp(C_FACTOR * P_VAR) * cos(dp + P_VAR);
    }

    let valve = BETA
        * cos(dp)
        * (n * p / sqrt(d))
        * (1.0 + CHAOS * (d - 25.0) / 25.0)
        * (1.0 + POOF * cos(THETA_S + PI) + SUCTION * sin(THETA_S));
    let acoustic = 1.0
        + (A_BLEED * sin(1.0) * sin(1.0)) / PHI
        + (A_IN * cos(1.0) * cos(1.0)) / PHI;
    let phase = 1.0 + B_IN * P_VAR;
    let t3 = valve * acoustic * phase;
    K * (t1 + t3)
}

pub fn electromagnetism_scalar() -> f64 {
    compute_fsot_scalar(EM_D_EFF, EM_DELTA_PSI, EM_OBSERVED, EM_HITS)
}
