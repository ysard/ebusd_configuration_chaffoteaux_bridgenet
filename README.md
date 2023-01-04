
Here you will find a configuration for the ebusd demon adapted to the boiler Chaffoteaux Mira C Green.

Note: The messages supported are for the moment only those **broadcast** by the boiler.

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

# How to use it ?

Put the `.csv` file into a directory, then launch `ebusd` with `--configpath` argument.

Example of command used to launch ebusd daemon:

    ebusd -d 192.168.1.65:3333 --latency=200000 --configpath=/path_to_your_config_files/ --enablehex --receivetimeout=100 --sendretries=2

Logs will be generated into `/var/log/ebusd.log`.

Monitor unknown messages:

    watch -n 3 -d ./build/src/tools/ebusctl grab result


# Protocol description

## Primary & secondary command bytes (PBSB)

| PBSB  | Signification                             | Uncertain
|:--- |:--- |:--- |
| 2000  | signal ability to receive a kind of data  |
| 2001  | cast supported features                   |
| 2004  | error detection/disappearance             | x
| 2010  | cast supported features                   | x
| 2020  | cast manual changes, dump registers       |
| 2031  | master device identificator broadcasts    |
| 2034  | bus reset                                 |
| 2036  | early boot                                | x
| 2038  |                                           |
| 203a  | request slave device                      | x
| 203b  |                                           |
| 2050  |                                           |
| 2051  |                                           |
| 2070  | broadcast date                            |


## Command IDs

Note: Naming is subject to change.
Note: In case of multiple values, there is 1 value per zone (z1, z2, etc.).

| 	              	                | Observed commands (max 7 zones)       | Uncertain observed values     | Tech menu entry
|:--- |:--- |:--- |:--- |
| **Heat related commands**
| heat request                      | `0191,0291,0391,0491,0591,0691,0791`  |                               | 434
| heat temp range                   | `0081,0082,0083,0084,0085,0086,0087`  |                               | 420
| heat water target temp            | `6197,6297,6397,6497,6597,6697,6797`  |                               |
| heat water max temp               | `6071,6072,6073,6074,6075,6076,6077`  |                               | 425
| heat water min temp               | `6171,6172,6173,6174,6175,6176,6177`  |                               | 426
| heat day temp                     | `6271,6272,6273,6267,6265,6266,6267`  |                               |
| heat night temp                   | `6371,6372,6373,6374,6375,6376,6377`  |                               |
| heat offset                       | `6471,6472,6473,6467,6465,6466,6467`  |                               | 423
| heat setpoint temp                | `6571,6572,6573,6574,6575,6576,6577`  |                               | 402
| ?                                 | `6671,6672,6673,6667,6665,6666,6667`  |                               |
| ?                                 | `6771,6772,6773,6774,6775,6776,6777`  |                               |
| ?                                 | `6971,6972,6973,6974,6975,6976,6977`  |                               |
| heat slope                        | `6a71,6a72,6a73,6a67,6a65,6a66,6a67`  |                               |
| ?                                 | `6b71,6b72,6b73,6b74,6b75,6b76,6b77`  |                               | 422
| ?                                 | `6c71,6c72,6c73,6c67,6c65,6c66,6c67`  |                               |
| boiler status                     | `c04b`                                | 0x65,0x23,0x06 values unknown |
| heat thermoregulation selection   | `c079,c07a,c07b,c07c,c07d,c07e,c07f`  |                               | 421
| heat room temp influence          | `c279,c27a,c27b,c27c,c27d,c27e,c27f`  |                               | 424
| ?                                 | `c679,c67a,c67b,c67c,c67d,c67e,c67f`  |                               |
| ?                                 | `c979,c97a,c97b,c97c,c97d,c97e,c97f`  |                               |
| **Domestic Hot Water (DHW) related commands**
| DHW comfort mode            	    | `c028`                                |                               | 250
| DHW water target temp             | `6147`                                |                               | 200
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
| **Unknown**
|                                   | `d140`                                |                               |
|                                   | `6047`                                |                               |
|                                   | `6d26`                                |                               |
|                                   | `7647`                                |                               |
|                                   | `7f97`                                |                               |
|                                   | `6126,6226,6426`                      |                               |
|                                   | `7426`                                |                               |
|                                   | `c679,c67a,c67b`                      |                               |
|                                   | `7118,7218,7318,7418,7518,7618,7718`


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
