//! Host replay of Circuit seed identities. Not the ESP32 firmware.

fn main() {
    let phi = (1.0_f64 + 5.0_f64.sqrt()) / 2.0;
    let alpha = 10.0_f64;
    let r = 1800.0_f64;
    let rc = alpha * r / phi;
    let ga = -(1.0 / 2200.0 + 1.0 / 3300.0);
    let gb = -1.0 / 3300.0;
    let a = r * ga;
    let b = r * gb;
    let c_eff = 0.9577022026205613_f64;
    let p_var = 0.9579871226722757_f64;
    let theta = c_eff * p_var;

    assert!((phi - 1.618033988749895).abs() < 1e-12);
    assert!((rc - 11124.611797498106).abs() < 1e-6);
    assert!((a - (-15.0 / 11.0)).abs() < 1e-12);
    assert!((b - (-6.0 / 11.0)).abs() < 1e-12);
    assert!((theta - 0.9174663774653723).abs() < 1e-12);
    println!("FSOT_CIRCUIT_RUST_OK");
    println!("phi={phi:.15}");
    println!("R_c={rc:.10}");
    println!("a={a:.15}");
    println!("b={b:.15}");
    println!("theta={theta:.15}");
}
