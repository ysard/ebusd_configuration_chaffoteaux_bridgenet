# Hardware reversing

About thermostat & temperature sensor.

## External temperature sensor

The official sensor is sell with the ref. 3318599 for ~50€.

Specifications:

    10 K +/- 1% β=3977
    Cable EBUS2*
    Max. 50m
    Min. 0,5 mm2

Yes, it's a 10kΩ at 25°C CTN thermistor...

It costs cents to 2€, but you can found them for nothing in lithium computer batteries for example.


Voltage measured at no load at the terminals of the boiler socket: 4.93V

Measurements with fixed resistors:

 Ohms  | Temp   | Voltage   | Current I = U/R
| :--- | :---   | :---      | :---
61.2K  | -14°C  | 4.68V     | 0,076 mA
44.3K  | -7°C   | ?         | ?
20.1K  | 8.6°C  | 4.16v     | 0,206 mA
14.68K | 16°C   | 3.94V     | 0,268 mA
9.84K  | 25 °C  | 3.6V      | 0,365 mA
7.48K  | 30°C   | ?         | ?
7.4K   | 31°C   | 3.3V      | 0,445 mA
4.66K  | 41°C   | 2.76V     | 0,592 mA
2K     | -      | 1.74V     | 0,87  mA
1.5K   | -      | -         | -

So the current is not constant, it's not a constant current generator ???

## Water compensation formulas

![](./water_compensation.png)
*Water compensation curves from the constructor doc*

Formulas are from official technical "leaked" documentation of Chaffoteaux.

### Outdoor sensor only mode

Ohms | ext temp (°C )| theoric temp (°C )| measured temp (°C ) | delta
:--- | :--- | :--- | :--- | :---
|15K    | 16.2  | 34.56 | 35   | -0.44 (unreliable because water can't be set below 35°C)
|20.1K  | 8.6   | 43.68 | 43.6 | 0.08
|44.3K  | -7.6  | 63.12 | ?    |
|48.5K  | -8.8  | 64.56 | 64.4 | 0.16
|51.85K | -9.2  | 65.04 | 64.9 | 0.14
|69.5K  | -14.8 | 71.76 | 71.6 | 0.16

The general formula is:

`f(x) = -ax + b + offset`

This gives the following formula:

`f(ext_temp) = (-slope * ext_temp + y-intercept) + zone_temp_offset`

With for example a slope of 1.2, the y-intercept is 54.

Available line attributes:

> **Note**
>
> For high temp range regulation:<br>
> y-intercept = slope*20°C + 30°C<br>
> Since the heat stops at an external temp of 20°C, and the water temp target is always 30°C at this point.
> This gives the final formula:<br>
> `f(ext_temp) = slope * (20 - ext_temp) + 30 + zone_temp_offset`
>
> For low temp range regulation:<br>
> y-intercept = slope*20°C + 20°C<br>
> Since the heat stops at an external temp of 20°C, and the water temp target is always 20°C at this point.
> This gives the final formula:<br>
> `f(ext_temp) = slope * (20 - ext_temp) + 20 + zone_temp_offset`

slope | y-intercept | temp range
:--- | :--- | :---
0,2 | 24    | low
0,4 | 28    | low
0,6 | 32    | low
0,8 | 36    | low
1   | 50    | high
1,2 | 54    | high
1,5 | 60    | high
2   | 70    | high
2,5 | 80    | high
3   | 90    | high
3,5 | 100   | high

> **Note**
>
> The water temp can't be set below 35°C. But the curves show that they are calibrated for
> a minimalvalue of 30°C. This minimal temp is called water_min_temp in the following formulas.

A generic variant of the formula above, taking into account the setpoint temperature can be used:

`f(ext_temp) = slope * (room_temp_setpoint - ext_temp) + water_min_temp + zone_temp_offset`

### Room temp only

`f(room_temp_measured) = room_temp_influence  * (room_temp_setpoint - room_temp_measured) + water_min_temp + zone_temp_offset`

### Outdoor + Room sensors

This is a merge of the regulation based on outdoor sensor + room temp only.

It's the "most advanced" in use with costly ambient sensor. The geater the difference with the setpoint,
the higher the water target temp, until the setpoint is reached.
Once reached the formula will almost turn off the boiler by setting a very low water temp.

For example at 8.6°C ext, with a difference of 1°C between a setpoint of 20°C and real temp (19°C),
and a slope of 1.2 the target will be 67.7°C vs 43.6°C...

```
f(ext_temp, room_temp_measured) = slope * (room_temp_setpoint - ext_temp) +
slope * room_temp_influence  * (room_temp_setpoint - room_temp_measured) + water_min_temp + zone_temp_offset
```

## Thermostat

Here is a quick description of the thermostat "Easy Control Bus" sold by Chaffoteaux and
produced by Honeywell under the reference 3318604.
It's a ON/OFF thermostat, not an ambient probe but it uses eBUS to communicate with the boiler.

### PCB

![](Honeywell_small.webp)

The circuit is powered on via the eBUS wires.

Main components:

- A: Atmega 329 as the main mcu and LCD driver
- B: LDO unknown ref, 3.3V
- C: LM393A

The power supply is based on an LDO generating a voltage of 3.3V.
The LM393A voltage comparator is directly powered by this source.
The MCU ATMEGA 329 is powered by 2.95V when the EBUS power is off via a 1F capacitor.

You might be tempted to connect a device such as an ESP12 to this circuit and feed it
with the LDO, unfortunately it seems to be designed only to provide a very low current.
The ESP with WiFi activated consumes 75mA on average.
The voltage instantly drops to ~1.5V which will cause glitches on the 2 devices
and incessant reboots of the boiler.

Warnings:

- On the image, an external 3.3V power supply is used for the ESP but the ground plane
**must be common** to both devices.
- Such a connection will mute the thermostat; the TX pin of the ESP will have priority.
- You cannot receive what you are sending on the line. **To sniff out what the thermostat
is sending you will need to put the RX pin of the ESP on the TX of the Atmega**.

### eBUS circuit

All components related to the TX/RX lines are displayed.
Only capacitors values are unknown.

![](Honeywell_reversing_Easy_Control_Bus.svg)


### Firmware

The firmware was flashed without protecting fuses. It's easy to dump it via the SPI interface.
*BUT* it will be very frustrating to study, because there is no debugging information.

BTW, the firmware dump is posted on the current directory [here](./flash+eeprom.bin.tar.gz).

Anyway an alternative firmware could be written from scratch.
