# 6502-on-HX1K
A simple set-up for running Arlet's 6502 on iCE40HX1K (as found on the iceblink board), called from migen.

# Memory map
| Start    |   End    | Subsystem      |
|---------:|---------:|---------------:|
| `0x0000` | `0x8000` | RAM            |
| `0xFE60` | `0xFE60` | LED port       |
| `0xFF00` | `0xFFFF` | ROM            |

# Notes
The ROM needs cc65 to build; the appropriate linker script is included.
