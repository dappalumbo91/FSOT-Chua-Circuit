//! Host replay of Circuit seed identities. Not the ESP32 firmware, but it compiles the firmware's
//! scalar module unchanged (pin AEB2AD) so the constants on the chip are checked against the authority.

#[path = "../../../firmware/esp32_rlc_observer/src/scalar.rs"]
mod scalar;

fn main() {
    let phi = (1.0_f64 + 5.0_f64.sqrt()) / 2.0;
    let alpha = 10.0_f64;
    let r = 1800.0_f64;
    let rc = alpha * r / phi;
    // Kennedy NIC: R1 = R2 = 220, R3 = 2200, R4 = R5 = 22k, R6 = 3.3k
    let (r1, r2, r3, r4, r5, r6) = (220.0_f64, 220.0, 2200.0, 22000.0, 22000.0, 3300.0);
    let ga = -r2 / (r1 * r3) - r5 / (r4 * r6);
    let gb = -r2 / (r1 * r3) + 1.0 / r4;
    let gc = 1.0 / r1 + 1.0 / r4;
    let (a, b, c) = (r * ga, r * gb, r * gc);
    let esat = (r5 + r6) / r6; // Bp1 = 1 V
    let bp2 = esat * r3 / (r2 + r3);
    let theta = scalar::COLLAPSE_THRESHOLD;
    let s_em = scalar::electromagnetism_scalar();

    assert!((phi - 1.618033988749895).abs() < 1e-12);
    assert!((rc - 11124.611797498106).abs() < 1e-6);
    assert!((ga - (-1.0 / 1320.0)).abs() < 1e-15);
    assert!((gb - (-9.0 / 22000.0)).abs() < 1e-15);
    assert!((gc - (101.0 / 22000.0)).abs() < 1e-15);
    assert!((a - (-15.0 / 11.0)).abs() < 1e-12);
    assert!((b - (-81.0 / 110.0)).abs() < 1e-12);
    assert!((c - (909.0 / 110.0)).abs() < 1e-12);
    assert!((bp2 - 230.0 / 33.0).abs() < 1e-12);
    assert!((theta - 0.9175102712064876).abs() < 1e-12);
    assert!((s_em - 0.9557285700955828).abs() < 1e-12, "firmware S_EM {s_em}");
    assert!(s_em.abs() >= theta); // scalar trit +1 at AEB2AD
    println!("FSOT_CIRCUIT_RUST_OK");
    println!("phi={phi:.15}");
    println!("R_c={rc:.10}");
    println!("a={a:.15}");
    println!("b={b:.15}");
    println!("c={c:.15}");
    println!("Bp2={bp2:.15}");
    println!("theta={theta:.16}");
    println!("S_EM_firmware={s_em:.16}");
}
