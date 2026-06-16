# linkedin-brave-blaster

Opens 24 LinkedIn job search tabs in one shot, inside a specific Brave profile, without touching your other profiles or windows.

---

## What it does

Builds percent-encoded LinkedIn search URLs from a list of hiring keywords, launches Brave into the right profile if it isn't already open, creates a single window, and floods it with tabs — one per search term. Takes about 48 seconds to finish.

---

## Usage

```bash
chmod +x main.sh
./main.sh
```

Tweak the config block at the top before running:

```bash
DELAY=2              # seconds between tabs
PROFILE_NAME="Jobs"  # your Brave profile's display name
```

---

## Requirements

Nothing to install. Everything used ships with macOS:

- `bash` (via `env`, not system bash)
- `python3` — URL encoding and JSON parsing
- `osascript` — AppleScript bridge to Brave
- `pgrep` — checks if Brave is already running
- Brave Browser installed at `/Applications/Brave Browser.app`

---

## How it works

Reads `~/Library/Application Support/BraveSoftware/Brave-Browser/Local State` to match your profile's display name to its internal directory (`Profile 8`, `Default`, etc.), then passes that to Brave via `--profile-directory`. Each tab is opened through a fresh `osascript` subprocess using `window 1` as a live positional reference rather than a stored window ID.

---

## License

View-only. See root [`README.md`](../README.md).
