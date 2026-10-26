#!/usr/bin/env python3
"""
Open a real browser so you can log in manually, then save the session
to a file that crawl.py can reuse via --storage-state.

Usage:
    python save_login.py https://app.example.com/login auth.json
"""
import sys

from playwright.sync_api import sync_playwright

if len(sys.argv) != 3:
    sys.exit("usage: python save_login.py <login-url> <output.json>")

url, out = sys.argv[1], sys.argv[2]

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(url)
    input("Log in in the browser window, then press ENTER here to save the session... ")
    ctx.storage_state(path=out)
    browser.close()

print(f"Saved session to {out}")
