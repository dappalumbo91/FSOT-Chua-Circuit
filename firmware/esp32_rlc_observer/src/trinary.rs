//! Voltage and scalar collapse onto FSOT trits {−1, 0, +1}.

use crate::scalar::COLLAPSE_THRESHOLD;

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Trit {
    Damping = -1,
    Quiescent = 0,
    Emergence = 1,
}

impl Trit {
    pub fn as_i8(self) -> i8 {
        self as i8
    }

    pub fn label(self) -> &'static str {
        match self {
            Trit::Emergence => "+1",
            Trit::Quiescent => "0",
            Trit::Damping => "-1",
        }
    }
}

pub fn from_voltage(v: f64, breakpoint: f64) -> Trit {
    if v < -breakpoint {
        Trit::Damping
    } else if v > breakpoint {
        Trit::Emergence
    } else {
        Trit::Quiescent
    }
}

pub fn from_scalar(s: f64) -> Trit {
    if libm::fabs(s) < COLLAPSE_THRESHOLD {
        Trit::Quiescent
    } else if s > 0.0 {
        Trit::Emergence
    } else {
        Trit::Damping
    }
}

/// 12-bit ESP32 code → V_C1 after the 100 kΩ / 100 kΩ 1.65 V bias.
pub fn decode_vc1(code: u16) -> f64 {
    let volts = (code as f64) * 3.3 / 4095.0;
    (volts - 1.65) / 0.5
}
