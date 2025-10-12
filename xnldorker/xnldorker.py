#!/usr/bin/env python
# Python 3
# xnldorker - by @Xnl-h4ck3r: Gather results of dorks across a number of search engines
# Full help here: https://github.com/xnl-h4ck3r/xnldorker/blob/main/README.md
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

from ast import arg
import requests
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
try:
    from . import __version__
except:
    pass

# Available sources to search
SOURCES = ['duckduckgo','bing','startpage','yahoo', 'google', 'yandex', 'ecosia', 'baidu', 'seznam']

DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'

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
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko"
]

# Global variables
args = None
browser = None
stopProgram = False
stopProgramCount = 0
inputDork = ''
duckduckgoEndpoints = set()
bingEndpoints = set()
yahooEndpoints = set()
googleEndpoints = set()
startpageEndpoints = set()
yandexEndpoints = set()
ecosiaEndpoints = set()
baiduEndpoints = set()
seznamEndpoints = set()
allSubs = set()
sourcesToProcess = []

# Functions used when printing messages dependant on verbose options
def verbose():
    return args.verbose or args.vverbose
def vverbose():
    return args.vverbose

def write(text='',pipe=False):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or if the tool has been piped and the pipe parameter is True
    if sys.stdout.isatty() or (not sys.stdout.isatty() and pipe):
        sys.stdout.write(text+'\n')

def writerr(text=''):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or If the tool has been piped to output the send to stderr
    if sys.stdout.isatty():
        sys.stdout.write(text+'\n')
    else:
        sys.stderr.write(text+'\n')

def showVersion():
    try:
        try:
            resp = requests.get('https://raw.githubusercontent.com/xnl-h4ck3r/xnldorker/main/xnldorker/__init__.py',timeout=3)
        except:
            write('Current xnldorker version '+__version__+' (unable to check if latest)\n')
        if __version__ == resp.text.split('=')[1].replace('"','').strip():
            write('Current xnldorker version '+__version__+' ('+colored('latest','green')+')\n')
        else:
            write('Current xnldorker version '+__version__+' ('+colored('outdated','red')+')\n')
    except:
        pass
      
def showBanner():
    writerr('')
    writerr(colored(r'            _     _            _', 'red'))
    writerr(colored(r'__  ___ __ | | __| | ___  _ __| | _____ _ __', 'yellow'))
    writerr(colored(r"\ \/ / '_ \| |/ _` |/ _ \| '__| |/ / _ \ '__|", 'green'))
    writerr(colored(r' >  <| | | | | (_| | (_) | |  |   <  __/ |', 'cyan'))
    writerr(colored(r'/_/\_\_| |_|_|\__,_|\___/|_|  |_|\_\___|_|', 'magenta'))
    writerr(colored('                             by Xnl-h4ck3r','white'))
    writerr('')
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
            writerr(colored('>>> Please be patient... Trying to save data and end gracefully!','red'))
        elif stopProgramCount == 2:
            writerr(colored('>>> SERIOUSLY... YOU DON\'T WANT YOUR DATA SAVED?!','red'))
        elif stopProgramCount == 3:
            writerr(colored('>>> Patience isn\'t your strong suit eh? ¯\_(ツ)_/¯','red'))
            sys.exit()
    else:
        stopProgram = True
        writerr(colored('>>> "Oh my God, they killed Kenny... and xnldorker!" - Kyle',"red"))
        writerr(colored('>>> Attempting to rescue any data gathered so far...', "red"))

def getSubdomain(url):
    try:
        # Just get the hostname of the url 
        tldExtract = tldextract.extract(url)
        return tldExtract.subdomain
    except Exception as e:
        writerr(colored('ERROR getSubdomain 1: ' + str(e), 'red')) 

