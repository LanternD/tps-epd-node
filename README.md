# About "TPS-EPD"

"TPS" stands for "two point seven", corresponding to the 2.7 screen size. "EPD" means "e-paper display".

This repo contains the code for controling a small Raspberry Pi hat.

# About the EPD Hat

I bought it on [Amazon](https://www.amazon.com/gp/product/B075FQKSZ9/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1).

Basically, it is plug-and-play. In addition, it has 4 buttons on the PCB, which are convenient for user input.

It has been working for several months, without any issue. I think it is durable enough.

# Development Reources

- [HAT Wiki](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT_(B))
- [User Manual](https://www.waveshare.com/w/upload/3/32/2.7inch-e-paper-hat-b-user-manual-en.pdf)
- [Example Code](https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/examples/epd_2in7b_V2_test.py)

# How to Run

1. Install the HAT driver:

``` shell
git clone https://github.com/waveshare/e-Paper
cd e-Paper
sudo python setup.py install
```

This will install the dependencies. If you encounter any errors, they should be easily solved by StackOverflow.
For example, `libtiff5` is required but not included in the Raspberry OS Lite.

The `setup.py` script will install `numpy==1.16.2`, which is too old for another package `yfinance`. So we need to install it by ourselves.

Another note here is that, do not install `numpy` via `sudo apt-get install python3-numpy`. 
Use `pip` to get the latest version of `numpy` to prevent old version warnings and other possible errors.

2. Dependencies installed by `pip`: `pillow`, `RPi.GPIO`, `yfinance`. 
3. To run: `python tps_epd_node_main.py`

# Apps

So far I implemented several apps, listed below. They are switched by buttons.

## Stock Price Board

The first application is a board showing the designated stock prices. I use Yahoo Finance API to get the latest stock price quote. Then I format everything onto the screen.

Fetching stock price quotes:

![img1](./assets/stock-app-1.jpg)

Showing stock price:

![img2](./assets/stock-app-2.jpg)

### Yahoo Finance Module

I use this library and it works great: https://github.com/ranaroussi/yfinance

Useful fields in `info` variable: `open, previousClose, regularMarketOpen, regularMarketDayHigh, regularMarketDayLow, regularMarketPrice`.

## Sitting Posture Reminder

Sometimes I slouch after sitting for too long. The solution is to refresh the display temporarily showing "UP RIGHT!" for 5 seconds to remind me the posture. Then I can sit up right to protect my spine.

![img4](./assets/posture-app.jpg)

This app is simple. There is an update timer, which triggers the refresh every 5 minutes.

This app works together with the aforementioned stock board.

## Clock App

My second app is a simple clock. What makes it special is that the time is refreshed every 3 minutes instead of 1 minutes. I don't need it to be precise.

Simple clock effect:

![img3](./assets/clock-app.jpg)
