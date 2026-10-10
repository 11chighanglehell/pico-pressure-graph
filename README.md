# Pico Pressure Graph

A standalone MicroPython project for reading a BMP280 and drawing a pressure
history graph on a Waveshare 2.13-inch e-Paper HAT. This project is separate
from piRadar.

## Hardware

- Freenove Raspberry Pi Pico 2 W
- GY-BMP280-3.3 barometric pressure sensor
- Waveshare 2.13-inch e-Paper HAT V4, 250x122 monochrome

The Pico GPIO uses 3.3 V logic. Do not connect 5 V to its GPIO pins. Connect
all grounds together and power down before wiring.

Suggested wiring (GPIO numbers, not physical header pin numbers):

| Signal | Pico GPIO |
| --- | --- |
| BMP280 SDA | GP4 |
| BMP280 SCL | GP5 |
| Display DIN / MOSI | GP19 |
| Display CLK / SCK | GP18 |
| Display CS | GP17 |
| Display DC | GP16 |
| Display RST | GP20 |
| Display BUSY | GP21 |

Connect sensor power to 3V3 and GND. For I2C, set the BMP280 CSB pin high;
select its address with SDO (normally `0x76` or `0x77`). Connect display power
and ground according to the exact HAT documentation. The HAT has a Raspberry
Pi-style 40-pin connector, so use individual jumper wires or a suitable
adapter rather than assuming it plugs directly onto the Pico.

## Run

Copy `config.py`, `graph.py`, `bmp280.py`, `epd2in13_v4.py`, and `main.py` to
the Pico (for example with `py -m mpremote connect COMx fs cp file.py :file.py`).
`main.py` reads the BMP280 every `SAMPLE_INTERVAL_SECONDS`, draws the history
graph, and refreshes the display. `epd2in13_v4.py` is Waveshare's official
[Pico V4 driver](https://github.com/waveshareteam/Pico_ePaper_Code/blob/main/python/Pico_ePaper-2.13_V4.py),
modified only to use the SPI and pin settings in `config.py`.
