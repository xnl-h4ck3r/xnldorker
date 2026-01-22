## Changelog

- v4.1

  - New

    - Check for `Seznam` Captcha page
    - If `-rwos` / `--resubmit-without-subs` arg is passed, don't process `Seznam` the second time around because it does not recognise the syntax of removed words with `-` so just displays all the same results again.
    - If Kagi site says `Searches will be paused until you upgrade to a paid subscription` then it will be reported to the user and skipped.

  - Changed

    - Set `Bing` and `Ecosia` sources as auto excluded because these don't work right now. They may work for someone in a different region or something for some reason, so they can be included with `--source` if required.
    - BUG FIX: Remove a debug print line from Yandex processing.

- v4.0

  - New

    - Add DuckDuckGo Lite (`duckgolite`) as a new search source. This uses the text-only version of DuckDuckGo at `lite.duckduckgo.com/lite/` which may be less likely to trigger bot detection. 
    - Add a check for the text `Unfortunately, bots use DuckDuckGo` to determine if the page is a bot detection page for existing DuckDuckGo source and also the new DuckGoLite source.
    - Check for `Error getting results` at start of DuckDuckGo and Lite because that is part of bot protection if the browser is not shown.

- v3.4

  - Changed

    - When processing a file of dorks as input, results are now written to the output file after each line in the file has been processed, rather than only at the end.
    - If the `-ow` / `--output-overwrite` argument is passed, it will only overwrite the file for the first dork processed; subsequent dorks will append to the file.

- v3.3

  - Changed

    - BUG FIX: Fixed `[ Forward Proxy ] Worker error: task_done() called too many times` error when using `-rwos` or multiple dorks.
    - Improved proxy worker thread lifecycle: ensuring only one thread runs and all queued endpoints are processed before normal program exit.
    - BUG FIX: The unique endpoints sent count in the exit message now correctly shows the total across all search passes (including `-rwos`).

