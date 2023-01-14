
Here you will find a configuration for the ebusd demon adapted to the boiler Chaffoteaux Mira C Green.

~Note: The messages supported are for the moment only those **broadcast** by the boiler.~

Update: The messages supported are explicit read/write & those broadcast by the boiler.

Any help in filling in the gaps is **VERY** welcome.


# Foreword

In an ethical world we wouldn't have to spend so much time trying to reverse this kind of proprietary protocols.
If you don't think it's appropriate, if you don't have the energy to do this tedious/time-consuming/<insert anything here> work,
or if you don't want to buy the overpriced devices sold by these companies, then you should consider
to go with manufacturers who respect your right to repair/modify what you own without ruining yourself.

And you would be wise to do so.


# Official documentation

Some links to understand the interest of these data and their organization.

- [Message-definition](https://github.com/john30/ebusd/wiki/4.1.-Message-definition)
- [Defaults](https://github.com/john30/ebusd/wiki/4.2.-Defaults)
- [Builtin-data-types](https://github.com/john30/ebusd/wiki/4.3.-Builtin-data-types)
- [Field-templates](https://github.com/john30/ebusd/wiki/4.4.-Field-templates)


# How to install it ?

Put the `.csv` file into a directory, then launch `ebusd` with `--configpath` argument.

Example of command used to launch ebusd daemon:

    ebusd -d 192.168.1.65:3333 --latency=200000 --configpath=/path_to_your_config_files/ --enablehex --receivetimeout=100 --sendretries=2

Logs will be generated into `/var/log/ebusd.log`.

Monitor unknown messages:

    watch -n 3 -d ./build/src/tools/ebusctl grab result


# How to use it ?

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


# Protocol description

## Primary & secondary command bytes (PBSB)

| PBSB  | Signification                             | Uncertain
|:--- |:--- |:--- |
| 2000  | cast features/read values                 |
| 2001  | cast features                             |
| 2004  | error detection/disappearance             |
| 200f  |                                           |
| 2010  | cast supported features                   | x
| 2020  | cast manual changes/dump registers/set values       |
| 2031  | master device identificator broadcasts    |
| 2034  | bus reset                                 |
| 2036  | handshake                                 | x
| 2038  |                                           |
| 203a  | request slave device                      | x
| 203b  | cast slave addr                           |
| 2050  |                                           |
| 2051  | cast comfort timer programs*              |
| 2070  | broadcast date                            |


*: Timer programs protocol is described below

## Command IDs

Note: Naming is subject to change.
Note: In case of multiple values, there is 1 value per zone (z1, z2, etc.).

| 	              	                | Observed commands (max 7 zones)       | Uncertain observed values     | Tech menu entry
|:--- |:--- |:--- |:--- |
| **Heat related commands**
| heat request status               | `0191,0291,0391,0491,0591,0691,0791`  |                               | 434
| heat activation                   | `1919,...??`                          |                               |
| heat temp range                   | `0081,0082,0083,0084,0085,0086,0087`  |                               | 420
| heat water computed target temp   | `6197,6297,6397,6497,6597,6697,6797`  |                               | 830
| heat water max temp               | `6071,6072,6073,6074,6075,6076,6077`  |                               | 425
| heat water min temp               | `6171,6172,6173,6174,6175,6176,6177`  |                               | 426
| heat day temp                     | `6271,6272,6273,6267,6265,6266,6267`  |                               |
| heat night temp                   | `6371,6372,6373,6374,6375,6376,6377`  |                               |
| heat offset                       | `6471,6472,6473,6467,6465,6466,6467`  |                               | 423
| heat fixed temp                   | `6571,6572,6573,6574,6575,6576,6577`  |                               | 402
| ?                                 | `6671,6672,6673,6667,6665,6666,6667`  |                               |
| ?                                 | `6771,6772,6773,6774,6775,6776,6777`  |                               |
| ?                                 | `6971,6972,6973,6974,6975,6976,6977`  |                               |
| heat slope                        | `6a71,6a72,6a73,6a67,6a65,6a66,6a67`  |                               |
| ?                                 | `6b71,6b72,6b73,6b74,6b75,6b76,6b77`  |                               | 422
| ?                                 | `6c71,6c72,6c73,6c67,6c65,6c66,6c67`  |                               |
| boiler status                     | `c04b`                                | 0x65,0x23,0x06 unknown        |
| heat thermoregulation selection   | `c079,c07a,c07b,c07c,c07d,c07e,c07f`  |                               | 421
| heat room temp influence          | `c279,c27a,c27b,c27c,c27d,c27e,c27f`  |                               | 424
| heat request mode                 | `c679,c67a,c67b,c67c,c67d,c67e,c67f`  |                               |
| ?                                 | `c979,c97a,c97b,c97c,c97d,c97e,c97f`  |                               |
| heat water temp out               | `6810`                                |                               | 831
| heat water temp in                | `6910`                                |                               | 832
| **Domestic Hot Water (DHW) related commands**
| DHW comfort mode            	    | `c028`                                |                               | 250
| DHW water target temp             | `6126`                                |                               | 200
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
| boiler life time (minutes)        | `50d9`                                |                               |
| ignition cycles                   | `42d8`                                |                               | 813
| external temp                     | `7647`                                |                               | 835
| external temp offset              | `7426`                                |                               | 249
| room temp                         | `7118,7218,7318,7418,7518,7618,7718`  |                               |
| **Unknown**
|                                   | `6047`                                |                               |
|                                   | `6d26`                                |                               |
|                                   | `7f97`                                |                               |
|                                   | `6226,6426`                           |                               |
|                                   | `6997,6a97,6b97,6c97,6d97,6e97,6f97`  |                               |
|                                   | `7997,7a97,7b97,7c97,7d97,7e97,7f97`  |                               |
|                                   | `0119,0219,0319,0419,0519,0619,0719`  |                               |
|                                   | `0990,0a90,0b90,0c90,0d90,0e90,0f90`  |                               |

## Protocol of Timer programs

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

# Help request

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

# Other repositories & inspirations

- https://github.com/wrongisthenewright/ebusd-configuration-ariston-bridgenet
- https://github.com/komw/ariston-bus-bridgenet-ebusd
- https://github.com/john30/ebusd-configuration/issues/103
- https://github.com/john30/ebusd-configuration/issues/27
