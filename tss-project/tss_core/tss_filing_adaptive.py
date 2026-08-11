import subprocess
import json
import socket
import binascii
import time
from playwright.sync_api import sync_playwright

CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 9051
COOKIE_PATH = "/home/idor/.local/share/tor/control_auth_cookie"
TARGET_URL = "https://www.sec.gov/whistleblower"
WAF_MARKERS = ["request rate threshold exceeded", "access denied", "rate limit"]


class AdaptiveFilingBot:
    """v12 M1: RealFilingBot + circuit rotation (NEWNYM) + honest WAF classification."""

    def __init__(self, tor_proxy="socks5://127.0.0.1:9050", max_circuits=3):
        self.tor_proxy = tor_proxy
        self.max_circuits = max_circuits
        self.circuits_rotated = 0

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

    def rotate_circuit(self):
        """Signal NEWNYM over the Tor control port using cookie auth."""
        try:
            cookie = open(COOKIE_PATH, "rb").read()
            s = socket.create_connection((CONTROL_HOST, CONTROL_PORT), timeout=10)
            s.sendall(b"AUTHENTICATE " + binascii.hexlify(cookie) + b"\r\n")
            resp = s.recv(1024)
            if b"250" not in resp:
                s.close()
                return False
            s.sendall(b"SIGNAL NEWNYM\r\n")
            resp = s.recv(1024)
            s.sendall(b"QUIT\r\n")
            s.close()
            ok = b"250" in resp
            if ok:
                self.circuits_rotated += 1
            return ok
        except Exception:
            return False

    @staticmethod
    def _is_waf_blocked(title, html):
        joined = (title or "") + " " + html[:4000].lower()
        return any(m in joined for m in WAF_MARKERS)

    def dry_run_sec_tcr(self):
        if not self.verify_tor():
            return {"status": "TOR_FAILED", "error": "Tor not routing"}
        last = None
        for attempt in range(1, self.max_circuits + 1):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, proxy={"server": self.tor_proxy})
                    page = browser.new_page()
                    page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
                    html = page.content()
                    title = page.title()
                    url = page.url
                    browser.close()
                waf = self._is_waf_blocked(title, html)
                result = {
                    "status": "DOM_CAPTURED",
                    "tor": True,
                    "url": url,
                    "title": title,
                    "attempt": attempt,
                    "circuits_rotated": self.circuits_rotated,
                    "waf_blocked": waf,
                }
                if waf:
                    result["status"] = "WAF_BLOCKED"
                    result["selectors"] = {}
                    last = result
                    if attempt < self.max_circuits:
                        rotated = self.rotate_circuit()
                        time.sleep(10)
                        if not rotated:
                            break
                        continue
                    return result
                selectors = {
                    "tip_text": "tip_text" in html,
                    "entity_name": "entity_name" in html,
                    "submit_button": "submit" in html.lower(),
                    "form_present": "<form" in html.lower(),
                    "title_contains_whistleblower": "whistleblower" in title.lower(),
                }
                result["selectors"] = selectors
                result["selectors_ok"] = sum(selectors.values()) >= 3
                return result
            except Exception as e:
                return {"status": "FAILED", "error": str(e), "tor": True, "attempt": attempt}
        return last


if __name__ == "__main__":
    bot = AdaptiveFilingBot()
    result = bot.dry_run_sec_tcr()
    print(json.dumps(result, indent=2))
