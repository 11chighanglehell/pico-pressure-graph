"""Hardware smoke test: BMP280 over I2C, then the e-paper display."""

import framebuf
from machine import I2C, Pin

from config import (
    BMP280_I2C_ADDRESS,
    DISPLAY_BUSY_PIN,
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    I2C_ID,
    I2C_SCL_PIN,
    I2C_SDA_PIN,
)


def test_sensor():
    from bmp280 import BMP280

    i2c = I2C(I2C_ID, sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=100_000)
    found = [hex(a) for a in i2c.scan()]
    print("I2C devices:", found)
    if BMP280_I2C_ADDRESS not in i2c.scan():
        print("SENSOR FAIL: BMP280 not found (check SDA/SCL/power/address)")
        return None
    temperature, pressure = BMP280(i2c, BMP280_I2C_ADDRESS).read()
    print("SENSOR OK: {:.1f} C, {:.2f} hPa".format(temperature, pressure))
    return pressure


def test_display(pressure):
    print("BUSY pin idle level:", Pin(DISPLAY_BUSY_PIN, Pin.IN).value(), "(expect 0)")
    from epd2in13_v4 import EPD_2in13_V4_Landscape

    epd = EPD_2in13_V4_Landscape()
    epd.fill(1)
    epd.rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0)
    epd.line(0, 0, DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1, 0)
    epd.line(0, DISPLAY_HEIGHT - 1, DISPLAY_WIDTH - 1, 0, 0)
    epd.text("SMOKE TEST OK", 70, 50, 0)
    if pressure is not None:
        epd.text("{:.2f} hPa".format(pressure), 80, 66, 0)
    epd.init()
    epd.display(epd.buffer)
    print("DISPLAY: refresh completed without timeout")


pressure = test_sensor()
test_display(pressure)
