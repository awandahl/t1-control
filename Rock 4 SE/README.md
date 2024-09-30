### T1 control by Rock 4 SE  

The Rock 4 SE, like other Rock 4 series boards, uses a different GPIO numbering system compared to the Raspberry Pi. This is due to the different SoC (System on Chip) used in these boards.  
For the Rock 4 SE:  
1. GPIO numbering is based on the RK3399 chip's GPIO banks and pins within those banks.  
2. The formula to calculate the GPIO number is:  
3. GPIO number = (bank number * 32) + (group number * 8) + pin number  
For example, GPIO4_C2 (physical pin 11) is calculated as:  
4 * 32 + 2 * 8 + 2 = 146
    
There isn't a direct way to use physical pin numbers in the Rock 4 SE's GPIO system like you can with the Raspberry Pi. You need to use the calculated GPIO numbers or the GPIO bank and pin designations (like GPIO4_C2).  



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

