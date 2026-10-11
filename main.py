"""Pico pressure graph application entry point."""

import time

from config import (
    BMP280_I2C_ADDRESS,
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    GROUND_ELEVATION_M,
    HISTORY_FILE,
    HISTORY_SAMPLES,
    I2C_ID,
    I2C_SCL_PIN,
    I2C_SDA_PIN,
    ROTATE_180,
    SAMPLE_INTERVAL_SECONDS,
)


def draw(epd, image, width, height):
    epd.fill(1)
    if not ROTATE_180:
        epd.blit(image, 0, 0)
        return
    for y in range(height):
        for x in range(width):
            epd.pixel(width - 1 - x, height - 1 - y, image.pixel(x, y))


def main():
    import framebuf
    from machine import I2C, Pin

    from bmp280 import BMP280
    from epd2in13_v4 import EPD_2in13_V4_Landscape
    from graph import render
    from history import append_sample, load_history, save_history

    i2c = I2C(
        I2C_ID,
        sda=Pin(I2C_SDA_PIN),
        scl=Pin(I2C_SCL_PIN),
        freq=100_000,
    )
    addresses = i2c.scan()
    if BMP280_I2C_ADDRESS not in addresses:
        raise OSError(
            "BMP280 not found at 0x{:02x}; I2C devices found: {}".format(
                BMP280_I2C_ADDRESS, [hex(address) for address in addresses]
            )
        )
    sensor = BMP280(i2c, BMP280_I2C_ADDRESS)

    epd = EPD_2in13_V4_Landscape()
    samples = load_history(HISTORY_FILE, HISTORY_SAMPLES)
    if samples:
        save_history(HISTORY_FILE, samples)
    print("Restored {} pressure samples".format(len(samples)))
    samples_since_compaction = 0
    refreshes = 0

    while True:
        _, pressure = sensor.read()
        samples.append(pressure)
        del samples[:-HISTORY_SAMPLES]
        append_sample(HISTORY_FILE, pressure)
        samples_since_compaction += 1
        if samples_since_compaction >= HISTORY_SAMPLES:
            save_history(HISTORY_FILE, samples)
            samples_since_compaction = 0
        print("Pressure: {:.2f} hPa".format(pressure))

        pixels = render(
            samples,
            SAMPLE_INTERVAL_SECONDS,
            HISTORY_SAMPLES,
            DISPLAY_WIDTH,
            DISPLAY_HEIGHT,
            GROUND_ELEVATION_M,
        )
        image = framebuf.FrameBuffer(
            pixels, DISPLAY_WIDTH, DISPLAY_HEIGHT, framebuf.MONO_HLSB
        )
        draw(epd, image, DISPLAY_WIDTH, DISPLAY_HEIGHT)

        refreshes += 1
        if refreshes % 30 == 1:
            epd.init()
            epd.display(epd.buffer)
        else:
            epd.displayPartial(epd.buffer)
        time.sleep(SAMPLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
