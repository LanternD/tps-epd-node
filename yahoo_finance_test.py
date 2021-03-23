import logging

from YahooFinanceFetcher import YahooFinanceFetcher

logging.basicConfig(
    format="\033[92m[%(levelname)s]\033[00m %(message)s", level=logging.INFO
)


def test_yh_finance_main():
    stk_list = ["TSLA", "AAPL", "ARKW", "ARKK", "NIO", "AMZN"]
    my_yhff = YahooFinanceFetcher(stk_list)
    my_yhff.refresh_stock_info_dict()
    # logging.info("Previous close: {0}".format(my_yhff.get_previous_close()))
    # logging.info("Price: {0}".format(my_yhff.get_regular_markget_price()))
    logging.info(my_yhff.format_display_2in7())
    # my_yhff.check_stock_integrity('NIO')
    # logging.info("Market open: {0}".format(my_yhff.is_market_open()))


if __name__ == "__main__":
    test_yh_finance_main()
