# Schematic and placement

## Topology (the thing that was wrong at 3%)

Three **identical** nodes in a **triangle**. Each node talks to the other two through one pot. Every node has degree 2. That is the object FSOT κ assumes.

```
        [ Node A ]----- Rc_AB (11.12 kΩ) -----[ Node B ]
             \                                   /
              \                                 /
           Rc_CA (11.12 kΩ)              Rc_BC (11.12 kΩ)
                \                             /
                 \                           /
                  +-------[ Node C ]-------+
                           |
                      ESP32 ADC
                    A→GPIO34  B→GPIO35  C→GPIO32
```

A 1-D chain (A—B—C only) makes the ends different from the middle. That was the 3% residual.

## One node (repeat three times)

```
±9 V ── TL082 dual op-amp (NIC: 220, 220, 2.2k, 22k, 22k, 3.3k)
                │
VC1 ── C1 10nF ─┴── R 1.8k ── VC2 ── C2 100nF ── analog GND
                │                 │
               NIC               L 22mH
                │                 │
            analog GND         analog GND

VC1 ── 100k ──●── GPIO 34/35/32
              │
             100k to ESP32 GND, 100k to ESP32 3V3
              + 1N4148 to 3V3 and GND
```

## ESP32 DevKit V1 (30-pin) — left header is the ADC side

Looking at the USB connector **up**:

**Left column (top to bottom, typical DOIT DevKit V1):**  
`EN, VP(36), VN(39), 34, 35, 32, 33, 25, 26, 27, 14, 12, 13, GND, VIN`

| Wire | Pin | Why |
|------|-----|-----|
| Node A \(V_{C1}\) (biased) | **GPIO 34** | ADC1_CH6, **input only** — correct, we never drive it |
| Node B \(V_{C1}\) (biased) | **GPIO 35** | ADC1_CH7, input only |
| Node C \(V_{C1}\) (biased) | **GPIO 32** | ADC1_CH4 |
| ESP32 ground | **GND** (next to VIN) | Common with analog ground at **one star point only** |
| Onboard LED | **GPIO 2** | Firmware lock indicator (right-column D2). Do not jumper it. |
| USB | micro-USB | 5 V in, 3.3 V from AMS1117. Serial 115200. |

Do **not** use GPIO 34/35 as outputs. Do **not** put ±9 V on any ESP32 pin.

## Power islands (keep them apart)

1. **Analog island:** ±9 V batteries. All three TL082 V+ / V−. Analog GND.
2. **Digital island:** USB 5 V → DevKit 3.3 V. ESP32 GND.
3. Tie analog GND to ESP32 GND at **exactly one** breadboard hole (star). Extra ground loops make the trits chatter.

## Breadboard placement (top view)

```
[ 9V+ ]                    [ 9V− ]
   |                          |
  V+ rail                  V− rail
   |                          |
[ Node A island ]    [ Node B island ]
   C1,R,L,C2,TL082      C1,R,L,C2,TL082
         \                /
          \    Rc pots   /
           \            /
            [ Node C island ]
            C1,R,L,C2,TL082
                  |
            bias 100k/100k
                  |
        [ ESP32 DevKit USB facing you ]
          left header: 34 35 32 GND
```

Leave a row of unused holes between analog ±9 V and the DevKit. If a 9 V lead slips onto GPIO 34 you kill the pad.

## Two-position experiment (no scope)

| Test | Set all three pots to | What you must see |
|------|------------------------|-------------------|
| Unlocked | 20 kΩ (σ ≈ 0.9 < φ) | UART `FSOT_RLC_LOCK=0`, trits disagree, LED blinks |
| Locked | **11.12 kΩ** (σ = φ) | `FSOT_RLC_LOCK=1`, three trits equal, LED solid on +1 |

That is the physical falsification. Open coupling is independent chaos. The φ operating point is the lock.
