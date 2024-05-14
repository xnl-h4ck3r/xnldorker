## Changelog

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
