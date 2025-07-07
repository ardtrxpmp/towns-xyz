import os
import time
import json
from pathlib import Path
from loguru import logger
from requests import Session
from core.utils.decorators import retry
from core.utils.networks import Networks
from core.clients.evm_client import EvmClient
from core.modules.metamask_pw import MetamaskConnector
from core.modules.gpt import ask_chatgpt
from playwright.sync_api import Page, BrowserContext, Playwright, Locator
from core.modules.email_parser import connect_imap, get_accesstoken
from core.utils.user_data import get_user_data_path, remove_user_data, EXTENSION_PATH
from core.utils.helpers import (
    get_pw_proxy_config,
    process_email_item,
    get_random_amount,
    get_random_town,
)


class Towns(EvmClient):
    def __init__(
        self,
        account_name: str | int,
        private_key: str,
        user_agent: str,
        proxy: str,
        email_data: str,
        openai_api_key: str,
        headless_browser: bool = False,
        playwright_instance: Playwright | None = None,
    ):
        super().__init__(
            account_name=account_name,
            private_key=private_key,
            network=Networks.Base,
            user_agent=user_agent,
            proxy=proxy,
        )
        self.email_data = email_data
        self.session = Session()
        self.module_name = "Towns"
        self.proxy_config = get_pw_proxy_config(self.proxy)
        self.email_item = process_email_item(self.email_data)
        self.api_key = openai_api_key
        self.headless = headless_browser
        self.pw = playwright_instance

    def init_browser_instance(
        self,
        is_for_link: bool = False,
        launch_headless: bool = False,
        inject_storage: bool = False,
    ):
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - creating browser instance...'
        )
        self.persistent_context = False

        pw = self.pw

        if is_for_link:
            if launch_headless:
                context = pw.chromium.launch_persistent_context(
                    user_data_dir=get_user_data_path(account_id=self.account_name),
                    headless=True,
                    proxy=self.proxy_config,
                    slow_mo=1000,
                    java_script_enabled=True,
                    user_agent=self.user_agent,
                    accept_downloads=True,
                    args=[
                        f"--disable-extensions-except={EXTENSION_PATH}",
                        f"--load-extension={EXTENSION_PATH}",
                        "--enable-clipboard",
                        "--disable-blink-features=AutomationControlled",
                    ],
                    locale="en-US",
                    screen={"height": 720, "width": 1280},
                    viewport={"height": 1080, "width": 1920},
                    timeout=80000,
                )
            else:
                context = pw.chromium.launch_persistent_context(
                    user_data_dir=get_user_data_path(account_id=self.account_name),
                    headless=False,
                    proxy=self.proxy_config,
                    slow_mo=1000,
                    java_script_enabled=True,
                    user_agent=self.user_agent,
                    accept_downloads=True,
                    args=[
                        f"--disable-extensions-except={EXTENSION_PATH}",
                        f"--load-extension={EXTENSION_PATH}",
                        "--enable-clipboard",
                        "--disable-blink-features=AutomationControlled",
                    ],
                    locale="en-US",
                    viewport={"height": 1080, "width": 1920},
                    screen={"height": 720, "width": 1280},
                    timeout=80000,
                )
                self.persistent_context = True
        else:
            if launch_headless:
                if inject_storage:

                    browser = pw.chromium.launch(
                        headless=True,
                        proxy=self.proxy_config,
                        slow_mo=1000,
                        args=[
                            f"--disable-extensions-except={EXTENSION_PATH}",
                            f"--load-extension={EXTENSION_PATH}",
                            "--enable-clipboard",
                            "--disable-blink-features=AutomationControlled",
                        ],
                        timeout=80000,
                    )
                    context = browser.new_context(
                        storage_state=os.path.join(
                            os.getcwd(),
                            Path(
                                f'data/storage_states/{self.email_item["email"].split("@")[0]}.json'
                            ),
                        ),
                        java_script_enabled=True,
                        viewport={"height": 1080, "width": 1920},
                        screen={"height": 720, "width": 1280},
                        user_agent=self.user_agent,
                    )
                    self.browser = browser
                else:
                    browser = pw.chromium.launch(
                        headless=True,
                        proxy=self.proxy_config,
                        slow_mo=1000,
                        args=[
                            f"--disable-extensions-except={EXTENSION_PATH}",
                            f"--load-extension={EXTENSION_PATH}",
                            "--enable-clipboard",
                            "--disable-blink-features=AutomationControlled",
                        ],
                        timeout=80000,
                    )
                    context = browser.new_context(
                        java_script_enabled=True,
                        viewport={"height": 1080, "width": 1920},
                        screen={"height": 720, "width": 1280},
                        user_agent=self.user_agent,
                    )
                    self.browser = browser
            else:
                if inject_storage:

                    browser = pw.chromium.launch(
                        headless=False,
                        proxy=self.proxy_config,
                        slow_mo=1000,
                        args=[
                            f"--disable-extensions-except={EXTENSION_PATH}",
                            f"--load-extension={EXTENSION_PATH}",
                            "--enable-clipboard",
                            "--disable-blink-features=AutomationControlled",
                        ],
                        timeout=80000,
                    )
                    context = browser.new_context(
                        storage_state=os.path.join(
                            os.getcwd(),
                            Path(
                                f'data/storage_states/{self.email_item["email"].split("@")[0]}.json'
                            ),
                        ),
                        java_script_enabled=True,
                        viewport={"height": 1080, "width": 1920},
                        screen={"height": 720, "width": 1280},
                        user_agent=self.user_agent,
                    )
                    self.browser = browser
                else:
                    browser = pw.chromium.launch(
                        headless=False,
                        proxy=self.proxy_config,
                        slow_mo=1000,
                        args=[
                            f"--disable-extensions-except={EXTENSION_PATH}",
                            f"--load-extension={EXTENSION_PATH}",
                            "--enable-clipboard",
                            "--disable-blink-features=AutomationControlled",
                        ],
                        timeout=80000,
                    )
                    context = browser.new_context(
                        java_script_enabled=True,
                        viewport={"height": 1080, "width": 1920},
                        screen={"height": 720, "width": 1280},
                        user_agent=self.user_agent,
                    )
                    self.browser = browser

        self.pw = pw
        self.context: BrowserContext = context
        self.context.grant_permissions(
            ["clipboard-read", "clipboard-write", "storage-access"]
        )

        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - browser instance created.'
        )

    def init_metamask_connector(self, page: Page):
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - initializing wallet connector'
        )

        self.metamask = MetamaskConnector(
            account_name=self.account_name,
            private_key=self.private_key,
            page=page,
            context=self.context,
        )

        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - wallet connector initialized'
        )

    @retry
    def fetch_code(self) -> str | int | None:
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - attempting to fetch verification code'
        )

        email_addr = self.email_item["email"]
        refresh_token = self.email_item["refresh_token"]
        client_id = self.email_item["client_id"]
        access_token = get_accesstoken(refresh_token=refresh_token, client_id=client_id)
        if access_token:
            res = connect_imap(emailadr=email_addr, access_token=access_token)
            logger.success(
                f'{self.account_name} | {self.email_item["email"]} - got code: {res}'
            )
            return res
        raise Exception("Failed to get access token")

    def login(
        self, is_for_link: bool = False, persistent_context: bool = False
    ) -> Page:
        from data.config import WORKING_DIR

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - started logging in'
        )

        res_cookie_inject = None

        if not persistent_context:

            if os.path.exists(
                path=os.path.join(
                    WORKING_DIR,
                    Path(
                        f'data/saved_cookies/{self.email_item["email"].split("@")[0]}.json'
                    ),
                )
            ) and os.path.exists(
                path=os.path.join(
                    WORKING_DIR,
                    Path(
                        f'data/storage_states/{self.email_item["email"].split("@")[0]}.json'
                    ),
                )
            ):
                if is_for_link:
                    self.init_browser_instance(
                        launch_headless=self.headless,
                        inject_storage=True,
                        is_for_link=True,
                    )
                else:
                    self.init_browser_instance(
                        launch_headless=self.headless,
                        inject_storage=True,
                        is_for_link=False,
                    )
                page = self.context.new_page()
                res_cookie_inject = self.load_cookies()

            if res_cookie_inject:

                page.goto("https://app.towns.com/explore")
                page.wait_for_load_state(timeout=10000)
                page.wait_for_timeout(10000)
                logger.success(
                    f'{self.account_name} | {self.email_item["email"]} - cookie login complete!'
                )
                return page

            if is_for_link:
                self.init_browser_instance(launch_headless=False, is_for_link=True)
            else:
                self.init_browser_instance(
                    launch_headless=self.headless, is_for_link=False
                )

            page = self.context.new_page()

            page.goto("https://app.towns.com")
            page.wait_for_load_state(timeout=60000)
            page.wait_for_timeout(10000)

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - choosing login option'
            )

            login_button = page.locator(
                '//*[@id="root"]/div[1]/div/div[2]/div/div/div/button/div[1]'
            )
            login_button.click(force=True, timeout=2000)

            more_options = page.locator(
                '//*[@id="privy-modal-content"]/div/div[1]/div[3]/div/button[4]/div'
            )
            more_options.click(force=True, timeout=1000)
            page.wait_for_timeout(1000)
            email_login = page.locator(
                '//*[@id="privy-modal-content"]/div/div[1]/div[2]/div/div[4]/button'
            )
            email_login.click(force=True, timeout=1000)
            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - submitting email'
            )
            email_input = page.locator('//*[@id="email-input"]')
            email_input.click(force=True, timeout=2000)
            email_input.fill(force=True, value=self.email_item["email"], timeout=15000)
            page.wait_for_timeout(1000)
            submit_button = page.locator(
                '//*[@id="privy-modal-content"]/div/div[1]/div[2]/div/div[3]/div/label/button/span[2]/span'
            )

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - sending verification code'
            )

            submit_button.click(force=True, timeout=1000)
            page.wait_for_timeout(5000)

            all_subfields = [
                f'//*[@id="privy-modal-content"]/div/div[1]/div[2]/div[2]/div[1]/div[2]/input[{idx}]'
                for idx in range(1, 7)
            ]

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - fetching code'
            )

            time.sleep(25)
            res = self.fetch_code()

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - pasting code'
            )

            for arr_id, xpath in enumerate(all_subfields, start=0):
                locator = page.locator(xpath)
                locator.fill(res[arr_id], force=True, timeout=1000)

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - waiting for privy login to complete'
            )
            page.wait_for_load_state()
            page.wait_for_timeout(10000)
            page.goto("https://app.towns.com/explore")
            page.wait_for_load_state()
            page.wait_for_timeout(10000)

            self.save_cookies()
            self.save_storage()
            return page
        else:
            if is_for_link:
                self.init_browser_instance(launch_headless=False, is_for_link=True)
            else:
                self.init_browser_instance(
                    launch_headless=self.headless, is_for_link=False
                )

            page = self.context.new_page()

            page.goto("https://app.towns.com")
            page.wait_for_load_state(timeout=60000)
            page.wait_for_timeout(10000)

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - choosing login option'
            )

            login_button = page.locator(
                '//*[@id="root"]/div[1]/div/div[2]/div/div/div/button/div[1]'
            )
            login_button.click(force=True, timeout=2000)

            more_options = page.locator(
                '//*[@id="privy-modal-content"]/div/div[1]/div[3]/div/button[4]/div'
            )
            more_options.click(force=True, timeout=2000)
            page.wait_for_timeout(1000)
            email_login = page.locator(
                '//*[@id="privy-modal-content"]/div/div[1]/div[2]/div/div[4]/button'
            )
            email_login.click(force=True, timeout=1000)

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - submitting email'
            )

            email_input = page.locator('//*[@id="email-input"]')
            email_input.click(force=True, timeout=2000)
            email_input.fill(force=True, value=self.email_item["email"], timeout=15000)
            page.wait_for_timeout(1000)
            submit_button = page.locator(
                '//*[@id="privy-modal-content"]/div/div[1]/div[2]/div/div[3]/div/label/button/span[2]/span'
            )

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - sending verification code'
            )

            submit_button.click(force=True, timeout=1000)
            page.wait_for_timeout(10000)
            all_subfields = [
                f'//*[@id="privy-modal-content"]/div/div[1]/div[2]/div[2]/div[1]/div[2]/input[{idx}]'
                for idx in range(1, 7)
            ]

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - fetching code'
            )

            time.sleep(25)
            res = self.fetch_code()

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - pasting code'
            )

            for arr_id, xpath in enumerate(all_subfields, start=0):
                locator = page.locator(xpath)
                locator.fill(res[arr_id], force=True, timeout=1000)

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - waiting for privy login to complete'
            )
            page.wait_for_load_state()
            page.wait_for_timeout(10000)
            page.goto("https://app.towns.com/explore")
            page.wait_for_load_state()
            page.wait_for_timeout(10000)

            self.save_cookies()
            self.save_storage()
            return page

    def fetch_internal_wallet(self, page: Page) -> str:
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - resetting to the Explore page'
        )

        if (
            page.url == "https://app.towns.com/explore"
            or page.url == "app.towns.com/explore"
        ):
            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - we are already on the Explore page'
            )
        else:
            page.goto("https://app.towns.com/explore")
            page.wait_for_load_state()
            page.wait_for_timeout(5000)

        page.reload()
        page.wait_for_load_state()
        page.wait_for_timeout(20000)

        logger.info(
            f"{self.account_name} | {self.email_item['email']} - opening profile"
        )

        profile_menu = page.locator(
            '//*[@id="root"]/div[1]/div/div[1]/div/div[4]/div[4]/div/div/div/div'
        )
        profile_menu.wait_for(state="visible", timeout=30000)
        profile_menu.click(force=True, timeout=5000)
        page.wait_for_timeout(2000)

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - copying to clipboard'
        )

        copy_field = page.locator(
            '//*[@id="root"]/div[1]/div/div[2]/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/div/div/div/span/span'
        )
        copy_field.click(force=True, timeout=10000)

        clipboard = page.evaluate("navigator.clipboard.readText()")
        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - Clipboard content copied: {clipboard}'
        )

        return clipboard, page

    @retry
    def fund_internal_wallet(self, internal_wallet_address: str):
        wallet, _ = internal_wallet_address
        self.logger.info(
            f'{self.account_name} | {self.email_item["email"]} - funding Towns wallet {wallet} from {self.address}'
        )

        amount = get_random_amount()
        amount_wei = self.to_wei(amount=amount, decimals=18)

        tx_data = self.get_tx_params(
            to_address=self.w3.to_checksum_address(wallet),
            value=amount_wei,
            data="0x",
        )

        signed = self.sign_transaction(tx_dict=tx_data)
        if signed:
            tx_hash = self.send_tx(signed_tx=signed)
            if tx_hash:
                return True

            return False

        return False

    def link_wallet(self, page: Page) -> bool:
        self.init_metamask_connector(page=page)
        page = self.metamask.setup_extension()
        if page:
            page.goto("https://app.towns.com/explore")
            page.wait_for_load_state()
            page.wait_for_timeout(5000)

            logger.info(
                f"{self.account_name} | {self.email_item['email']} - opening profile"
            )

            profile_menu = page.locator(
                '//*[@id="root"]/div[1]/div/div[1]/div/div[4]/div[4]/div/div/div/div'
            )
            profile_menu.click(force=True, timeout=1000)

            linked_wallets_button = page.locator(
                '//*[@id="root"]/div[1]/div/div[2]/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div/div[2]/button[1]'
            )
            linked_wallets_button.click(force=True, timeout=2000)

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - starting to link wallet {self.address}'
            )

            link_wallet = page.locator(
                '//*[@id="root"]/div[1]/div/div[2]/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div/button'
            )
            link_wallet.click(force=True, timeout=2000)

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - connecting wallet...'
            )

            metamask_connect = page.locator(
                '//*[@id="privy-modal-content"]/div/div[1]/div[3]/button[1]'
            )

            popup = None

            with self.context.expect_page() as mm_popup_info:
                metamask_connect.click(force=True, timeout=2000)
                page.wait_for_timeout(5000)
                popup = mm_popup_info.value

            if not popup:
                return False

            logger.success(
                f'{self.account_name} | {self.email_item["email"]} - wallet connected!'
            )

            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - connecting to Base...'
            )

            confirm_connection = popup.get_by_test_id("confirm-btn")
            confirm_connection.click(force=True, timeout=1000)
            popup.wait_for_load_state()
            connect_base = popup.get_by_test_id("confirmation-submit-button")

            logger.success(
                f'{self.account_name} | {self.email_item["email"]} - Base connected!'
            )

            sig_popup = None

            with self.context.expect_page() as sig_popup_info:
                connect_base.click(force=True, timeout=2000)
                page.wait_for_timeout(5000)
                sig_popup = sig_popup_info.value

            if not sig_popup:
                return False

            sig_popup.wait_for_load_state()
            sig_confirmation = sig_popup.get_by_test_id("confirm-footer-button")
            sig_confirmation.click(force=True, timeout=10000)

            page.wait_for_timeout(10000)
            page.wait_for_load_state()
            pay_eth_button = page.get_by_text("Pay with ETH").first
            pay_eth_button.click(force=True, timeout=15000)
            page.wait_for_timeout(10000)

            logger.success(
                f'{self.account_name} | {self.email_item["email"]} - wallet {self.address} connected successfully!'
            )

            return True

    def join_from_invite_link(self, page: Page, username: str):
        town_link = get_random_town()
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - got town link: {town_link}'
        )
        page.goto(town_link)

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - resetting to town page'
        )

        page.reload()
        page.wait_for_load_state()
        page.wait_for_timeout(10000)

        logger.info(
            f"{self.account_name} | {self.email_item['email']} - joining the town"
        )

        for _ in range(3):
            try:
                join_button = page.locator(
                    '//*[@id="root"]/div[1]/div[2]/div/div[3]/div/div[3]/div/button/div[1]'
                )
                join_button.click(force=True, timeout=2000)
                break
            except Exception:
                if page.url == town_link:
                    continue
                else:
                    try:
                        # Assuming already joined:
                        name = page.get_by_test_id("town-username-input")
                        name.fill(username, force=True, timeout=2000)
                        join_town = (
                            page.get_by_role("button").get_by_text("Join town").first
                        )
                        join_town.click(force=True, timeout=2000)
                        return page, page.url
                    except Exception as e:
                        logger.warning(f"didnt require nickname: {str(e)}")
                        return page, page.url

        page.wait_for_load_state()
        page.wait_for_timeout(15000)
        pay_eth = page.get_by_text("Pay with ETH").first
        pay_eth.click(force=True, timeout=2000)
        page.wait_for_timeout(65000)

        try:
            name = page.get_by_test_id("town-username-input")
            name.fill(username, force=True, timeout=2000)
            join_town = page.get_by_role("button").get_by_text("Join town").first
            join_town.click(force=True, timeout=2000)
        except Exception as e:
            logger.warning(f"didnt require nickname: {str(e)}")

        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - successfully joined town!'
        )
        self.save_town_data(
            town_name="Invite", town_link=page.url, created_by_user=False
        )
        return page, page.url

    def create_town(
        self,
        page: Page,
        town_name: str,
        file_path: str | Path,
        username: str,
        is_paid: bool = False,
    ):
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - resetting to the Explore page'
        )

        if (
            page.url == "https://app.towns.com/explore"
            or page.url == "app.towns.com/explore"
        ):
            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - we are already on the Explore page'
            )
        else:
            page.goto("https://app.towns.com/explore")
            page.wait_for_load_state()
            page.wait_for_timeout(5000)

        page.reload()
        page.wait_for_load_state()
        page.wait_for_timeout(10000)

        logger.info(
            f"{self.account_name} | {self.email_item['email']} - creating new town"
        )

        page.wait_for_load_state()

        add_town_button = page.locator(
            '//*[@id="root"]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[2]/a/div/div/div/div'
        )
        add_town_button.click(force=True, timeout=10000)

        page.wait_for_load_state()

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - town name: {town_name}'
        )
        name_input = page.locator('//*[@id="slideNameAndIcon.spaceName"]')
        name_input.fill(town_name, force=True, timeout=2000)

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - uploading Town image'
        )

        file_input_form = page.query_selector(
            '//*[@id="CreateTownForm"]/div[1]/div/div[1]/div[2]/div/div/div/div/div[2]/input'
        )
        file_input_form.set_input_files(file_path)

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - waiting for the town picture to upload'
        )
        page.wait_for_timeout(15000)

        if not is_paid:
            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - choosing free town'
            )

            selector = page.locator(
                '//*[@id="container"]/div[1]/div/label[1]/div/div[1]/div'
            )
            selector.click(force=True, timeout=2000)
        else:
            logger.info(
                f"{self.account_name} | {self.email_item['email']} - choosing paid dynamic town"
            )

            selector = page.get_by_test_id("option-towntype-paid").locator("div").first
            selector.click(force=True, timeout=2000)
            dynamic_fee = page.get_by_test_id("option-fee-dynamic").locator("div").first
            dynamic_fee.click(force=True, timeout=2000)

        create_town_button = page.get_by_text("Create town").first
        create_town_button.click(force=True, timeout=10000)

        page.wait_for_timeout(10000)

        pay_eth_button = page.locator(
            '//*[@id="above-app-progress-root"]/div/div[2]/div/div[3]/button'
        )
        pay_eth_button.click(force=True, timeout=2000)

        page.wait_for_load_state()
        page.wait_for_timeout(5000)

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - waiting for the town creation to finalize'
        )
        page.wait_for_timeout(60000)

        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - created town {town_name}'
        )

        try:
            name = page.get_by_test_id("town-username-input")
            name.fill(username, force=True, timeout=2000)
            join_town = page.get_by_role("button").get_by_text("Join town").first
            join_town.click(force=True, timeout=2000)
        except Exception as e:
            logger.warning(f"didnt require nickname: {str(e)}")

        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - successfully joined town!'
        )
        self.save_town_data(
            town_name=town_name, town_link=page.url, created_by_user=True
        )

        return page, page.url

    def daily_task(self, page: Page):
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - resetting to the Explore page'
        )

        if (
            page.url == "https://app.towns.com/explore"
            or page.url == "app.towns.com/explore"
        ):
            logger.info(
                f'{self.account_name} | {self.email_item["email"]} - we are already on the Explore page'
            )
        else:
            page.goto("https://app.towns.com/explore")
            page.wait_for_load_state()
            page.wait_for_timeout(5000)

        page.reload()
        page.wait_for_load_state()
        page.wait_for_timeout(10000)

        logger.info(
            f"{self.account_name} | {self.email_item['email']} - opening daily task"
        )

        beaver_button = page.locator(
            '//*[@id="root"]/div[1]/div/div[1]/div/div[4]/div[1]'
        )
        beaver_button.click(force=True, timeout=2000)
        page.wait_for_load_state()
        page.wait_for_timeout(5000)
        beaver_hitbox = page.locator(
            '//*[@id="root"]/div[1]/div/div[2]/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[1]'
        )
        beaver_hitbox.click(force=True, timeout=15000, delay=1000)
        page.wait_for_timeout(10000)
        page.wait_for_load_state()
        pay_eth_button = page.get_by_text("Pay with ETH").first
        pay_eth_button.click(force=True, timeout=15000)
        page.wait_for_timeout(10000)

        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - daily task complete!'
        )

        return page

    def chat(self, page: Page, chat_link: str) -> bool:
        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - starting chat parsing process'
        )

        logger.info(
            f'{self.account_name} | {self.email_item["email"]} - heading to chat link'
        )
        page.goto(chat_link)
        page.wait_for_load_state()
        page.wait_for_timeout(30000)

        def random_tip(chat_page: Page, message_to_tip: Locator):
            import random

            logger.info(f"{self.account_name} - starting random tip process")
            chance = 20
            rand_num = random.randint(1, 100)

            try:
                if rand_num <= chance:
                    logger.info(
                        f'{self.account_name} | {self.email_item["email"]} - Chance for tip triggered!'
                    )
                    message_to_tip.click(force=True, delay=1000)
                    chat_page.keyboard.press("t", delay=1000)
                    chat_page.wait_for_timeout(1000)

                    input_tag = chat_page.get_by_placeholder("Amount", exact=True).first
                    input_tag.click(force=True, delay=1000)
                    input_tag.fill("0.1", force=True, timeout=2000)
                    chat_page.wait_for_timeout(1000)
                    tip_button = chat_page.get_by_text("Tip", exact=True)
                    tip_button.click(force=True, delay=1000)
                    chat_page.wait_for_timeout(2000)
                    send_tip_button = chat_page.get_by_role("button").get_by_text(
                        "Send", exact=True
                    )
                    send_tip_button.click(force=True, delay=2000)
                    chat_page.wait_for_timeout(20000)
                    logger.success(
                        f'{self.account_name} | {self.email_item["email"]} - tip success!'
                    )
                    return True
                else:
                    logger.info(
                        f'{self.account_name} | {self.email_item["email"]} - tip will not come through'
                    )
                    return True
            except Exception as e:
                logger.warning(f"Exception: {str(e)}")
                return False

        attempts = 0

        while True:
            message_tags = (
                page.get_by_test_id("vlist-main")
                .get_by_test_id("vlist-container")
                .get_by_test_id("vlist-content")
                .get_by_test_id("vlist-offset")
                .get_by_test_id("chat-message-container")
                .all()[::-1]
            )

            for tag in message_tags:
                message_tag = tag
                chat_text = message_tag.all_inner_texts()[0]

                if "Waiting for message to decrypt" in chat_text:
                    logger.info(
                        f'{self.account_name} | {self.email_item["email"]} - Messages have not loaded in properly yet, waiting for 10 seconds...'
                    )
                    page.wait_for_timeout(10000)
                    attempts += 1
                    message_tag = None
                    message_text = None
                    if attempts == 120:
                        try:
                            res = ask_chatgpt(
                                api_key=self.api_key,
                                message=None,
                                advanced_chat=False,
                            )
                            print(res)
                            input_field = page.locator(
                                '//*[@id="editor-container"]/div[2]/div[2]/div[1]/div[1]/div/div/p/span'
                            )
                            input_field.click(force=True, delay=1000)
                            input_field.fill(res, force=True, timeout=15000)
                            send_button = page.locator(
                                '//*[@id="editor-container"]/div[2]/div[2]/div[1]/div[2]/div/div/button'
                            )
                            send_button.click(force=True, timeout=10000)
                            page.wait_for_timeout(5000)
                            logger.success(
                                f'{self.account_name} | {self.email_item["email"]} - message sent successfully'
                            )
                            return True
                        except Exception as err:
                            logger.error(
                                f'{self.account_name} | {self.email_item["email"]} - error: {str(err)}'
                            )
                            raise Exception("Probably a bad viewport")
                    break

                if any(
                    [
                        item in chat_text
                        for item in [
                            "#general",
                            "Today",
                            "Yesterday",
                            "Mon",
                            "Tue",
                            "Wed",
                            "Thu",
                            "Fri",
                            "Sat",
                            "Sun",
                            "Dec",
                            "Jan",
                            "Mar",
                            "Apr",
                            "May",
                        ]
                    ]
                ):
                    message_tag = None
                    message_text = None
                    continue

                else:
                    message_text = chat_text.split("\n")[3]
                    try:
                        random_tip(chat_page=page, message_to_tip=tag)

                        res = ask_chatgpt(
                            api_key=self.api_key,
                            message=message_text,
                            advanced_chat=True,
                        )
                        print(res)
                        input_field = page.locator(
                            '//*[@id="editor-container"]/div[2]/div[2]/div[1]/div[1]/div/div/p/span'
                        )
                        input_field.click(force=True, delay=1000)
                        input_field.fill(res, force=True, timeout=15000)
                        send_button = page.locator(
                            '//*[@id="editor-container"]/div[2]/div[2]/div[1]/div[2]/div/div/button'
                        )
                        send_button.click(force=True, timeout=10000)
                        page.wait_for_timeout(5000)
                        logger.success(
                            f'{self.account_name} | {self.email_item["email"]} - message sent successfully'
                        )
                        return True
                    except Exception as err:
                        logger.error(
                            f'{self.account_name} | {self.email_item["email"]} - error: {str(err)}'
                        )
                        raise Exception("Probably a bad viewport")
            else:
                try:
                    res = ask_chatgpt(
                        api_key=self.api_key, message=None, advanced_chat=False
                    )
                    print(res)
                    input_field = page.locator(
                        '//*[@id="editor-container"]/div[2]/div[2]/div[1]/div[1]/div/div/p/span'
                    )
                    input_field.click(force=True, delay=1000)
                    input_field.fill(res, force=True, timeout=15000)
                    send_button = page.locator(
                        '//*[@id="editor-container"]/div[2]/div[2]/div[1]/div[2]/div/div/button'
                    )
                    send_button.click(force=True, timeout=10000)
                    page.wait_for_timeout(5000)
                    logger.success(
                        f'{self.account_name} | {self.email_item["email"]} - message sent successfully'
                    )
                    return True
                except Exception as err:
                    logger.error(
                        f'{self.account_name} | {self.email_item["email"]} - error: {str(err)}'
                    )
                    raise Exception("Probably a bad viewport")

    def save_cookies(self) -> bool:
        from data.config import WORKING_DIR

        cookies = self.context.cookies()
        file_to_write = os.path.join(
            WORKING_DIR,
            Path(f'data/saved_cookies/{self.email_item["email"].split("@")[0]}.json'),
        )
        with open(file_to_write, "w") as f:
            json.dump(cookies, f)

        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - cookies dumped to {file_to_write}'
        )
        return True

    def load_cookies(self):
        from data.config import WORKING_DIR

        file_to_search = os.path.join(
            WORKING_DIR,
            Path(f'data/saved_cookies/{self.email_item["email"].split("@")[0]}.json'),
        )

        try:
            with open(file_to_search, "r") as f:
                cookies = json.load(f)
            self.context.add_cookies(cookies)
            return True
        except Exception:
            logger.warning(
                f'{self.account_name} | {self.email_item["email"]} - cookies not found'
            )
            return False

    def save_storage(self) -> bool:
        from data.config import WORKING_DIR

        file_path = os.path.join(
            WORKING_DIR,
            Path(f'data/storage_states/{self.email_item["email"].split("@")[0]}.json'),
        )
        self.context.storage_state(path=file_path)
        logger.success(
            f'{self.account_name} | {self.email_item["email"]} - dumped storage state to {file_path}'
        )
        return True

    def save_town_data(self, town_name: str, town_link: str, created_by_user: bool):
        from data.config import WORKING_DIR

        filename = os.path.join(
            WORKING_DIR,
            Path(
                f'data/registered_towns/{self.email_item["email"].split("@")[0]}.json'
            ),
        )

        town_entry = {
            "name": town_name,
            "url": town_link,
            "created_by_user": created_by_user,
        }

        # Check if the file exists
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    data = json.load(file)
                    if not isinstance(data, list):
                        data = []
                except json.JSONDecodeError:
                    data = []

            # Append new entry
            data.append(town_entry)
        else:
            # Create a new file with the first entry
            data = [town_entry]

        # Write back to the file
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

    def cleanup(self):
        try:
            # General context cleanup
            if hasattr(self, "context") and self.context:
                self.context.clear_cookies()
                self.context.clear_permissions()
                self.context.close()
                self.context = None
            # In cases with no persistent context
            if hasattr(self, "browser") and self.browser:
                self.browser.close()
                self.browser = None
        except Exception as e:
            logger.warning(f"Cleanup error for account {self.account_name}: {e}")
        # Removes user data folder for a specific account with account name id
        remove_user_data(account_id=self.account_name)
