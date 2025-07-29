#!/usr/bin/env python3
import logging
import time

import requests
from playwright.sync_api import sync_playwright

from config import get_chat_id, get_telegram_token, load_config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductChecker:
    def __init__(self, config):
        self.config = config
        self.token = get_telegram_token(config)
        self.chat_id = get_chat_id(config)
        self.product_states = {}
        self.playwright = None
        self.browser = None

        for product in config["product"]:
            self.product_states[product["name"]] = (
                True  # Assume value is present initially
            )

    def check_product(self, product):
        name = product["name"]
        url = product["url"]
        expected_value = product["value"]
        timeout = self.config.get("timeout", 5) * 1000  # Playwright uses milliseconds

        logger.info(f"Checking product: {name}")

        try:
            # Initialize browser if needed
            if not self.browser:
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.firefox.launch(headless=True)

            # Create new page for this request
            page = self.browser.new_page()

            # Set cache-busting and realistic behavior
            page.set_extra_http_headers(
                {"Cache-Control": "no-cache", "Pragma": "no-cache"}
            )

            # Navigate to the page with timeout
            page.goto(url, timeout=timeout)

            # Wait a moment for dynamic content to load
            page.wait_for_timeout(1000)  # 1 second

            # Get page content
            content = page.content()
            value_present = expected_value in content

            logger.info(
                f"Product '{name}': checking for '{expected_value}' in content, value present: {value_present}"
            )

            was_value_present = self.product_states[name]

            if not value_present and was_value_present:
                logger.info(
                    f"Product '{name}': value '{expected_value}' is no longer present!"
                )
                self.send_value_changed_message(name, url, expected_value)
                self.product_states[name] = False
            elif value_present and not was_value_present:
                logger.info(
                    f"Product '{name}': value '{expected_value}' is present again!"
                )
                self.send_value_restored_message(name, url, expected_value)
                self.product_states[name] = True

            # Close the page
            page.close()

        except Exception as e:
            error_msg = f"Error checking product '{name}': {e}"
            logger.error(error_msg)
            self.send_error_message(name, url, str(e))

    def send_value_changed_message(self, product_name, product_url, expected_value):
        message = f'🔄 "{product_name}" - Site has changed!\nValue "{expected_value}" is not present anymore.\n{product_url}'
        self.send_telegram_message(message)

    def send_value_restored_message(self, product_name, product_url, expected_value):
        message = f'✅ "{product_name}" - Value restored!\nValue "{expected_value}" is present again.\n{product_url}'
        self.send_telegram_message(message)

    def send_error_message(self, product_name, product_url, error):
        message = f'❌ Error checking "{product_name}":\n{product_url}\nError: {error}'
        self.send_telegram_message(message)

    def send_telegram_message(self, message):
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}

            response = requests.post(url, json=data)
            response.raise_for_status()

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    def cleanup(self):
        """Clean up Playwright resources"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def run(self):
        logger.info(f"Monitoring {len(self.config['product'])} products...")

        while True:
            for product in self.config["product"]:
                self.check_product(product)

            time.sleep(self.config["interval"])


def main():
    checker = None
    try:
        config = load_config()
        checker = ProductChecker(config)
        checker.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Failed to start: {e}")
    finally:
        if checker:
            checker.cleanup()


if __name__ == "__main__":
    main()
