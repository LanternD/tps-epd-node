import datetime
import logging
import time
import urllib

#import schedule
from Display2In7Driver import Display2In7Driver, EpdHatButtonHandler
from YahooFinanceFetcher import YahooFinanceFetcher

logging.basicConfig(
    format="\033[92m[%(levelname)s]\033[00m %(message)s", level=logging.INFO
)

# State machine (macro)
NULL_STATE = 0
STOCK_STREAMING = 1
POSTURE_REMINDER = 2
CLOCK = 3

stk_list = ["AAPL", "ARKW", "TSLA", "U", "TQQQ", "MSFT"]


def epd_node_main():
    "The information from the submodules is merged here and redistributed to the corresponding destination modules. Timestamp-based state machine"

    # Handler/Driver initialization
    disp_drv = Display2In7Driver("HW")
    yhff = YahooFinanceFetcher(stk_list)
    btns = EpdHatButtonHandler()

    refresh_count = 0
    previous_stock_list = None
    last_ts = {"stock": 0, "posture": time.time()}  # last timestamp
    prev_refresh_quotient = -1
    prev_key_state = STOCK_STREAMING  # fall back after upright reminder.

    run_state = STOCK_STREAMING  # state machine
    clock_next_refresh_minute = 0

    while True:
        # May need some other way to halt the program.

        # Scan for pressed key
        key_pressed = -1
        for idx, st in enumerate(btns.status_table):
            if st == 1:
                key_pressed = idx + 1
                break

        if key_pressed == 1:
            run_state = STOCK_STREAMING
            prev_key_state = STOCK_STREAMING
            # Display previous list but not fetching new data.
            if previous_stock_list is not None:
                disp_drv.display_stock_ft24_page(previous_stock_list)  # switch back
        elif key_pressed == 2:
            run_state = CLOCK
            prev_key_state = CLOCK
            clock_next_refresh_minute = datetime.datetime.today().minute
        elif key_pressed in {3, 4}:
            run_state = NULL_STATE
            disp_drv.debug_button_press_display(key_pressed)
        else:
            # No key pressed
            # run_state = NULL_STATE
            pass  # do not change state.

        btns.clear_status()

        if run_state == NULL_STATE:
            time.sleep(0.5)
            continue

        screen_updated = 0
        if run_state == STOCK_STREAMING and time.time() - last_ts["stock"] > 300:
            if previous_stock_list is None or yhff.is_market_open():
                # No need to update repeatedly during market close.
                if previous_stock_list is None:
                    # Only show this during the first fetch
                    disp_drv.display_stock_welcome_screen(yhff.stock_list)

                stock_disp_list = stock_streaming(yhff)
                if stock_disp_list != previous_stock_list:
                    disp_drv.display_stock_ft24_page(stock_disp_list)
                    previous_stock_list = stock_disp_list
                    last_ts["stock"] = time.time()  # update timestamp
                    screen_updated = 1

                else:
                    logging.debug(
                        "No change from the last stock list, do not update screen."
                    )
            run_state = POSTURE_REMINDER
        elif (
            run_state == POSTURE_REMINDER
            and time.time() - last_ts["posture"] > 300
            and yhff.is_working_time()
        ):
            # TODO: put the is_working_time() function to other module.
            posture_reminder_routine(disp_drv)
            last_ts["posture"] = time.time()
            if previous_stock_list is not None:
                disp_drv.display_stock_ft24_page(previous_stock_list)  # switch back
            screen_updated = 1
            run_state = prev_key_state
        elif run_state == CLOCK:
            is_updated = clock_refresh_routine(disp_drv, clock_next_refresh_minute)
            if is_updated:
                clock_next_refresh_minute = (clock_next_refresh_minute + 3) % 60
                screen_updated = 1

        else:
            pass

        time.sleep(0.5)  # wake up periodically to check
        refresh_count += screen_updated
        if refresh_count % 10 == 0 and refresh_count // 10 != prev_refresh_quotient:
            logging.info("Screen refresh count: {0}".format(refresh_count))
            prev_refresh_quotient = refresh_count // 10
    exit()


def posture_reminder_routine(epd_driver):
    epd_driver.display_posture_reminder_sign()
    time.sleep(5)


def stock_streaming(yhf_fetcher):
    "A sub-routine for displaying the stock price info."
    try:
        yhf_fetcher.refresh_stock_info_dict()
        return yhf_fetcher.format_display_2in7()
    except (urllib.error.HTTPError, IndexError):
        err_stock_list = []
        for stk in stk_list:
            err_stock_list.append((stk, "  Service N/A"))
        return err_stock_list


def clock_refresh_routine(epd_driver, next_refresh_minute):
    current_min = datetime.datetime.today().minute
    if current_min == next_refresh_minute:
        epd_driver.display_clock_current_time()
        return True
    else:
        return False


if __name__ == "__main__":
    epd_node_main()
