#!/usr/bin/env python3
import logging
import time

import requests

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
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
            }
        )

        for product in config["product"]:
            self.product_states[product["name"]] = (
                True  # Assume value is present initially
            )

    def check_product(self, product):
        name = product["name"]
        url = product["url"]
        expected_value = product["value"]
        timeout = self.config.get("timeout", 5)

        logger.info(f"Checking product: {name}")

        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            content = response.text
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

    def run(self):
        logger.info(f"Monitoring {len(self.config['product'])} products...")

        while True:
            for product in self.config["product"]:
                self.check_product(product)

            time.sleep(self.config["interval"])


def main():
    try:
        config = load_config()
        checker = ProductChecker(config)
        checker.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Failed to start: {e}")


if __name__ == "__main__":
    main()
