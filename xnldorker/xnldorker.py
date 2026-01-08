#!/usr/bin/env python
# Python 3
# xnldorker - by @Xnl-h4ck3r: Gather results of dorks across a number of search engines
# Full help here: https://github.com/xnl-h4ck3r/xnldorker/blob/main/README.md
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import os
import sys
import argparse
import datetime
from signal import SIGINT, signal
from termcolor import colored
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import tldextract
from urllib.parse import unquote, urlparse, parse_qs
import html
import time
import random
import threading
import queue
import yaml

try:
    from . import __version__
except Exception:
    pass

# Available sources to search
SOURCES = [
    "duckduckgo",
    "duckgolite",
    "bing",
    "startpage",
    "yahoo",
    "google",
    "yandex",
    "ecosia",
    "baidu",
    "seznam",
    "kagi",
    "googlecs",
]

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"

# Uer Agents
UA_DESKTOP = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.6; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (X11; Linux i686; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
]

# Variables to hold config.yml values
KAGI_SESSION_LINK = ""
GOOGLE_SEARCH_API_KEY = ""
GOOGLE_SEARCH_CHAT_ID = ""

# Global variables
args = None
browser = None
stopProgram = False
stopProgramCount = 0
inputDork = ""
duckduckgoEndpoints = set()
duckgoliteEndpoints = set()
bingEndpoints = set()
yahooEndpoints = set()
googleEndpoints = set()
googlecsEndpoints = set()
startpageEndpoints = set()
yandexEndpoints = set()
ecosiaEndpoints = set()
baiduEndpoints = set()
seznamEndpoints = set()
kagiEndpoints = set()
allSubs = set()
sourcesToProcess = []
proxy_queue = None
proxy_thread = None
proxy_session = None
proxy_sent_endpoints = set()
googlecs_session = None
googlecs_request_lock = asyncio.Lock()


# Functions used when printing messages dependant on verbose options
def verbose():
    return args.verbose or args.vverbose


def vverbose():
    return args.vverbose


def write(text="", pipe=False):
    # Only send text to stdout if the tool isn't piped to pass output to something else,
    # or if the tool has been piped and the pipe parameter is True
    if sys.stdout.isatty() or (not sys.stdout.isatty() and pipe):
        sys.stdout.write(text + "\n")


def writerr(text=""):
    # Only send text to stdout if the tool isn't piped to pass output to something else,
    # or If the tool has been piped to output the send to stderr
    if sys.stdout.isatty():
        sys.stdout.write(text + "\n")
    else:
        sys.stderr.write(text + "\n")


def getConfig():
    """
    Try to get the values from the config file, otherwise use the defaults
    """
    global KAGI_SESSION_LINK, GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CHAT_ID
    try:

        # Try to get the config file values
        try:
            # Put config in global location based on the OS.
            xnldorkerPath = (
                Path(os.path.join(os.getenv("APPDATA", ""), "xnldorker"))
                if os.name == "nt"
                else (
                    Path(os.path.join(os.path.expanduser("~"), ".config", "xnldorker"))
                    if os.name == "posix"
                    else (
                        Path(
                            os.path.join(
                                os.path.expanduser("~"),
                                "Library",
                                "Application Support",
                                "xnldorker",
                            )
                        )
                        if os.name == "darwin"
                        else None
                    )
                )
            )

            xnldorkerPath.absolute()
            if xnldorkerPath == "":
                configPath = "config.yml"
            else:
                configPath = Path(xnldorkerPath / "config.yml")
            config = yaml.safe_load(open(configPath))

            try:
                KAGI_SESSION_LINK = config.get("KAGI_SESSION_LINK")
                if str(KAGI_SESSION_LINK) == "None":
                    KAGI_SESSION_LINK = ""
            except Exception:
                KAGI_SESSION_LINK = ""

            try:
                GOOGLE_SEARCH_API_KEY = config.get("GOOGLE_SEARCH_API_KEY")
                if str(GOOGLE_SEARCH_API_KEY) == "None":
                    GOOGLE_SEARCH_API_KEY = ""
            except Exception:
                GOOGLE_SEARCH_API_KEY = ""

            try:
                GOOGLE_SEARCH_CHAT_ID = config.get("GOOGLE_SEARCH_CHAT_ID")
                if str(GOOGLE_SEARCH_CHAT_ID) == "None":
                    GOOGLE_SEARCH_CHAT_ID = "DEFAULT"
            except Exception:
                GOOGLE_SEARCH_CHAT_ID = "DEFAULT"

        except Exception:
            writerr(
                colored(
                    'WARNING: Cannot find file "config.yml", so using default values',
                    "yellow",
                )
            )
            KAGI_SESSION_LINK = ""
            GOOGLE_SEARCH_API_KEY = ""
            GOOGLE_SEARCH_CHAT_ID = "DEFAULT"

    except Exception as e:
        writerr(colored("ERROR getConfig 1: " + str(e), "red"))


def showVersion():
    try:
        try:
            resp = requests.get(
                "https://raw.githubusercontent.com/xnl-h4ck3r/xnldorker/main/xnldorker/__init__.py",
                timeout=3,
            )
        except Exception:
            write(
                "Current xnldorker version "
                + __version__
                + " (unable to check if latest)\n"
            )
        if __version__ == resp.text.split("=")[1].replace('"', "").strip():
            write(
                "Current xnldorker version "
                + __version__
                + " ("
                + colored("latest", "green")
                + ")\n"
            )
        else:
            write(
                "Current xnldorker version "
                + __version__
                + " ("
                + colored("outdated", "red")
                + ")\n"
            )
    except Exception:
        pass


