Here you will find a configuration for the ebusd demon adapted to the Chaffoteaux boilers Mira C Green, Serelia and Talia Green.
This configuration should also be compatible with other brands of the Ariston company
using the BridgeNet/eBus2 protocol (Elco, Ariston, etc.).

The messages supported are explicit read/write & those broadcast by the boiler.

The goal is to achieve complete control of the device on solutions like Home Assistant:

![](./home_assistant_integration/assets/ha_global_screenshot.webp)

If you are interested in more/other details, do not hesitate to consult this series of blog articles (french)
[Domotiser son chauffage avec Home Assistant](https://pro-domo.ddns.net/blog/domotiser-son-chauffage-avec-home-assistant-partie-1.html).

Hardware related information is at: [./hardware_reversing/](./hardware_reversing/).

Any help in filling in the gaps is **VERY** welcome.


## :book: Foreword

In an ethical world we wouldn't have to spend so much time trying to reverse this kind of proprietary protocols.
If you don't think it's appropriate, if you don't have the energy to do this tedious/time-consuming/<insert anything here> work,
or if you don't want to buy the overpriced devices sold by these companies, then you should consider
to go with manufacturers who respect your right to repair/modify what you own without ruining yourself.

And you would be wise to do so.


## :bank: Donations

This project took a **LOT** of time in reverse engineering, making the integration with Home Assistant,
including documentation & tests.
If it has been useful to you in any way, saving you time and hopefully energy or money for your home,
you can consider the following **donation links** or at least **add a star to the project**.
Any participation is appreciated because it means that the time invested was not in vain.

[![Donate](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/Ysard/donate)

![](https://img.shields.io/badge/Bitcoin-000000?style=for-the-badge&logo=bitcoin&logoColor=yellow)

1EB6dc6YULzHR4TMqLi5fomZ6wmdP3N5cW

## Official documentation

Some links to understand the interest of these data and their organization.

- [Message-definition](https://github.com/john30/ebusd/wiki/4.1.-Message-definition)
- [Defaults](https://github.com/john30/ebusd/wiki/4.2.-Defaults)
- [Builtin-data-types](https://github.com/john30/ebusd/wiki/4.3.-Builtin-data-types)
- [Field-templates](https://github.com/john30/ebusd/wiki/4.4.-Field-templates)


## How to install it ?

Put the `.csv` files into a directory, then launch `ebusd` with `--configpath` argument.

Example of command used to launch ebusd daemon:

    ebusd -d 192.168.1.65:3333 --latency=200000 --configpath=/path_to_your_config_files/ --enablehex --receivetimeout=100 --sendretries=2

Logs will be generated into `/var/log/ebusd.log`.

Monitor unknown messages:

    watch -n 3 -d ./build/src/tools/ebusctl grab result


## How to install Home Assistant integration ?

See the Readme here: [./home_assistant_integration/](./home_assistant_integration/).


## How to use it ?

Here is a quick usage example. Keep in mind that `read` queries return cached values by default (see `-m` setting of ebusctl).
Raw hex queries are not concerned by caching issues.

Turn on the heating (winter mode/ability to heat water in heaters if you prefer):

    $ ebusctl write -c boiler heating_status on
    # or
    $ ebusctl hex 3c 2020 03 0120 01

Activate the heating of the water (command sent by thermostat for example):

    $ ebusctl write -c boiler z1_heating_activation on
    # or
    $ ebusctl hex 3c 2020 03 1919 01

In SRA mode with an external temp probe, read the computed temp for the first 3 zones:

    $ ebusctl read -c boiler hot_water_target_temp_1
    43.4;58.0;58.0
    # or
    $ ebusctl hex 3c 2000 02 6197

Now, increase the offset of temp starting the computed temp:

    $ ebusctl write -c boiler z1_thermoreg_offset 6

Check the modification:

    $ ebusctl read -c boiler hot_water_target_temp_1
    49.4;58.0;58.0


## Protocol description

### Primary & secondary command bytes (PBSB)

| PBSB  | Signification                             | Uncertain
|:--- |:--- |:--- |
| 2000  | cast features/read values                 |
| 2001  | cast features/read values with additional data (allowed range of values?) | x
| 2002  | error log interrogation                   |
| 2004  | error detection/disappearance             |
| 200f  |                                           |
| 2010  | cast features/cast data read-only values/set values* |
| 2020  | cast manual changes/dump registers/set values* |
| 2031  | master device identificator broadcasts    |
| 2034  | bus reset                                 |
| 2036  | handshake                                 | x
| 2038  |                                           |
| 203a  | request slave device                      | x
| 203b  | cast slave addr                           |
| 2050  | time related data                         | x
| 2051  | cast comfort timer programs**             |
| 2070  | broadcast date                            |

*: 2010 command may be for values that should not be modified by a device and that
should be accepted by another.
i.e calculated/measured/status values (current temp measured, boiler status,
settings change counter, computed target temp, heat request status).
2020 commands may be for values that can be modified on the device and accepted by another.

**: Timer programs protocol is described below

### Command IDs

Note: Naming is subject to change.
Note: In case of multiple values, there is 1 value per zone (z1, z2, etc.).

| 	              	                | Observed commands (max 7 zones)       | Uncertain observed values     | Tech menu entry
|:--- |:--- |:--- |:--- |
| **Heat related commands**
| heat request status               | `0191,0291,0391,0491,0591,0691,0791`  |                               | 434
| heat activation                   | `1919,1a19,1b19,1c19,1d19,1e19,1f19`  |                               |
| heat temp range                   | `0081,0082,0083,0084,0085,0086,0087`  |                               | 420
| heat water computed target temp   | `6197,6297,6397,6497,6597,6697,6797`  |                               | 830
| heat water max temp               | `6071,6072,6073,6074,6075,6076,6077`  |                               | 425
| heat water min temp               | `6171,6172,6173,6174,6175,6176,6177`  |                               | 426
| heat day temp                     | `6271,6272,6273,6274,6275,6276,6277`  |                               |
| heat night temp                   | `6371,6372,6373,6374,6375,6376,6377`  |                               |
| heat offset                       | `6471,6472,6473,6474,6475,6476,6477`  |                               | 423
| heat fixed temp                   | `6571,6572,6573,6574,6575,6576,6577`  |                               | 402
| ?                                 | `6671,6672,6673,6674,6675,6676,6677`  |                               |
| ?                                 | `6771,6772,6773,6774,6775,6776,6777`  |                               |
| ?                                 | `6971,6972,6973,6974,6975,6976,6977`  |                               |
| heat slope                        | `6a71,6a72,6a73,6a74,6a75,6a76,6a77`  |                               | 422
| ?                                 | `6b71,6b72,6b73,6b74,6b75,6b76,6b77`  |                               |
| ?                                 | `6c71,6c72,6c73,6c74,6c75,6c76,6c77`  |                               |
| boiler status                     | `c04b`                                | 0x65,0x06,0x12 (pump circ??) unknown             |
| heat thermoregulation selection   | `c079,c07a,c07b,c07c,c07d,c07e,c07f`  |                               | 421
| heat room temp influence          | `c279,c27a,c27b,c27c,c27d,c27e,c27f`  |                               | 424
| heat request mode                 | `c679,c67a,c67b,c67c,c67d,c67e,c67f`  |                               |
| ?                                 | `c979,c97a,c97b,c97c,c97d,c97e,c97f`  |                               |
| heat water temp out               | `6810`                                |                               | 831
| heat water temp in                | `6910`                                |                               | 832
| heat boost time (s)               | `602b`                                |                               | 244
| fan speed (x100 rpm)              | `4013`                                |                               | 822
| **Domestic Hot Water (DHW) related commands**
| DHW comfort mode            	    | `c028`                                |                               | 250
| DHW water target temp             | `6126`                                |                               | 200
| DHW water antifreeze temp [0.2;15]| `6426`                                |                               |
| DHW water real temp               | `6147`                                |                               |
| DHW comfort zones                 | `d746`                                |                               | 250
| ?                                 | `da46`                                |                               |
| ?                                 | `dc46`                                |                               |
| ?                                 | `de46`                                |                               |
| DHW cleansing function ??         | `0b20`                                |                               |
| DHW Celectic status               | `0f20`                                |                               | 256
| **Face panel related commands**
| heating status                    | `0120`                                |                               |
| DHW status                        | `0220`                                |                               |
| SRA status                        | `0520`                                |                               | 224
| **Misc**
| settings change counter           | `d140`                                |                               |
| boiler life time (minutes)*       | `50d9`                                |                               |
| ignition cycles                   | `42d8`                                |                               | 813
| external temp                     | `7647`                                |                               | 835
| external temp offset              | `7426`                                |                               | 249
| room temp                         | `7118,7218,7318,7418,7518,7618,7718`  |                               |
| heating in progress               | `0c19`                                |                               |
| burner heat life time             | `4bd1`                                |                               | 810
| **Unknown**
|                                   | `6047`                                |                               |
|                                   | `6d26`                                |                               |
|                                   | `6f10`                                |                               |
|                                   | `7526`                                |                               |
|                                   | `c528`                                |                               |
|                                   | `6226,6426`                           |                               |
|                                   | `6bc0,2b70`                           |                               |
|                                   | `6997,6a97,6b97,6c97,6d97,6e97,6f97`  |                               |
|                                   | `7997,7a97,7b97,7c97,7d97,7e97,7f97`  |                               |
|                                   | `0119,0219,0319,0419,0519,0619,0719`  |                               |
|                                   | `0990,0a90,0b90,0c90,0d90,0e90,0f90`  |                               |


*: Yes, the boiler life time value is accessible in read AND write modes...

### Protocol of Timer programs

- packets are emitted every minute
- there are 14 different packets
- the rotation of packets occurs every 14 minutes
- the usable field is alternated every minute
- there are 2 different fields per program
- each usable field is composed of 24 nibbles/quartet, so 12 bytes, it covers 12 hours with a precision of 30 min

Packets dump (packets are ordered by reception time):

QQZZPBSB length ID | Default program           | Prog 1                    | Prog 2                    | Prog3
|:--- |:--- |:--- |:--- |:--- |
37fe2051 0e 0007   | 000000000000004055150000  | 000000000000555555555555  | 000000000000555500000000  | 000000000000555500000000
37fe2051 0e 1007   | 000000000000000000000000  | 555555555555555555550000  | 555500000055555555550000  | 000000005555555555550000
37fe2051 0e 0107   | 000000000000004055150000  | 000000000000555555555555  | 000000000000555500000000  | 000000000000555500000000
37fe2051 0e 1107   | 000000000000000000000000  | 555555555555555555550000  | 555500000055555555550000  | 000000005555555555550000
37fe2051 0e 0207   | 000000000000004055150000  | 000000000000555555555555  | 000000000000555500000000  | 000000000000555500000000
37fe2051 0e 1207   | 000000000000000000000000  | 555555555555555555550000  | 555500000055555555550000  | 000000005555555555550000
37fe2051 0e 0307   | 000000000000004055150000  | 000000000000555555555555  | 000000000000555500000000  | 000000000000555500000000
37fe2051 0e 1307   | 000000000000000000000000  | 555555555555555555550000  | 555500000055555555550000  | 000000005555555555550000
37fe2051 0e 0407   | 000000000000004055150000  | 000000000000555555555555  | 000000000000555500000000  | 000000000000555500000000
37fe2051 0e 1407   | 000000000000000000000000  | 555555555555555555550000  | 555500000055555555550000  | 000000005555555555550000
37fe2051 0e 0507   | 000000000000004055150000  | 000000000000555555555555  | 000000000000555500000000  | 000000000000555500000000
37fe2051 0e 1507   | 000000000000000000000000  | 555555555555555555550000  | 555500000055555555550000  | 000000005555555555550000
37fe2051 0e 0607   | 000000000000004055150000  | 000000000000555555555555  | 000000000000555500000000  | 000000000000555500000000
37fe2051 0e 1607   | 000000000000000000000000  | 555555555555555555550000  | 555500000055555555550000  | 000000005555555555550000

```
Prog 1
000000000000555555555555    => Heating enabled from 6h to 12h
555555555555555555550000    => Heating enabled from 12h to 22h
Prog 2
000000000000555500000000    => Heating enabled from 6h to 8h
555500000055555555550000    => Heating enabled from 12h to 14h, then from 17h to 22h
Prog 3
000000000000555500000000    => Heating enabled from 6h to 8h
000000005555555555550000    => Heating enabled from 16h to 22h
Default prog
000000000000004055150000    => ???
000000000000000000000000    => no heating
```

## Protocol for the errors

- Appearance/disappearance packets always go through 3 repetitions.
- The order of appearance plays no role since they can be deleted in any order.
However, an error masks the previous one on the display.
- Unknown errors (not supported by the boiler) are displayed as `---`, and cannot
(for now?) be removed unless a bus reset command is sent.
However, they do not prevent further testing of other errors.
- Some errors are silent because they are not displayed. For example, disconnecting the external
temperature sensor always triggers an error (`0xec`). On the other hand, disconnecting
it when the control mode is 3 or 4 (external sensor required) will generate an additional
error `0x0c`, code `114`, which is displayed this time.
- The resolution command is made of the error code, followed by a default byte.
- The minimal trigger command is made of the error code, followed by the default byte + a flag value.
- You can generate/replay errors by broadcasting them, not just by touching the hardware
(which is very useful for reversing).
In this way, the following command will generate a `411` error (z1 missing ambient probe)
on the boiler display :

    ~/ebusd/build/src/tools/ebusctl hex fe20040469030061

However, to remove it, you need to use its resolution command :

    ~/ebusd/build/src/tools/ebusctl hex fe200403690100


### Overall packet structure:

Any packet error consists of:

```
QQ,ZZ,PBSB,SS,XX,YY,00,ZZ
```

- QQ: src address
- ZZ: dest address
- PBSB: command bytes, always 2004 here
- SS: packet length in bytes
- XX: error code (which we want to map with the code displayed on the boiler)
- YY: zone flags (see below)
- 00: spacer ?
- ZZ: specific error codes sent by the boiler but not mandatory to define an error
=> redundant data ?


Each bit in YY byte has a signification. The LSB seems to be always set when a zone is concerned.

Here is a table with all the zone flags deducted from packet sniffing operations :

| zone flags  | dec value       | bin value    |
|:--- |:--- |:--- |
| zone_enable | 1               | `0b00000001` |
| z1          | 2               | `0b00000010` |
| z2          | 4               | `0b00000100` |
| z3          | 8               | `0b00001000` |
| z4          | 16              | `0b00010000` |
| z5          | 32              | `0b00100000` |
| z6          | 64              | `0b01000000` |
| z7          | non-functional? | `?`          |

### Examples

The XX and YY bytes, for a missing ambient probe on z1 (error 411) **and** z2 (error 412) will be :

    XX: 0x69                                       <= code for "missing ambient probe" error
    YY: zone_enable + z1 + z2 = 1 + 2 + 4 = 0x07

Thus, the minimal trigger command will be :

`fe2004026907`

The resolution command is the YY byte without the flags, but it's still an error related to some zones,
so the `zone_enable` flag must be set :

`fe2004026901`

In fact, other bytes are present after YY such as ZZ sequence; but they are not mandatory
to trigger and resolute errors.

### Packet sniffing

Steps to reverse the protocol:

- Disconnect ambient probe from eBus if there is one ;
- Set the thermoregulation type (command ids c079,c07a,c07b,c07c,c07d,c07e)
to a mode that require it (4) for the various zones (z1 to z6) ;
- Wait for packets in ebusd logs ;
- Switch the thermoregulation type to 0 or 1 for a zone and wait for the resolution packet

```shell
# Trigger missing ambient probe z1 (411) by switching c079 to mode 4
~/ebusd/build/src/tools/ebusctl hex fe202003c07904
00:44:57.863     37fe200404 69030061
00:44:57.985     37fe200404 69030061
00:45:27.857     37fe200404 69030061
# Resolution by switching to mode 0
~/ebusd/build/src/tools/ebusctl hex fe202003c07900
00:49:15.420     37fe200403 690100
00:49:17.620     37fe200403 690100
00:49:27.642     37fe200403 690100
# Trigger missing ambient probe z2 (412) by switching c07a to mode 4
~/ebusd/build/src/tools/ebusctl hex fe202003c07a04
00:55:03.297     37fe200404 69050062
00:55:07.301     37fe200404 69050062
00:55:27.314     37fe200404 69050062
# Resolution by switching to mode 1
~/ebusd/build/src/tools/ebusctl hex fe202003c07a01
00:55:56.450     37fe200403 690100
00:55:57.279     37fe200403 690100
00:57:27.213     37fe200403 690100
# Trigger missing ambient probe z3 (413) by switching c07b to mode 4
~/ebusd/build/src/tools/ebusctl hex fe202003c07b04
0:58:44.920      37fe200404 69090063
0:58:47.124      37fe200404 69090063
0:59:27.108      37fe200404 69090063
# Resolution by switching to mode 1
~/ebusd/build/src/tools/ebusctl hex fe202003c07b01
01:00:28.030     37fe200403 690100
01:00:37.280     37fe200403 690100
01:01:27.235     37fe200403 690100
```

### Cumulated errors & flags discovery

Trigger missing ambient probe errors for z4 + z5 + z6 + z3 + z2 + z1 via the previously showed commands.

| QQZZPBSPSS | XX | YY | 00 | ZZ            | Action | YY flag formula
|:--- |:--- |:--- |:--- |:--- |:--- |:--- |
| 37fe200404 | 69 | 11 | 00 | 64            | +z4    | 0x11-0x01 = 16
| 37fe200405 | 69 | 31 | 00 | 6465          | +z5    | 0x31-0x11 = 32
| 37fe200406 | 69 | 71 | 00 | 646566        | +z6    | 0x71-0x31 = 64
| 37fe200407 | 69 | 79 | 00 | 63646566      | +z3    | 0x79-0x71 = 8
| 37fe200408 | 69 | 7d | 00 | 6263646566    | +z2    | 0x7d-0x79 = 4
| 37fe200409 | 69 | 7f | 00 | 616263646566  | +z1    | 0x7f-0x7d = 2
| 37fe200408 | 69 | 3f | 00 | 6162636465    | -z6    |
| 37fe200407 | 69 | 1f | 00 | 61626364      | -z5    |
| 37fe200406 | 69 | 0f | 00 | 616263        | -z4    |
| 37fe200405 | 69 | 07 | 00 | 6162          | -z3    |
| 37fe200404 | 69 | 03 | 00 | 61            | -z2    |
| 37fe200403 | 69 | 01 | 00 |               | -z1    |


### Discovering error codes

See: [Bruteforce the errors to discover their corresponding codes](#bruteforce-the-errors-to-discover-their-corresponding-codes).


### Home Assistant integration

See the Readme here: [./home_assistant_integration/](./home_assistant_integration/).

### Full error codes for Mira C Green

| YY | Displayed code | Documented (x if yes) | Signification
|:--- |:--- |:--- |:--- |
| 00  | 101 | x   | Surchauffe du circuit primaire
| 01  | 102 |     | Anomalie capteur de pression (court-circuité ou pas de signal)
| 02  | 1P1 | x   | Anomalie débit chauffage
| 03  | 1P2 | x   | Anomalie débit chauffage
| 04  | 1P3 | x   | Anomalie débit chauffage
| 05  | 104 | x   | Anomalie débit chauffage
| 06  | 107 | x   | Anomalie débit chauffage
| 07  | 1P4 |     | Pression insuffisante, remplissage demandé
| 08  | 1P4 |     | Pression insuffisante, remplissage demandé
| 09  | 109 |     | Pression excessive >= 3bars
| 0a  | 110 | x   | Défaut sonde sortie échangeur princ.
| 0b  | 112 | x   | Défaut sonde entrée échangeur princ
| 0c  | 114 | x   | Anomalie sonde extérieure
| 0d  | 116 | x   | Thermostat plancher ouvert
| 0e  | 118 | x   | Anomalie sonde circuit primaire
| 0f  | 103 | x   | Anomalie débit chauffage
| 10  | 105 | x   | Anomalie débit chauffage
| 11  | 106 | x   | Anomalie débit chauffage
| 12  | 108 | x   | Remplissage circuit chauffage demandé
| 13  | 111 |     |
| 14  | 1P5 |     |
| 15  | 1P6 |     |
| 16  | 1P7 |     |
| 17  | 1P8 |     |
| 18  | 201 | x   | Anomalie sonde sanitaire - URBIA/ SERELIA GREEN
| 19  | 309 |     | Dysfonctionnement du bloc Gaz
| 1a  | 203 | x   | Anomalie sonde ballon - URBIA/ SERELIA GREEN
| 1b  | 308 |     | Erreur de configuration atmosphérique
| 1c  | 205 | x   | Anomalie sonde entrée sanitaire (solaire)
| 1e  | 2P2 |     | Anti bactérie non complété (Urbia Green Evo Mod)
| 1f  | 209 | x   | Surchauffe ballon - URBIA/ SERELIA GREEN
| 20  | 301 | x   | Anomalie afficheur EEPROM
| 21  | 303 | x   | Anomalie carte principale
| 22  | 304 | x   | Trop de reset effectués (> 5 pour < 15min)
| 24  | 306 | x   | Anomalie carte principale
| 26  | 120 |     |
| 27  | 121 |     |
| 28  | 122 |     |
| 29  | 123 |     |
| 2a  | 311 |     |
| 2b  | 312 |     |
| 2d  | 501 | x   | Absence de flamme
| 2e  | 502 | x   | Détect. flamme vanne gaz fermée
| 2f  | 504 | x   | Anomalie ionisation brûleur en fonct.
| 30  | 5P1 | x   | Echec première tentative allumage
| 31  | 5P2 | x   | Echec seconde tentative allumage
| 32  | 5P3 | x   | Décollement de flamme
| 33  | 5P4 |     | Anomalie ionisation brûleur en fonct.
| 34  | 601 |     | Anomalie débordement fumée (modèle CF)
| 35  | 602 |     | Contact de la sécurité VMC (modèle VMC)
| 36  | 604 |     | Vitesse de l'extracteur insuffisante/Anomalie tachymètre
| 38  | 607 |     | Contact pressostat fermé avec extracteur non alimenté
| 39  | 421 |     |
| 3b  | 610 | x   | Surchauffe échangeur primaire ; thermofusible ouvert
| 3c  | 612 | x   | Anomalie sur ventilateur ; vitesse de ventilation faible pas de signal du tachymètre au démarrage
| 3d  | 6P1 |     | Pas de fermeture contact du pressostat après 20s alimentation extracteur
| 3e  | 6P2 |     | Défaut du pressostat lors d'un fonctionnement de l'extracteur
| 41  | 422 |     |
| 42  | 510 |     |
| 47  | 511 |     |
| 49  | 3P9 | x   | Prévoir entretien. Contacter SAV
| 4b  | 620 |     |
| 4c  | 621 |     |
| 69  | 410 | x*  | Sonde ambiance zone (*) non dispo.
| 69  | 411 | x   | Sonde ambiance zone z1 non dispo.
| 69  | 412 | x   | Sonde ambiance zone z2 non dispo.
| 69  | 413 | x   | Sonde ambiance zone z3 non dispo.
| 69  | 414 |     | Sonde ambiance zone z4 non dispo.
| 69  | 415 |     | Sonde ambiance zone z5 non dispo.
| 69  | 416 |     | Sonde ambiance zone z6 non dispo.
| ec  | --- |     | Sonde extérieure débranchée

*: Zone error : variations for each zone are not displayed

Missing codes for Mira C Green (not supported?) : '302', '305', '307'


## Tools

### Bruteforce the errors to discover their corresponding codes

Just use the interactive script [here](./tools/bruteforce_errors.py).
It can be adapted with the displayed expected codes from the boiler documentation.
Feel free to modify the settings of the script (i.e. the variables
EBUSCTL_BIN_PATH, LOG_FILE, EXPECTED_ERRORS).

Every boiler owner should run this program to obtain the error codes for your equipment.
These are quite specific, and this procedure remains necessary until a database is built up.

* Installation:

    $ pip install --user (--break-system-packages) argparse  colorama

    Use --break-system-packages if you know what you are doing
    and not working inside a virtual env.

* Usage:

```shell
$ ./bruteforce_errors.py -h
usage: bruteforce_errors.py [-h] {find_errors,analysis} ...

options:
-h, --help              show this help message and exit

subcommands:
{find_errors,analysis}
    find_errors         Broadcast errors & waits for the user to enter the
                        code displayed on the boiler. Results are stored in
                        the log file defined in LOG_FILE. User can skip the
                        current code or quit at any time. Each error code is
                        reset before the next test. If the reset is not
                        effective, a bus reset can be triggered.
    analysis            Display missing & extra codes vs the expected ones
                        defined in EXPECTED_ERRORS ; Output mapped errors for
                        ebusd config file : _templates.csv.
```
```shell
$ ./bruteforce_errors.py find_errors -h
usage: bruteforce_errors.py find_errors [-h] [-s START] [-e END]

options:
  -h, --help            show this help message and exit
  -s START, --start START
                        Start value for code search (0 <= val <= 255) (default: 0)
  -e END, --end END     End value for code search (0 <= val <= 255) (default: 128)
```

For example, to analyze the results of a boiler interrogation:
```
$ ./bruteforce_errors.py analysis
Missing codes:
 ['302', '305', '307', '411', '412', '413']
Excess codes:
 ['---', '102', '109', '111', '120', '121', ...]
CSV template string:
 0=101;1=102;2=1P1;3=1P2;4=1P3;5=104;6=107;7=1P4;8=1P4;...
```

Missing codes, are expected codes from your user manual but not found/functional ;
excess codes are codes that are not in the user manual but are supported by the hardware.

The CSV template string can be used as it is in the ebusd config file (`_templates.csv`).


### Finding registers

Use the interactive script [here](./tools/bruteforce_registers.py).
**Take the time to read the comments and adapt the script to your needs!**


If you're looking for a register that manages an option you can read/modify
on your boiler control panel, then this script is for you.

Like *Cheat Engine*, by successive iterations and pruning, you'll be able to identify the register.

The script is mainly made to search for registers like the very important `1919`,
which is used to switch the boiler ON/OFF from a thermostat for the Mira C Green boiler.

This register seems to be sent only by an eBus thermostat
and it stays at 0 without it.
The boiler doesn't broadcast its status.

People without "smart" thermostat (i.e. people that only have a thermostat with
dry contact connected to the TA1 pins of the boiler's motherboard)
can't guess the register without such a bruteforce script.


General process:

- With some "read" iterations you will find registers that have changed
(ex: Those that have a value of 0 when the boiler is off, and that have
a value of 1 when it's on). The script can be modified to adopt another behaviour.

- Then, "write" tests can be started. Multiple registers are tested
until the boiler responds. The interactive script will help you to find the
unique triggering register.


Installation:

    $ pip install --user (--break-system-packages) colorama

Use --break-system-packages if you know what you are doing
and not working inside a virtual env.


## Handshake procedure

TODO: help needed; See Issue ysard/ebusd_configuration_chaffoteaux_bridgenet#3.


## Help request

- Handshake study of new device on the bus in order to emulate it with a custom one.
- Packet dissections for missing ids. For example:

```
37fe2020 0c c079 01 c07a 01 c07b 01 c07c 01
            z1 heat thermoregulation selection
37fe2020 0c c07d 01 c07e 01 c07f 01 c279 0a
            ^z5     ^z6     ^z7     ^z1 heat room temp influence
37fe2020 0c c27a 0a c27b 0a c27c 0a c27d 0a
            ^z2     ^z3     ^z4     ^z5 heat room temp influence
37fe2020 0c c27e 0a c27f 0a c679 03 c67a 03
            ^z6     ^z7     ^z1 ??  ^z2 ??
37fe2020 0c c67b 03 c67c 03 c67d 03 c67e 03
            ^z3     ^z4     ^z5 ??  ^z6 ??
37fe2020 0c c67f 03 c979 06 c97a 06 c97b 06
            ^z7     ^z1     ^z2 ??  ^z3 ??
37fe2020 0c c97c 06 c97d 06 c97e 06 c97f 06
            ^z4     ^z5     ^z6 ??  ^z7 ??
```

## Other repositories & inspirations

- https://github.com/wrongisthenewright/ebusd-configuration-ariston-bridgenet
- https://github.com/komw/ariston-bus-bridgenet-ebusd
- https://github.com/john30/ebusd-configuration/issues/103
- https://github.com/john30/ebusd-configuration/issues/27
