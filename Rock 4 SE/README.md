### T1 control Rock 4 SE  
#### This is a python script where the fq of my QRP Labs QDX/QMX can control the band memory setting on the Elecraft T1 automatic tuner. Any transceiver using rigctld can be used, of course...


Rock 4 SE specific information:  
GPIO numbers like 18 and 22 are derived from an offset calculation based on the GPIO bank and pin. For instance, GPIO4_C2 means:  

GPIO bank 4, port C (where C represents an offset of 2, starting from A as 0).
Each bank has 32 pins (A-D).
The formula is: GPIO number = Bank * 32 + Port offset * 8 + Pin number.
For example:

GPIO4_C2 = 4 * 32 + 2 = 18
GPIO4_C6 = 4 * 32 + 6 = 22.

You can refer to this GPIO wiki for more details.


https://wiki.radxa.com/Rock4/hardware/gpio

```
aw@5x7w:~$ cat /etc/os-release
PRETTY_NAME="Armbian 24.5.5 bookworm"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
HOME_URL="https://www.armbian.com"
SUPPORT_URL="https://forum.armbian.com"
BUG_REPORT_URL="https://www.armbian.com/bugs"
ARMBIAN_PRETTY_NAME="Armbian 24.5.5 bookworm"
```

```sudo apt install libgpiod-dev python3-libgpiod```  

