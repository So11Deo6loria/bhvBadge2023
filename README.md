# Introduction 
Badgetastic is a synergistic exercise in awesomeness for thrill seekers. Come one come all. Making a dope AF badge for BHV @ DEF CON 31. If you don't get the reference: https://www.youtube.com/watch?v=d0VO-zi5EgY

# Prototyping
Here are the basic parts that were used during development of the badge: 
- [Raspberry Pi Pico](https://www.amazon.com/seeed-studio-Raspberry-Microcontroller-Dual-core/dp/B08TQSDP28/ref=sr_1_4?crid=3BR4CFGZY09KV&keywords=raspberry%2Bpi%2Bpico&qid=1673276394&s=electronics&sprefix=raspberry%2Bpi%2Bpico%2Celectronics%2C110&sr=1-4&th=1)
- [HR Monitor](https://www.amazon.com/dp/B07QC67KMQ?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- [NeoPixel Array](https://www.amazon.com/dp/B00IEDH26K?ref=nb_sb_ss_w_as-reorder-t1_ypp_rep_k6_1_9&amp=&crid=1X40AQY7KP3FN&amp=&sprefix=neopixel+)

Wiring: 
- HR Monitor (VIN/RPi3V3, GND/RPiGND, SCL/RPiGP17, and SDA/RPiGP16)
- LEDs (5VDC/RPiVSYS, GND/RPiGND, DIN/RPiGP15 or RPiGP22)

# Firmware Development
1. Download the MicroPython UF2 file: https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2
1. Hold BOOTSEL while connecting to your computer via micro-USB cable
1. Device will reset and then you can use Thonny but it kind of stinks. I use Visual Studio Code for proper version control / IDE. 
1. Connect to the pico given the tty interface
`rshell -p /dev/tty.usbmodemXXXXXX --buffer-size 512`
1. Sync your local changes (assuming you have the firmware repo pulled down locally)
`rsync -m . /pyboard`
1. Connect to the REPL shell
`repl`
1. Soft reboot the pico to run main.py
`CTRL-D`
1. To exit you can press CTRL+C and to leave the repl shell you need to press CTRL+X

# Hardware Development
cadlab is cool: https://cadlab.io/project/26426/master/files 