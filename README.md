# Reddit CLI

A lightweight terminal-based Reddit client built with Textual, using JSON feeds to serve threads.

Browse subreddit feeds via RSS or JSON, navigate posts with Vim-style bindings, and view content directly in your terminal.

Works via Reddit feeds to avoid paid API requirements.

---

## Getting Your JSON/RSS Feed for Your Personal Frontpage

Reddit provides a personal feed for your subreddit subscriptions.

You can find them on the [feeds page](https://www.reddit.com/prefs/feeds).

These are private feeds with an access token and the link should not be shared as the token can never be revoked.

## Other Feeds

You can get feeds for any subreddit by appending `/.rss` or `/.json` to the end of a url, e.g. `https://www.reddit.com/r/python/.json`

Example feeds are included in `config.sample.yaml`.

# JSON vs RSS

Both types of feed are supported but JSON is superior as it includes much more information. I originally designed this for RSS, but this will likely be deprecated at a later date.

---

## Quick Start

### Prerequisites

- Python 3.11+ (tested on 3.13.11)
- A modern terminal with Unicode support
- Optional: Kitty, iTerm2, or other image-capable terminals for best image support (your image-support mileage may vary)

---

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 2. Install the project

```bash
pip install -e .
```

This installs the project in editable mode.

---

### 3. Configure feeds (optional)

If `config.yaml` does not exist, copy the sample:

```bash
cp config.sample.yaml config.yaml
```

Example configuration:

```yaml
feeds:
    - name: All
    url: https://www.reddit.com/r/all/.json

    - name: reddit.com (time capsule)
    url: https://www.reddit.com/r/reddit.com/.json

    - name: Python
    url: https://www.reddit.com/r/python/.json

    - name: Linux
    url: https://www.reddit.com/r/linux/.json

    - name: Programming
    url: https://www.reddit.com/r/programming/.json

theme: default
```

You can add or remove feeds as you like.

---

### 4. Run the application

```bash
python app.py
```

**OPTIONAL:** Boss Mode! Want to browse Reddit from your Terminal without having REDDIT CLI splashed across the top of the page? Use `--boss-mode`

```bash
python app.py --boss-mode
```

Boss mode will alter the ASCII art to be work related, powered by synergy! It also does not load any images.

---

## Controls

### Feed List

- j / ↓ – Move down
- k / ↑ – Move up
- Ctrl+D – Page down
- Ctrl+U – Page up
- Enter – Open feed
- q – Quit

### Post List

- j / ↓ – Move down
- k / ↑ – Move up
- Ctrl+D – Page down
- Ctrl+U – Page up
- Enter – View post
- h / ← – Go back
- r – Refresh feed

At the bottom of the feed:
- Ctrl+L – Load more posts

### Post Detail

- j / k – Scroll
- Ctrl+D – Page down
- Ctrl+U – Page up
- h / ← – Go back

---

## Features

- RSS-based Reddit browsing
- Themed UI (Textual CSS themes)
- Scrollable post viewer
- State stack navigation
- Vim-style keybindings
- No Reddit API required

---

## Themes

Themes are located in:

```bash
src/reddit_cli/style/themes/
```

Each theme is a .tcss file.

To create a custom theme:

1. Copy default.tcss
2. Rename it (example: mytheme.tcss)
3. Modify styles
4. Set in config.yaml:

I have included one additional theme called 'terrible' as an example.

```yaml
theme: mytheme
```

Restart the app to apply changes.

---

## Project Structure

```bash
app.py                     – Application entry point
config.sample.yaml         – Example configuration
config.yaml                – User configuration
pyproject.toml             – Project metadata & dependencies

src/reddit_cli/
    common.py              – Shared models and structures
    feed_handlers.py       – Feed parsing logic
    utils.py               – Helper utilities
    style/
        themes/            – Textual CSS themes
    states/                – States/State Manager
        ...
```