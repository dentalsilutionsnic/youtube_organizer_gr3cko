---
name: youtube-organize
description: Organize a YouTube library - Liked videos or Watch Later - into topic playlists. Use this whenever the user mentions sorting, categorizing, cleaning up, or organizing their YouTube liked videos, watch later list, saved videos, or playlists by subject, even if they don't say "playlist". Dumps the videos with scripts/yt_organize.py, has Claude classify them by topic, then bulk-creates private playlists via the official YouTube Data API.
---

# YouTube Organize

Three steps: **dump** videos to a JSON file → **classify** them (you do this, in the conversation) → **apply** to create and fill playlists. All plumbing is in `${CLAUDE_SKILL_DIR}/scripts/yt_organize.py` (~100 lines); read it if anything behaves unexpectedly.

The user may not be a developer. Explain each step in plain language, tell them exactly where to click, and wait for them whenever they have to do something.

## Facts that shape this skill
- The official YouTube Data API **can** read Liked videos but **cannot** read Watch Later - it returns an empty list. Watch Later comes in via a Google Takeout CSV instead.
- Free quota is 10,000 units/day. Creating a playlist or adding one video costs 50 units, so about **190 videos/day**. The script saves progress and resumes; a big library takes several days of running `apply`. Tell the user this up front.
- Playlists are created **private**. The script never deletes or removes anything from the user's account. Never add code that does.
- Never commit, upload or paste the contents of `client_secret.json` or `token.json`.

## One-time setup
1. **Project folder**: create `~/Documents/YouTubeOrganize` (or the user's choice) and copy `${CLAUDE_SKILL_DIR}/scripts/yt_organize.py` into it. Run every command from that folder.
2. **Python + libraries** (a private virtual environment keeps the user's system untouched, and works with both Apple's and Homebrew's Python):
   `python3 -m venv .venv && .venv/bin/pip install -q google-api-python-client google-auth-oauthlib`
   On a Mac without Python, `python3` offers to install the Command Line Tools - click Install, then re-run.
3. **Google Cloud Console** (console.cloud.google.com), signed in with the YouTube account:
   - Project picker → **New project** → name it `YouTubeOrganize` → Create, then select it.
   - **APIs & Services → Library** → search **YouTube Data API v3** → **Enable**.
   - **Google Auth Platform** (formerly "OAuth consent screen") → **Get started**: app name, support email → Audience **External** → contact email → agree to the policy → Create.
   - **Audience → Test users → Add users** → the user's own Gmail → Save.
   - **Clients → Create client** → Application type **Desktop app** → Create → **Download JSON** (only possible before closing that dialog). Save it in the project folder as `client_secret.json`.
4. The first run opens the browser to sign in. Tell the user: pick their account → "Google hasn't verified this app" is expected (it is their own app) → **Continue** (or Advanced → Go to …) → allow YouTube access → close the tab. A `token.json` is saved so it doesn't ask again.

If your own shell cannot reach googleapis.com (sandboxed environments), give the user the commands to paste into their Mac/PC terminal instead, one at a time.

## Step 1 - Dump
- Liked videos: `.venv/bin/python yt_organize.py dump liked`
- Watch Later: user goes to takeout.google.com → deselect all → select **YouTube and YouTube Music** → "All YouTube data included" → keep only **playlists** → export. Unzip, find `Takeout/YouTube and YouTube Music/playlists/Watch later-videos.csv`, then `.venv/bin/python yt_organize.py dump takeout "<path to that csv>"`.

Output: `data/videos.json`, a list of `{id, title, channel, description}`. Python version warnings printed by Google's libraries are harmless.

## Step 2 - Classify (token-efficient)
Do NOT read thousands of full entries into context. Instead:
1. Run a one-liner that groups `videos.json` by channel: channel name, count, and 3 sample titles, sorted by count. Read that summary. (For a small library, under ~200 videos, reading `channel | title` for every video is fine and more accurate.)
2. Propose **10-20 topics** with a one-line definition each. Ask the user to approve, rename, merge or split them - topic names become playlist titles.
3. Write a small `classify.py` in the project folder: a `channel -> topic` map for the big channels, a `keyword -> topic` map for titles, and a fallback topic like "Misc" (or an explicit video-id map for small libraries). Have it write `data/assignments.json` as `{"videoId": "Topic", ...}` and print per-topic counts plus 5 sample titles per topic.
4. Show the counts and samples. Let the user re-route channels or fix individual videos. Iterate until they say go. Only the leftover "Misc" titles should ever need reading one by one.

**Re-runs (new videos since last time):** after a fresh dump, classify only the video ids that are not already keys in `data/assignments.json`, prefer the existing topics, merge them into that file, and keep every existing entry unchanged.

## Step 3 - Apply
`.venv/bin/python yt_organize.py apply` - creates one private playlist per topic (reusing any listed in `data/playlists.json`), adds the videos, logs each one in `data/added.json` so nothing is added twice. If it stops with a quota message, tell the user to run it again the next day. Videos that were deleted or made private are skipped and reported.

## Verify
Open youtube.com → You → Playlists and spot-check a couple of the new playlists against the counts from step 2. If the user wants to slim down the original list afterwards, that's manual in YouTube's UI - this skill deliberately does not remove anything.
