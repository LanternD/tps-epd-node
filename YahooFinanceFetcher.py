import datetime
import logging as lg
import requests
import urllib

import yfinance as yh


class YahooFinanceFetcher:
    def __init__(self, stock_list):
        "Call the Yahoo Finance API to fetch the latest stock info"
        if len(stock_list) > 6:
            stock_list = stock_list[:6]
        elif len(stock_list) == 0:
            lg.error("Empty stock list. Program stopped")
            return

        self.stock_list = stock_list
        lg.info("Stock List: {0}".format(stock_list))

        self.tks = {x: None for x in self.stock_list}  # assume they are valid
        self.tks_info = {x: None for x in self.stock_list}
        self.create_stock_handler()

    def create_stock_handler(self):
        "May not need this again. (20201221)"
        for tk in self.stock_list:
            self.tks[tk] = yh.Ticker(tk)

    def check_stock_integrity(self, stock_name):
        "Some stock, like UVXY, failed to get info thru API. This function test whether the whole process works for the stock or not."
        temp_stock = yh.Ticker(stock_name)
        try:
            info_d = temp_stock.info
            lg.info("The given stock {0} works well.".format(stock_name))
            lg.info("Stock price: {0}".format(info_d["regularMarketPrice"]))
        except IndexError:
            lg.error("The given stock {0} is not working.".format(stock_name))
        return

    def refresh_stock_info_dict(self):
        "Recreate the ticker handlers to triger the fetch."
        for tk in self.stock_list:
            # TODO: this is not elegant. find a better way later.
            self.tks[tk] = None
            self.tks[tk] = yh.Ticker(tk)  # re-create the stock handler.
            try:
                info_json = self.tks[tk].info  # fetch from server
            except (requests.exceptions.ConnectionError, urllib.error.HTTPError, KeyError, IndexError, requests.exceptions.ChunkedEncodingError):
                lg.error("Connection error, waiting for the next round")
                info_json = {"previousClose": 0, "bid": 0, "ask": 0, "bidSize": 1, "askSize": 1}
                self.tks_info[tk] = info_json
            else:   
                self.tks_info[tk] = info_json

    def get_stock_markget_price(self):
        "Price now. Make sure the info dict is refreshed."

        def calculate_price_quote(bid, bid_size, ask, ask_size):
            "Weighted average"
            return (bid * bid_size + ask * ask_size) / (bid_size + ask_size)

        pd = {}
        for tk in self.stock_list:
            quotes = calculate_price_quote(
                self.tks_info[tk]["bid"],
                self.tks_info[tk]["bidSize"],
                self.tks_info[tk]["ask"],
                self.tks_info[tk]["askSize"],
            )
            pd[tk] = quotes
        return pd

    def get_previous_close(self):
        "Close price. Make sure the info dict is refreshed."
        pcd = {}
        for tk in self.stock_list:
            pcd[tk] = self.tks_info[tk]["previousClose"]
        return pcd

    def format_display_2in7(self):
        "From dictionary to EPD format."
        rg_dict = self.get_stock_markget_price()
        cp_dict = self.get_previous_close()
        text_list = []

        for tk in self.stock_list:
            text_buf = "{0:.2f}".format(rg_dict[tk])
            price_diff = rg_dict[tk] - cp_dict[tk]

            if price_diff < 0:
                text_buf += " ▼{0:.2f}".format(-price_diff)
            else:
                text_buf += " ▲{0:.2f}".format(price_diff)
            text_list.append((tk, text_buf))
        return text_list

    def is_market_open(self):
        "Determine whether the market is open"
        td = datetime.datetime.today()
        wd = td.weekday()
        if wd >= 5:
            return False
        hour = td.hour
        minu = td.minute
        if not (8, 55) <= (hour, minu) <= (16, 55):
            return False

        return True

    def is_working_time(self):
        "Determine whether to show the up-right sign"
        td = datetime.datetime.today()
        hour = td.hour
        minu = td.minute
        if (0, 5) <= (hour, minu) <= (9, 00):
            return False

        return True
