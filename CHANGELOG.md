## Changelog

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
