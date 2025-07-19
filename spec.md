
# 🛠 Product Availability Checker (Rust + Docker)

A lightweight tool to monitor product availability via website scraping with JavaScript support. Sends Telegram notifications when monitored products change availability.

---

## 📋 Features

* Monitor multiple products (up to \~10) via a JSON config.
* Scrapes JavaScript-rendered web pages using headless Chrome.
* Exact string match to detect product unavailability.
* Sends Telegram messages on:

  * Product becoming available
  * Product page error (e.g., timeout, HTTP error)
* Runs in Docker as a lightweight, continuously running tool.
* Checks products in parallel, at fixed intervals.
* Logs errors to both `stdout` and `error.log`.

---

## 📁 JSON Config Format

Path: `/app/config.json` (mounted into the container)

```json
{
  "telegram": "<TELEGRAM_BOT_TOKEN>:<CHAT_ID>",
  "interval": 60,
  "timeout": 5,
  "product": [
    {
      "name": "Product 1",
      "url": "https://example.com/item1",
      "value": "Out of stock"
    },
    {
      "name": "Product 2",
      "url": "https://example.com/item2",
      "value": "Currently unavailable"
    }
  ]
}
```

* `telegram`: String containing both the Telegram bot token and hardcoded chat ID.
* `interval`: Number of seconds between each availability check (global).
* `timeout`: (Optional) Request timeout in seconds. Defaults to `5` if not set.
* `product`: List of products with:

  * `name`: Display name of the product.
  * `url`: Full URL to the product page.
  * `value`: Exact string that indicates the product is *unavailable*.

---

## 📤 Telegram Messaging

* **One-way only**: The bot only sends messages; it does not handle commands.
* Sends message **once** when availability changes:

  * Available → Notification sent
  * Becomes unavailable → Reset internal state (no notification)
* On request error (e.g., timeout, 404):

  ```
  ❌ Error checking "Product 1":
  https://example.com/item1
  Error: timed out
  ```
* On availability:

  ```
  ✅ "Product 1" is now available!
  https://example.com/item1
  ```

---

## ⚙️ Behavior

* All product checks are run **in parallel** every `interval` seconds.
* Pages are rendered using **headless Chrome** to support JavaScript.
* SSL certificates are verified.
* Follows no redirects (301/302 → error).
* Chrome is restarted if it crashes.
* Uses Firefox user-agent.
* Error logs go to both `stdout` and `./error.log`.
* Shows a short startup message (e.g., "Monitoring 2 products...").
* Terminates immediately on shutdown (no graceful handling).

---

## 🐳 Docker Setup

### Dockerfile

* Multi-stage build:

  * Compiles Rust binary in a build stage.
  * Copies binary into a minimal runtime image.
  * Installs headless Chrome in the runtime stage.
* Uses **non-root** user.
* No health checks.
* Config is mounted at runtime (not baked in).

### Example Docker Run

```bash
docker build -t product-checker .
docker run -v "$(pwd)/config.json:/app/config.json" product-checker
```

---

## 🔒 Assumptions & Notes

* No proxy support.
* No rate limiting.
* No live reload of config (restart required).
* No limit on HTML size.
* No graceful shutdown.
* Chrome must be bundled and launched inside the container.

