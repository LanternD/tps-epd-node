#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime
import logging
import os
import os.path as op
import sys
import time
import traceback

from PIL import Image, ImageDraw, ImageFont

from gpiozero import Button
from waveshare_epd import epd2in7


class EpdHatButtonHandler(object):
    def __init__(self):
        "Deal with the button events."
        """Table:
        Key1 - GPIO5 - (29)
        Key2 - GPIO6 - (31)
        Key3 - GPIO13 - (33)
        Key4 - GPUI19 - (35)
        Ref: https://gpiozero.readthedocs.io/en/stable/recipes.html#button"""
        self.btn1 = Button(5)
        self.btn2 = Button(6)
        self.btn3 = Button(13)
        self.btn4 = Button(19)
        self.status_table = [0, 0, 0, 0]
        # 0: not pressed, 1: pressed. Only 1 field can be 1.

        # Link events
        self.btn1.when_pressed = self.set_btn1_status
        self.btn2.when_pressed = self.set_btn2_status
        self.btn3.when_pressed = self.set_btn3_status
        self.btn4.when_pressed = self.set_btn4_status

    def set_btn1_status(self):
        self.status_table = [1, 0, 0, 0]

    def set_btn2_status(self):
        self.status_table = [0, 1, 0, 0]

    def set_btn3_status(self):
        self.status_table = [0, 0, 1, 0]

    def set_btn4_status(self):
        self.status_table = [0, 0, 0, 1]

    def clear_status(self):
        "Call this after the event is handled."
        self.status_table = [0, 0, 0, 0]


