import time

import schedule
from Display2In7Driver import Display2In7Driver, EpdHatButtonHandler


def test_epd2in7_main(demo_choice=1):
    disp_drv = Display2In7Driver("HW")

    if demo_choice == 1:

        text_list = [
            "hello world, DY!",
            "hello world, MS!",
            "Time for lunch!",
            "Robinhood: 1995.43",
            "UVXY: 11.33",
            "Temp: -2, -5/-3",
        ]
        # disp_drv.update_screen_example()
        disp_drv.display_ft24_page(text_list)
    elif demo_choice == 2:
        stock_examples = [
            ("TSLA", "668.90 ▲13.00"),
            ("AAPL", "128.96 ▲0.26"),
            ("ARKW", "151.05 ▲1.59"),
            ("ARKK", "127.57 ▲1.50"),
        ]
        disp_drv.display_stock_ft24_page(stock_examples)

    elif demo_choice == 3:
        disp_drv.display_posture_reminder_sign()

    elif demo_choice == 4:
        btns = EpdHatButtonHandler()
        while True:
            key_pressed = -1
            for idx, st in enumerate(btns.status_table):
                if st == 1:
                    key_pressed = idx + 1
                    break

            if key_pressed != -1:
                disp_drv.debug_button_press_display(key_pressed)
                btns.clear_status()

            time.sleep(0.5)

    elif demo_choice == 5:
        disp_drv.display_clock_current_time()
        schedule.every(3).minutes.do(disp_drv.display_clock_current_time)
        # Do not update that too frequently.
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    test_epd2in7_main(5)
