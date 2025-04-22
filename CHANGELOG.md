## Changelog

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