class Display2In7Driver(object):
    def __init__(self, node_id):
        self.prj_dir = os.getcwd()
        self.font_dir = os.path.join(self.prj_dir, "fonts")
        self.lib_dir = os.path.join(self.prj_dir, "lib")  # not used

        self.node_id = node_id
        self.canvas_id = 1  # incremental.
        self.init_epd27()
        self.set_font()
        self.init_default_canvas()

    def init_epd27(self):  # 27 here means 2.7 inches.
        self.epd = epd2in7.EPD()
        self.epd.init()
        self.width = self.epd.width  # 264
        self.height = self.epd.height  # 176
        self.epd.Clear(0xFF)

    def set_font(self):
        self.font18 = ImageFont.truetype(
            op.join(self.font_dir, "LiberationSans-Regular.ttf"), 18
        )
        self.font24 = ImageFont.truetype(
            op.join(self.font_dir, "LiberationSans-Regular.ttf"), 24
        )  # 6 rows, 20 cols
        self.font35 = ImageFont.truetype(
            op.join(self.font_dir, "LiberationSans-Regular.ttf"), 35
        )
        self.font_mono_18 = ImageFont.truetype(
            op.join(self.font_dir, "SourceCodePro-Regular.otf"), 18
        )
        self.font_mono_24 = ImageFont.truetype(
            op.join(self.font_dir, "SourceCodePro-Regular.otf"), 24
        )
        self.font_mono_35 = ImageFont.truetype(
            op.join(self.font_dir, "SourceCodePro-Regular.otf"), 35
        )
        self.font_mono_bold_18 = ImageFont.truetype(
            op.join(self.font_dir, "SourceCodePro-Bold.otf"), 18
        )
        self.font_mono_bold_24 = ImageFont.truetype(
            op.join(self.font_dir, "SourceCodePro-Bold.otf"), 24
        )
        self.font_mono_bold_35 = ImageFont.truetype(
            op.join(self.font_dir, "SourceCodePro-Bold.otf"), 35
        )

    def init_default_canvas(self):
        self.dft_image = Image.new("1", (self.height, self.width), 1)
        # 255: clear the frame
        self.dft_drawer = ImageDraw.Draw(self.dft_image)

    def clean_screen(self):
        self.epd.Clear(0xFF)

    def display_ft24_page(self, text_list):
        if len(text_list) < 1:
            logging.warning("Empty text list.")
            return
        elif len(text_list) > 6:
            logging.warning("List too long, will truncate.")
        canvas = Image.new("1", (self.height, self.width), 1)
        # 255: clear the frame
        self.canvas_id += 1
        drawer = ImageDraw.Draw(canvas)
        for row, txt in enumerate(text_list):
            drawer.text((10, row * 28 + 4), txt, font=self.font24, fill=0)

        self.epd.display(self.epd.getbuffer(canvas))
        # self.epd.sleep()

    def display_stock_welcome_screen(self, stock_list):
        "Make sure there is no white screen while fetching stocks."
        logging.info("Show STOCK module welcome screen.")
        stock_welcome_img = Image.new("1", (self.height, self.width), 1)
        sw_drawer = ImageDraw.Draw(stock_welcome_img)
        sw_drawer.text((10, 10), "Fetching stocks", font=self.font35, fill=0)
        sw_drawer.text(
            (10, 65), " ".join(stock_list[:3]), font=self.font_mono_bold_24, fill=0
        )
        sw_drawer.text(
            (10, 95), " ".join(stock_list[3:]), font=self.font_mono_bold_24, fill=0
        )
        self.epd.display(self.epd.getbuffer(stock_welcome_img))

    def display_stock_ft24_page(self, text_list):
        "Display stock. ticker uses mono font. Others use normal font. Input: list of tuple of text"
        if len(text_list) < 1:
            logging.warning("Empty text list.")
            return
        elif len(text_list) > 6:
            logging.warning("List too long, will truncate.")
        canvas = Image.new("1", (self.height, self.width), 1)
        # 255: clear the frame
        self.canvas_id += 1
        drawer = ImageDraw.Draw(canvas)
        for row, txt in enumerate(text_list):
            drawer.text((10, row * 28 + 4), txt[0], font=self.font_mono_bold_24, fill=0)
            drawer.text((85, row * 28 + 4), txt[1], font=self.font24, fill=0)

        self.epd.display(self.epd.getbuffer(canvas))
        # self.epd.sleep()

    def update_screen_example(self):
        logging.info("Draw an example")
        Himage = Image.new("1", (self.height, self.width), 1)
        # 1: white color
        drawer = ImageDraw.Draw(Himage)
        drawer.text((10, 0), "Text mode, AB!", font=self.font24, fill=0)
        drawer.line([(10, 29), (254, 29)], fill=0)
        drawer.text((10, 30), "hello world, CD!", font=self.font_mono_24, fill=0)
        drawer.line([(10, 59), (254, 59)], fill=0)
        drawer.text((10, 60), "Time for dinner!", font=self.font24, fill=0)
        drawer.text((10, 90), "Rainy: Yes", font=self.font24, fill=0)
        drawer.text((10, 120), "TODO: laundry", font=self.font_mono_24, fill=0)
        drawer.text((10, 150), "Leetcode: 154", font=self.font24, fill=0)
        self.epd.display(self.epd.getbuffer(Himage))
        # self.epd.sleep()

    def epd_exit(self):
        self.epd.Dev_exit()
        epd2in7.epdconfig.module_exit()

    def display_posture_reminder_sign(self):
        pr_img = Image.new("1", (self.height, self.width), 1)
        pr_drawer = ImageDraw.Draw(pr_img)
        pr_font = ImageFont.truetype(
            op.join(self.font_dir, "SourceCodePro-Bold.otf"), 80
        )

        pr_drawer.text((70, 0), "UP!", font=pr_font, fill=0)
        pr_drawer.text((10, 80), "RIGHT", font=pr_font, fill=0)

        self.epd.display(self.epd.getbuffer(pr_img))

    def debug_button_press_display(self, pressed_btn_idx):
        "Show the press event on the screen."
        ind_img = Image.new("1", (self.height, self.width), 1)
        ind_drawer = ImageDraw.Draw(ind_img)
        ind_drawer.text(
            (10, 10),
            "Button {0} pressed".format(pressed_btn_idx),
            font=self.font24,
            fill=0,
        )
        self.epd.display(self.epd.getbuffer(ind_img))

    def display_clock_current_time(self):

        clk_img = Image.new("1", (self.height, self.width), 1)
        clk_drawer = ImageDraw.Draw(clk_img)
        clk_font = ImageFont.truetype(
            op.join(self.font_dir, "LiberationSans-Regular.ttf"), 100
        )

        timestamp = datetime.datetime.today()
        clk_drawer.text(
            (5, 0),
            "{0:02d}:{1:02d}".format(timestamp.hour, timestamp.minute),
            font=clk_font,
            fill=0,
        )
        self.epd.display(self.epd.getbuffer(clk_img))


