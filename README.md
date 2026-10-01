# YouTube Organize: a free Claude Code plugin

**Turn a messy pile of YouTube Liked videos into neat, private playlists sorted by topic, in one conversation with Claude.**

You've liked hundreds of videos and can never find anything again. This plugin fixes that:

1. Claude reads your Liked videos (or Watch Later).
2. It suggests 10–20 topics, like "Cooking", "Python Tutorials" or "Travel", and **you** approve or rename them.
3. It sorts every video, shows you counts and sample titles, and lets you fix anything.
4. When you say "go", it builds **private** playlists on your YouTube account.

**Safe by design**
- Uses Google's official YouTube API with your own key. No third-party servers.
- Playlists are created **private**.
- It **never deletes or removes** anything from your account.
- Free. YouTube's free daily limit covers about 190 videos per day, and bigger libraries resume the next day automatically.

---

## Install (Claude Code)

In Claude Code, run these two commands:

```
/plugin marketplace add dentalsilutionsnic/youtube_organizer_gr3cko
/plugin install youtube-organize@youtube-organize
```

Then just ask:

> Organize my YouTube Liked videos into playlists by topic.

Claude walks you through everything step by step, including the one-time Google setup below. No coding needed.

## What you need

- A Mac, Windows or Linux computer with **Python 3** (Claude checks this and helps you install it)
- A Google account with your YouTube library
- About 10 minutes for the one-time Google Cloud setup (free, no credit card)

## The one-time Google setup, in short

Google requires each person to create their own free API key. Claude guides you through each click, but here's the overview:

1. Go to **console.cloud.google.com** and create a project called `YouTubeOrganize`.
2. Turn on **YouTube Data API v3**.
3. In **Google Auth Platform**, set up the app as **External** and add your own Gmail as a **test user**.
4. Create a **Desktop app** client and **Download JSON**. Save it as `client_secret.json` in your project folder.
5. The first time it runs, a Google sign-in page opens. Google will say *"Google hasn't verified this app"*. That's expected, because it's **your own** app. Click **Continue** and allow YouTube access.

> 🔒 Never share or upload `client_secret.json` or `token.json`. They're your private keys.

## Watch Later

YouTube's API can't read Watch Later, so this plugin uses a **Google Takeout** export instead. Claude explains how when you ask.

## Running it again later

Liked more videos? Ask Claude to *"sort my new Liked videos into my existing playlists"*. It only sorts the new ones, and nothing gets added twice.

## FAQ

**Is it really free?** Yes. The plugin is MIT-licensed, and Google's API quota is free.

**Will it touch my existing playlists or likes?** It never removes anything. It only creates new private playlists and adds videos to them.

**It stopped halfway.** You probably hit YouTube's daily limit. Run it again tomorrow and it picks up where it left off.

## License

MIT © Gr3cko.G0rdon. Free to use, change and share.
