import subprocess
import json
from playwright.sync_api import sync_playwright

class RealFilingBot:
    def __init__(self, tor_proxy="socks5://127.0.0.1:9050"):
        self.tor_proxy = tor_proxy

    def verify_tor(self):
        try:
            result = subprocess.run(
                ["curl", "--socks5-hostname", "127.0.0.1:9050", "-s", "--max-time", "15",
                 "https://check.torproject.org"],
                capture_output=True, text=True, timeout=20
            )
            return "Congratulations" in result.stdout
        except Exception:
            return False

    def dry_run_sec_tcr(self):
        if not self.verify_tor():
            return {"status": "TOR_FAILED", "error": "Tor not routing"}
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    proxy={"server": self.tor_proxy}
                )
                context = browser.new_context()
                page = context.new_page()
                page.goto("https://www.sec.gov/whistleblower",
                         wait_until="domcontentloaded", timeout=30000)
                html = page.content()
                selectors = {
                    "tip_text": "tip_text" in html,
                    "entity_name": "entity_name" in html,
                    "submit_button": "submit" in html.lower(),
                    "form_present": "<form" in html.lower(),
                    "title_contains_whistleblower": "whistleblower" in page.title().lower()
                }
                url = page.url
                title = page.title()
                browser.close()
                return {
                    "status": "DOM_CAPTURED",
                    "selectors": selectors,
                    "tor": True,
                    "url": url,
                    "title": title
                }
        except Exception as e:
            return {"status": "FAILED", "error": str(e), "tor": True}

if __name__ == "__main__":
    bot = RealFilingBot()
    result = bot.dry_run_sec_tcr()
    print(json.dumps(result, indent=2))
