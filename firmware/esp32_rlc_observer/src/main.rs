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
    println!("FSOT_RLC_PIN=D1D38A");
    println!("FSOT_RLC_D_EFF={EM_D_EFF:.1}");
    println!("FSOT_RLC_S={s_em:.17}");
    println!("FSOT_RLC_THETA={COLLAPSE_THRESHOLD:.17}");
    println!("FSOT_RLC_SCALAR_TRIT={}", s_trit.as_i8());

    let mut frame: u32 = 0;
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
        let lock = t0 == t1 && t1 == t2;

        if frame % 50 == 0 {
            println!("FSOT_RLC_FRAME_START frame={frame}");
            println!("FSOT_RLC_S={s_em:.17}");
            println!("FSOT_RLC_THETA={COLLAPSE_THRESHOLD:.17}");
            println!("FSOT_RLC_SCALAR_TRIT={}", s_trit.as_i8());
            println!("FSOT_RLC_LOCK={}", if lock { 1 } else { 0 });
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