async def wait_for_word_or_sleep(word, timeout):
    """
    Called when an antibot screen is detected on a source. It will resume again when the timeout is reached, or if the passed word is typed and ENTER pressed
    """
    loop = asyncio.get_event_loop()
    word_entered = asyncio.Event()

    def on_input_received():
        input_text = sys.stdin.readline().strip()
        if input_text == word:
            word_entered.set()

    loop.add_reader(sys.stdin.fileno(), on_input_received)

    try:
        await asyncio.wait_for(word_entered.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass  # Timeout reached, continue with the script
    finally:
        loop.remove_reader(sys.stdin.fileno())
              
async def getResultsDuckDuckGo(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        div_content = soup.find('div', id='web_content_wrapper')
        if div_content:
            a_tags = div_content.find_all('a')
            for a in a_tags:
                href = a.get('href')
                if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*duckduckgo\.[^\/\.]{2,}', href):
                    endpoints.append(href.strip())
                    # If the same search is going to be resubmitted without subs, get the subdomain
                    if args.resubmit_without_subs:
                        allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR getResultsDuckDuckGo 1: ' + str(e), 'red')) 
        
async def getDuckDuckGo(browser, dork, semaphore):
    global stopProgram
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ DuckDuckGo ] Starting...', 'green'))
        
        # Call with parameters:
        #  kc=-1 - Don't auto load images
        await page.goto(f'https://duckduckgo.com/?kc=-1&ia=web&q={dork}', timeout=args.timeout*1000)
        pageNo = 1
        
        # If captcha is shown then allow time to submit it
        captcha = await page.query_selector('#anomaly-modal__modal.anomaly-modal__modal')
        if captcha:
            if args.show_browser:
                writerr(colored(f'[ DuckDuckGo ] reCAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "duckduckgo" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("duckduckgo", args.antibot_timeout)
                writerr(colored(f'[ DuckDuckGo ] Resuming...', 'green'))
            else:
                writerr(colored('[ DuckDuckGo ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)
        
        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass

        captcha = await page.query_selector('#anomaly-modal__modal.anomaly-modal__modal')
        if captcha:
            writerr(colored('[ DuckDuckGo ] Failed to complete reCAPTCHA','red'))
            return set(endpoints)
               
        # Function to check if the button is disabled and enable it if necessary
        async def enable_more_results():
            more_results_button = await page.query_selector('#more-results')
            if more_results_button:
                is_disabled = await more_results_button.evaluate('(element) => element.disabled')
                if is_disabled:
                    await page.evaluate('(element) => element.disabled = false', more_results_button)

        # Function to check for the presence of the button and click it if available
        async def click_more_results():
            if await page.query_selector('#more-results'):
                await page.click('#more-results')
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)

        # Loop to repeatedly check for the button and click it until it doesn't exist
        while await page.query_selector('#more-results'):
            if stopProgram:
                break
            await enable_more_results()
            if vverbose():
                pageNo += 1
                writerr(colored('[ DuckDuckGo ] Clicking "More Results" button to display page '+str(pageNo), 'green', attrs=['dark'])) 
            await click_more_results()
            # Get the results so far, just in case it ends early
            endpoints =  await getResultsDuckDuckGo(page, endpoints)

        # Get all the results
        endpoints = await getResultsDuckDuckGo(page, endpoints)
        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ DuckDuckGo ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
     
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ DuckDuckGo ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ DuckDuckGo ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ DuckDuckGo ] ERROR getDuckDuckGo 1: ' + str(e), 'red'))  
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('DuckDuckGo',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
def extractBingEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        div_content = soup.find('div', id='b_content')
        if div_content:
            a_tags = div_content.find_all('a')
            for a in a_tags:
                href = a.get('href')
                recommendations = a.find_parent('div', class_='pageRecoContainer')
                if href and href.startswith('http') and not recommendations and not re.match(r'^https?:\/\/([\w-]+\.)*bing\.[^\/\.]{2,}', href) and not re.match(r'^https?:\/\/go\.microsoft\.com', href):
                    endpoints.append(href.strip())
                    # If the same search is going to be resubmitted without subs, get the subdomain
                    if args.resubmit_without_subs:
                        allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR extractBingEndpoints 1: ' + str(e), 'red')) 
        
async def getBing(browser, dork, semaphore):
    try:
        endpoints = [] 
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Bing ] Starting...', 'green'))
            
        await page.goto(f'https://www.bing.com/search?q={dork}', timeout=args.timeout*1000)

        # If captcha is shown then allow time to submit it
        content = await page.content()
        if "One last step" in content:
            if args.show_browser:
                writerr(colored(f'[ Bing ] Cloudflare Captcha needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "bing" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("bing", args.antibot_timeout)
                writerr(colored(f'[ Bing ] Resuming...', 'green'))
            else:
                writerr(colored('[ Bing ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)
            
        # Check if the cookie banner exists and click reject if it does
        if await page.query_selector('#bnp_btn_reject'):
            # Click the button to reject
            await page.click('#bnp_btn_reject')
            
        # Collect endpoints from the initial page
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        pageNo = 1
        endpoints = extractBingEndpoints(soup)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        while True:
            if stopProgram:
                break
            # Find the link with the title "Next page"
            if await page.query_selector('a[title="Next page"]'):
                await page.click('a[title="Next page"]')
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
                pageNo += 1
                if vverbose():
                    writerr(colored('[ Bing ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
                
                # Collect endpoints from the current page
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                endpoints += extractBingEndpoints(soup)
            else:
                # No "Next page" link found, exit the loop
                break

        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Bing ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Bing ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Bing ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Bing ] ERROR getBing 1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Bing',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
def extractStartpageEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        result_links = soup.find_all('a', class_=re.compile('.*result-link.*'))
        for link in result_links:
            href = link.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*startpage\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR extractStartpageEndpoints 1: ' + str(e), 'red')) 
        
async def getStartpage(browser, dork, semaphore):
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Startpage ] Starting...', 'green'))
            
        await page.goto(f'https://www.startpage.com/', timeout=args.timeout*1000)
        
        # Wait for the search results to be fully loaded
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        
        # Check if bot detection is shown
        if '/sp/captcha' in page.url:
            if args.show_browser:
                writerr(colored(f'[ Startpage ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "startpage" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("startpage", args.antibot_timeout)
                writerr(colored(f'[ Startpage ] Resuming...', 'green'))
            else:
                writerr(colored('[ Startpage ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)

        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass

        # Check if bot detection is still shown
        if '/sp/captcha' in page.url:
            writerr(colored('[ Startpage ] Failed to complete CAPTCHA','red'))
            return set(endpoints)
        
        await page.fill('input[title="Search"]', dork)
        await page.click('button.search-btn')
        
        # Wait for the search results to be fully loaded
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        
        # Check if any '.result-link' exists
        try:
            await page.wait_for_selector('.result-link', timeout=1000)  # Short timeout to check existence
        except:
            if verbose():
                writerr(colored('[ Startpage ] Complete! - 0 endpoints found', 'green')) 
            await page.close()
            return set() 
        
        # Collect endpoints from the initial page
        if vverbose():
            writerr(colored('[ Startpage ] Getting endpoints from page 1', 'green', attrs=['dark'])) 
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        pageNo = 1
        endpoints = extractStartpageEndpoints(soup)

        # Loop until there is no submit button in the last form with action="/sp/search"
        while True:
            if stopProgram:
                break
            # Check if bot detection is shown
            if '/sp/captcha' in page.url:
                if args.show_browser:
                    writerr(colored(f'[ Startpage ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "startpage" and press ENTER...','yellow')) 
                    await wait_for_word_or_sleep("startpage", args.antibot_timeout)
                    writerr(colored(f'[ Startpage ] Resuming...', 'green'))
                else:
                    writerr(colored('[ Startpage ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                    return set(endpoints)
            
            try:
                # Wait for the search results to be fully loaded and have links
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
            except:
                pass

            # Check if bot detection is still shown
            if '/sp/captcha' in page.url:
                writerr(colored('[ Startpage ] Failed to complete CAPTCHA','red'))
                return set(endpoints)
        
            # Locate all forms with action="/sp/search" on the page
            forms = await page.query_selector_all('form[action="/sp/search"]')
            last_form = forms[-1]  # Get the last form
            
            # Get the current value of the "page" input field
            try:
                curr_page_value = await last_form.evaluate('(form) => form.querySelector("input[name=\'page\']").value')
            except:
                curr_page_value = 1
            
            # If the current "page" value has not increased, break out of the loop
            if pageNo == curr_page_value:
                break
            
            # Click the submit button for the last form
            await last_form.click()

            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)

            # Check if any '.result-link' exists
            try:
                await page.wait_for_selector('.result-link', timeout=1000)  # Short timeout to check existence
            except:
                break  # Break the loop if no '.result-link' found
        
            if vverbose():
                writerr(colored('[ Startpage ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
            
            # Collect endpoints from the current page
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            endpoints += extractStartpageEndpoints(soup)

            # Update the previous "page" value
            pageNo = curr_page_value

        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Startpage ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Startpage ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Startpage ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Startpage ] ERROR getStartpage1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Startpage',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
def extractYahooEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        div_content = soup.find('div', id='results')
        if div_content:
            a_tags = div_content.find_all('a')
            for a in a_tags:
                # Don't add links from Ads
                if not a.find_parent(class_="searchCenterTopAds") and not a.find_parent(class_="searchCenterBottomAds"):
                    href = a.get('href')
                    if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*yahoo\.[^\/\.]{2,}', href) and not re.match(r'^https?:\/\/([\w-]+\.)*bingj\.com', href):
                        endpoints.append(href.strip())
                        # If the same search is going to be resubmitted without subs, get the subdomain
                        if args.resubmit_without_subs:
                            allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR extractYahooEndpoints 1: ' + str(e), 'red')) 
        
def extractYahooResultNumber(url):
    try:
        match = re.search(r'\b(?:b=)([^&]+)', url)
        if match:
            return match.group(1)
        return 0
    except Exception as e:
        writerr(colored('ERROR extractYahooResultNumber 1: ' + str(e), 'red')) 
        
async def getYahoo(browser, dork, semaphore):
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Yahoo ] Starting...', 'green'))
        
        await page.goto(f'https://www.yahoo.com/search?q={dork}', timeout=args.timeout*1000)

        # Check if the cookie banner exists and click "Go to end" and then "Agree" if it does
        cookie = await page.query_selector('#scroll-down-btn')
        if cookie:
            await cookie.click()
        cookieAgree = await page.query_selector('button[name="agree"][value="agree"]')
        if cookieAgree:
            await cookieAgree.click()
        
        # Submit the search form
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        await page.wait_for_selector("form")
        await page.press("form", "Enter")
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        
        # Collect endpoints from the initial page
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        endpoints = extractYahooEndpoints(soup)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        pageNo = 1
        oldResultNumber = 1
        while True:
            if stopProgram:
                break
            # Find the link with the title "Next page"
            next_page_link = await page.query_selector('a.next')
            if next_page_link:
                # Extract Result number value from the URL of the current page
                pageUrl = page.url
                nextResultNumber = extractYahooResultNumber(pageUrl)
                # If it is the same as the last page, exit the loop
                if nextResultNumber == oldResultNumber:
                    break
                oldResultNumber = nextResultNumber
                
                await next_page_link.click()
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
                pageNo += 1
                if vverbose():
                    writerr(colored('[ Yahoo ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
                
                # Collect endpoints from the current page
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                endpoints += extractYahooEndpoints(soup)
                
            else:
                # No "Next page" link found, exit the loop
                break
        
        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Yahoo ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Yahoo ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Yahoo ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Yahoo ] ERROR getYahoo1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Yahoo',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
async def getResultsGoogle(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        a_tags = soup.find_all('a')
        for a in a_tags:
            href = a.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*google\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR getResultsGoogle 1: ' + str(e), 'red')) 
        
async def getGoogle(browser, dork, semaphore):
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Google ] Starting...', 'green'))
        
        # Use the parameters:
        #  tbs=li:1 - Verbatim search
        #  hl=en - English language
        #  filter=0 - Show near duplicate content
        await page.goto(f'https://www.google.com/search?tbs=li:1&hl=en&filter=0&q={dork}', timeout=args.timeout*1000)
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        
        pageNo = 1
        
        # If captcha is shown then allow time to submit it
        captcha = await page.query_selector('form#captcha-form')
        if captcha:
            if args.show_browser:
                writerr(colored(f'[ Google ] reCAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "google" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("google", args.antibot_timeout)
                writerr(colored(f'[ Google ] Resuming...', 'green'))
            else:
                writerr(colored('[ Google ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)
        
        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass

        # Check if bot detection is still shown
        captcha = await page.query_selector('form#captcha-form')
        if captcha:
            writerr(colored('[ Google ] Failed to complete reCAPTCHA','red'))
            return set(endpoints)
        
        # If the cookies notice is shown, accept it
        cookieAccept = await page.query_selector('button:has-text("Accept all")')
        if cookieAccept:
            await cookieAccept.click()
        
        # If the dialog box asking if you want location specific search, say Not now
        locationSpecific = await page.query_selector('g-raised-button:has-text("Not now")')
        if locationSpecific:
            await locationSpecific.click()
    
        # Collect endpoints from the initial page
        endpoints = await getResultsGoogle(page, endpoints)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        while True:
            if stopProgram:
                break
            # Get href from the Next button
            next_button = await page.query_selector('#pnnext')
            if next_button:
                next_href = await next_button.get_attribute('href')
                if next_href:
                    next_url = 'https://www.google.com' + next_href
                    await page.goto(next_url, timeout=args.timeout * 1000)
                    await page.wait_for_load_state('domcontentloaded', timeout=args.timeout * 1000)

                    pageNo += 1
                    if vverbose():
                        writerr(colored('[ Google ] Getting endpoints from page ' + str(pageNo), 'green', attrs=['dark']))
                    
                    # Collect endpoints from the current page
                    endpoints += await getResultsGoogle(page, endpoints)
            else:
                # No "Next" button found, exit the loop
                break

        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Google ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Google ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Google ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Google ] ERROR getGoogle1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Google',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass

def extractYandexEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        result_links = soup.find_all('a', class_=re.compile('.*organic__url.*'))
        for link in result_links:
            href = link.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*yandex\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR extractYandexEndpoints 1: ' + str(e), 'red')) 
        
async def getYandex(browser, dork, semaphore):
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        # Set the gdpr cookie to reduce the chances of getting Captcha page a bit
        context = await browser.new_context(
            storage_state={
                'cookies': [{
                    'name': 'gdpr',
                    'value': '0',
                    'domain': '.yandex.com',
                    'path': '/'
                }]
            }
        )
        page = await context.new_page()
    
        if verbose():
            writerr(colored('[ Yandex ] Starting...', 'green'))
        
        await page.goto(f'https://yandex.com/search/?text={dork}', timeout=args.timeout*1000)
    
        # Check if bot detection is shown
        if '/showcaptcha' in page.url:
            if args.show_browser:
                writerr(colored(f'[ Yandex ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("yandex", args.antibot_timeout)
                writerr(colored(f'[ Yandex ] Resuming...', 'green'))
            else:
                writerr(colored('[ Yandex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)
        try:
            await page.wait_for_load_state('networkidle', timeout=1000)
        except:
            pass

        # If still on Captcha page, then exit
        if '/showcaptcha' in page.url:
            writerr(colored('[ Yandex ] Failed to complete CAPTCHA','red'))
            return set(endpoints)
        
        # Collect endpoints from the initial page
        if vverbose():
            writerr(colored('[ Yandex ] Getting endpoints from page 1', 'green', attrs=['dark'])) 
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        pageNo = 1
        endpoints = extractYandexEndpoints(soup)

        # Loop until there is no submit button in the last form with action="/sp/search"
        while True:
            if stopProgram:
                break

            # Click the Next button
            await page.click('a[aria-label="Next page"]')
            pageNo += 1
            
            # Check if bot detection is shown
            if '/showcaptcha' in page.url:
                if args.show_browser:
                    writerr(colored(f'[ Yandex ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...','yellow')) 
                    await wait_for_word_or_sleep("yandex", args.antibot_timeout)
                    writerr(colored(f'[ Yandex ] Resuming...', 'green'))
                else:
                    writerr(colored('[ Yandex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                    return set(endpoints)

            try:
                # Wait for the search results to be fully loaded and have links
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
            except:
                pass

            # If still on Captcha page, then exit
            if '/showcaptcha' in page.url:
                writerr(colored('[ Yandex ] Failed to complete CAPTCHA','red'))
                return set(endpoints)

            # Check if any classes containing organic__url exist
            try:
                await page.wait_for_selector('.organic__url', timeout=1000)
            except:
                break  # Break the loop if no '.organic__url' found
        
            if vverbose():
                writerr(colored('[ Yandex ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
            
            # Collect endpoints from the current page
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            endpoints += extractYandexEndpoints(soup)

        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Yandex ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Yandex ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Yandex ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Yandex ] ERROR getYandex1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Yandex',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass

async def getResultsEcosia(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        a_tags = soup.find_all('a', attrs={'data-test-id': 'result-link'})
        for a in a_tags:
            href = a.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*ecosia\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR getResultsEcosia 1: ' + str(e), 'red')) 
        
async def getEcosia(browser, dork, semaphore):
    global stopProgram
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Ecosia ] Starting...', 'green'))
        
        # Call with parameters:
        await page.goto(f'https://www.ecosia.org/search?q={dork}', timeout=args.timeout*1000)
        pageNo = 1
        
        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass    
        
        # Check if the cookie banner exists and click reject if it does
        if await page.query_selector('#didomi-notice-disagree-button'):
            # Click the button to reject
            await page.click('#didomi-notice-disagree-button')
    
        # Get the results so far, just in case it ends early
        endpoints =  await getResultsEcosia(page, endpoints)
            
        async def click_Next():
            next_button = await page.query_selector('span:has-text("Next")')
            if next_button:
                await next_button.click()
                await page.wait_for_load_state('networkidle', timeout=args.timeout * 1000)

        # Loop to repeatedly check for the Next button and click it until it doesn't exist
        while await page.query_selector('span:has-text("Next")'):
            if stopProgram:
                break
            #await click_Next()
            if vverbose():
                pageNo += 1
                writerr(colored('[ Ecosia ] Clicking "Next" button to display page '+str(pageNo), 'green', attrs=['dark'])) 
            await click_Next()
            # Get the results so far, just in case it ends early
            endpoints =  await getResultsEcosia(page, endpoints)
        
        # Get all the results
        endpoints = await getResultsEcosia(page, endpoints)
        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Ecosia ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
     
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Ecosia ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Ecosia ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Ecosia ] ERROR getEcosia 1: ' + str(e), 'red'))  
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Ecosia',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
async def getResultsBaidu(page, endpoints):
    global allSubs
    try:
        await page.wait_for_load_state("networkidle")

        # Wait until at least one feedback div exists
        try:
            await page.wait_for_selector("div.cosc-feedback", timeout=1000)
        except:
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
            url_value = query_params.get('url')
            if not url_value:
                continue

            decoded_url = html.unescape(unquote(url_value[0]))
            endpoints.append(decoded_url.strip())

            if args.resubmit_without_subs:
                allSubs.add(getSubdomain(decoded_url.strip()))

        return endpoints

    except Exception as e:
        writerr(colored('ERROR getResultsBaidu: ' + str(e), 'red'))
        return endpoints


async def getBaidu(browser, dork, semaphore):
    global stopProgram
    page = None
    endpoints = []

    try:
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)

        if verbose():
            writerr(colored('[ Baidu ] Starting...', 'green'))

        # Go to search page
        await page.goto(f'https://www.baidu.com/s?ie=utf-8&ct=0&wd={dork}', timeout=args.timeout*1000)

        # Wait for results to load
        try:
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass

        # Check if bot detection captcha is displayed
        if 'captcha' in page.url:
            if args.show_browser:
                writerr(colored(f'[ Baidu ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "baidu" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("baidu", args.antibot_timeout)
                writerr(colored(f'[ Baidu ] Resuming...', 'green'))
            else:
                writerr(colored('[ Baidu ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)
        else:
            # Else wait for a popup window to disappear
            time.sleep(5)

        pageNo = 1
        while True:
            # Get results from current page
            endpoints = await getResultsBaidu(page, endpoints)

            # Find next page button
            next_button = await page.query_selector('a.n:has(span:has-text("下一页"))')
            if not next_button or stopProgram:
                break

            pageNo += 1
            if vverbose():
                writerr(colored(f'[ Baidu ] Clicking "Next" button to display page {pageNo}', 'green', attrs=['dark']))

            # Remember old feedback div IDs
            old_feedback_divs = await page.query_selector_all("div.cosc-feedback")
            old_ids = [await div.get_attribute("id") for div in old_feedback_divs]

            # Click next
            await next_button.scroll_into_view_if_needed()
            await next_button.click()

            # Wait for new feedback divs to appear (max ~4 seconds)
            for _ in range(20):
                await page.wait_for_timeout(200)
                new_feedback_divs = await page.query_selector_all("div.cosc-feedback")
                new_ids = [await div.get_attribute("id") for div in new_feedback_divs]
                if set(new_ids) != set(old_ids):
                    break

        setEndpoints = set(endpoints)
        if verbose():
            writerr(colored(f'[ Baidu ] Complete! {len(setEndpoints)} endpoints found', 'green'))

        return setEndpoints

    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Baidu ] Page timed out - got {noOfEndpoints} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Baidu ] Search aborted - got {noOfEndpoints} results', 'red')) 
        else:
            writerr(colored('[ Baidu ] ERROR getBaidu: ' + str(e), 'red'))  

        if args.debug and page is not None:
            await savePageContents('Baidu', page)

        return set(endpoints)

    finally:
        try:
            if page is not None:
                await page.close()
            semaphore.release()
        except:
            pass
        
async def getResultsSeznam(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        a_tags = soup.find_all('a', attrs={'tabindex': '0'})
        for a in a_tags:
            href = a.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*seznam\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR getResultsSeznam 1: ' + str(e), 'red'))

async def getSeznam(browser, dork, semaphore):
    global stopProgram
    page = None
    endpoints = []

    try:
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)

        if verbose():
            writerr(colored('[ Seznam ] Starting...', 'green'))

        # Go to search page
        await page.goto(f'https://search.seznam.cz/?q={dork}', timeout=args.timeout*1000)

        pageNo = 1
        
        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass    
    
        # Get the results so far, just in case it ends early
        endpoints =  await getResultsSeznam(page, endpoints)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        while True:
            if stopProgram:
                break
            # Find the link with the title "Další strana" (Next page)
            if await page.query_selector('a[title="Další strana"]'):
                await page.click('a[title="Další strana"]')
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
                pageNo += 1
                if vverbose():
                    writerr(colored('[ Seznam ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
                
                try:
                    # Wait for the search results to be fully loaded and have links
                    await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
                except:
                    pass   
        
                # Get all the results
                endpoints = await getResultsSeznam(page, endpoints)
            else:
                # No "Next page" link found, exit the loop
                break
        
        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Seznam ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Seznam ] Page timed out - got {noOfEndpoints} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Seznam ] Search aborted - got {noOfEndpoints} results', 'red')) 
        else:
            writerr(colored('[ Seznam ] ERROR getSeznam: ' + str(e), 'red'))  

        if args.debug and page is not None:
            await savePageContents('Seznam', page)

        return set(endpoints)

    finally:
        try:
            if page is not None:
                await page.close()
            semaphore.release()
        except:
            pass

async def savePageContents(source, page):
    try:
        # Press the "Escape" key to stop page loading
        await page.keyboard.press("Escape")

        # Wait for a short duration to ensure the page loading is stopped
        await asyncio.sleep(2)
        
        # Get the page contents and save to file
        content = await page.content()
        if content != '' and content != '<html><head></head><body></body></html>':
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d-%H%M%S")
            filename = f"xnldorker_{source}_{timestamp}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)
            writerr(colored(f'[ {source} ] Saved HTML content to {filename}', 'cyan')) 
    except Exception as e:
        writerr(colored(f'[ {source} ] Unable to save page contents: {str(e)}', 'cyan')) 

async def processInput(dork):
    global browser, sourcesToProcess, duckduckgoEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, yandexEndpoints, ecosiaEndpoints, baiduEndpoints, seznamEndpoints, stopProgram
    try:
        
        # Create a single browser instance
        async with async_playwright() as p:
            if args.show_browser:
                browser = await p.firefox.launch(headless=False)
                #browser = await p.chromium.launch(headless=False)
            else:
                browser = await p.firefox.launch(headless=True)

            # Define a dictionary to hold the results for each source
            resultsDict = {}
            
            # Define a semaphore to limit concurrent tasks. This is determined by the -cs / --concurrent-sources argument
            concurrentSources = args.concurrent_sources
            if concurrentSources == 0 or concurrentSources > len(sourcesToProcess):
                concurrentSources = len(sourcesToProcess)
            semaphore = asyncio.Semaphore(concurrentSources)
            
            # Define a list to hold the sources included in the gather call
            includedSources = []
            
            # Check and add coroutines for any required sources
            try:
                if 'duckduckgo' in sourcesToProcess:
                    includedSources.append(getDuckDuckGo(browser, dork, semaphore))
                if 'bing' in sourcesToProcess:
                    includedSources.append(getBing(browser, dork, semaphore))
                if 'startpage' in sourcesToProcess:
                    includedSources.append(getStartpage(browser, dork, semaphore))
                if 'yahoo' in sourcesToProcess:
                    includedSources.append(getYahoo(browser, dork, semaphore))
                if 'google' in sourcesToProcess:
                    includedSources.append(getGoogle(browser, dork, semaphore))
                if 'yandex' in sourcesToProcess:
                    includedSources.append(getYandex(browser, dork, semaphore))
                if 'ecosia' in sourcesToProcess:
                    includedSources.append(getEcosia(browser, dork, semaphore))
                if 'baidu' in sourcesToProcess:
                    includedSources.append(getBaidu(browser, dork, semaphore))
                if 'seznam' in sourcesToProcess:
                    includedSources.append(getSeznam(browser, dork, semaphore))
            except:
                pass
            
            # Run all searches concurrently using the same browser instance
            results = await asyncio.gather(*includedSources)
            
            # Populate the results dictionary and endpoint lists
            for source, result in zip(sourcesToProcess, results):
                if stopProgram:
                    break 
                if source not in resultsDict:  # Check if the source is not already in the resultsDict
                    resultsDict[source] = result  # If not, add it
                else:
                    # If the source is already in the resultsDict, append new data to existing data
                    resultsDict[source].update(result)

                # Update the endpoint lists as well
                if source == 'duckduckgo':
                    duckduckgoEndpoints.update(result)
                elif source == 'bing':
                    bingEndpoints.update(result)
                elif source == 'startpage':
                    startpageEndpoints.update(result)
                elif source == 'yahoo':
                    yahooEndpoints.update(result)
                elif source == 'google':
                    googleEndpoints.update(result)
                elif source == 'yandex':
                    yandexEndpoints.update(result)
                elif source == 'ecosia':
                    ecosiaEndpoints.update(result)
                elif source == 'baidu':
                    baiduEndpoints.update(result)
                elif source == 'seznam':
                    seznamEndpoints.update(result)
        
            # Close the browser instance once all searches are done
            try:
                await browser.close()
            except:
                pass
        
    except Exception as e:
        writerr(colored('ERROR processInput 1: ' + str(e), 'red')) 
    finally:
        try:
            await browser.close()
        except:
            pass
    
async def processOutput():
    global duckduckgoEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, yandexEndpoints, ecosiaEndpoints, baiduEndpoints, seznamEndpoints, sourcesToProcess
    try:
        allEndpoints = set()

        # If --output-sources was passed, then keep the source in the endpoint, otherwise we need a unique set without source
        if args.output_sources:
            if duckduckgoEndpoints:
                allEndpoints.update(f'[ DuckDuckGo ] {endpoint}' for endpoint in duckduckgoEndpoints)
            if bingEndpoints:
                allEndpoints.update(f'[ Bing ] {endpoint}' for endpoint in bingEndpoints)
            if startpageEndpoints:
                allEndpoints.update(f'[ StartPage ] {endpoint}' for endpoint in startpageEndpoints)
            if yahooEndpoints:
                allEndpoints.update(f'[ Yahoo ] {endpoint}' for endpoint in yahooEndpoints)
            if googleEndpoints:
                allEndpoints.update(f'[ Google ] {endpoint}' for endpoint in googleEndpoints)
            if yandexEndpoints:
                allEndpoints.update(f'[ Yandex ] {endpoint}' for endpoint in yandexEndpoints)
            if ecosiaEndpoints:
                allEndpoints.update(f'[ Ecosia ] {endpoint}' for endpoint in ecosiaEndpoints)
            if baiduEndpoints:
                allEndpoints.update(f'[ Baidud ] {endpoint}' for endpoint in baiduEndpoints)
            if seznamEndpoints:
                allEndpoints.update(f'[ Seznam ] {endpoint}' for endpoint in seznamEndpoints)
        else:
            if duckduckgoEndpoints:
                allEndpoints |= duckduckgoEndpoints
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

        if verbose() and sys.stdin.isatty():
            writerr(colored('\nTotal endpoints found: '+str(len(allEndpoints))+' 🤘  ', 'cyan')+str(sourcesToProcess))
            
        # If the -ow / --output_overwrite argument was passed and the file exists already, get the contents of the file to include
        appendedResults = False
        if args.output and not args.output_overwrite:
            try:
                existingEndpoints = open(os.path.expanduser(args.output), "r")
                appendedResults = True
                for endpoint in existingEndpoints.readlines():
                    allEndpoints.add(endpoint.strip())
            except:
                pass

        # If an output file was specified, open it
        if args.output is not None:
            try:
                # If the filename has any "/" in it, remove the contents after the last one to just get the path and create the directories if necessary
                try:
                    f = os.path.basename(args.output)
                    p = args.output[:-(len(f))-1]
                    if p != "" and not os.path.exists(p):
                        os.makedirs(p)
                except Exception as e:
                    if verbose():
                        writerr(colored("ERROR processOutput 5: " + str(e), "red"))
                outFile = open(os.path.expanduser(args.output), "w")
            except Exception as e:
                if vverbose():
                    writerr(colored("ERROR processOutput 2: " + str(e), "red"))    
        
        # Initialize reusable session object for sending requests to the proxy
        sendToProxy = False
        if args.proxy:
            proxies = {
                        "http": args.proxy,
                        "https": args.proxy,
                    }
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            sendToProxy = True
            
        # Output all endpoints
        for endpoint in allEndpoints:
            try:
                # If an output file was specified, write to the file
                if args.output is not None:
                    outFile.write(endpoint + '\n')
                else:    
                    # If output is piped or the --output argument was not specified, output to STDOUT
                    if not sys.stdin.isatty() or args.output is None:
                        write(endpoint,True)
            except Exception as e:
                writerr(colored('ERROR processOutput 6: Could not output links found - ' + str(e), 'red'))
                    
            # If the -proxy argument is passed, send the link to the specified proxy
            if sendToProxy:
                try:
                    # Make the request
                    resp = requests.get(
                        endpoint,
                        allow_redirects=True,
                        verify=False,
                        proxies=proxies,
                        headers = {"User-Agent": "xnldorker by @xnl-h4ck3r"},
                    )
                    
                except Exception as e:
                    writerr(colored(f"[ Proxy ] Failed to send {endpoint} to proxy: {str(e)}", "red"))
                    writerr(colored(f"[ Proxy ] Proxy disabled. Check value {args.proxy} is correct.", "red"))
                    sendToProxy = False
            
        # Close the output file if it was opened
        try:
            if args.output is not None:
                if appendedResults:
                    write(colored('Output successfully appended to file: ', 'cyan')+colored(args.output,'white'))
                else:
                    write(colored('Output successfully written to file: ', 'cyan')+colored(args.output,'white'))
                write()
                outFile.close()
        except Exception as e:
            writerr(colored('ERROR processOutput 3: ' + str(e), 'red'))
                            
    except Exception as e:
        writerr(colored('ERROR processOutput 1: ' + str(e), 'red'))

def showOptionsAndConfig():
    global sourcesToProcess, inputDork
    try:
        write(colored('Selected options:', 'cyan'))
        if os.path.isfile(os.path.expanduser(args.input)):
            write(colored('-i: ' + args.input, 'magenta')+colored(' The file of dorks used to search on the sources.','white'))
        else:
            write(colored('-i: ' + inputDork, 'magenta')+colored(' The dork used to search on the sources.','white'))
        if args.output is not None:
            write(colored('-o: ' + args.output, 'magenta')+colored(' Where gathered endpoints will be written.','white'))
        else:
            write(colored('-o: <STDOUT>', 'magenta')+colored(' An output file wasn\'t given, so output will be written to STDOUT.','white'))
        write(colored("-ow: " + str(args.output_overwrite), "magenta")+colored(" Whether the output will be overwritten if it already exists.", "white" ))
        if args.sources:
            write(colored('-s: ' + args.sources, 'magenta')+colored(' The sources requested to search.','white'))
        if args.exclude_sources:
            write(colored('-es: ' + args.exclude_sources, 'magenta')+colored(' The sources excluded from the search.','white'))
        if args.concurrent_sources == 0:
            write(colored('-cs: ALL', 'magenta')+colored(' The browser timeout in seconds','white'))
        else:
            write(colored('-cs: ' + str(args.concurrent_sources), 'magenta')+colored(' The number of concurrent sources that will be searched at a time.','white'))
        write(colored('-t: ' + str(args.timeout), 'magenta')+colored(' The browser timeout in seconds','white'))
        write(colored('-sb: ' + str(args.show_browser), 'magenta')+colored(' Whether the browser will be shown. If False, then headless mode is used.','white'))
        write(colored('-rwos: ' + str(args.resubmit_without_subs), 'magenta')+colored(' Whether the query will be resubmitted, but excluding the sub domains found in the first search.','white'))
        if args.proxy:
            write(colored('-proxy: ' + str(args.proxy), 'magenta')+colored(' The proxy to send found links to.','white'))
        write(colored('Sources being checked: ', 'magenta')+str(sourcesToProcess))
        write('')
        
    except Exception as e:
        writerr(colored('ERROR showOptionsAndConfig 1: ' + str(e), 'red'))    

# For validating arguments -s and -es
def argcheckSources(value):
    # Split the value by commas to get individual sources
    sources = value.split(',')

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
        description='xnldorker - by @Xnl-h4ck3r: Gather results of dorks across a number of search engines.'    
    )
    parser.add_argument(
        '-i',
        '--input',
        action='store',
        help='A dork to use on the search sources.'
    )
    parser.add_argument(
        '-o',
        '--output',
        action='store',
        help='The output file that will contain the results (default: output.txt). If piped to another program, output will be written to STDOUT instead.',
    )
    parser.add_argument(
        "-ow",
        "--output-overwrite",
        action="store_true",
        help="If the output file already exists, it will be overwritten instead of being appended to.",
    )
    parser.add_argument(
        '-os',
        '--output-sources',
        action='store_true',
        help='Show the source of each endpoint in the output. Each endpoint will be prefixed, e.g. "[ Bing ] https://example.com".',
    )
    parser.add_argument(
        '-s',
        '--sources',
        action='store',
        help='Specific sources to use when searching (-s duckduckgo,bing). Use -ls to display all available sources.',
        type=argcheckSources,
        metavar='string[]'
    )
    parser.add_argument(
        '-es',
        '--exclude-sources',
        action='store',
        help='Specific sources to exclude searching (-s google,startpage). Use -ls to display all available sources.',
        type=argcheckSources,
        metavar='string[]'
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
        '-ls',
        '--list-sources',
        action='store_true',
        help='List all available sources.',
    )
    default_timeout = 30
    parser.add_argument(
        "-t",
        "--timeout",
        help="How many seconds to wait for the source to respond (default: " + str(default_timeout) + " seconds).",
        default=default_timeout,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        '-sb',
        '--show-browser',
        action='store_true',
        help='View the browser instead of using headless browser.',
    )
    default_abt = 90
    parser.add_argument(
        "-abt",
        "--antibot-timeout",
        help="How many seconds to wait when the -sb option was used and a known anti-bot mechanism is encountered. This is the time you have to manually respond to the anti-bot mechanism before it tries to continue.",
        default=default_abt,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        '-rwos',
        '--resubmit-without-subs',
        action='store_true',
        help='After the initial search, search again but exclude all subs found previously to get more links.',
    )
    parser.add_argument(
        "-proxy",
        action="store",
        help="Send the links found to a proxy, e.g http://127.0.0.1:8080",
        default="",
    )
    parser.add_argument('--debug', action='store_true', help='Save page contents on error.')
    parser.add_argument('-nb', '--no-banner', action='store_true', help='Hides the tool banner.')
    parser.add_argument('--version', action='store_true', help='Show version number')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    parser.add_argument('-vv', '--vverbose', action='store_true', help='Increased verbose output.')
    args = parser.parse_args()

    # If --version was passed, display version and exit
    if args.version:
        write(colored('xnldorker - v' + __version__,'cyan'))
        sys.exit()
    
    # If --list-sources was passed, display sources and exit
    if args.list_sources:
        if not args.no_banner:
            showBanner()
        write(colored('These are the available sources: ','green')+str(SOURCES))
        sys.exit()
        
    try:
        # If no input was given, raise an error
        if sys.stdin.isatty():
            if args.input is None:
                writerr(colored('You need to provide input with -i argument or through <stdin>. This will be a dork used to search the requested sources, e.g. "site:example.com"', 'red'))
                sys.exit()
        
        # Determine the sources to process
        if args.sources is None:
            sourcesToProcess = SOURCES
        else:
            sourcesToProcess = args.sources.split(',')
        if args.exclude_sources is not None:
            sourcesToProcess = [source for source in sourcesToProcess if source not in args.exclude_sources]

        # Get the input dork, depending on the input type
        dorks = []
        if sys.stdin.isatty():
            if os.path.isfile(os.path.expanduser(args.input)):
                with open(os.path.expanduser(args.input), 'r') as f:
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
            if not re.match(r'(^|\s)[a-z]*:', inputDork, re.IGNORECASE) and ' ' not in inputDork:
                inputDork = 'site:'+inputDork
            
            # Only for first dork...
            # If input is not piped, show the banner, and if --verbose option was chosen show options and config values
            if firstDork and sys.stdin.isatty():
                firstDork = False
                # Show banner unless requested to hide
                if not args.no_banner:
                    showBanner()
                if verbose():
                    showOptionsAndConfig()
                    
            # Process the input given on -i (--input), or <stdin>
            write(colored('Processing dork: ', 'cyan') + colored(inputDork, 'white'))
            await processInput(inputDork)

        # If there were some subs found, and the --resubmit-without-subs was passed, then run again with subdomains removed
        if len(allSubs) > 0 and args.resubmit_without_subs:
            inputDork = inputDork + ' ' + ' '.join(['-{}'.format(sub) for sub in allSubs if sub])
            write(colored('\nResubmitting again for input: ', 'magenta')+colored(inputDork,'white'))
            await processInput(inputDork)
        
        # Output the saved urls with parameters
        await processOutput()
        
    except Exception as e:
        writerr(colored('ERROR main 1: ' + str(e), 'red'))      

    # Show ko-fi link if verbose and not piped
    try:
        if verbose() and sys.stdin.isatty():
            writerr(colored('✅ Want to buy me a coffee? ☕ https://ko-fi.com/xnlh4ck3r 🤘', 'green'))
    except:
        pass

def main():
    asyncio.run(run_main())
    
if __name__ == '__main__':
    main()
