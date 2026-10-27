#!/usr/bin/env python3
"""
crawl.py - ONE script: crawl a site, click every button, screenshot everything,
and write a single screenshots.md (GitHub-friendly <img> tags).

Examples:
  python crawl.py http://127.0.0.1:8000
  python crawl.py http://127.0.0.1:8000 --username anjali.gupta --password 'Employee@123'
  python crawl.py http://127.0.0.1:8000 --username hr_admin --password 'HR@company123' --out hr_shots
  python crawl.py --md-only --out screenshots        # just rebuild the .md

Login: with --username/--password (or env CRAWL_USERNAME / CRAWL_PASSWORD) the
script finds the login form itself, signs in, and signs in again whenever the
session is lost. Logout links/buttons are never visited or clicked.

Only run this against sites you own or have permission to test.
"""
import argparse
import hashlib
import html
import json
import os
import re
import struct
import time
from collections import deque
from pathlib import Path
from urllib.parse import quote, urldefrag, urlparse

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

CLICKABLE = (
    'button, [role="button"], input[type="button"], input[type="submit"], '
    'summary, a[href^="#"], [onclick]'
)

# Button labels that look like they change data / end the session -> skipped.
DANGEROUS = re.compile(
    r"delete|remove|log\s?out|sign\s?out|unsubscribe|pay\b|purchase|buy now|"
    r"place order|deactivate|cancel (subscription|account)|reset|destroy|erase",
    re.I,
)
# URLs / form actions that end the session -> never visited or submitted.
LOGOUT_URL = re.compile(r"log[-_]?out|sign[-_]?out|log[-_]?off", re.I)

SKIP_EXT = (
    ".pdf", ".zip", ".rar", ".gz", ".tar", ".png", ".jpg", ".jpeg", ".gif",
    ".svg", ".webp", ".ico", ".mp4", ".mp3", ".avi", ".mov", ".doc", ".docx",
    ".xls", ".xlsx", ".ppt", ".pptx", ".exe", ".dmg", ".css", ".js", ".json", ".xml",
)


def slugify(text, maxlen=40):
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:maxlen] or "item"


def normalize(url):
    url, _ = urldefrag(url)
    return url.rstrip("/") if urlparse(url).path not in ("", "/") else url.rstrip("/") + "/"


def page_slug(url):
    p = urlparse(url)
    base = slugify(p.path + ("-" + p.query if p.query else ""), 50) if p.path.strip("/") else "home"
    return f"{base}-{hashlib.md5(url.encode()).hexdigest()[:6]}"