"""
# Originally in: https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/examples/epd_2in7b_V2_test.py
try:

    logging.info("epd2in7 Demo")
    epd = epd2in7.EPD()

    # 2Gray(Black and white) display
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)
    font24 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 18)
    font35 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 35)
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new("1", (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((10, 0), "hello world", font=font24, fill=0)
    draw.text((150, 0), u"微雪电子", font=font24, fill=0)
    draw.line((20, 50, 70, 100), fill=0)
    draw.line((70, 50, 20, 100), fill=0)
    draw.rectangle((20, 50, 70, 100), outline=0)
    draw.line((165, 50, 165, 100), fill=0)
    draw.line((140, 75, 190, 75), fill=0)
    draw.arc((140, 50, 190, 100), 0, 360, fill=0)
    draw.rectangle((80, 50, 130, 100), fill=0)
    draw.chord((200, 50, 250, 100), 0, 360, fill=0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    # Drawing on the Vertical image
    logging.info("2.Drawing on the Vertical image...")
    Limage = Image.new("1", (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Limage)
    draw.text((2, 0), "hello world", font=font18, fill=0)
    draw.text((20, 50), u"微雪电子", font=font18, fill=0)
    draw.line((10, 90, 60, 140), fill=0)
    draw.line((60, 90, 10, 140), fill=0)
    draw.rectangle((10, 90, 60, 140), outline=0)
    draw.line((95, 90, 95, 140), fill=0)
    draw.line((70, 115, 120, 115), fill=0)
    draw.arc((70, 90, 120, 140), 0, 360, fill=0)
    draw.rectangle((10, 150, 60, 200), fill=0)
    draw.chord((70, 150, 120, 200), 0, 360, fill=0)
    epd.display(epd.getbuffer(Limage))
    time.sleep(2)

    logging.info("3.read bmp file")
    Himage = Image.open(os.path.join(picdir, "2in7.bmp"))
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    logging.info("4.read bmp file on window")
    Himage2 = Image.new("1", (epd.height, epd.width), 255)  # 255: clear the frame
    bmp = Image.open(os.path.join(picdir, "100x100.bmp"))
    Himage2.paste(bmp, (50, 10))
    epd.display(epd.getbuffer(Himage2))
    time.sleep(2)

    # 4Gray display
    logging.info("4Gray display--------------------------------")
    epd.Init_4Gray()

    Limage = Image.new("L", (epd.width, epd.height), 0)  # 255: clear the frame
    draw = ImageDraw.Draw(Limage)
    draw.text((20, 0), u"微雪电子", font=font35, fill=epd.GRAY1)
    draw.text((20, 35), u"微雪电子", font=font35, fill=epd.GRAY2)
    draw.text((20, 70), u"微雪电子", font=font35, fill=epd.GRAY3)
    draw.text((40, 110), "hello world", font=font18, fill=epd.GRAY1)
    draw.line((10, 140, 60, 190), fill=epd.GRAY1)
    draw.line((60, 140, 10, 190), fill=epd.GRAY1)
    draw.rectangle((10, 140, 60, 190), outline=epd.GRAY1)
    draw.line((95, 140, 95, 190), fill=epd.GRAY1)
    draw.line((70, 165, 120, 165), fill=epd.GRAY1)
    draw.arc((70, 140, 120, 190), 0, 360, fill=epd.GRAY1)
    draw.rectangle((10, 200, 60, 250), fill=epd.GRAY1)
    draw.chord((70, 200, 120, 250), 0, 360, fill=epd.GRAY1)
    epd.display_4Gray(epd.getbuffer_4Gray(Limage))
    time.sleep(2)

    # display 4Gra bmp
    Himage = Image.open(os.path.join(picdir, "2in7_Scale.bmp"))
    epd.display_4Gray(epd.getbuffer_4Gray(Himage))
    time.sleep(2)

    logging.info("Clear...")
    epd.Clear(0xFF)
    logging.info("Goto Sleep...")
    epd.sleep()
    time.sleep(3)

    epd.Dev_exit()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit()
    exit()
"""