- v3.2

  - New

    - Add Google Custom Search API as a source called `googlecs`. Thanks to [pdstat](https://github.com/pdstat) for the idea and code.
    - Added `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CHAT_ID` to the `config.yml` file.
    - Implemented exponential backoff for `googlecs` using a `requests.Session` for 429 status codes and throttled `googlecs` requests to 100 per minute.
    
- v3.1

  - Changed

    - BUG FIX: When Ctrl-C is pressed, ensure that any links found so far are saved.
    - BUG FIX: Fixed error `'NoneType' object is not iterable` in `processInput` that could occur when Ctrl-C was pressed.

- v3.0

  - New

    - Add Kagi search engine as a source. Kagi is a premium, ad-free search engine that focuses on privacy and quality results.
    - Kagi search performs multiple passes with different parameters to maximize results, including Default, No Region, Verbatim, and Non-Personalized modes.
    - Added a configuration system: `config.yml` is now used to store the `KAGI_SESSION_LINK`. This file is automatically created in the user's config directory during installation.
    
  - Changed

    - Make changes to pass ruff and black checks.
    - Update README.md to include Kagi search engine.

- v2.3

  - New

    - `-sb/--show-browser` argument now accepts optional values `tabs` or `windows`. Use `-sb windows` to open each source in a separate browser window instead of tabs. Default is `tabs` if no value specified.
    - Tabs and windows now close automatically when each source completes (unless `--debug` is used). Use `--debug` flag to keep all tabs/windows open for inspection and debugging.
    - If `--debug` is passed then keep all tabs or windows open until the user presses Enter to end the program. This lets you see the page the source stopped on.
    - Add `xnldorker_*.html` to `.gitignore` to ignore any debug files created.
    - Check for a different google captcha that appears with the text `detected unusual traffic from your computer`.
    - Add some ant-bot measures to try and reduce detection.
      - Added browser launch arguments to disable automation detection features like AutomationControlled
      - Injected JavaScript to hide the navigator.webdriver property that browsers expose when controlled by automation
      - Added realistic HTTP headers including Accept-Language, DNT, and proper Accept headers
      - Set a consistent User-Agent across all contexts
      - Added a small random delay (0.5-1.5 seconds) before navigation to appear more human-like
      - More comprehensive JavaScript injections - hiding plugins, languages, chrome runtime, and permissions API

  - Changed

    - BUG FIX: Fixed memory leak issue when getting Google endpoints. This often led to the program getting `Killed` in the terminal.
    - BUG FIX: If more than one source required a captcha to be submitted at the same time, it would only listen for the last source word in the terminal. Each source calling `wait_for_word_or_sleep()` would overwrite the previous stdin reader.
    - BUG FIX: Improved error handling when browser windows are manually closed during searches. All sources now properly detect and log when the browser is closed, displaying messages like `"[ Source ] Search aborted - got X results"` instead of throwing raw errors.
    - BUG FIX: Fixed inconsistent page creation across sources. All sources now correctly use `context.new_page()` instead of some using `browser.new_page()`.
    - BUG FIX: Set explicit viewport size (1280x720) for browser context to prevent small black windows.
    - BUG FIX: Browser and context are no longer closed when using `-sb/--show-browser`. The browser instance now stays open until the user manually closes it, preventing all windows from disappearing when searches complete.
    - BUG FIX: Baidu was only checking for Captcha on the first page
    - BUG FIX: Fixed an issue with Seznam source where it was timing out after pressing the Next button for the first time.
    - BUG FIX: Sometimes Baidu threw the error `ERROR getBaidu: Page.query_selector_all: Execution context was destroyed, most likely because of a navigation` after clicking the next page.
    - BUG FIX: Endpoints weren't correctly retrieved from a Bing page because they changed to site.
    - Changed back from Firefox to Chromium browser engine for improved stability and reliability when using `-sb/--show-browser` option.
    - Change help text for `--antibot-timeout` to show default value, and add the parameter when showing the options using `-v`.
    - BUG FIX: Seznam was very very slow when not showing the browser. It is now the same speed regardless whether the browser is shown or not.
    - Seznam - Only check further for links and clicking next if the text "Bohužel jsem nic nenašel" (Unfortunately I didn't find anything) isn't shown.
    - Baidu - Only wait for the popup to disappear and check further for links and clicking next if the text "抱歉，未找到相关结果" (Sorry, no relevant results were found) isn't shown.
    - If `--debug` was passed and a source is complete with 0 results, write the contents of the page to file so it can be checked for any potential problems.

- v2.2

  - New

    - Add `--request-proxy` argument for browser request proxying. Can be a proxy string (e.g. `http://user:pass@1.2.3.4:8000`, `socks5://host:port`) or a file containing proxy list (one per line, random selection).

  - Changed

    - Rename `-proxy` argument to `--forward-proxy` for sending found links to a proxy (e.g. Caido, Burp Suite).Also, it now sends endpoints to the proxy as they are found (real-time) instead of at the end of the search, using a separate background thread to avoid impacting search performance.
    - BUG FIX: Getting endpoints from Yandex wasn't always working correctly. This has been rewritten to be more robust and to avoid timing out when there are no results.

- v2.1

  - New

  - Add seznam.cz search engine as a source. It can return a lot more results that other search engines. I have not come across a captcha on this site yet, so if one does happen it will not be paused.

- v2.0

  - New

    - Add Ecosia search engine as a source. This usually returns up to 200 links for any search query. I have not come across a captcha on this site yet, so if one does happen it will not be paused.
    - Add Baidu search engine as a source. This usually returns up to around 200 links for any search query, but running the same query more than once can actually get a few extra links.

  - Change

    - BUG FIX: When `-debug` was used, the file of the current content wasn't being written. The `sleep` command was waiting for 2000 seconds instead of 2!!!

- v1.7

  - New

    - Add code to recognise the captcha on Bing.

  - Change

    - Use Firefox instead of Chrome for the browser. This fixed an issue with DuckDuckGo blocking for bot detection.
    - Google seems to have made a change where the link used is only showing 5 pages and max links returned was 40. By removing the `&num=100` parameter, this is getting the maximum links again.
    - BUG FIX: There were a few references to `arg.antibot_timeout` which causes an error because it should be `args.antibot_timeout`.

- v1.6

  - New

    - Allow a file of dorks to be passed as input. If the input value is the name of a valid file it will be treated as a file and each line will be run as a separate dork, otherwise it is assumed the input value is a single dork.

  - Changed

    - Show what dork is currently being processed, not just if `-v` was passed.

- v1.5

  - Changed

    - BUG FIX: Google changed, so stopped working because it failed to click the "Next page" link. Changed to get the `href` instead and navigate to the next page via URL instead.

- v1.4

  - Changed

    - BUG FIX: Bing changed, so stopped working because it failed to click the "Next page" link. The reference to the link had gone stale by the time it was clicked, so the code will now fetch again just before clicking.

- v1.3

  - New

    - Add `-proxy` argument. This can be used to send the links found to a proxy, e.g. `http://127.0.0.1:8080`
    - When initially requesting Google, use query parameter `num=100` to show as many links on one page as possible.

  - Changed

    - Google have changed their site so it no longer had the `More Results` link that keeps showing the links on the page. They have returned to the `Next` button being displayed. The code will be changed to click the button each time and get links from each page.

- v1.2

  - Changed

    - The regex to check whether to prefix the input with `site:` is incorrect. THis has been fixed and improved.
    - Add `dist/` to `.gitignore`.

- v1.1

  - New

    - Add `yandex` as a source (unfortunately it does display the anti-bot screen a LOT!!)
    - If an anti-bot mechanism screen is shown for any source, it pauses for the Timeout period, but you can no also manually resume by typing the name of the source in lower case and pressing ENTER.
    - If there were no results found, don't resubmit with subdomains removed.
    - Add the `.gitignore` file.

  - Changed

    - Fix a bug that showed the version as outdated, even if the current one.
    - Wait for the Startpage.com page to complete loading before checking for the Captcha page because sometimes if fails to recognise it's on that page and stops.
    - Change the default value for `-abt`/`--antibot-timeout` to 90 seconds.

- v1.0

  - Initial release. Please see README.md
