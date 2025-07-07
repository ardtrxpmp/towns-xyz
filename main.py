import random
import pyuseragents
from loguru import logger
from traceback import format_exc
from core.modules.towns import Towns
from core.utils.helpers import sleeping
from playwright.sync_api import sync_playwright

from functions import (
    towns_login,
    join_town_from_invite,
    create_town,
    fund_towns_wallet,
    link_wallet,
    daily_tap,
)
from data.config import PRIVATE_KEYS, PROXIES, CONFIG_FILE, ACCOUNT_NAMES, EMAILS

shuffle_keys = CONFIG_FILE["settings"]["randomize"]["shuffle_keys"]
chatgpt_api_key = CONFIG_FILE["settings"]["gpt"]["api_key"]


def main():
    module_choice = int(
        input(
            "Choose module:\n\n"
            "[1] Create town\n"
            "[2] Join town from invite\n"
            "[3] Fund Towns wallet\n"
            "[4] Link EVM to Towns\n"
            "[5] Daily Tap(Beaver)\n"
        )
    )

    module_mapping = {
        1: create_town,
        2: join_town_from_invite,
        3: fund_towns_wallet,
        4: link_wallet,
        5: daily_tap,
    }

    account_names = ACCOUNT_NAMES
    private_keys = PRIVATE_KEYS
    proxies = PROXIES
    emails = EMAILS

    if shuffle_keys:
        combined_items = list(zip(PRIVATE_KEYS, PROXIES, EMAILS))
        if len(combined_items) > 1:
            random.shuffle(combined_items)
            private_keys, proxies, emails = zip(*combined_items)

    for name, key, proxy, email in list(
        zip(account_names, private_keys, proxies, emails)
    ):

        # Doesn't work without context manager
        with sync_playwright() as pw:
            for _ in range(5):
                user_agent = pyuseragents.random()
                try:
                    if module_choice == 4:
                        towns = Towns(
                            account_name=name,
                            private_key=key,
                            user_agent=user_agent,
                            proxy=proxy,
                            email_data=email,
                            openai_api_key=chatgpt_api_key,
                            headless_browser=False,
                            playwright_instance=pw,
                        )
                        page = towns_login(
                            towns=towns, link_wallet=True, persistent_context=True
                        )
                        link_wallet(towns=towns, page=page)
                        break
                    else:
                        towns = Towns(
                            account_name=name,
                            private_key=key,
                            user_agent=user_agent,
                            proxy=proxy,
                            email_data=email,
                            openai_api_key=chatgpt_api_key,
                            headless_browser=True,
                            playwright_instance=pw,
                        )
                    page = towns_login(towns=towns)
                    res = module_mapping[module_choice](towns, page)
                    if module_choice in [1, 2]:
                        new_page, chat_url = res
                        towns.chat(page=new_page, chat_link=chat_url)
                    break
                except Exception:
                    logger.error(f"Exception - account {name}, error: {format_exc()}")
                finally:
                    towns.cleanup()

        sleeping(2)


if __name__ == "__main__":
    main()
