
Here you will find a configuration for the ebusd demon adapted to the boiler Chaffoteaux Mira C Green.

Note: The messages supported are for the moment only those **broadcast** by the boiler.

Any help in filling in the gaps is **VERY** welcome.


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
| 2050  |                                           |
| 2051  |                                           |
| 2070  | broadcast date                            |


## Command IDs

Note: Naming is subject to change.
Note: In case of multiple values, there is 1 value per zone (z1, z2, etc.).

| 	              	                | Observed commands                     | Uncertain observed values     | Corresponding boiler menu
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
|                                   | `6671,6672,6673,6667,6665,6666,6667`  |                               |
|                                   | `6771,6772,6773,6774,6775,6776,6777`  |                               |
|                                   | `6971,6972,6973,6974,6975,6976,6977`  |                               |
| heat slope                        | `6a71,6a72,6a73,6a67,6a65,6a66,6a67`  |                               |
|                                   | `6b71,6b72,6b73,6b74,6b75,6b76,6b77`  |                               | 422
|                                   | `6c71,6c72,6c73,6c67,6c65,6c66,6c67`  |                               |
| boiler status                     | `c04b                              `  | 0x65,0x23,0x06 values unknown |
| heat thermoregulation selection   | `c079,c07a,c07b,c07c,c07d,c07e,c07f`  |                               | 421
| heat room temp influence          | `c279,c27a,c27b,c27c,c27d,c27e,c27f`  |                               | 424
|                                   | `c679,c67a,c67b,c67c,c67d,c67e,c67f`  |                               |
|                                   | `c979,c97a,c97b,c97c,c97d,c97e,c97f`  |                               |
| **Domestic Hot Water (DHW) related commands**
| DHW comfort mode            	    | `c028`                                |                               |250
| DHW water target temp             | `6147`                                |                               |200
| DHW comfort zones                 | `d746`                                |                               |250
|                                   | `da46`                                |                               |
|                                   | `dc46`                                |                               |
|                                   | `de46`                                |                               |
| DHW cleansing function ??         | `0b20`                                |                               |
| DHW Celectic status               | `0f20`                                |                               |256
| Face panel related commands       | `    `                                |                               |
| heating status                    | `0120`                                |                               |
| DHW status                        | `0220`                                |                               |
| SRA status                        | `0520`                                |                               |224
| **Unknown**                         `    `
|                                   | `d140`                                |                               |
|                                   | `6047`                                |                               |
|                                   | `6d26`                                |                               |
|                                   | `7647`                                |                               |
|                                   | `7f97`                                |                               |
|                                   | `6126,6226,6426`                      |                               |
|                                   | `7426`                                |                               |
|                                   | `c679,c67a,c67b`                      |                               |