def selectRequestProxy(proxy_input):
    """
    Handle request proxy selection - either from file or direct value
    """
    try:
        if os.path.isfile(os.path.expanduser(proxy_input)):
            with open(os.path.expanduser(proxy_input), "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                selected_proxy = random.choice(proxies)
                return selected_proxy
            else:
                writerr(colored("ERROR: Request proxy file is empty", "red"))
                return None
        else:
            return proxy_input
    except Exception as e:
        writerr(colored(f"ERROR selectRequestProxy: {str(e)}", "red"))
        return None


def proxy_worker():
    """
    Worker thread function to send endpoints to forward proxy
    """
    global proxy_queue, proxy_session, stopProgram

    q = proxy_queue
    while not stopProgram:
        try:
            # Get endpoint from queue with timeout
            endpoint = q.get(timeout=1)
            if endpoint is None:  # Sentinel value to stop thread
                q.task_done()
                break

            try:
                # Send to proxy
                proxy_session.get(
                    endpoint,
                    allow_redirects=True,
                    verify=False,
                    headers={"User-Agent": "xnldorker by @xnl-h4ck3r"},
                    timeout=10,
                )
                if vverbose():
                    writerr(
                        colored(
                            f"[ Forward Proxy ] Sent {endpoint}",
                            "green",
                            attrs=["dark"],
                        )
                    )

            except Exception as e:
                if verbose():
                    writerr(
                        colored(
                            f"[ Forward Proxy ] Failed to send {endpoint}: {str(e)}",
                            "yellow",
                        )
                    )

            q.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            if verbose():
                writerr(colored(f"[ Forward Proxy ] Worker error: {str(e)}", "red"))
            break


def start_proxy_thread():
    """
    Initialize and start the proxy forwarding thread
    """
    global proxy_queue, proxy_thread, proxy_session

    if not args.forward_proxy or (proxy_thread and proxy_thread.is_alive()):
        return

    try:
        # Initialize queue and session
        proxy_queue = queue.Queue()
        proxy_session = requests.Session()
        proxy_session.proxies = {
            "http": args.forward_proxy,
            "https": args.forward_proxy,
        }
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        # Start worker thread
        proxy_thread = threading.Thread(target=proxy_worker, daemon=True)
        proxy_thread.start()

        if verbose():
            writerr(
                colored(
                    f"[ Forward Proxy ] Started background thread for {args.forward_proxy}",
                    "cyan",
                )
            )

    except Exception as e:
        writerr(colored(f"ERROR start_proxy_thread: {str(e)}", "red"))


def stop_proxy_thread():
    """
    Stop the proxy forwarding thread gracefully
    """
    global proxy_queue, proxy_thread, proxy_sent_endpoints

    if proxy_queue and proxy_thread:
        try:
            # Wait for all endpoints currently in the queue to be processed
            if not stopProgram and not proxy_queue.empty():
                if verbose():
                    writerr(
                        colored(
                            "[ Forward Proxy ] Waiting for all endpoints to be sent...",
                            "cyan",
                        )
                    )
                proxy_queue.join()

            # Send sentinel value to stop worker
            proxy_queue.put(None)
            # Wait for thread to finish with timeout
            proxy_thread.join(timeout=5)
            if verbose():
                sent_count = len(proxy_sent_endpoints)
                if sent_count > 0:
                    writerr(
                        colored(
                            f"[ Forward Proxy ] Sent {sent_count} unique endpoints to proxy",
                            "cyan",
                        )
                    )
        except Exception as e:
            if verbose():
                writerr(colored(f"ERROR stop_proxy_thread: {str(e)}", "red"))


def send_to_proxy(endpoint):
    """
    Add endpoint to proxy queue for background processing (with deduplication)
    """
    global proxy_queue, proxy_sent_endpoints

    if proxy_queue and args.forward_proxy:
        try:
            # Only send if we haven't sent this endpoint before
            if endpoint not in proxy_sent_endpoints:
                proxy_sent_endpoints.add(endpoint)
                proxy_queue.put(endpoint)
        except Exception as e:
            if verbose():
                writerr(colored(f"ERROR send_to_proxy: {str(e)}", "red"))


def showBanner():
    writerr("")
    writerr(colored(r"            _     _            _", "red"))
    writerr(colored(r"__  ___ __ | | __| | ___  _ __| | _____ _ __", "yellow"))
    writerr(colored(r"\ \/ / '_ \| |/ _` |/ _ \| '__| |/ / _ \ '__|", "green"))
    writerr(colored(r" >  <| | | | | (_| | (_) | |  |   <  __/ |", "cyan"))
    writerr(colored(r"/_/\_\_| |_|_|\__,_|\___/|_|  |_|\_\___|_|", "magenta"))
    writerr(colored("                             by Xnl-h4ck3r", "white"))
    writerr("")
    showVersion()


def handler(signal_received, frame):
    """
    This function is called if Ctrl-C is called by the user
    An attempt will be made to try and clean up properly
    """
    global stopProgram, stopProgramCount

    if stopProgram:
        stopProgramCount = stopProgramCount + 1
        if stopProgramCount == 1:
            writerr(
                colored(
                    ">>> Please be patient... Trying to save data and end gracefully!",
                    "red",
                )
            )
        elif stopProgramCount == 2:
            writerr(colored(">>> SERIOUSLY... YOU DON'T WANT YOUR DATA SAVED?!", "red"))
        elif stopProgramCount == 3:
            writerr(
                colored(">>> Patience isn't your strong suit eh? ¯\_(ツ)_/¯", "red")
            )
            sys.exit()
    else:
        stopProgram = True
        writerr(
            colored(
                '>>> "Oh my God, they killed Kenny... and xnldorker!" - Kyle', "red"
            )
        )
        writerr(colored(">>> Attempting to rescue any data gathered so far...", "red"))


def detect_proxy_type_error(proxy_url, error_msg):
    """
    Detect if user is trying to use HTTP intercepting proxy as request proxy
    """
    # Check for common intercepting proxy ports and SSL errors
    common_intercept_ports = ["8080", "8081", "8082", "9090", "3128"]
    ssl_errors = [
        "SEC_ERROR_UNKNOWN_ISSUER",
        "SSL_ERROR",
        "CERT_",
        "certificate",
        "TLS",
    ]

    # Extract port from proxy URL
    proxy_port = None
    if ":" in proxy_url:
        try:
            proxy_port = proxy_url.split(":")[-1]
        except Exception:
            pass

    # Check if this looks like an intercepting proxy issue
    is_common_port = proxy_port in common_intercept_ports
    is_ssl_error = any(ssl_term in error_msg.upper() for ssl_term in ssl_errors)

    if is_common_port and is_ssl_error or "NS_ERROR_UNKNOWN_PROXY_HOST" in error_msg:
        return True
    return False


def show_proxy_usage_hint(proxy_url):
    """
    Show helpful message about proxy usage
    """
    writerr(colored("━" * 60, "yellow"))
    writerr(colored("💡 PROXY USAGE HINT:", "yellow", attrs=["bold"]))
    writerr(
        colored(
            "It looks like you might be using an HTTP intercepting proxy (like Caido/Burp Suite)",
            "white",
        )
    )
    writerr(
        colored(
            "as a --request-proxy. This typically doesn't work as expected.", "white"
        )
    )
    writerr("")
    writerr(colored("For intercepting proxies, use --forward-proxy instead:", "cyan"))
    writerr(colored(f"  --forward-proxy {proxy_url}", "green"))
    writerr("")
    writerr(colored("Proxy Usage Guide:", "white", attrs=["bold"]))
    writerr(
        colored(
            "• --request-proxy: For routing browser traffic (VPNs, SOCKS proxies)",
            "white",
        )
    )
    writerr(
        colored(
            "• --forward-proxy: For sending found endpoints to Caido/Burp/etc.", "white"
        )
    )
    writerr(colored("━" * 60, "yellow"))


def getSubdomain(url):
    try:
        # Just get the hostname of the url
        tldExtract = tldextract.extract(url)
        return tldExtract.subdomain
    except Exception as e:
        writerr(colored("ERROR getSubdomain 1: " + str(e), "red"))


# Global dictionary to track all active captcha waits
_active_captcha_waits = {}
_stdin_reader_active = False


async def wait_for_word_or_sleep(word, timeout):
    """
    Called when an antibot screen is detected on a source. It will resume again when the timeout is reached, or if the passed word is typed and ENTER pressed
    Supports multiple sources waiting for different words simultaneously.
    """
    global _active_captcha_waits, _stdin_reader_active

    loop = asyncio.get_event_loop()
    word_entered = asyncio.Event()

    # Register this word in the active waits
    _active_captcha_waits[word] = word_entered

    def on_input_received():
        """Shared input handler for all waiting sources"""
        try:
            input_text = sys.stdin.readline().strip()
            # Check if the input matches any of the active waits
            if input_text in _active_captcha_waits:
                _active_captcha_waits[input_text].set()
        except Exception:
            pass

    # Only add the reader if it's not already active
    if not _stdin_reader_active:
        loop.add_reader(sys.stdin.fileno(), on_input_received)
        _stdin_reader_active = True

    try:
        await asyncio.wait_for(word_entered.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass  # Timeout reached, continue with the script
    finally:
        # Remove this word from active waits
        if word in _active_captcha_waits:
            del _active_captcha_waits[word]

        # Only remove the reader if no more waits are active
        if not _active_captcha_waits and _stdin_reader_active:
            loop.remove_reader(sys.stdin.fileno())
            _stdin_reader_active = False


async def get_or_create_context(context_param):
    """
    Helper function to get a context for a source.
    In 'windows' mode (context_param is None), creates a new context.
    In 'tabs' mode or headless, returns the shared context.
    Returns tuple of (context, should_close_context)
    """
    if context_param is None and args.show_browser == "windows":
        # Windows mode - create a new context for this source
        context_options = {}
        if args.request_proxy:
            context_options["ignore_https_errors"] = True
        context_options["viewport"] = {"width": 1280, "height": 720}
        context_options["user_agent"] = DEFAULT_USER_AGENT
        # Add extra headers to avoid bot detection
        context_options["extra_http_headers"] = {
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        new_context = await browser.new_context(**context_options)
        # Inject script to hide webdriver property and other automation indicators
        await new_context.add_init_script(
            """
            // Hide webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override the plugins to make it non-empty
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """
        )
        return new_context, True
    else:
        # Tabs mode or headless - use the shared context
        return context_param, False


async def getResultsDuckDuckGo(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        div_content = soup.find("div", id="web_content_wrapper")
        if div_content:
            a_tags = div_content.find_all("a")
            for a in a_tags:
                href = a.get("href")
                if (
                    href
                    and href.startswith("http")
                    and not re.match(
                        r"^https?:\/\/([\w-]+\.)*duckduckgo\.[^\/\.]{2,}", href
                    )
                ):
                    endpoint = href.strip()
                    endpoints.append(endpoint)
                    # Send to forward proxy in background thread
                    send_to_proxy(endpoint)
                    # If the same search is going to be resubmitted without subs, get the subdomain
                    if args.resubmit_without_subs:
                        allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR getResultsDuckDuckGo 1: " + str(e), "red"))
        return endpoints


async def getDuckDuckGo(context, dork, semaphore):
    global stopProgram
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        # Add small random delay to appear more human-like
        await asyncio.sleep(random.uniform(0.5, 1.5))

        if verbose():
            writerr(colored("[ DuckDuckGo ] Starting...", "green"))

        # Call with parameters:
        #  kc=-1 - Don't auto load images
        await page.goto(
            f"https://duckduckgo.com/?kc=-1&ia=web&q={dork}",
            timeout=args.timeout * 1000,
        )
        pageNo = 1

        # If captcha is shown then allow time to submit it
        captcha = await page.query_selector(
            "#anomaly-modal__modal.anomaly-modal__modal"
        )
        # Also check for bot detection text
        if not captcha:
            page_content = await page.content()
            if (
                "unfortunately, bots use duckduckgo" in page_content.lower()
                or "error getting results" in page_content.lower()
            ):
                captcha = True
        if captcha:
            if args.show_browser:
                writerr(
                    colored(
                        f'[ DuckDuckGo ] reCAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "duckduckgo" and press ENTER...',
                        "yellow",
                    )
                )
                await wait_for_word_or_sleep("duckduckgo", args.antibot_timeout)
                writerr(colored("[ DuckDuckGo ] Resuming...", "green"))
            else:
                writerr(
                    colored(
                        "[ DuckDuckGo ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser",
                        "red",
                    )
                )
                return set(endpoints)

        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
        except Exception as wait_e:
            if "Target page, context or browser has been closed" in str(wait_e):
                raise
            pass

        captcha = await page.query_selector(
            "#anomaly-modal__modal.anomaly-modal__modal"
        )
        # Also check for bot detection text
        if not captcha:
            page_content = await page.content()
            if (
                "unfortunately, bots use duckduckgo" in page_content.lower()
                or "error getting results" in page_content.lower()
            ):
                captcha = True
        if captcha:
            writerr(colored("[ DuckDuckGo ] Failed to complete reCAPTCHA", "red"))
            return set(endpoints)

        # Function to check if the button is disabled and enable it if necessary
        async def enable_more_results():
            more_results_button = await page.query_selector("#more-results")
            if more_results_button:
                is_disabled = await more_results_button.evaluate(
                    "(element) => element.disabled"
                )
                if is_disabled:
                    await page.evaluate(
                        "(element) => element.disabled = false", more_results_button
                    )

        # Function to check for the presence of the button and click it if available
        async def click_more_results():
            if await page.query_selector("#more-results"):
                await page.click("#more-results")
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )

        # Loop to repeatedly check for the button and click it until it doesn't exist
        while await page.query_selector("#more-results"):
            if stopProgram:
                break
            await enable_more_results()
            if vverbose():
                pageNo += 1
                writerr(
                    colored(
                        '[ DuckDuckGo ] Clicking "More Results" button to display page '
                        + str(pageNo),
                        "green",
                        attrs=["dark"],
                    )
                )
            await click_more_results()
            # Get the results so far, just in case it ends early
            endpoints = await getResultsDuckDuckGo(page, endpoints)

        # Get all the results
        endpoints = await getResultsDuckDuckGo(page, endpoints)
        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("DuckDuckGo", page)
            writerr(
                colored(
                    f"[ DuckDuckGo ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ DuckDuckGo ] Page timed out - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ DuckDuckGo ] Search aborted - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        else:
            writerr(colored("[ DuckDuckGo ] ERROR getDuckDuckGo 1: " + str(e), "red"))
            # Check if this looks like a proxy type error and show helpful hint
            if args.request_proxy and detect_proxy_type_error(
                args.request_proxy, str(e)
            ):
                show_proxy_usage_hint(args.request_proxy)
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("DuckDuckGo", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def getResultsDuckGoLite(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        # Find all links with class "result-link" - these are the actual search result links
        a_tags = soup.find_all("a", class_="result-link")
        for a in a_tags:
            href = a.get("href")
            # If the link starts with "//duckduckgo.com/l/?uddg=" then remove that and then URL decode it
            if href.startswith("//duckduckgo.com/l/?uddg="):
                href = href[25:]
                href = unquote(href)
            if (
                href
                and href.startswith("http")
                and not re.match(
                    r"^https?:\/\/([\w-]+\.)*duckduckgo\.[^\/\.]{2,}", href
                )
            ):
                endpoint = href.strip()
                endpoints.append(endpoint)
                # Send to forward proxy in background thread
                send_to_proxy(endpoint)
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR getResultsDuckGoLite 1: " + str(e), "red"))
        return endpoints


async def getDuckGoLite(context, dork, semaphore):
    """
    Search DuckDuckGo Lite (text-only version) and extract all result links.
    Paginates by clicking "Next Page" button until it no longer exists.
    """
    global stopProgram
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        # Add small random delay to appear more human-like
        await asyncio.sleep(random.uniform(0.5, 1.5))

        if verbose():
            writerr(colored("[ DuckGoLite ] Starting...", "green"))

        # Navigate to DuckDuckGo Lite
        await page.goto(
            f"https://lite.duckduckgo.com/lite/?q={dork}",
            timeout=args.timeout * 1000,
        )
        pageNo = 1

        try:
            # Wait for the search results to be fully loaded
            await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
        except Exception as wait_e:
            if "Target page, context or browser has been closed" in str(wait_e):
                raise
            pass

        # Function to check if Next Page button exists and click it
        async def click_next_page():
            # The Next button is an input submit button inside a form
            next_button = await page.query_selector('input.navbutton[value*="Next"]')
            if next_button:
                await next_button.click()
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )
                return True
            return False

        # Loop: get endpoints from current page, then try to go to next page
        pageNo = 1
        while True:
            if stopProgram:
                break

            # If captcha is shown then allow time to submit it
            captcha = await page.query_selector(
                "#anomaly-modal__modal.anomaly-modal__modal"
            )
            # Also check for bot detection text
            if not captcha:
                page_content = await page.content()
                if (
                    "unfortunately, bots use duckduckgo" in page_content.lower()
                    or "error getting results" in page_content.lower()
                ):
                    captcha = True
            if captcha:
                if args.show_browser:
                    writerr(
                        colored(
                            f'[ DuckGoLite ] reCAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "duckgolite" and press ENTER...',
                            "yellow",
                        )
                    )
                    await wait_for_word_or_sleep("duckgolite", args.antibot_timeout)
                    writerr(colored("[ DuckGoLite ] Resuming...", "green"))
                else:
                    writerr(
                        colored(
                            "[ DuckGoLite ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser",
                            "red",
                        )
                    )
                return set(endpoints)

            # Get endpoints from current page
            if vverbose():
                writerr(
                    colored(
                        f"[ DuckGoLite ] Getting links from page {pageNo}",
                        "green",
                        attrs=["dark"],
                    )
                )
            endpoints = await getResultsDuckGoLite(page, endpoints)

            # Try to click Next Page button
            if await click_next_page():
                pageNo += 1
                if vverbose():
                    writerr(
                        colored(
                            f'[ DuckGoLite ] Clicked "Next Page" button, now on page {pageNo}',
                            "green",
                            attrs=["dark"],
                        )
                    )
            else:
                # No more Next button, we're done
                break

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("DuckGoLite", page)
            writerr(
                colored(
                    f"[ DuckGoLite ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ DuckGoLite ] Page timed out - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ DuckGoLite ] Search aborted - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        else:
            writerr(colored("[ DuckGoLite ] ERROR getDuckGoLite 1: " + str(e), "red"))
            # Check if this looks like a proxy type error and show helpful hint
            if args.request_proxy and detect_proxy_type_error(
                args.request_proxy, str(e)
            ):
                show_proxy_usage_hint(args.request_proxy)
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("DuckGoLite", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


def extractBingEndpoints(soup):
    global allSubs
    try:
        import base64

        endpoints = []
        # Find all b_algo elements
        b_algo_elements = soup.find_all("li", class_="b_algo")
        for element in b_algo_elements:
            # Find links within each b_algo element
            a_tags = element.find_all("a", href=True)
            for a in a_tags:
                href = a.get("href")
                if href:
                    # Check if it's a Bing redirect URL
                    if "/ck/a?" in href or "bing.com/ck/a?" in href:
                        # Parse the URL to extract the 'u' parameter
                        parsed = urlparse(href)
                        params = parse_qs(parsed.query)
                        if "u" in params:
                            encoded_url = params["u"][0]
                            # Decode the custom base64-like encoding
                            # Remove the 'a1' prefix if present
                            if encoded_url.startswith("a1"):
                                encoded_url = encoded_url[2:]
                            # URL decode it
                            try:
                                padding = (
                                    "=" * (4 - len(encoded_url) % 4)
                                    if len(encoded_url) % 4
                                    else ""
                                )
                                decoded_url = base64.b64decode(
                                    encoded_url + padding
                                ).decode("utf-8", errors="ignore")
                                if decoded_url.startswith("http"):
                                    endpoint = decoded_url.strip()
                                    endpoints.append(endpoint)
                                    send_to_proxy(endpoint)
                                    if args.resubmit_without_subs:
                                        allSubs.add(getSubdomain(endpoint))
                            except Exception:
                                pass
                    elif (
                        href.startswith("http")
                        and not re.match(
                            r"^https?:\/\/([\w-]+\.)*bing\.[^\/\.]{2,}", href
                        )
                        and not re.match(r"^https?:\/\/go\.microsoft\.com", href)
                    ):
                        # Direct URL (fallback)
                        endpoint = href.strip()
                        endpoints.append(endpoint)
                        send_to_proxy(endpoint)
                        if args.resubmit_without_subs:
                            allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR extractBingEndpoints 1: " + str(e), "red"))
        return endpoints


async def getBing(context, dork, semaphore):
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Bing ] Starting...", "green"))

        await page.goto(
            f"https://www.bing.com/search?q={dork}&pq={dork}&qs=n",
            timeout=args.timeout * 1000,
        )

        # If captcha is shown then allow time to submit it
        content = await page.content()
        if "One last step" in content:
            if args.show_browser:
                writerr(
                    colored(
                        f'[ Bing ] Cloudflare Captcha needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "bing" and press ENTER...',
                        "yellow",
                    )
                )
                await wait_for_word_or_sleep("bing", args.antibot_timeout)
                writerr(colored("[ Bing ] Resuming...", "green"))
            else:
                writerr(
                    colored(
                        "[ Bing ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser",
                        "red",
                    )
                )
                return set(endpoints)

        # Check if the cookie banner exists and click reject if it does
        if await page.query_selector("#bnp_btn_reject"):
            # Click the button to reject
            await page.click("#bnp_btn_reject")

        # Collect endpoints from the initial page
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        pageNo = 1
        endpoints = extractBingEndpoints(soup)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        while True:
            if stopProgram:
                break
            # Find the link with the title "Next page"
            if await page.query_selector('a[title="Next page"]'):
                await page.click('a[title="Next page"]')
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )
                pageNo += 1
                if vverbose():
                    writerr(
                        colored(
                            "[ Bing ] Getting endpoints from page " + str(pageNo),
                            "green",
                            attrs=["dark"],
                        )
                    )

                # Collect endpoints from the current page
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                endpoints += extractBingEndpoints(soup)
            else:
                # No "Next page" link found, exit the loop
                break

        # Close page/tab unless in debug mode
        if page and not args.debug:
            await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Bing", page)
            writerr(
                colored(
                    f"[ Bing ] Complete! {str(noOfEndpoints)} endpoints found", "green"
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Bing ] Page timed out - got {str(noOfEndpoints)} results", "red"
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Bing ] Search aborted - got {str(noOfEndpoints)} results", "red"
                )
            )
        else:
            writerr(colored("[ Bing ] ERROR getBing 1: " + str(e), "red"))
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("Bing", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


def extractStartpageEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        result_links = soup.find_all("a", class_=re.compile(".*result-link.*"))
        for link in result_links:
            href = link.get("href")
            if (
                href
                and href.startswith("http")
                and not re.match(r"^https?:\/\/([\w-]+\.)*startpage\.[^\/\.]{2,}", href)
            ):
                endpoint = href.strip()
                endpoints.append(endpoint)
                # Send to forward proxy in background thread
                send_to_proxy(endpoint)
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR extractStartpageEndpoints 1: " + str(e), "red"))
        return endpoints


async def getStartpage(context, dork, semaphore):
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Startpage ] Starting...", "green"))

        await page.goto("https://www.startpage.com/", timeout=args.timeout * 1000)

        # Wait for the search results to be fully loaded
        await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)

        # Check if bot detection is shown
        if "/sp/captcha" in page.url:
            if args.show_browser:
                writerr(
                    colored(
                        f'[ Startpage ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "startpage" and press ENTER...',
                        "yellow",
                    )
                )
                await wait_for_word_or_sleep("startpage", args.antibot_timeout)
                writerr(colored("[ Startpage ] Resuming...", "green"))
            else:
                writerr(
                    colored(
                        "[ Startpage ] CAPTCHA needed responding to. Consider using option -sb / --show-browser",
                        "red",
                    )
                )
                return set(endpoints)

        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
        except Exception as wait_e:
            if "Target page, context or browser has been closed" in str(wait_e):
                raise
            pass

        # Check if bot detection is still shown
        if "/sp/captcha" in page.url:
            writerr(colored("[ Startpage ] Failed to complete CAPTCHA", "red"))
            return set(endpoints)

        await page.fill('input[title="Search"]', dork)
        await page.click("button.search-btn")

        # Wait for the search results to be fully loaded
        await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)

        # Check if any '.result-link' exists
        try:
            await page.wait_for_selector(
                ".result-link", timeout=1000
            )  # Short timeout to check existence
        except Exception:
            if verbose():
                writerr(colored("[ Startpage ] Complete! - 0 endpoints found", "green"))
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            return set()

        # Collect endpoints from the initial page
        if vverbose():
            writerr(
                colored(
                    "[ Startpage ] Getting endpoints from page 1",
                    "green",
                    attrs=["dark"],
                )
            )
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        pageNo = 1
        endpoints = extractStartpageEndpoints(soup)

        # Loop until there is no submit button in the last form with action="/sp/search"
        while True:
            if stopProgram:
                break
            # Check if bot detection is shown
            if "/sp/captcha" in page.url:
                if args.show_browser:
                    writerr(
                        colored(
                            f'[ Startpage ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "startpage" and press ENTER...',
                            "yellow",
                        )
                    )
                    await wait_for_word_or_sleep("startpage", args.antibot_timeout)
                    writerr(colored("[ Startpage ] Resuming...", "green"))
                else:
                    writerr(
                        colored(
                            "[ Startpage ] CAPTCHA needed responding to. Consider using option -sb / --show-browser",
                            "red",
                        )
                    )
                    return set(endpoints)

            try:
                # Wait for the search results to be fully loaded and have links
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )
            except Exception:
                pass

            # Check if bot detection is still shown
            if "/sp/captcha" in page.url:
                writerr(colored("[ Startpage ] Failed to complete CAPTCHA", "red"))
                return set(endpoints)

            # Locate all forms with action="/sp/search" on the page
            forms = await page.query_selector_all('form[action="/sp/search"]')
            last_form = forms[-1]  # Get the last form

            # Get the current value of the "page" input field
            try:
                curr_page_value = await last_form.evaluate(
                    "(form) => form.querySelector(\"input[name='page']\").value"
                )
            except Exception:
                curr_page_value = 1

            # If the current "page" value has not increased, break out of the loop
            if pageNo == curr_page_value:
                break

            # Click the submit button for the last form
            await last_form.click()

            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)

            # Check if any '.result-link' exists
            try:
                await page.wait_for_selector(
                    ".result-link", timeout=1000
                )  # Short timeout to check existence
            except Exception:
                break  # Break the loop if no '.result-link' found

            if vverbose():
                writerr(
                    colored(
                        "[ Startpage ] Getting endpoints from page " + str(pageNo),
                        "green",
                        attrs=["dark"],
                    )
                )

            # Collect endpoints from the current page
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            endpoints += extractStartpageEndpoints(soup)

            # Update the previous "page" value
            pageNo = curr_page_value

        # Close page/tab unless in debug mode
        if page and not args.debug:
            await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Startpage", page)
            writerr(
                colored(
                    f"[ Startpage ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Startpage ] Page timed out - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Startpage ] Search aborted - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        else:
            writerr(colored("[ Startpage ] ERROR getStartpage1: " + str(e), "red"))
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("Startpage", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


def extractYahooEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        div_content = soup.find("div", id="results")
        if div_content:
            a_tags = div_content.find_all("a")
            for a in a_tags:
                # Don't add links from Ads
                if not a.find_parent(class_="searchCenterTopAds") and not a.find_parent(
                    class_="searchCenterBottomAds"
                ):
                    href = a.get("href")
                    if (
                        href
                        and href.startswith("http")
                        and not re.match(
                            r"^https?:\/\/([\w-]+\.)*yahoo\.[^\/\.]{2,}", href
                        )
                        and not re.match(r"^https?:\/\/([\w-]+\.)*bingj\.com", href)
                    ):
                        endpoint = href.strip()
                        endpoints.append(endpoint)
                        # Send to forward proxy in background thread
                        send_to_proxy(endpoint)
                        # If the same search is going to be resubmitted without subs, get the subdomain
                        if args.resubmit_without_subs:
                            allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR extractYahooEndpoints 1: " + str(e), "red"))
        return endpoints


def extractYahooResultNumber(url):
    try:
        match = re.search(r"\b(?:b=)([^&]+)", url)
        if match:
            return match.group(1)
        return 0
    except Exception as e:
        writerr(colored("ERROR extractYahooResultNumber 1: " + str(e), "red"))


async def getYahoo(context, dork, semaphore):
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Yahoo ] Starting...", "green"))

        await page.goto(
            f"https://www.yahoo.com/search?q={dork}", timeout=args.timeout * 1000
        )

        # Check if the cookie banner exists and click "Go to end" and then "Agree" if it does
        cookie = await page.query_selector("#scroll-down-btn")
        if cookie:
            await cookie.click()
        cookieAgree = await page.query_selector('button[name="agree"][value="agree"]')
        if cookieAgree:
            await cookieAgree.click()

        # Submit the search form
        await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
        await page.wait_for_selector("form")
        await page.press("form", "Enter")
        await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)

        # Collect endpoints from the initial page
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        endpoints = extractYahooEndpoints(soup)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        pageNo = 1
        oldResultNumber = 1
        while True:
            if stopProgram:
                break
            # Find the link with the title "Next page"
            next_page_link = await page.query_selector("a.next")
            if next_page_link:
                # Extract Result number value from the URL of the current page
                pageUrl = page.url
                nextResultNumber = extractYahooResultNumber(pageUrl)
                # If it is the same as the last page, exit the loop
                if nextResultNumber == oldResultNumber:
                    break
                oldResultNumber = nextResultNumber

                await next_page_link.click()
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )
                pageNo += 1
                if vverbose():
                    writerr(
                        colored(
                            "[ Yahoo ] Getting endpoints from page " + str(pageNo),
                            "green",
                            attrs=["dark"],
                        )
                    )

                # Collect endpoints from the current page
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                endpoints += extractYahooEndpoints(soup)

            else:
                # No "Next page" link found, exit the loop
                break

        # Close page/tab unless in debug mode
        if page and not args.debug:
            await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Yahoo", page)
            writerr(
                colored(
                    f"[ Yahoo ] Complete! {str(noOfEndpoints)} endpoints found", "green"
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Yahoo ] Page timed out - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Yahoo ] Search aborted - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        else:
            writerr(colored("[ Yahoo ] ERROR getYahoo1: " + str(e), "red"))
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("Yahoo", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def getResultsGoogle(page, endpoints):
    global allSubs
    try:
        # Retry getting content if page is still navigating
        page_content = None
        for attempt in range(3):
            try:
                page_content = await page.content()
                break
            except Exception as e:
                if "page is navigating" in str(e).lower():
                    await page.wait_for_timeout(1000)  # Wait 1 second and retry
                else:
                    raise

        if not page_content:
            return endpoints

        soup = BeautifulSoup(page_content, "html.parser")
        a_tags = soup.find_all("a")
        for a in a_tags:
            href = a.get("href")
            if (
                href
                and href.startswith("http")
                and not re.match(r"^https?:\/\/([\w-]+\.)*google\.[^\/\.]{2,}", href)
            ):
                endpoint = href.strip()
                endpoints.append(endpoint)
                # Send to forward proxy in background thread
                send_to_proxy(endpoint)
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR getResultsGoogle 1: " + str(e), "red"))
        return endpoints  # Return what we have so far instead of None


async def getGoogle(context, dork, semaphore):
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Google ] Starting...", "green"))

        # Use the parameters:
        #  tbs=li:1 - Verbatim search
        #  hl=en - English language
        #  filter=0 - Show near duplicate content
        await page.goto(
            f"https://www.google.com/search?tbs=li:1&hl=en&filter=0&q={dork}",
            timeout=args.timeout * 1000,
        )
        await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)

        pageNo = 1

        # If captcha is shown then allow time to submit it
        try:
            captcha = await page.query_selector("form#captcha-form")
            # Also check for text-based captcha warning
            if not captcha:
                page_text = await page.text_content("body")
                if (
                    page_text
                    and "detected unusual traffic from your computer"
                    in page_text.lower()
                ):
                    captcha = True  # Set to True to trigger captcha handling
        except Exception as e:
            if "Execution context was destroyed" in str(e):
                # Page is navigating, wait a moment and skip captcha check
                await page.wait_for_timeout(1000)
                captcha = None
            else:
                raise

        if captcha:
            if args.show_browser:
                writerr(
                    colored(
                        f'[ Google ] reCAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "google" and press ENTER...',
                        "yellow",
                    )
                )
                await wait_for_word_or_sleep("google", args.antibot_timeout)
                writerr(colored("[ Google ] Resuming...", "green"))
            else:
                writerr(
                    colored(
                        "[ Google ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser",
                        "red",
                    )
                )
                return set(endpoints)

        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
        except Exception as wait_e:
            if "Target page, context or browser has been closed" in str(wait_e):
                raise
            pass

        # Check if bot detection is still shown
        try:
            captcha = await page.query_selector("form#captcha-form")
            # Also check for text-based captcha warning
            if not captcha:
                page_text = await page.text_content("body")
                if (
                    page_text
                    and "detected unusual traffic from your computer"
                    in page_text.lower()
                ):
                    captcha = True  # Set to True to trigger captcha handling
        except Exception as e:
            if "Execution context was destroyed" in str(e):
                # Page is navigating, wait a moment and skip captcha check
                await page.wait_for_timeout(1000)
                captcha = None
            else:
                raise

        if captcha:
            writerr(colored("[ Google ] Failed to complete reCAPTCHA", "red"))
            return set(endpoints)

        # If the cookies notice is shown, accept it
        cookieAccept = await page.query_selector('button:has-text("Accept all")')
        if cookieAccept:
            await cookieAccept.click()

        # If the dialog box asking if you want location specific search, say Not now
        locationSpecific = await page.query_selector(
            'g-raised-button:has-text("Not now")'
        )
        if locationSpecific:
            await locationSpecific.click()

        # Collect endpoints from the initial page
        endpoints = await getResultsGoogle(page, endpoints)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        while True:
            if stopProgram:
                break
            # Check if bot detection is still shown
            try:
                captcha = await page.query_selector("form#captcha-form")
                # Also check for text-based captcha warning
                if not captcha:
                    page_text = await page.text_content("body")
                    if (
                        page_text
                        and "detected unusual traffic from your computer"
                        in page_text.lower()
                    ):
                        captcha = True  # Set to True to trigger captcha handling
            except Exception as e:
                if "Execution context was destroyed" in str(e):
                    # Page is navigating, wait a moment and skip captcha check
                    await page.wait_for_timeout(1000)
                    captcha = None
                else:
                    raise

            if captcha:
                if args.show_browser:
                    writerr(
                        colored(
                            f'[ Google ] reCAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "google" and press ENTER...',
                            "yellow",
                        )
                    )
                    await wait_for_word_or_sleep("google", args.antibot_timeout)
                    writerr(colored("[ Google ] Resuming...", "green"))
                else:
                    writerr(
                        colored(
                            "[ Google ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser",
                            "red",
                        )
                    )
                    return set(endpoints)

            # Get href from the Next button
            next_button = await page.query_selector("#pnnext")
            if next_button:
                next_href = await next_button.get_attribute("href")
                if next_href:
                    next_url = "https://www.google.com" + next_href
                    try:
                        await page.goto(next_url, timeout=args.timeout * 1000)
                        await page.wait_for_load_state(
                            "domcontentloaded", timeout=args.timeout * 1000
                        )
                    except Exception as e:
                        if "Target page, context or browser has been closed" in str(e):
                            raise
                        # Page timed out, but wait a bit to ensure navigation completed
                        try:
                            await page.wait_for_load_state("load", timeout=5000)
                        except Exception:
                            await page.wait_for_timeout(2000)

                    try:
                        # Wait for the search results to be fully loaded and have links
                        await page.wait_for_load_state(
                            "networkidle", timeout=args.timeout * 1000
                        )
                    except Exception as wait_e:
                        if "Target page, context or browser has been closed" in str(
                            wait_e
                        ):
                            raise
                        pass

                    pageNo += 1
                    if vverbose():
                        writerr(
                            colored(
                                "[ Google ] Getting endpoints from page " + str(pageNo),
                                "green",
                                attrs=["dark"],
                            )
                        )

                    # Collect endpoints from the current page
                    endpoints = await getResultsGoogle(page, endpoints)
            else:
                # No "Next" button found, exit the loop
                break

        # Close page/tab unless in debug mode
        if page and not args.debug:
            await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Google", page)
            writerr(
                colored(
                    f"[ Google ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Google ] Page timed out - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Google ] Search aborted - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        else:
            writerr(colored("[ Google ] ERROR getGoogle1: " + str(e), "red"))
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("Google", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def getGoogleCS(context, dork, semaphore):
    global stopProgram, GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CHAT_ID, allSubs, googlecs_session, googlecs_request_lock
    endpoints = []
    try:
        await semaphore.acquire()

        if verbose():
            writerr(colored("[ GoogleCS ] Starting...", "green"))

        # If Google CSE API key or Chat ID are NOT provided, warn the user
        if not GOOGLE_SEARCH_API_KEY:
            writerr(
                colored(
                    "[ GoogleCS ] API key not provided in config.yml. Please provide GOOGLE_SEARCH_API_KEY.",
                    "red",
                )
            )
            return set(endpoints)

        # If the Chat ID is set to default context, warn the user
        if not GOOGLE_SEARCH_CHAT_ID or GOOGLE_SEARCH_CHAT_ID == "DEFAULT":
            writerr(
                colored(
                    "[ GoogleCS ] Chat ID is set to default context. Please provide a valid GOOGLE_SEARCH_CHAT_ID in config.yml if required.",
                    "yellow",
                )
            )

        # Initialize session with retry logic if not already done
        if googlecs_session is None:
            retry_strategy = Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[429],
                allowed_methods=["GET"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            googlecs_session = requests.Session()
            googlecs_session.mount("https://", adapter)

        start_index = 1
        pageNo = 1
        while pageNo <= 10:
            if stopProgram:
                break

            if vverbose():
                writerr(
                    colored(
                        f"[ GoogleCS ] Getting endpoints from API page {pageNo}",
                        "green",
                        attrs=["dark"],
                    )
                )

            api_url = f"https://www.googleapis.com/customsearch/v1?q={unquote(dork)}&key={GOOGLE_SEARCH_API_KEY}&cx={GOOGLE_SEARCH_CHAT_ID}&start={start_index}"
            try:
                # Use a lock to ensure only one googlecs request happens at once
                # and sleep to throttle requests to 100 per minute (60s / 100 = 0.6s)
                async with googlecs_request_lock:
                    if stopProgram:
                        break
                    # Use run_in_executor to prevent synchronous requests from blocking the event loop
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: googlecs_session.get(api_url, timeout=args.timeout),
                    )
                    if response.status_code != 200:
                        try:
                            error_msg = response.json().get("error", {}).get("message")
                            if error_msg:
                                writerr(
                                    colored(
                                        f"[ GoogleCS ] API ERROR: {response.status_code} - {error_msg}",
                                        "red",
                                    )
                                )
                            else:
                                writerr(
                                    colored(
                                        f"[ GoogleCS ] API ERROR: {response.status_code} - {response.reason}",
                                        "red",
                                    )
                                )
                        except Exception:
                            writerr(
                                colored(
                                    f"[ GoogleCS ] API ERROR: {response.status_code} - {response.reason}",
                                    "red",
                                )
                            )
                        break

                    data = response.json()
                    await asyncio.sleep(0.6)

                items = data.get("items", [])
                if not items:
                    break

                for item in items:
                    if stopProgram:
                        break
                    endpoint = item.get("link")
                    if endpoint:
                        endpoint = endpoint.strip()
                        endpoints.append(endpoint)
                        send_to_proxy(endpoint)
                        if args.resubmit_without_subs:
                            allSubs.add(getSubdomain(endpoint))

                # Check if there's a next page or if we've reached the end
                next_page = data.get("queries", {}).get("nextPage")
                if not next_page:
                    break

                start_index = next_page[0].get("startIndex")
                pageNo += 1

            except Exception as api_e:
                if "too many 429 error responses" in str(api_e):
                    writerr(
                        colored(
                            "[ GoogleCS ] API ERROR: too many 429 error responses",
                            "red",
                        )
                    )
                else:
                    writerr(colored(f"[ GoogleCS ] API ERROR: {str(api_e)}", "red"))
                break

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(
                colored(
                    f"[ GoogleCS ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        writerr(colored("[ GoogleCS ] ERROR getGoogleCS: " + str(e), "red"))
        return set(endpoints)
    finally:
        try:
            semaphore.release()
        except Exception:
            pass


def extractYandexEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        result_links = soup.find_all("a", class_=re.compile(".*organic__url.*"))
        for link in result_links:
            href = link.get("href")
            print(href)
            if (
                href
                and href.startswith("http")
                and not re.match(r"^https?:\/\/([\w-]+\.)*yandex\.[^\/\.]{2,}", href)
            ):
                endpoint = href.strip()
                endpoints.append(endpoint)
                # Send to forward proxy in background thread
                send_to_proxy(endpoint)
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR extractYandexEndpoints 1: " + str(e), "red"))
        return endpoints


async def getYandex(context, dork, semaphore):
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Yandex ] Starting...", "green"))

        await page.goto(
            f"https://yandex.com/search/?text={dork}", timeout=args.timeout * 1000
        )

        # Check if bot detection is shown
        if "/showcaptcha" in page.url:
            if args.show_browser:
                writerr(
                    colored(
                        f'[ Yandex ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...',
                        "yellow",
                    )
                )
                await wait_for_word_or_sleep("yandex", args.antibot_timeout)
                writerr(colored("[ Yandex ] Resuming...", "green"))
            else:
                writerr(
                    colored(
                        "[ Yandex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser",
                        "red",
                    )
                )
                return set(endpoints)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=1000)
        except Exception:
            pass

        # If still on Captcha page, then exit
        if "/showcaptcha" in page.url:
            writerr(colored("[ Yandex ] Failed to complete CAPTCHA", "red"))
            return set(endpoints)

        # Collect endpoints from the initial page
        if vverbose():
            writerr(
                colored(
                    "[ Yandex ] Getting endpoints from page 1", "green", attrs=["dark"]
                )
            )
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        pageNo = 1
        endpoints = extractYandexEndpoints(soup)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        while True:
            if stopProgram:
                break

            next_button = await page.query_selector('a[aria-label="Next page"]')

            if not next_button:
                # No "Next" button found, exit the loop
                break

            await next_button.click()

            pageNo += 1

            try:
                # Yandex shows a "Skeleton" loading overlay.
                # Wait for this overlay to become hidden.
                await page.wait_for_selector(
                    "div.Skeleton", state="hidden", timeout=args.timeout * 1000
                )
                # Add a final wait for the network to be idle.
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )
            except Exception as e:
                if "Target page, context or browser has been closed" in str(e):
                    raise
                if "timeout" in str(e).lower():
                    if verbose():
                        writerr(
                            colored(
                                f"[ Yandex ] Timed out waiting for page {pageNo} to load (skeleton).",
                                "yellow",
                            )
                        )
                else:
                    if verbose():
                        writerr(
                            colored(
                                f"[ Yandex ] Error waiting for skeleton to disappear: {e}",
                                "yellow",
                            )
                        )
                break  # exit loop

            # Check if bot detection is shown
            if "/showcaptcha" in page.url:
                if args.show_browser:
                    writerr(
                        colored(
                            f'[ Yandex ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...',
                            "yellow",
                        )
                    )
                    await wait_for_word_or_sleep("yandex", args.antibot_timeout)
                    writerr(colored("[ Yandex ] Resuming...", "green"))
                else:
                    writerr(
                        colored(
                            "[ Yandex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser",
                            "red",
                        )
                    )
                    return set(endpoints)

            # If still on Captcha page, then exit
            if "/showcaptcha" in page.url:
                writerr(colored("[ Yandex ] Failed to complete CAPTCHA", "red"))
                break

            if vverbose():
                writerr(
                    colored(
                        "[ Yandex ] Getting endpoints from page " + str(pageNo),
                        "green",
                        attrs=["dark"],
                    )
                )

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            new_endpoints = extractYandexEndpoints(soup)

            if not new_endpoints:
                # If no endpoints found on the new page, assume we are done.
                if verbose():
                    writerr(
                        colored(
                            f"[ Yandex ] No more results found on page {pageNo}.",
                            "yellow",
                        )
                    )
                break

            endpoints += new_endpoints

        # Close page/tab unless in debug mode
        if page and not args.debug:
            await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Yandex", page)
            writerr(
                colored(
                    f"[ Yandex ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Yandex ] Page timed out - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Yandex ] Search aborted - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        else:
            writerr(colored("[ Yandex ] ERROR getYandex1: " + str(e), "red"))
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("Yandex", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def getResultsEcosia(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        a_tags = soup.find_all("a", attrs={"data-test-id": "result-link"})
        for a in a_tags:
            href = a.get("href")
            if (
                href
                and href.startswith("http")
                and not re.match(r"^https?:\/\/([\w-]+\.)*ecosia\.[^\/\.]{2,}", href)
            ):
                endpoint = href.strip()
                endpoints.append(endpoint)
                # Send to forward proxy in background thread
                send_to_proxy(endpoint)
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR getResultsEcosia 1: " + str(e), "red"))
        return endpoints


async def getEcosia(context, dork, semaphore):
    global stopProgram
    source_context = None
    should_close_context = False
    try:
        endpoints = []
        page = None
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Ecosia ] Starting...", "green"))

        # Call with parameters:
        await page.goto(
            f"https://www.ecosia.org/search?q={dork}", timeout=args.timeout * 1000
        )

        # Check if bot detection is shown (e.g. Cloudflare Turnstile)
        is_bot_detected = False
        try:
            page_title = await page.title()
            page_content = await page.content()
            if (
                "Just a moment" in page_title
                or "cloudflare" in page.url.lower()
                or "unblock challenges.cloudflare.com" in page_content
            ):
                is_bot_detected = True
        except Exception:
            pass

        if is_bot_detected:
            if args.show_browser:
                writerr(
                    colored(
                        f'[ Ecosia ] Cloudflare challenge/CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "ecosia" and press ENTER...',
                        "yellow",
                    )
                )
                await wait_for_word_or_sleep("ecosia", args.antibot_timeout)
                writerr(colored("[ Ecosia ] Resuming...", "green"))
            else:
                writerr(
                    colored(
                        "[ Ecosia ] Cloudflare challenge/CAPTCHA needed responding to. Consider using option -sb / --show-browser",
                        "red",
                    )
                )
                return set(endpoints)

        pageNo = 1

        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
        except Exception as wait_e:
            if "Target page, context or browser has been closed" in str(wait_e):
                raise
            pass

        # Check if the cookie banner exists and click reject if it does
        if await page.query_selector("#didomi-notice-disagree-button"):
            # Click the button to reject
            await page.click("#didomi-notice-disagree-button")

        # Get the results so far, just in case it ends early
        endpoints = await getResultsEcosia(page, endpoints)

        async def click_Next():
            next_button = await page.query_selector('span:has-text("Next")')
            if next_button:
                await next_button.click()
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )

        # Loop to repeatedly check for the Next button and click it until it doesn't exist
        while await page.query_selector('span:has-text("Next")'):
            if stopProgram:
                break
            # await click_Next()
            if vverbose():
                pageNo += 1
                writerr(
                    colored(
                        '[ Ecosia ] Clicking "Next" button to display page '
                        + str(pageNo),
                        "green",
                        attrs=["dark"],
                    )
                )
            await click_Next()
            # Get the results so far, just in case it ends early
            endpoints = await getResultsEcosia(page, endpoints)

        # Get all the results
        endpoints = await getResultsEcosia(page, endpoints)
        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Ecosia", page)
            writerr(
                colored(
                    f"[ Ecosia ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Ecosia ] Page timed out - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Ecosia ] Search aborted - got {str(noOfEndpoints)} results",
                    "red",
                )
            )
        else:
            writerr(colored("[ Ecosia ] ERROR getEcosia 1: " + str(e), "red"))
            # Check if this looks like a proxy type error and show helpful hint
            if args.request_proxy and detect_proxy_type_error(
                args.request_proxy, str(e)
            ):
                show_proxy_usage_hint(args.request_proxy)
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents("Ecosia", page)
        return set(endpoints)
    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def getResultsBaidu(page, endpoints):
    global allSubs
    try:
        await page.wait_for_load_state("networkidle")

        # Wait until at least one feedback div exists
        try:
            await page.wait_for_selector("div.cosc-feedback", timeout=1000)
        except Exception:
            return endpoints

        # Query feedback divs fresh
        feedback_divs = await page.query_selector_all("div.cosc-feedback")

        for div in feedback_divs:
            hover_attempts = 0
            while hover_attempts < 5:
                try:
                    await div.hover()
                    await page.wait_for_timeout(200)
                    break
                except Exception:
                    hover_attempts += 1
                    await page.wait_for_timeout(200)
            else:
                pass

        # Collect all anchors that appeared after hovering
        a_tags = await page.query_selector_all('a[href*="tools?url="]')
        for a in a_tags:
            href = await a.get_attribute("href")
            if not href:
                continue
            if href.startswith("//"):
                href = "https:" + href

            parsed = urlparse(href)
            query_params = parse_qs(parsed.query)
            url_value = query_params.get("url")
            if not url_value:
                continue

            decoded_url = html.unescape(unquote(url_value[0]))
            endpoint = decoded_url.strip()
            endpoints.append(endpoint)
            # Send to forward proxy in background thread
            send_to_proxy(endpoint)

            if args.resubmit_without_subs:
                allSubs.add(getSubdomain(endpoint))

        return endpoints

    except Exception as e:
        writerr(colored("ERROR getResultsBaidu: " + str(e), "red"))
        return endpoints


async def getBaidu(context, dork, semaphore):
    global stopProgram
    source_context = None
    should_close_context = False
    page = None
    endpoints = []

    try:
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Baidu ] Starting...", "green"))

        # Go to search page
        try:
            await page.goto(
                f"https://www.baidu.com/s?ie=utf-8&ct=0&wd={dork}",
                timeout=args.timeout * 1000,
            )
        except Exception:
            pass

        # Wait for results to load
        try:
            await page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
        except Exception:
            pass

        # Check if bot detection captcha is displayed
        if "captcha" in page.url:
            if args.show_browser:
                writerr(
                    colored(
                        f'[ Baidu ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "baidu" and press ENTER...',
                        "yellow",
                    )
                )
                await wait_for_word_or_sleep("baidu", args.antibot_timeout)
                writerr(colored("[ Baidu ] Resuming...", "green"))
            else:
                writerr(
                    colored(
                        "[ Baidu ] CAPTCHA needed responding to. Consider using option -sb / --show-browser",
                        "red",
                    )
                )
                return set(endpoints)

        # Carry on if it doesn't say "抱歉，未找到相关结果" (Sorry, no relevant results were found)
        text = await page.text_content("body")
        if text and "抱歉，未找到相关结果" not in text:
            # Wait for a popup window to disappear
            time.sleep(5)

            pageNo = 1
            while True:
                if stopProgram:
                    break
                # Get results from current page
                endpoints = await getResultsBaidu(page, endpoints)

                # Find next page button
                next_button = await page.query_selector(
                    'a.n:has(span:has-text("下一页"))'
                )
                if not next_button or stopProgram:
                    break

                pageNo += 1

                # Check if bot detection captcha is displayed
                if "captcha" in page.url:
                    if args.show_browser:
                        writerr(
                            colored(
                                f'[ Baidu ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "baidu" and press ENTER...',
                                "yellow",
                            )
                        )
                        await wait_for_word_or_sleep("baidu", args.antibot_timeout)
                        writerr(colored("[ Baidu ] Resuming...", "green"))
                    else:
                        writerr(
                            colored(
                                "[ Baidu ] CAPTCHA needed responding to. Consider using option -sb / --show-browser",
                                "red",
                            )
                        )
                        return set(endpoints)

                # Remember old feedback div IDs
                old_feedback_divs = await page.query_selector_all("div.cosc-feedback")
                old_ids = [await div.get_attribute("id") for div in old_feedback_divs]

                # Click next
                if vverbose():
                    writerr(
                        colored(
                            f'[ Baidu ] Clicking "Next" button to display page {pageNo}',
                            "green",
                            attrs=["dark"],
                        )
                    )
                await next_button.scroll_into_view_if_needed()
                await next_button.click()

                # Wait for new feedback divs to appear (max ~4 seconds)
                for _ in range(20):
                    await page.wait_for_timeout(200)
                    try:
                        new_feedback_divs = await page.query_selector_all(
                            "div.cosc-feedback"
                        )
                        new_ids = [
                            await div.get_attribute("id") for div in new_feedback_divs
                        ]
                        if set(new_ids) != set(old_ids):
                            break
                    except Exception as e:
                        if "Execution context was destroyed" in str(e):
                            # Context destroyed (likely popup/navigation), wait a bit and retry
                            await page.wait_for_timeout(500)
                        else:
                            raise  # Re-raise if it's a different error

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Baidu", page)
            writerr(
                colored(
                    f"[ Baidu ] Complete! {str(noOfEndpoints)} endpoints found", "green"
                )
            )

        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Baidu ] Page timed out - got {noOfEndpoints} results", "red"
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Baidu ] Search aborted - got {noOfEndpoints} results", "red"
                )
            )
        else:
            writerr(colored("[ Baidu ] ERROR getBaidu: " + str(e), "red"))

        if args.debug and page is not None:
            await savePageContents("Baidu", page)

        return set(endpoints)

    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def getResultsSeznam(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        a_tags = soup.find_all("a", attrs={"tabindex": "0"})
        for a in a_tags:
            href = a.get("href")
            if (
                href
                and href.startswith("http")
                and not re.match(r"^https?:\/\/([\w-]+\.)*seznam\.[^\/\.]{2,}", href)
            ):
                endpoint = href.strip()
                endpoints.append(endpoint)
                # Send to forward proxy in background thread
                send_to_proxy(endpoint)
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR getResultsSeznam 1: " + str(e), "red"))
        return endpoints


async def getSeznam(context, dork, semaphore):
    global stopProgram
    source_context = None
    should_close_context = False
    page = None
    endpoints = []

    try:
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Seznam ] Starting...", "green"))

        # Go to search page
        await page.goto(
            f"https://search.seznam.cz/?q={dork}", timeout=args.timeout * 1000
        )

        pageNo = 1

        try:
            # Wait for search results to appear instead of networkidle
            # This is much faster than waiting for all network activity to stop
            await page.wait_for_selector('a[tabindex="0"]', timeout=args.timeout * 1000)
            # Add a small delay to ensure results are fully rendered
            await asyncio.sleep(0.5)
        except Exception as wait_e:
            if "Target page, context or browser has been closed" in str(wait_e):
                raise
            # If selector not found, try networkidle as fallback
            try:
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )
            except Exception:
                pass

        # Carry on if it doesn't say "Bohužel jsem nic nenašel" (Unfortunately I didn't find anything)
        text = await page.text_content("body")
        if text and "Bohužel jsem nic nenašel" not in text:

            if vverbose():
                writerr(
                    colored(
                        "[ Seznam ] Getting endpoints from page " + str(pageNo),
                        "green",
                        attrs=["dark"],
                    )
                )

            # Get the results so far, just in case it ends early
            endpoints = await getResultsSeznam(page, endpoints)

            # Main loop to keep navigating to next pages until there's no "Next page" link
            while True:
                if stopProgram:
                    break
                # Find the link with the title "Další strana" (Next page)
                if await page.query_selector('a[title="Další strana"]'):
                    await page.click('a[title="Další strana"]')
                    try:
                        # Wait for new results to appear instead of networkidle
                        await page.wait_for_selector(
                            'a[tabindex="0"]', timeout=args.timeout * 1000
                        )
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass

                    pageNo += 1
                    if vverbose():
                        writerr(
                            colored(
                                "[ Seznam ] Getting endpoints from page " + str(pageNo),
                                "green",
                                attrs=["dark"],
                            )
                        )

                    # Get all the results
                    endpoints = await getResultsSeznam(page, endpoints)
                else:
                    # No "Next page" link found, exit the loop
                    break

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Seznam", page)
            writerr(
                colored(
                    f"[ Seznam ] Complete! {str(noOfEndpoints)} endpoints found",
                    "green",
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(
                    f"[ Seznam ] Page timed out - got {noOfEndpoints} results", "red"
                )
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(
                    f"[ Seznam ] Search aborted - got {noOfEndpoints} results", "red"
                )
            )
        else:
            writerr(colored("[ Seznam ] ERROR getSeznam: " + str(e), "red"))

        if args.debug and page is not None:
            await savePageContents("Seznam", page)

        return set(endpoints)

    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def getResultsKagi(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        # Links are the href of <a> tags with specific classes
        a_tags = soup.find_all(
            "a", class_=lambda x: x and ("__sri_title_link" in x or "_0_URL" in x)
        )
        for a in a_tags:
            href = a.get("href")
            if (
                href
                and href.startswith("http")
                and not re.match(r"^https?:\/\/([\w-]+\.)*kagi\.[^\/\.]{2,}", href)
            ):
                endpoint = href.strip()
                if endpoint not in endpoints:
                    endpoints.append(endpoint)
                    # Send to forward proxy in background thread
                    send_to_proxy(endpoint)
                    # If the same search is going to be resubmitted without subs, get the subdomain
                    if args.resubmit_without_subs:
                        allSubs.add(getSubdomain(endpoint))
        return endpoints
    except Exception as e:
        writerr(colored("ERROR getResultsKagi 1: " + str(e), "red"))
        return endpoints


async def getKagi(context, dork, semaphore):
    global stopProgram, KAGI_SESSION_LINK
    source_context = None
    should_close_context = False
    page = None
    endpoints = []

    try:
        await semaphore.acquire()

        # Get context for this source (new context in windows mode, shared in tabs mode)
        source_context, should_close_context = await get_or_create_context(context)

        page = await source_context.new_page()
        await page.set_extra_http_headers({"User-Agent": DEFAULT_USER_AGENT})

        if verbose():
            writerr(colored("[ Kagi ] Starting...", "green"))

        base_url = KAGI_SESSION_LINK

        # Kagi search passes
        search_urls = [
            base_url,  # Default region
            base_url + "&r=no_region",  # No region
            base_url + "&verbatim=1",  # Verbatim
            base_url + "&r=no_region&verbatim=1",  # No region + Verbatim
            base_url + "&personalized=0",  # No personalized
            base_url + "&r=no_region&personalized=0",  # No region + No personalized
        ]

        for base_url in search_urls:
            if stopProgram:
                break

            if vverbose():
                params = []
                if "no_region" in base_url:
                    params.append("no_region")
                if "verbatim=1" in base_url:
                    params.append("verbatim")
                if "personalized=0" in base_url:
                    params.append("no_personalized")

                param_msg = " + ".join(params) if params else "default settings"
                writerr(
                    colored(
                        f"[ Kagi ] Performing search with {param_msg}...",
                        "green",
                        attrs=["dark"],
                    )
                )

            # Go to Kagi URL
            await page.goto(base_url, timeout=args.timeout * 1000)

            # Enter the dork into the field
            await page.fill("#searchBar", dork)
            # Press the search button
            await page.click("#searchFormSubmit")

            # Wait for results to load
            try:
                await page.wait_for_load_state(
                    "networkidle", timeout=args.timeout * 1000
                )
            except Exception:
                pass

            pageNo = 1
            max_pages = 50  # Safety limit to prevent infinite/long loops

            # Loop for "More Results" button until it no longer exists or is not visible
            while pageNo < max_pages:
                if stopProgram:
                    break

                more_results_button = await page.query_selector("#load_more_results")
                if more_results_button and await more_results_button.is_visible():
                    if vverbose():
                        writerr(
                            colored(
                                '[ Kagi ] Clicking "More Results" button to display page '
                                + str(pageNo + 1),
                                "green",
                                attrs=["dark"],
                            )
                        )

                    try:
                        await more_results_button.click()
                        # Use domcontentloaded + sleep as it's more robust than networkidle for some sites
                        await page.wait_for_load_state(
                            "domcontentloaded", timeout=args.timeout * 1000
                        )
                        await asyncio.sleep(1)  # Small pause for results to render
                        if vverbose():
                            writerr(
                                colored(
                                    f"[ Kagi ] Page {pageNo + 1} loaded",
                                    "green",
                                    attrs=["dark"],
                                )
                            )
                    except Exception as click_e:
                        if vverbose():
                            writerr(
                                colored(
                                    f"[ Kagi ] Error clicking more results: {str(click_e)}",
                                    "yellow",
                                )
                            )
                        break

                    pageNo += 1
                else:
                    break

            if pageNo >= max_pages and vverbose():
                writerr(colored("[ Kagi ] Maximum pagination limit reached", "yellow"))

            if vverbose():
                writerr(
                    colored(
                        "[ Kagi ] Getting endpoints from page", "green", attrs=["dark"]
                    )
                )

            # Get results after all "More Results" clicks for this pass
            endpoints = await getResultsKagi(page, endpoints)

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            if noOfEndpoints == 0 and args.debug and page is not None:
                await savePageContents("Kagi", page)
            writerr(
                colored(
                    f"[ Kagi ] Complete! {str(noOfEndpoints)} endpoints found", "green"
                )
            )
        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if "net::ERR_TIMED_OUT" in str(e) or "Timeout" in str(e):
            writerr(
                colored(f"[ Kagi ] Page timed out - got {noOfEndpoints} results", "red")
            )
        elif "net::ERR_ABORTED" in str(
            e
        ) or "Target page, context or browser has been closed" in str(e):
            writerr(
                colored(f"[ Kagi ] Search aborted - got {noOfEndpoints} results", "red")
            )
        else:
            writerr(colored("[ Kagi ] ERROR getKagi: " + str(e), "red"))

        if args.debug and page is not None:
            await savePageContents("Kagi", page)

        return set(endpoints)

    finally:
        try:
            # Close page/tab unless in debug mode
            if page and not args.debug:
                await page.close()
            # Close context (window) in windows mode unless in debug mode
            if should_close_context and source_context and not args.debug:
                await source_context.close()
            semaphore.release()
        except Exception:
            pass


async def savePageContents(source, page):
    try:
        # Press the "Escape" key to stop page loading
        await page.keyboard.press("Escape")

        # Wait for a short duration to ensure the page loading is stopped
        await asyncio.sleep(2)

        # Get the page contents and save to file
        content = await page.content()
        if content != "" and content != "<html><head></head><body></body></html>":
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d-%H%M%S")
            filename = f"xnldorker_{source}_{timestamp}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)
            writerr(colored(f"[ {source} ] Saved HTML content to {filename}", "cyan"))
    except Exception as e:
        writerr(colored(f"[ {source} ] Unable to save page contents: {str(e)}", "cyan"))


async def processInput(dork):
    global browser, sourcesToProcess, duckduckgoEndpoints, duckgoliteEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, googlecsEndpoints, yandexEndpoints, ecosiaEndpoints, baiduEndpoints, seznamEndpoints, kagiEndpoints, stopProgram, proxy_sent_endpoints
    try:
        # Start proxy forwarding thread if needed
        start_proxy_thread()

        # Create a single browser instance
        async with async_playwright() as p:
            # Configure request proxy if provided
            proxy_config = None
            context_options = {}
            if args.request_proxy:
                proxy_config = {"server": args.request_proxy}
                context_options["ignore_https_errors"] = True
                if verbose():
                    writerr(
                        colored(
                            f"[ Request Proxy] Using browser request proxy: {args.request_proxy}",
                            "cyan",
                        )
                    )

            # Launch with additional args to avoid bot detection
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
            if args.show_browser:
                browser = await p.chromium.launch(
                    headless=False, proxy=proxy_config, args=browser_args
                )
            else:
                browser = await p.chromium.launch(
                    headless=True, proxy=proxy_config, args=browser_args
                )

            # For "windows" mode, each source will create its own context
            # For "tabs" mode or headless, use a single shared context
            if args.show_browser == "windows":
                # Don't create context yet - each source will create its own
                context = None
            else:
                # Create a shared context with viewport and ignore HTTPS errors if using proxy
                context_options["viewport"] = {"width": 1280, "height": 720}
                context_options["user_agent"] = DEFAULT_USER_AGENT
                # Add extra headers to avoid bot detection
                context_options["extra_http_headers"] = {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
                context = await browser.new_context(**context_options)
                # Inject script to hide webdriver property and other automation indicators
                await context.add_init_script(
                    """
                    // Hide webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Override the plugins to make it non-empty
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Override languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    // Chrome runtime
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """
                )

            # Define a dictionary to hold the results for each source
            resultsDict = {}

            # Define a semaphore to limit concurrent tasks. This is determined by the -cs / --concurrent-sources argument
            concurrentSources = args.concurrent_sources
            if concurrentSources == 0 or concurrentSources > len(sourcesToProcess):
                concurrentSources = len(sourcesToProcess)
            semaphore = asyncio.Semaphore(concurrentSources)

            # Define a list to hold the sources included in the gather call
            includedSources = []

            # Map source names to their coroutine functions
            source_map = {
                "duckduckgo": getDuckDuckGo,
                "duckgolite": getDuckGoLite,
                "bing": getBing,
                "startpage": getStartpage,
                "yahoo": getYahoo,
                "google": getGoogle,
                "yandex": getYandex,
                "ecosia": getEcosia,
                "baidu": getBaidu,
                "seznam": getSeznam,
                "kagi": getKagi,
                "googlecs": getGoogleCS,
            }

            # Add coroutines for requested sources in the order they appear in sourcesToProcess
            for source in sourcesToProcess:
                if source in source_map:
                    includedSources.append(source_map[source](context, dork, semaphore))

            # Run all searches concurrently using the same browser instance
            results = await asyncio.gather(*includedSources)

            # Populate the results dictionary and endpoint lists
            for source, result in zip(sourcesToProcess, results):
                if result is None:
                    result = set()

                if (
                    source not in resultsDict
                ):  # Check if the source is not already in the resultsDict
                    resultsDict[source] = result  # If not, add it
                else:
                    # If the source is already in the resultsDict, append new data to existing data
                    resultsDict[source].update(result)

                # Update the endpoint lists as well
                if source == "duckduckgo":
                    duckduckgoEndpoints.update(result)
                elif source == "duckgolite":
                    duckgoliteEndpoints.update(result)
                elif source == "bing":
                    bingEndpoints.update(result)
                elif source == "startpage":
                    startpageEndpoints.update(result)
                elif source == "yahoo":
                    yahooEndpoints.update(result)
                elif source == "google":
                    googleEndpoints.update(result)
                elif source == "yandex":
                    yandexEndpoints.update(result)
                elif source == "ecosia":
                    ecosiaEndpoints.update(result)
                elif source == "baidu":
                    baiduEndpoints.update(result)
                elif source == "seznam":
                    seznamEndpoints.update(result)
                elif source == "kagi":
                    kagiEndpoints.update(result)
                elif source == "googlecs":
                    googlecsEndpoints.update(result)

            # If debug mode and showing browser, wait for user to press ENTER before closing
            if args.debug and args.show_browser:
                try:
                    writerr(colored("DEBUG: PRESS ENTER TO FINISH", "yellow"))
                    input()
                except Exception:
                    pass

            # Close the browser instance once all searches are done
            try:
                await browser.close()
            except Exception:
                pass

    except Exception as e:
        writerr(colored("ERROR processInput 1: " + str(e), "red"))
    finally:
        try:
            if "context" in locals():
                await context.close()
            await browser.close()
        except Exception:
            pass


async def processOutput():
    global duckduckgoEndpoints, duckgoliteEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, googlecsEndpoints, yandexEndpoints, ecosiaEndpoints, baiduEndpoints, seznamEndpoints, kagiEndpoints, sourcesToProcess
    try:
        allEndpoints = set()

        # If --output-sources was passed, then keep the source in the endpoint, otherwise we need a unique set without source
        if args.output_sources:
            if duckduckgoEndpoints:
                allEndpoints.update(
                    f"[ DuckDuckGo ] {endpoint}" for endpoint in duckduckgoEndpoints
                )
            if duckgoliteEndpoints:
                allEndpoints.update(
                    f"[ DuckGoLite ] {endpoint}" for endpoint in duckgoliteEndpoints
                )
            if bingEndpoints:
                allEndpoints.update(
                    f"[ Bing ] {endpoint}" for endpoint in bingEndpoints
                )
            if startpageEndpoints:
                allEndpoints.update(
                    f"[ StartPage ] {endpoint}" for endpoint in startpageEndpoints
                )
            if yahooEndpoints:
                allEndpoints.update(
                    f"[ Yahoo ] {endpoint}" for endpoint in yahooEndpoints
                )
            if googleEndpoints:
                allEndpoints.update(
                    f"[ Google ] {endpoint}" for endpoint in googleEndpoints
                )
            if yandexEndpoints:
                allEndpoints.update(
                    f"[ Yandex ] {endpoint}" for endpoint in yandexEndpoints
                )
            if ecosiaEndpoints:
                allEndpoints.update(
                    f"[ Ecosia ] {endpoint}" for endpoint in ecosiaEndpoints
                )
            if baiduEndpoints:
                allEndpoints.update(
                    f"[ Baidu ] {endpoint}" for endpoint in baiduEndpoints
                )
            if seznamEndpoints:
                allEndpoints.update(
                    f"[ Seznam ] {endpoint}" for endpoint in seznamEndpoints
                )
            if kagiEndpoints:
                allEndpoints.update(
                    f"[ Kagi ] {endpoint}" for endpoint in kagiEndpoints
                )
            if googlecsEndpoints:
                allEndpoints.update(
                    f"[ GoogleCS ] {endpoint}" for endpoint in googlecsEndpoints
                )
        else:
            if duckduckgoEndpoints:
                allEndpoints |= duckduckgoEndpoints
            if duckgoliteEndpoints:
                allEndpoints |= duckgoliteEndpoints
            if bingEndpoints:
                allEndpoints |= bingEndpoints
            if startpageEndpoints:
                allEndpoints |= startpageEndpoints
            if yahooEndpoints:
                allEndpoints |= yahooEndpoints
            if googleEndpoints:
                allEndpoints |= googleEndpoints
            if yandexEndpoints:
                allEndpoints |= yandexEndpoints
            if ecosiaEndpoints:
                allEndpoints |= ecosiaEndpoints
            if baiduEndpoints:
                allEndpoints |= baiduEndpoints
            if seznamEndpoints:
                allEndpoints |= seznamEndpoints
            if kagiEndpoints:
                allEndpoints |= kagiEndpoints
            if googlecsEndpoints:
                allEndpoints |= googlecsEndpoints

        if verbose() and sys.stdin.isatty():
            writerr(
                colored(
                    "\nTotal endpoints found: " + str(len(allEndpoints)) + " 🤘  ",
                    "cyan",
                )
                + str(sourcesToProcess)
            )

        # If the -ow / --output_overwrite argument was passed and the file exists already, get the contents of the file to include
        appendedResults = False
        if args.output and not args.output_overwrite:
            try:
                existingEndpoints = open(os.path.expanduser(args.output), "r")
                appendedResults = True
                for endpoint in existingEndpoints.readlines():
                    allEndpoints.add(endpoint.strip())
            except Exception:
                pass

        # If an output file was specified, open it
        if args.output is not None:
            try:
                # If the filename has any "/" in it, remove the contents after the last one to just get the path and create the directories if necessary
                try:
                    f = os.path.basename(args.output)
                    p = args.output[: -(len(f)) - 1]
                    if p != "" and not os.path.exists(p):
                        os.makedirs(p)
                except Exception as e:
                    if verbose():
                        writerr(colored("ERROR processOutput 5: " + str(e), "red"))
                outFile = open(os.path.expanduser(args.output), "w")
            except Exception as e:
                if vverbose():
                    writerr(colored("ERROR processOutput 2: " + str(e), "red"))

        # Output all endpoints
        for endpoint in allEndpoints:
            try:
                # If an output file was specified, write to the file
                if args.output is not None:
                    outFile.write(endpoint + "\n")
                else:
                    # If output is piped or the --output argument was not specified, output to STDOUT
                    if not sys.stdin.isatty() or args.output is None:
                        write(endpoint, True)
            except Exception as e:
                writerr(
                    colored(
                        "ERROR processOutput 6: Could not output links found - "
                        + str(e),
                        "red",
                    )
                )

        # Close the output file if it was opened
        try:
            if args.output is not None:
                if appendedResults:
                    write(
                        colored("Output successfully appended to file: ", "cyan")
                        + colored(args.output, "white")
                    )
                else:
                    write(
                        colored("Output successfully written to file: ", "cyan")
                        + colored(args.output, "white")
                    )
                write()
                outFile.close()
        except Exception as e:
            writerr(colored("ERROR processOutput 3: " + str(e), "red"))

        # Clear the endpoint sets so they don't get processed again if there are multiple dorks
        duckduckgoEndpoints.clear()
        duckgoliteEndpoints.clear()
        bingEndpoints.clear()
        startpageEndpoints.clear()
        yahooEndpoints.clear()
        googleEndpoints.clear()
        googlecsEndpoints.clear()
        yandexEndpoints.clear()
        ecosiaEndpoints.clear()
        baiduEndpoints.clear()
        seznamEndpoints.clear()
        kagiEndpoints.clear()

    except Exception as e:
        writerr(colored("ERROR processOutput 1: " + str(e), "red"))


def showOptionsAndConfig():
    global sourcesToProcess, inputDork, KAGI_SESSION_LINK, GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CHAT_ID
    try:
        write(colored("Selected options:", "cyan"))
        if os.path.isfile(os.path.expanduser(args.input)):
            write(
                colored("-i: " + args.input, "magenta")
                + colored(" The file of dorks used to search on the sources.", "white")
            )
        else:
            write(
                colored("-i: " + inputDork, "magenta")
                + colored(" The dork used to search on the sources.", "white")
            )
        if args.output is not None:
            write(
                colored("-o: " + args.output, "magenta")
                + colored(" Where gathered endpoints will be written.", "white")
            )
        else:
            write(
                colored("-o: <STDOUT>", "magenta")
                + colored(
                    " An output file wasn't given, so output will be written to STDOUT.",
                    "white",
                )
            )
        write(
            colored("-ow: " + str(args.output_overwrite), "magenta")
            + colored(
                " Whether the output will be overwritten if it already exists.", "white"
            )
        )
        if args.sources:
            write(
                colored("-s: " + args.sources, "magenta")
                + colored(" The sources requested to search.", "white")
            )
        if args.exclude_sources:
            write(
                colored("-es: " + args.exclude_sources, "magenta")
                + colored(" The sources excluded from the search.", "white")
            )
        if args.concurrent_sources == 0:
            write(
                colored("-cs: ALL", "magenta")
                + colored(" The browser timeout in seconds", "white")
            )
        else:
            write(
                colored("-cs: " + str(args.concurrent_sources), "magenta")
                + colored(
                    " The number of concurrent sources that will be searched at a time.",
                    "white",
                )
            )
        write(
            colored("-t: " + str(args.timeout), "magenta")
            + colored(" The browser timeout in seconds", "white")
        )
        write(
            colored("-sb: " + str(args.show_browser), "magenta")
            + colored(
                " Whether the browser will be shown. If False, then headless mode is used.",
                "white",
            )
        )
        write(
            colored("-rwos: " + str(args.resubmit_without_subs), "magenta")
            + colored(
                " Whether the query will be resubmitted, but excluding the sub domains found in the first search.",
                "white",
            )
        )
        if args.forward_proxy:
            write(
                colored("-fp: " + str(args.forward_proxy), "magenta")
                + colored(" The proxy to send found links to.", "white")
            )
        if args.request_proxy:
            write(
                colored("-rp: " + str(args.request_proxy), "magenta")
                + colored(
                    " The browser request proxy being used for searches.", "white"
                )
            )
        write(
            colored("-abt: " + str(args.antibot_timeout), "magenta")
            + colored(
                " The number of seconds you have to manually respond to the anti-bot mechanism before it tries to continue.",
                "white",
            )
        )
        if "kagi" in sourcesToProcess:
            if KAGI_SESSION_LINK == "":
                writerr(
                    colored("Kagi Session Link: ", "magenta")
                    + colored(
                        "No Kagi Session Link found in config.yml - skipping Kagi",
                        "red",
                    )
                )
                sourcesToProcess.remove("kagi")
            else:
                write(
                    colored("Kagi Session Link: ", "magenta")
                    + colored(str(KAGI_SESSION_LINK), "white")
                )
        if "googlecs" in sourcesToProcess:
            if GOOGLE_SEARCH_API_KEY == "" or GOOGLE_SEARCH_CHAT_ID == "":
                writerr(
                    colored("KGoogle Custom Search: ", "magenta")
                    + colored(
                        "Google Custom Search API Key and Chat ID not found in config.yml - skipping GoogleCS",
                        "red",
                    )
                )
                sourcesToProcess.remove("googlecs")
            else:
                write(
                    colored("Google Custom Search API Key: ", "magenta")
                    + colored(str(GOOGLE_SEARCH_API_KEY), "white")
                )
                write(
                    colored("Google Custom Search Chat ID: ", "magenta")
                    + colored(str(GOOGLE_SEARCH_CHAT_ID), "white")
                )
        write(
            colored("Sources being checked: ", "magenta")
            + colored(str(sourcesToProcess), "white")
        )
        write("")

    except Exception as e:
        writerr(colored("ERROR showOptionsAndConfig 1: " + str(e), "red"))


# For validating arguments -s and -es
def argcheckSources(value):
    # Split the value by commas to get individual sources
    sources = value.split(",")

    # Check if all sources are valid and exist in SOURCES
    if not all(source.strip() in SOURCES for source in sources):
        raise argparse.ArgumentTypeError(
            f"Invalid sources requested. Can only be a combination of {','.join(SOURCES)}"
        )
    return value


async def run_main():

    global args, sourcesToProcess, allSubs, inputDork

    # Tell Python to run the handler() function when SIGINT is received
    signal(SIGINT, handler)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="xnldorker - by @Xnl-h4ck3r: Gather results of dorks across a number of search engines."
    )
    parser.add_argument(
        "-i", "--input", action="store", help="A dork to use on the search sources."
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="The output file that will contain the results (default: output.txt). If piped to another program, output will be written to STDOUT instead.",
    )
    parser.add_argument(
        "-ow",
        "--output-overwrite",
        action="store_true",
        help="If the output file already exists, it will be overwritten instead of being appended to.",
    )
    parser.add_argument(
        "-os",
        "--output-sources",
        action="store_true",
        help='Show the source of each endpoint in the output. Each endpoint will be prefixed, e.g. "[ Bing ] https://example.com".',
    )
    parser.add_argument(
        "-s",
        "--sources",
        action="store",
        help="Specific sources to use when searching (-s duckduckgo,bing). Use -ls to display all available sources.",
        type=argcheckSources,
        metavar="string[]",
    )
    parser.add_argument(
        "-es",
        "--exclude-sources",
        action="store",
        help="Specific sources to exclude searching (-s google,startpage). Use -ls to display all available sources.",
        type=argcheckSources,
        metavar="string[]",
    )
    parser.add_argument(
        "-cs",
        "--concurrent-sources",
        action="store",
        help="The number of sources to search at the same time (default: 2). Passing 0 will run ALL specified sources at the same time (this could be very resource intensive and affect results).",
        type=int,
        default=2,
    )
    parser.add_argument(
        "-ls",
        "--list-sources",
        action="store_true",
        help="List all available sources.",
    )
    default_timeout = 30
    parser.add_argument(
        "-t",
        "--timeout",
        help="How many seconds to wait for the source to respond (default: "
        + str(default_timeout)
        + " seconds).",
        default=default_timeout,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        "-sb",
        "--show-browser",
        nargs="?",
        const="tabs",
        default=False,
        choices=["tabs", "windows"],
        help='View the browser instead of using headless browser. Options: "tabs" (default, opens sources in tabs) or "windows" (opens each source in a separate window).',
    )
    default_abt = 90
    parser.add_argument(
        "-abt",
        "--antibot-timeout",
        help="How many seconds to wait when the -sb option was used and a known anti-bot mechanism is encountered (default "
        + str(default_abt)
        + "). This is the time you have to manually respond to the anti-bot mechanism before it tries to continue.",
        default=default_abt,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        "-rwos",
        "--resubmit-without-subs",
        action="store_true",
        help="After the initial search, search again but exclude all subs found previously to get more links.",
    )
    parser.add_argument(
        "-fp",
        "--forward-proxy",
        action="store",
        help="Send the links found to a proxy such as Burp or Caido, e.g http://127.0.0.1:8080",
        default="",
    )
    parser.add_argument(
        "-rp",
        "--request-proxy",
        action="store",
        help="Browser request proxy to use. Can be a proxy string (e.g. http://user:pass@1.2.3.4:8000, socks5://host:port) or a file containing proxy list (one per line, random selection)",
        default="",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save page contents on error and leave all browser tabs/windows open until pressing Enter to end the program.",
    )
    parser.add_argument(
        "-nb", "--no-banner", action="store_true", help="Hides the tool banner."
    )
    parser.add_argument("--version", action="store_true", help="Show version number")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output.")
    parser.add_argument(
        "-vv", "--vverbose", action="store_true", help="Increased verbose output."
    )
    args = parser.parse_args()

    # If --version was passed, display version and exit
    if args.version:
        write(colored("xnldorker - v" + __version__, "cyan"))
        sys.exit()

    # If --list-sources was passed, display sources and exit
    if args.list_sources:
        if not args.no_banner:
            showBanner()
        write(colored("These are the available sources: ", "green") + str(SOURCES))
        sys.exit()

    # Get the config settings from the config.yml file
    getConfig()

    try:
        # If no input was given, raise an error
        if sys.stdin.isatty():
            if args.input is None:
                writerr(
                    colored(
                        'You need to provide input with -i argument or through <stdin>. This will be a dork used to search the requested sources, e.g. "site:example.com"',
                        "red",
                    )
                )
                sys.exit()

        # Determine the sources to process
        if args.sources is None:
            sourcesToProcess = SOURCES
        else:
            sourcesToProcess = args.sources.split(",")
        if args.exclude_sources is not None:
            sourcesToProcess = [
                source
                for source in sourcesToProcess
                if source not in args.exclude_sources
            ]

        # Get the input dork, depending on the input type
        dorks = []
        if sys.stdin.isatty():
            if os.path.isfile(os.path.expanduser(args.input)):
                with open(os.path.expanduser(args.input), "r") as f:
                    dorks = [line.strip() for line in f]
            else:
                dorks.append(args.input)
        else:
            dorks = [line.strip() for line in sys.stdin if line.strip()]

        firstDork = True
        for dork in dorks:
            inputDork = dork
            allSubs.clear()
            # If the input value doesn't seem to start with an advanced search operator and has no spaces, assume it is a domain only and prefix with "site:"
            if (
                not re.match(r"(^|\s)[a-z]*:", inputDork, re.IGNORECASE)
                and " " not in inputDork
            ):
                inputDork = "site:" + inputDork

            # Only for first dork...
            # If input is not piped, show the banner, and if --verbose option was chosen show options and config values
            if firstDork and sys.stdin.isatty():
                firstDork = False
                # Show banner unless requested to hide
                if not args.no_banner:
                    showBanner()
                if verbose():
                    showOptionsAndConfig()
                # Handle request proxy selection (file vs direct proxy)
                if args.request_proxy:
                    selected_proxy = selectRequestProxy(args.request_proxy)
                    if selected_proxy:
                        args.request_proxy = selected_proxy

                        # Check if this looks like an intercepting proxy and warn user
                        common_intercept_ports = [
                            "8080",
                            "8081",
                            "8082",
                            "9090",
                            "3128",
                        ]
                        proxy_port = None
                        if ":" in args.request_proxy:
                            try:
                                proxy_port = args.request_proxy.split(":")[-1]
                            except Exception:
                                pass

                        if proxy_port in common_intercept_ports:
                            writerr(
                                colored(
                                    "⚠️  WARNING: You're using --request-proxy with what appears to be an intercepting proxy port.",
                                    "yellow",
                                )
                            )
                            writerr(
                                colored(
                                    "   This routes ALL browser traffic through the proxy.",
                                    "white",
                                )
                            )
                            writerr(
                                colored(
                                    "   If you want to send discovered endpoints to the proxy instead, use:",
                                    "white",
                                )
                            )
                            writerr(
                                colored(
                                    f"   --forward-proxy {args.request_proxy}", "cyan"
                                )
                            )
                            writerr("")
                    else:
                        writerr(
                            colored(
                                "ERROR: Failed to select request proxy, continuing without proxy",
                                "red",
                            )
                        )
                        args.request_proxy = ""

            # Process the input given on -i (--input), or <stdin>
            write(colored("Processing dork: ", "cyan") + colored(inputDork, "white"))
            await processInput(inputDork)

            # If there were some subs found, and the --resubmit-without-subs was passed, then run again with subdomains removed
            if len(allSubs) > 0 and args.resubmit_without_subs:
                inputDork = (
                    inputDork
                    + " "
                    + " ".join(["-{}".format(sub) for sub in allSubs if sub])
                )
                write(
                    colored("\nResubmitting again for input: ", "magenta")
                    + colored(inputDork, "white")
                )
                await processInput(inputDork)

            # Output the saved urls with parameters
            await processOutput()

            # If output overwrite was passed, then it should only overwrite for the first line of the file, not subsequent ones
            if args.output_overwrite:
                args.output_overwrite = False

    except Exception as e:
        writerr(colored("ERROR main 1: " + str(e), "red"))
    finally:
        # Stop proxy forwarding thread
        stop_proxy_thread()

    # Show ko-fi link if verbose and not piped
    try:
        if verbose() and sys.stdin.isatty():
            writerr(
                colored(
                    "✅ Want to buy me a coffee? ☕ https://ko-fi.com/xnlh4ck3r 🤘",
                    "green",
                )
            )
    except Exception:
        pass


def main():
    asyncio.run(run_main())


if __name__ == "__main__":
    main()
