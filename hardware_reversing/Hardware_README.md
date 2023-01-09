# Hardware reversing

Here is a quick description of the thermostat "Easy Control Bus" sold by Chaffoteaux and
produced by Honeywell under the reference 3318604.
It's a ON/OFF thermostat, not an ambient probe but it uses eBUS to communicate with the boiler.

## PCB

![](Honeywell_small.webp)

The circuit is powered on via the eBUS wires.

Main components:

- A: Atmega 329 as the main mcu and LCD driver
- B: LDO unknown ref, 3.3V
- C: LM393A

The power supply is based on an LDO generating a voltage of 3.3V.
The LM393A voltage comparator is directly powered by this source.
The MCU ATMEGA 329 is powered by 2.95V when the EBUS power is cut via a 1F capacitor.

You might be tempted to connect a device such as an ESP12 to this circuit and feed it
with the LDO, unfortunately it seems to be designed only to provide a very low current.
The ESP with WiFi activated consumes 75mA on average.
The voltage instantly drops to ~1.5V which will cause glitches on the 2 devices
and incessant reboots of the boiler.

Warnings:

- On the image, an external 3.3V power supply is used for the ESP but the ground plane
**must be common** to the 2 devices.
- Such a connection will mute the thermostat; the TX pin of the ESP will have priority.
- You cannot receive what you are sending on the line. To sniff out what the thermostat
is sending you will need to put the RX pin of the ESP on the TX of the Atmega.

## eBUS circuit

All components related to the TX/RX lines are displayed.
Only capacitors values are unknown.

![](Honeywell_reversing_Easy_Control_Bus.svg)


## Firmware

The firmware was flashed without protecting fuses. It's easy to dump it via the SPI interface.
*BUT* it will be very frustrating to study, because there is no debugging information.

BTW, the firmware dump is posted on the current directory.

Anyway an alternative firmware could be written from scratch.
