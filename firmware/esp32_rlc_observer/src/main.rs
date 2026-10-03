//! Bare-metal FSOT observer for a 3-node nonlinear RLC array.
//!
//! GPIO 34 / 35 / 32  →  V_C1 of nodes 0 / 1 / 2 after the bias network.
//! UART 115200        →  FSOT_RLC_* frames (host twin: firmware/host_observer.py).
//!
//! Flash (from this crate, ESP32 classic):
//!   cargo install espflash
//!   cargo build --release
//!   espflash flash --monitor target/xtensa-esp32-none-elf/release/fsot-esp32-rlc

#![no_std]
#![no_main]

extern crate alloc;

mod scalar;
mod trinary;

use embassy_time::{Duration, Timer};
use esp_hal::{
    analog::adc::{Adc, AdcConfig, Attenuation},
    clock::CpuClock,
    delay::Delay,
    gpio::{Level, Output, OutputConfig},
    interrupt::software::SoftwareInterruptControl,
    ram,
    timer::timg::TimerGroup,
};
use esp_println::println;
use scalar::{electromagnetism_scalar, COLLAPSE_THRESHOLD, EM_D_EFF};
use trinary::{decode_vc1, from_scalar, from_voltage};

esp_bootloader_esp_idf::esp_app_desc!();

const BREAKPOINT_V: f64 = 1.0;
const SAMPLE_PERIOD_US: u64 = 100; // 10 kS/s — audio-band Chua (~3 kHz LC)
/// Outer NIC breakpoint Bp2 = Esat R3/(R2+R3) with Esat set by Bp1 = 1 V: 230/33 V. A node beyond it has left the
/// double scroll for the outer limit cycle (~±7.35 V), where the three nodes also synchronise. That is NOT the lock.
const BP2_V: f64 = 230.0 / 33.0;
const PHI_INV: f64 = 0.6180339887498949;
/// Lock window: 1024 samples = 102 ms ≈ 570 τ (τ = R C2 = 180 µs). Lock = trit agreement ≥ φ⁻¹ over the window
/// AND every |V_C1| < Bp2 over the window (amplitude condition, sim/chua_array.lock_law).
const LOCK_WINDOW: u32 = 1024;

#[esp_rtos::main]
async fn main(_spawner: embassy_executor::Spawner) -> ! {
    let config = esp_hal::Config::default().with_cpu_clock(CpuClock::max());
    let peripherals = esp_hal::init(config);
    esp_alloc::heap_allocator!(size: 32 * 1024);
    esp_alloc::heap_allocator!(#[ram(reclaimed)] size: 32 * 1024);

    let timg0 = TimerGroup::new(peripherals.TIMG0);
    let sw_int = SoftwareInterruptControl::new(peripherals.SW_INTERRUPT);
    esp_rtos::start(timg0.timer0, sw_int.software_interrupt0);

    let mut led = Output::new(peripherals.GPIO2, Level::Low, OutputConfig::default());
    let mut delay = Delay::new();
    for _ in 0..3 {
        led.toggle();
        delay.delay_millis(80);
    }

    let mut adc_config = AdcConfig::new();
    let mut pin0 = adc_config.enable_pin(peripherals.GPIO34, Attenuation::_11dB);
    let mut pin1 = adc_config.enable_pin(peripherals.GPIO35, Attenuation::_11dB);
    let mut pin2 = adc_config.enable_pin(peripherals.GPIO32, Attenuation::_11dB);
    let mut adc = Adc::new(peripherals.ADC1, adc_config);

    let s_em = electromagnetism_scalar();
    let s_trit = from_scalar(s_em);
    println!("FSOT RLC Observer v0.1");
    println!("FSOT_RLC_HARDWARE_BOOT=ok");
    println!("FSOT_RLC_PIN=AEB2AD");
    println!("FSOT_RLC_D_EFF={EM_D_EFF:.1}");
    println!("FSOT_RLC_S={s_em:.17}");
    println!("FSOT_RLC_THETA={COLLAPSE_THRESHOLD:.17}");
    println!("FSOT_RLC_SCALAR_TRIT={}", s_trit.as_i8());

    let mut frame: u32 = 0;
    let (mut win_n, mut win_agree, mut win_max) = (0u32, 0u32, 0.0f64);
    let (mut lock, mut amp_ok, mut last_agree, mut last_max) = (false, false, 0.0f64, 0.0f64);
    loop {
        let c0 = nb::block!(adc.read_oneshot(&mut pin0)).unwrap_or(0);
        let c1 = nb::block!(adc.read_oneshot(&mut pin1)).unwrap_or(0);
        let c2 = nb::block!(adc.read_oneshot(&mut pin2)).unwrap_or(0);
        let v0 = decode_vc1(c0);
        let v1 = decode_vc1(c1);
        let v2 = decode_vc1(c2);
        let t0 = from_voltage(v0, BREAKPOINT_V);
        let t1 = from_voltage(v1, BREAKPOINT_V);
        let t2 = from_voltage(v2, BREAKPOINT_V);
        win_n += 1;
        if t0 == t1 && t1 == t2 {
            win_agree += 1;
        }
        win_max = win_max
            .max(libm::fabs(v0))
            .max(libm::fabs(v1))
            .max(libm::fabs(v2));
        if win_n == LOCK_WINDOW {
            last_agree = win_agree as f64 / LOCK_WINDOW as f64;
            last_max = win_max;
            amp_ok = win_max < BP2_V;
            lock = last_agree >= PHI_INV && amp_ok;
            win_n = 0;
            win_agree = 0;
            win_max = 0.0;
        }

        if frame % 50 == 0 {
            println!("FSOT_RLC_FRAME_START frame={frame}");
            println!("FSOT_RLC_S={s_em:.17}");
            println!("FSOT_RLC_THETA={COLLAPSE_THRESHOLD:.17}");
            println!("FSOT_RLC_SCALAR_TRIT={}", s_trit.as_i8());
            println!("FSOT_RLC_LOCK={}", if lock { 1 } else { 0 });
            println!(
                "FSOT_RLC_AMP_OK={} max_abs_v={last_max:.3} bp2_v={BP2_V:.3}",
                if amp_ok { 1 } else { 0 }
            );
            println!("FSOT_RLC_TRIT_AGREE={last_agree:.4}");
            println!("FSOT_RLC_NODE|0|{c0}|{v0:.6}|{}", t0.as_i8());
            println!("FSOT_RLC_NODE|1|{c1}|{v1:.6}|{}", t1.as_i8());
            println!("FSOT_RLC_NODE|2|{c2}|{v2:.6}|{}", t2.as_i8());
            println!("FSOT_RLC_FRAME_END frame={frame}");
        }

        match (lock, t0) {
            (true, trinary::Trit::Emergence) => led.set_high(),
            (true, trinary::Trit::Quiescent) => led.set_low(),
            (true, trinary::Trit::Damping) => {
                led.toggle();
            }
            (false, _) => {
                led.toggle();
            }
        }

        frame = frame.wrapping_add(1);
        Timer::after(Duration::from_micros(SAMPLE_PERIOD_US)).await;
    }
}
