#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# linkedin_search.sh
# Opens every LinkedIn search term in a new tab inside your Brave "Jobs" profile
# macOS only — uses AppleScript to open a fresh window, not an existing one
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
DELAY=6                          # seconds between tabs (avoids rate-limiting)
PROFILE_NAME="Jobs"              # must match exactly what Brave shows in the menu
BRAVE="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# ── Search terms ─────────────────────────────────────────────────────────────
SEARCHES=(
  # Core titles
  "hiring \"data scientist\""
  "hiring \"ML engineer\""
  "hiring \"machine learning engineer\""
  "hiring \"analytics engineer\""
  "hiring \"data analyst\""
  "hiring \"applied scientist\""
  "looking for \"data scientist\" OR \"ML engineer\""
  "we're hiring \"data scientist\" Boston"

  # Adjacent roles
  "hiring \"product analyst\""
  "hiring \"quantitative analyst\""
  "hiring \"research scientist\" ML"
  "hiring \"AI engineer\""
  "hiring \"decision scientist\""
  "hiring \"growth analyst\""
  "hiring \"clinical data scientist\""
  "open role \"data scientist\" OR \"analytics engineer\" python"
  "join our team \"data science\" RAG OR LLM"

  # Domain / niche
  "hiring \"data scientist\" healthcare OR \"life sciences\""
  "hiring \"data scientist\" fintech OR \"financial services\""
  "hiring \"data scientist\" \"product analytics\""
  "hiring \"NLP engineer\" OR \"NLP scientist\""
  "hiring data scientist Airflow OR dbt OR Segment"
  "looking to hire python pytorch \"machine learning\""
  "hiring \"behavioral data scientist\" OR \"user data scientist\""
)

# ── Helpers ───────────────────────────────────────────────────────────────────
urlencode() {
  python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$1"
}

build_url() {
  local encoded
  encoded=$(urlencode "$1")
  echo "https://www.linkedin.com/search/results/all/?keywords=${encoded}"
}

find_profile_dir() {
  local state="$HOME/Library/Application Support/BraveSoftware/Brave-Browser/Local State"
  python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
cache = d.get('profile', {}).get('info_cache', {})
for k, v in cache.items():
    if v.get('name') == sys.argv[2]:
        print(k)
        break
" "$state" "$PROFILE_NAME"
}

# ── Pre-flight checks ─────────────────────────────────────────────────────────
if [[ ! -x "$BRAVE" ]]; then
  echo "❌  Brave not found at: $BRAVE"
  echo "    Edit the BRAVE variable at the top of this script with the correct path."
  exit 1
fi

echo "🔍  Locating Brave profile: \"$PROFILE_NAME\" ..."
PROFILE_DIR=$(find_profile_dir)

if [[ -z "$PROFILE_DIR" ]]; then
  echo "❌  Could not find a Brave profile named \"$PROFILE_NAME\"."
  echo "    Open Brave → top-right avatar → check the exact profile name, then"
  echo "    update PROFILE_NAME= at the top of this script."
  exit 1
fi

echo "✅  Found profile directory: $PROFILE_DIR"
echo "🚀  Opening ${#SEARCHES[@]} searches with ${DELAY}s delay between each..."
echo ""

# ── Ensure Brave is running with the right profile ───────────────────────────
if ! pgrep -x "Brave Browser" > /dev/null; then
  "$BRAVE" --profile-directory="$PROFILE_DIR" --no-startup-window &
  sleep 3
fi

# ── Open a brand-new Brave window with the first URL ─────────────────────────
# We use 'make new window' then immediately set its URL, and tag it as
# our target by always referring to 'window 1' after bringing it to front.
# Tracking by window id (-1728 error) is unreliable across AppleScript calls.
FIRST_URL=$(build_url "${SEARCHES[0]}")
echo "  [1/${#SEARCHES[@]}]  ${SEARCHES[0]}"

osascript <<EOF
tell application "Brave Browser"
  activate
  set newWin to make new window
  set URL of active tab of newWin to "${FIRST_URL}"
end tell
EOF

sleep 3   # let the window fully open before we start adding tabs

# ── Open remaining URLs as new tabs in that same window ──────────────────────
# Before each tab, we activate Brave and bring our window to the front
# so it is always 'window 1' — the most reliable AppleScript reference.
for i in "${!SEARCHES[@]}"; do
  [[ $i -eq 0 ]] && continue   # already opened above

  URL=$(build_url "${SEARCHES[$i]}")
  echo "  [$((i+1))/${#SEARCHES[@]}]  ${SEARCHES[$i]}"

  osascript <<EOF
tell application "Brave Browser"
  activate
  set frontWin to window 1
  make new tab at end of tabs of frontWin with properties {URL:"${URL}"}
end tell
EOF

  sleep "$DELAY"
done

echo ""
echo "✅  Done — ${#SEARCHES[@]} tabs opened in your \"$PROFILE_NAME\" profile."
echo "    Switch to Brave, click through the tabs, and sort each by 'Latest'."
