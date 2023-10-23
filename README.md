# pyplot

This is a super simple script I wrote to chunk HPGL commands from a given file into <60-byte chunks, as the HP7440A plotter I'm working with has a 60-byte buffer.

```
usage: pyplot.py <filename>

By default pyplot attempts to connect to the plotter via /dev/ttyUSB0.
Update the code in your local copy if your plotter has some other name in /dev/.
```
