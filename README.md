<center><img src="https://github.com/xnl-h4ck3r/xnldorker/blob/main/xnldorker/images/title.png"></center>

## About - v4.0

This is a tool used to run a dork on different search sites.
The available sources are currently: **DuckDuckGo, DuckGoLite, Bing, Startpage, Yahoo, Google, GoogleCS, Yandex, Ecosia, Baidu, Seznam, Kagi**

**ℹ️ IMPORTANT: This tool does not solve captchas for you, so it is advised you use the `-sb`/`--show-browser` argument and manually deal with the captchas to get best results. DO NOT interact with the browser unless the CLI says to solve a Captcha, and ONLY solve the capture and don't click anything else!**

**ℹ️ IMPORTANT: If you use advanced search operators, be aware that operators that work on some of the sources may not work on others. You may need to use the `--sources` (and/or `--exclude-source`) argument to specify the appropriate sources.**

**ℹ️ IMPORTANT: The GoogleCS source (Google Custom Search Engine) using an API and requires an API key and an optional Chat ID. Follow the instructions [below](#google-custom-search-instructions).**

**ℹ️ IMPORTANT: Kagi is a a premium, ad‑free search engine and search platform that you pay to use, focused on privacy and quality results. It provides a smaller result set, but higher chance of surfacing weird, niche, or forgotten pages when dorking. Find out more [here](https://kagi.com).**

**ℹ️ KNOWN ISSUES:**

These are issues that I see, but may vary based on Geo-Location or other factors:

- 🔴 Ecosia use Cloudflare which now shows a captcha straight away, and doesn't allow you to verify.
- 🔴 Bing does not like bots. If you show the browser you can solve the captcha and get one page of links but that's all for now.
- 🟠 DuckDuckGo & DuckGoLite is fine if you show the browser, but if you try using headless mode it will get no links due to their bot detection.
- 🟠 Yandex shows an insane number of captcha screens. If you show the browser, you can get a few pages of links before you get sick of solving them!

**⚠️ WARNING: If you use this tool a lot, then I guess there is the potential to get blocked on these source sites, so use sensibly. Using a VPN will help.**

## Installation

`xnldorker` supports **Python 3**.

Install `xnldorker` in default (global) python environment.

```bash
pip install xnldorker
```

OR

```bash
pip install git+https://github.com/xnl-h4ck3r/xnldorker.git -v
```

You can upgrade with

```bash
pip install --upgrade xnldorker
```

### pipx

Quick setup in isolated python environment using [pipx](https://pypa.github.io/pipx/)

```bash
pipx install git+https://github.com/xnl-h4ck3r/xnldorker.git
```

## Usage

| Argument | Long Argument        | Description                                                                                                                                                                                                                                                                                                                                               |
| -------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -i       | --input              | A dork to use on the search sources, or a file or dorks (one per line). If no advanced search operators (e.g. `site:`, `inurl:`, `intitle:`, etc.) are used in the input value, then it is assumed a domain only is passed, and will be prefixed with `site:`                                                                                             |
| -o       | --output             | The output file that will contain the results (default: output.txt). If piped to another program, output will be written to STDOUT instead.                                                                                                                                                                                                               |
| -ow      | --output-overwrite   | If the output file already exists, it will be overwritten instead of being appended to.                                                                                                                                                                                                                                                                   |
| -os      | --output-sources     | Show the source of each endpoint in the output. Each endpoint will be prefixed, e.g. `[ Bing ] https://example.com`.                                                                                                                                                                                                                                      |
| -s       | --sources            | Specific sources to use when searching (e.g. `-s duckduckgo,bing`). Use `-ls` to display all available sources.                                                                                                                                                                                                                                           |
| -es      | --exclude-sources    | Specific sources to exclude searching (`-s google,startpage`). Use `-ls` to display all available sources.                                                                                                                                                                                                                                                |
| -cs      | --concurrent-sources | The number of sources to search at the same time (default: `2`). Passing `0` will run **ALL** specified sources at the same time (this could be very resource intensive and negatively affect results).                                                                                                                                                   |
| -ls      | --list-sources       | List all available sources.                                                                                                                                                                                                                                                                                                                               |
| -t       | --timeout            | How many seconds to wait for the source to respond (default: 30 seconds)                                                                                                                                                                                                                                                                                  |
| -sb      | --show-browser       | View the browser instead of using a headless browser. Options: `tabs` (default, opens sources in tabs) or `windows` (opens each source in a separate window). This has an advantage because if there is a known anti-bot mechanism, then it will pause for a set time (determined by `-abt`) so you can manually resolve it before `xnldorker` continues. |
| -abt     | --antibot-timeout    | How many seconds to wait when the `-sb` option was used and a known anti-bot mechanism is encountered (default: 90). This is the time you have to manually respond to the anti-bot mechanism before it tries to continue.                                                                                                                                 |
| -rwos    | --resubmit-without-subs | After the initial search, search again but exclude all subs found previously to get more links.                                                                                                                                                                                                                                          |
| -fp      | --forward-proxy      | Send the links found to a proxy such as Burp or Caido, e.g `http://127.0.0.1:8080`.                                                                                                                                                                                                                                                                       |
| -rp      | --request-proxy      | Browser request proxy to use. Can be a proxy string (e.g. `http://user:pass@1.2.3.4:8000`, `socks5://host:port`) or a file containing proxy list (one per line, random selection).                                                                                                                                                                        |
|          | --debug              | Save page contents on error and leave all browser tabs/windows open until pressing Enter to end the program.                                                                                                                                                                                                                                              |
| -nb      | --no-banner          | Hides the tool banner (it is hidden by default if you pipe input to 'xnldorker') output.                                                                                                                                                                                                                                                                  |
|          | --version            | Show current version number.                                                                                                                                                                                                                                                                                                                              |
| -v       | --verbose            | Verbose output                                                                                                                                                                                                                                                                                                                                            |
| -vv      | --vverbose           | Increased verbose output                                                                                                                                                                                                                                                                                                                                  |

## Examples

### Basic use

```
# For single dork
xnldorker -i redbull.com -v

# For file of dorks
xnldorker -i dorksfile.txt -v
```

or

```
# For single dork
echo "redbull.com" | xnldorker -v

# For file of dorks
cat dorksfile.txt | xnldorker -v
```

(without any advanced search operators (e.g. `site:`, `inurl:`, `intitle:`, etc.) then a domain is assumed and prefied with `site:`. So in this case, `site:redbull.com` is searched for)

### Capture output

In this example, search `google` only and save any links for `redbull.com` that have an extension of `.php`

```
xnldorker -i "site:redbull.com ext:php" -s google -v -o redbull_endpoints.txt
```

The output can also be piped to another command.

<center><img src="https://github.com/xnl-h4ck3r/xnldorker/blob/main/xnldorker/images/example1.png"></center>

## config.yml

The `config.yml` file has the keys which can be updated to suit your needs:

- `KAGI_SESSION_LINK` - Your full Kagi Session Link that can be found on https://kagi.com/settings/user_details
- `GOOGLE_SEARCH_API_KEY` - Your Google Custom Search API Key
- `GOOGLE_SEARCH_CHAT_ID` - Your Google Custom Search Chat ID

## Recommendations

- Using `-v`/`--verbose` is always a good idea when you first start using a tool. It will help you understand what the tool is doing and highlight any potential problems too. Using very verbose mode (`-vv`) can give even more information.
- If you do not need to run silently in the background, **I would recommend using the `-sb`/`--show-browser` argument** because you can see what `xnldorker` is doing (and if it seems to be working ok), plus if there is any known ant-bot detection recognised (currently not for all sources) then you will be notified and have the option to resolve this before `xnldorker` continues.
- If you show the browsers and you get an anti-bot page shown, the process will be paused and wait for the number of seconds specified by `-abt`/`--antibot_timeout` (default 90 seconds). However, it you manually respond to the check and want it to resume quicker, you can enter the name of the source (in lowercase) and press ENTER to resume again.
- The number of concurrent sources processed defaults to 2. This can be changed with `-cs`/`--concurrent-sources`. If you are running `xnldorker` on a low spec VPS, it could be worth setting `-cs 1`. The higher the value of `-cs` the quicker the tool will be, but may affect the quality and quantity of results.
- You may want to run different dorks but write to the same output file. If you use the same output file in `-o`/`--output` then any results will be appended to that file automatically (and de-duplicated). But if you want to overwrite it every time, you can use the `-ow`/`--overwrite-output` argument.
- Use the `--resubmit-without-subs` option to resubmit the same search, but with all previously found subs removed from the search (where possible, dependant on the source).
- If I was looking at a new target, `example.com` I would start with running the command below. I would use `-v` to have more insight into what is happening, `-sb` to show the browsers so that I could respond to ant-bot mechanism if shown, `-rwos` to resubmit the same search but excluding the subdomains found in the first search, and `-o` to specify the output file to save the results:

```sh
xnldorker -i "example.com" -v -t 120 -sb -rwos -o example.com_xnldorker.txt
```

- After the previous point, I would consider changing my VPN to s different region and re-run to potentially get different results.

## Issues

If you come across any problems at all, or have ideas for improvements, please feel free to raise an issue on Github. If there is a problem, it will be useful if you can provide the exact command you ran and a detailed description of the problem. If possible, run with `-v` to reproduce the problem and let me know about any error messages that are given.
Also, if you have problems, it can be useful to use the `-sb`/`--show-browser` option to see what `xnldorker` is doing.
If you use the `--debug` option, then `xnldorker` will try to write a html file of the contents that it got stuck on, e.g. `xnldorker_Google_20240423_133700.html` and will also leave any browser tabs/windows open until you press Enter to end the program. It would also be useful to include these in the github issue.

## TODO

- Bing and Ecosia no longer works because of bot detection. Find a way around it.
- Deal with an issue where sometimes the process can get `Killed` because it uses too much memory.
- Identify anti bot mechanism pages on other sources (it's only on a few at the moment) so that `xnldorker` can pause to manually respond if the browser is being viewed.
- Find our what search operators work on which sources and adjust the `--sources` automatically depending on which sources will get the expected results.
- Add arguments that let you specify a certain time-frame for results which can often be specified with query parameters in the search engine request.
- Add argument that let you specify a certain Region for results which can often be specified with query parameters in the search engine request.

## Google Custom Search Instructions

Follow these instructions to use the `GoogleCS` source.

### Part 1: Setting up a Google Programmable Search Engine and Getting the CSE-ID

The CSE-ID is a unique identifier for your search engine configuration, referred to as the Chat ID.

#### 1. Navigate to the PSE Platform

* Go to the [Google Programmable Search Engine website](https://programmablesearchengine.google.com/) and sign in with your Google Account.

#### 2. Create a New Search Engine

* Click the **"Add"** or **"Get Started"** button to begin the setup.

#### 3. Configure the Engine

* **Name your search engine:** Provide a descriptive name (e.g., "My App Search").
* **What to search?:** Enter the domain(s) or URL pattern(s) you wish to index (e.g., `example.com/*`), or select the `Search the entire web` option.

* Click the **"Create"** button.

#### 4. Retrieve the Search Engine ID (CSE-ID)

* After creation, you will be taken to the engine's **All search engines** page.
* Click the name of the search engine you created.
* The **Search engine ID** is displayed prominently on this page.
* **Copy and save this ID.** It is a long alphanumeric string (e.g., `a5b7c9d1e3f5g7h9i1j3k5l7`).
* Paste this in your `config.yml` file, e.g. `GOOGLE_SEARCH_CHAT_ID: a5b7c9d1e3f5g7h9i1j3k5l7`


### Part 2: Creating an API Key in Google Cloud Console

The API key provides secure access to Google's Custom Search JSON API.

#### Step A: Set up a Project and Enable the API

#### 1. Go to Google Cloud Console

* Navigate to the [Google Cloud Console](https://console.cloud.google.com/) and sign in.

#### 2. Select or Create a Project

* Use the project selector dropdown at the top left to select an existing project or create a **"New Project"**.

#### 3. Enable the Custom Search API

* Use the **Search bar** at the top of the console.
* Search for **"Custom Search API"**.
* Click on the result and click the **"Enable"** button.

#### Step B: Generate and Secure the API Key

#### 1. Navigate to Credentials

* In the left-hand navigation menu, go to **"APIs and services"** -> **"Credentials"**.

#### 2. Generate the API Key

* Click the **"+ Create Credentials"** button at the top.
* Select **"API key"** from the dropdown menu.
* Enter the name you want for your API key, and click **API restrictions** -> **Restrict key**
* Check the **Custom Search API** option, click **OK** and then click **Create**
* Copy the value in **Your API key** IMMEDIATELY
* **Copy and save this key immediately.** and close the window.
* Paste this in your `config.yml` file, e.g. `GOOGLE_SEARCH_API_KEY: Your_API_Key`

## And finally...

Good luck and good hunting!
If you really love the tool (or any others), or they helped you find an awesome bounty, consider [BUYING ME A COFFEE!](https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

🤘 /XNL-h4ck3r

<p>
<a href='https://ko-fi.com/B0B3CZKR5' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
