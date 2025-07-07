from loguru import logger
from eth_account import Account
from playwright.sync_api import Page, expect, BrowserContext


class MetamaskConnector:
    def __init__(
        self,
        account_name: str | int,
        private_key: str,
        page: Page,
        context: BrowserContext,
    ):
        self.page = page
        self.context = context
        self.account_name = account_name
        self.private_key = private_key
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address

    def setup_extension(self):
        logger.info(f"{self.account_name} | {self.address} - loading extension")

        self.page.wait_for_load_state()
        self.page.wait_for_timeout(3500)

        logger.success(f"{self.account_name} | {self.address} - extension loaded")

        pages = self.context.pages

        for item in pages:
            if item.url.startswith(
                "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/"
            ):
                self.page = item
                break

        logger.info(f"{self.account_name} | {self.address} - pasting data")

        checkbox = self.page.locator('//*[@id="onboarding__terms-checkbox"]')
        checkbox.click(force=True, timeout=1500)

        logger.success("Checkbox - Success")

        active_create_wallet_button = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/ul/li[2]/button'
        )
        active_create_wallet_button.click(force=True, timeout=1500)

        logger.success("New wallet - Success")

        self.page.wait_for_load_state()
        reject_button = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/button[1]'
        )
        reject_button.click(force=True)

        logger.success("Reject diagnostic tracking - Success")

        self.page.wait_for_load_state()
        input_field = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/div[1]/label/input'
        )
        confirm_password_field = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/div[2]/label/input'
        )
        password = "dsadsadsa"

        for field in [input_field, confirm_password_field]:
            field.fill(password, force=True, timeout=2000)

        logger.success("Password pasting - Success")

        self.page.wait_for_timeout(1500)

        checkmark = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/div[3]/label/span[1]/input'
        )
        checkmark.click(force=True, timeout=1000)

        self.page.wait_for_timeout(1500)

        logger.success("Terms and conditions - Success")

        create_wallet_button = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/button'
        )
        create_wallet_button.click(force=True, timeout=2000)

        logger.success("Create wallet - Success")

        self.page.wait_for_load_state()
        remind_later_button = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/button[1]'
        )
        remind_later_button.click(force=True, timeout=1500)

        self.page.wait_for_timeout(2000)
        skip_checkmark = self.page.locator(
            '//*[@id="popover-content"]/div/div/section/div[1]/div/div/label/input'
        )
        skip_checkmark.click(force=True, timeout=1500)
        self.page.wait_for_timeout(3000)

        skip_button = self.page.locator(
            '//*[@id="popover-content"]/div/div/section/div[2]/div/button[2]'
        )
        skip_button.click(force=True, timeout=1500)

        logger.success("Refuse and skip saving - Success")

        self.page.wait_for_load_state()
        self.page.wait_for_timeout(5000)
        done_button = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[3]/button'
        )
        done_button.click(force=True, timeout=2000)
        self.page.wait_for_load_state()
        pin_button = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/button'
        )
        expect(pin_button).to_be_visible(timeout=10000)
        pin_button.click(force=True, timeout=3000)
        self.page.wait_for_load_state()
        last_done_button = self.page.locator(
            '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/button'
        )
        expect(last_done_button).to_be_visible(timeout=10000)
        last_done_button.click(force=True, timeout=3000)
        self.page.wait_for_load_state(timeout=30000)

        logger.success("Initial setup finished")
        logger.info(f"{self.account_name} | {self.address} - importing wallet")

        self.page.reload()
        self.page.wait_for_load_state()

        for _ in range(2):
            empty_field = self.page.locator(
                '//*[@id="app-content"]/div/div[3]/div/div/div/div[1]/div/div[1]'
            ).first
            empty_field.click(force=True, timeout=2000)

        try:
            old_version_noti = self.page.locator(
                '//*[@id="app-content"]/div/div[3]/div/div/div[2]/div[1]/div[2]/button'
            )
            old_version_noti.click(force=True, timeout=2000, delay=2000)
        except Exception:
            logger.info("No deprecation warning found")

        logger.success("Remove leftover notifications - Success")

        wallets_menu = self.page.get_by_text("Account 1").first
        wallets_menu.click(force=True, timeout=2000)

        add_wallet_button = self.page.get_by_test_id(
            "multichain-account-menu-popover-action-button"
        )
        add_wallet_button.click(force=True, timeout=2000)

        self.page.wait_for_load_state()
        self.page.wait_for_timeout(15000)

        import_account_button = self.page.locator(
            "//html/body/div[3]/div[3]/div/section/div/div[2]/button"
        )
        expect(import_account_button).to_be_visible(timeout=20000)
        import_account_button.click(force=True, timeout=2000)

        self.page.wait_for_load_state()
        pkey_input_field = self.page.locator('//*[@id="private-key-box"]')
        expect(pkey_input_field).to_be_visible(timeout=10000)
        pkey_input_field.fill(self.private_key, force=True, timeout=2000)

        self.page.wait_for_timeout(1500)
        import_wallet_button = self.page.get_by_test_id("import-account-confirm-button")
        import_wallet_button.click(force=True, timeout=2000)

        logger.success(f"{self.account_name} | Wallet {self.address} imported!")

        return self.page