# ----------------------------------------------------------------------------
# Markdown
# ----------------------------------------------------------------------------
def png_size(path):
    try:
        with open(path, "rb") as f:
            d = f.read(24)
        if d[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", d[16:24])
    except OSError:
        pass
    return None


def md_escape(text):
    text = html.escape(text, quote=False)
    return re.sub(r"([\\`*_\[\]])", r"\\\1", text)


def img_tag(path, alt, md_dir, base_url=None, max_width=0):
    rel = quote(os.path.relpath(path, md_dir).replace(os.sep, "/"))
    src = f"{base_url.rstrip('/')}/{rel}" if base_url else rel
    attrs = ""
    size = png_size(path)
    if size:
        w, h = size
        if max_width and w > max_width:
            h, w = round(h * max_width / w), max_width
        attrs = f'width="{w}" height="{h}" '
    return f'<img {attrs}alt="{html.escape(alt, quote=True)}" src="{src}" />'


def build_markdown(root, base_url=None, max_width=0):
    """Write <root>/screenshots.md from every report.json under root."""
    root = Path(root).resolve()
    out = root / "screenshots.md"
    lines = []
    for rp in sorted(root.rglob("report.json")):
        base = rp.parent
        for e in json.loads(rp.read_text()):
            if e.get("login_page"):
                continue
            shots = []
            for c in e.get("clicks", []):
                if c.get("screenshot"):
                    shots.append((c["label"], c["screenshot"]))
                for k, s in enumerate(c.get("popup_screenshots", []), 1):
                    shots.append((f"{c['label']} (popup {k})", s))
            if not e.get("screenshot") and not shots:
                continue
            lines += [f"## {e['url']}", ""]
            if e.get("screenshot"):
                tag = img_tag(base / e["screenshot"], e.get("title") or e["url"], root, base_url, max_width)
                lines += [f"### Page loaded {tag}", ""]
            for label, shot in shots:
                lines += [f"### {md_escape(label)}", img_tag(base / shot, label, root, base_url, max_width), ""]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


# ----------------------------------------------------------------------------
# Crawler
# ----------------------------------------------------------------------------
class Crawler:
    def __init__(self, args):
        self.args = args
        self.start = normalize(args.url)
        self.host = urlparse(self.start).netloc
        self.out = Path(args.out) / slugify(self.host, 60)
        self.out.mkdir(parents=True, exist_ok=True)
        self.exclude = re.compile(args.exclude) if args.exclude else None
        self.username = args.username or os.environ.get("CRAWL_USERNAME")
        self.password = args.password or os.environ.get("CRAWL_PASSWORD")
        self.creds = bool(self.username and self.password)
        self.login_url = normalize(args.login_url) if args.login_url else None
        self.seen = set()
        self.queue = deque()
        self.report = []

    # ---------- scope ----------
    def in_scope(self, url):
        p = urlparse(url)
        if p.scheme not in ("http", "https") or p.netloc != self.host:
            return False
        if p.path.lower().endswith(SKIP_EXT):
            return False
        if LOGOUT_URL.search(url) and not self.args.allow_dangerous:
            return False
        if self.exclude and self.exclude.search(url):
            return False
        return True

    def enqueue(self, url, depth):
        url = normalize(url)
        if url in self.seen or not self.in_scope(url) or depth > self.args.max_depth:
            return
        if len(self.seen) + len(self.queue) >= self.args.max_pages:
            return
        self.queue.append((url, depth))
        self.seen.add(url)

    # ---------- login ----------
    @staticmethod
    def looks_like_login(page):
        try:
            return page.locator('input[type="password"]:visible').count() > 0
        except Exception:
            return False

    def do_login(self, page):
        """Fill and submit the login form on the current page. True if it worked."""
        try:
            pw = page.locator('input[type="password"]:visible').first
            form = pw.locator("xpath=ancestor::form[1]")
            scope = form if form.count() else page
            user = scope.locator(
                'input[type="text"]:visible, input[type="email"]:visible, input:not([type]):visible'
            ).first
            user.fill(self.username)
            pw.fill(self.password)
            submit = scope.locator('button[type="submit"]:visible, input[type="submit"]:visible').first
            if not submit.count():
                submit = scope.get_by_role(
                    "button", name=re.compile(r"sign\s?in|log\s?in|login|submit|continue", re.I)
                ).first
            if submit.count():
                submit.click(timeout=4000)
            else:
                pw.press("Enter")
            self.settle(page)
            return not self.looks_like_login(page)
        except Exception as e:
            print(f"   ! login attempt error: {str(e).splitlines()[0][:120]}")
            return False

    def initial_login(self, ctx):
        if not self.creds:
            return
        page = ctx.new_page()
        target = self.args.login_url or self.start
        try:
            page.goto(target, wait_until="domcontentloaded", timeout=self.args.timeout * 3)
            self.settle(page)
            if self.looks_like_login(page):
                login_page_url = normalize(page.url)
                ok = self.do_login(page)
                print("Logged in." if ok else "!! Login FAILED - check --username/--password")
                self.login_url = self.login_url or login_page_url
                self.seen.add(login_page_url)
                if ok and login_page_url == self.start:
                    self.start = normalize(page.url)  # start page was the login page
            else:
                print("No login form at start page (already signed in or public site).")
        except Exception as e:
            print(f"!! initial login error: {e}")
        page.close()

    def is_login_url(self, url):
        return bool(self.login_url) and normalize(url) == self.login_url

    # ---------- page helpers ----------
    def settle(self, page):
        try:
            page.wait_for_load_state("networkidle", timeout=self.args.timeout)
        except PWTimeout:
            pass
        time.sleep(self.args.delay)

    def load(self, page, url):
        """Open url; if the session was lost, log in again and reopen it."""
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=self.args.timeout * 3)
        except Exception as e:
            print(f"   ! failed to load {url}: {str(e).splitlines()[0][:120]}")
            return False
        self.settle(page)
        if self.creds and not self.is_login_url(url) and self.looks_like_login(page):
            print("   (session lost -> signing in again)")
            if self.do_login(page):
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=self.args.timeout * 3)
                    self.settle(page)
                except Exception:
                    return False
            else:
                print("   ! re-login failed")
        return True

    def snap(self, page, path, skip_digest=None):
        """Screenshot -> (relative path or None, digest). Skips if identical to skip_digest."""
        try:
            data = page.screenshot(full_page=self.args.full_page)
        except Exception as e:
            print(f"   ! screenshot failed: {str(e).splitlines()[0][:100]}")
            return None, None
        digest = hashlib.md5(data).hexdigest()
        if skip_digest and digest == skip_digest and not self.args.keep_unchanged:
            return None, digest
        path.write_bytes(data)
        return str(path.relative_to(self.out)), digest

    def collect_links(self, page, depth):
        try:
            hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
        except Exception:
            return
        for h in hrefs:
            self.enqueue(h, depth + 1)

    @staticmethod
    def describe(el):
        for getter in (
            lambda: el.inner_text(timeout=500).strip(),
            lambda: el.get_attribute("aria-label"),
            lambda: el.get_attribute("value"),
            lambda: el.get_attribute("title"),
            lambda: el.get_attribute("id"),
        ):
            try:
                v = getter()
                if v:
                    return " ".join(v.split())[:60]
            except Exception:
                continue
        return ""

    # ---------- per page ----------
    def process_page(self, ctx, url, depth):
        page = ctx.new_page()
        page.on("dialog", lambda d: d.dismiss())
        popups = []
        page.on("popup", lambda p: popups.append(p))

        entry = {"url": url, "depth": depth, "screenshot": None, "clicks": []}
        self.report.append(entry)

        if not self.load(page, url):
            entry["error"] = "load failed"
            page.close()
            return

        pdir = self.out / page_slug(url)
        pdir.mkdir(parents=True, exist_ok=True)
        entry["title"] = page.title()
        entry["screenshot"], base_digest = self.snap(page, pdir / "00_page.png")

        if self.looks_like_login(page):
            entry["login_page"] = True
            hint = "login failed?" if self.creds else "pass --username/--password"
            print(f"   login page - not clicking, left out of the .md ({hint})")
            page.close()
            return

        self.collect_links(page, depth)

        if not self.args.no_click:
            count = min(page.locator(CLICKABLE).count(), self.args.max_buttons)
            entry["clickable"] = count
            print(f"   {count} clickable element(s)")
            for i in range(count):
                self.click_one(page, url, depth, pdir, i, popups, entry, base_digest)

        page.close()

    def click_one(self, page, url, depth, pdir, i, popups, entry, base_digest):
        if i > 0 and not self.load(page, url):  # fresh page for every click
            return
        el = page.locator(CLICKABLE).nth(i)
        try:
            if not el.is_visible(timeout=500):
                return
        except Exception:
            return

        label = self.describe(el) or f"Button {i + 1}"
        rec = {"index": i, "label": label}
        entry["clicks"].append(rec)

        try:
            target = el.evaluate(
                "e => (e.form && e.form.action) || e.getAttribute('formaction') || e.getAttribute('href') || ''"
            )
        except Exception:
            target = ""
        if not self.args.allow_dangerous and (DANGEROUS.search(label) or LOGOUT_URL.search(target or "")):
            rec["skipped"] = "looks destructive / logout"
            print(f"   - skip [{label}]")
            return

        popups.clear()
        try:
            el.scroll_into_view_if_needed(timeout=2000)
            el.click(timeout=3000)
        except Exception as e:
            rec["error"] = str(e).splitlines()[0][:150]
            print(f"   ! click failed [{label}]")
            return

        self.settle(page)

        moved = normalize(page.url) != url
        if moved and self.looks_like_login(page):
            rec["logged_out"] = True  # this click ended the session; next load signs in again
            print(f"   ! [{label}] logged us out - not saved")
            return

        name = f"btn_{i:02d}_{slugify(label)}"
        rec["screenshot"], _ = self.snap(page, pdir / f"{name}.png", skip_digest=base_digest)
        if rec["screenshot"]:
            print(f"   + clicked [{label}]")
        else:
            rec["unchanged"] = True
            print(f"   = clicked [{label}] (page looks unchanged, not saved)")

        if moved:
            rec["navigated_to"] = page.url
            self.enqueue(page.url, depth + 1)
        else:
            self.collect_links(page, depth)  # menus/modals may reveal links

        for n, pop in enumerate(list(popups)):
            try:
                pop.wait_for_load_state("domcontentloaded", timeout=5000)
                shot, _ = self.snap(pop, pdir / f"{name}_popup{n}.png")
                if shot:
                    rec.setdefault("popup_screenshots", []).append(shot)
                self.enqueue(pop.url, depth + 1)
                pop.close()
            except Exception:
                pass

    # ---------- run ----------
    def run(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=not self.args.headed)
            ctx = browser.new_context(
                viewport={"width": self.args.width, "height": self.args.height},
                storage_state=self.args.storage_state,
            )
            self.initial_login(ctx)
            self.enqueue(self.start, 0)
            n = 0
            while self.queue:
                url, depth = self.queue.popleft()
                n += 1
                print(f"[{n}] (depth {depth}) {url}")
                try:
                    self.process_page(ctx, url, depth)
                except Exception as e:
                    print(f"   ! error on page: {e}")
                self.write_report()
            browser.close()
        md = Path(self.args.out).resolve() / "screenshots.md"
        print(f"\nDone. {len(self.report)} page(s). Markdown: {md}")
        if not any(not e.get("login_page") for e in self.report):
            print("Only login pages were reached - run again with --username and --password.")

    def write_report(self):
        (self.out / "report.json").write_text(json.dumps(self.report, indent=2))
        try:  # combined .md rebuilt after every page
            build_markdown(self.args.out, self.args.base_url, self.args.max_width)
        except Exception as e:
            print(f"   ! markdown build failed: {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?", help="start URL (not needed with --md-only)")
    ap.add_argument("--out", default="screenshots", help="output folder (default: screenshots)")
    ap.add_argument("--username", help="login username (or env CRAWL_USERNAME)")
    ap.add_argument("--password", help="login password (or env CRAWL_PASSWORD)")
    ap.add_argument("--login-url", help="login page URL if it is not the start page / auto-redirect")
    ap.add_argument("--storage-state", help="optional Playwright auth file to start from")
    ap.add_argument("--max-pages", type=int, default=30)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-buttons", type=int, default=25, help="max clicks per page")
    ap.add_argument("--no-click", action="store_true", help="only screenshot pages, don't click")
    ap.add_argument("--allow-dangerous", action="store_true", help="also click/visit delete, logout, pay-like things")
    ap.add_argument("--keep-unchanged", action="store_true", help="save click screenshots even if the page didn't change")
    ap.add_argument("--exclude", help="regex of URLs to skip, e.g. '/admin|/export'")
    ap.add_argument("--full-page", action="store_true", help="full-height screenshots")
    ap.add_argument("--headed", action="store_true", help="show the browser")
    ap.add_argument("--width", type=int, default=1366)
    ap.add_argument("--height", type=int, default=800)
    ap.add_argument("--timeout", type=int, default=8000, help="ms to wait for network idle")
    ap.add_argument("--delay", type=float, default=0.5, help="extra seconds to wait after load/click")
    ap.add_argument("--base-url", help="absolute image URLs in the .md, e.g. https://raw.githubusercontent.com/USER/REPO/main/screenshots")
    ap.add_argument("--max-width", type=int, default=0, help="scale <img> sizes in the .md down to this width")
    ap.add_argument("--md-only", action="store_true", help="don't crawl, just rebuild screenshots.md from --out")
    args = ap.parse_args()

    if args.md_only:
        print(f"Wrote {build_markdown(args.out, args.base_url, args.max_width)}")
        return
    if not args.url:
        ap.error("url is required (or use --md-only)")
    Crawler(args).run()


if __name__ == "__main__":
    main()
