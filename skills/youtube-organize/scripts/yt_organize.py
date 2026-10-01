#!/usr/bin/env python3
"""yt_organize.py - dump your YouTube videos to JSON, then build topic playlists from an assignments file.

Usage (run from your project folder, e.g. ~/Documents/YouTubeOrganize):
  python3 yt_organize.py dump liked                    -> data/videos.json  (your Liked videos)
  python3 yt_organize.py dump takeout "Watch later.csv" -> data/videos.json  (Watch Later, via Google Takeout)
  python3 yt_organize.py apply                         -> reads data/assignments.json, creates + fills playlists

State lives in data/: videos.json, assignments.json ({videoId: topic}), playlists.json, added.json.
Everything is resumable: re-running 'apply' skips playlists and videos already done.
"""
import csv, json, os, re, sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube"]
DATA = Path("data"); DATA.mkdir(exist_ok=True)
VIDEOS, ASSIGN, PLAYLISTS, ADDED = (DATA / f for f in ("videos.json", "assignments.json", "playlists.json", "added.json"))

def load(p, default): return json.loads(p.read_text()) if p.exists() else default
def save(p, obj): p.write_text(json.dumps(obj, indent=1, ensure_ascii=False))

def youtube():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES) if os.path.exists("token.json") else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
        else: creds = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES).run_local_server(port=0)
        Path("token.json").write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def paged(req_fn, **kw):
    token = None
    while True:
        resp = req_fn(pageToken=token, maxResults=50, **kw).execute()
        yield from resp.get("items", [])
        token = resp.get("nextPageToken")
        if not token: return

def slim(vid, sn):
    return {"id": vid, "title": sn.get("title", ""), "channel": sn.get("videoOwnerChannelTitle") or sn.get("channelTitle", ""),
            "description": sn.get("description", "")[:160]}

def dump_liked(yt):
    likes_id = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["likes"]
    vids = [slim(i["contentDetails"]["videoId"], i["snippet"])
            for i in paged(yt.playlistItems().list, part="snippet,contentDetails", playlistId=likes_id)]
    save(VIDEOS, vids); print(f"saved {len(vids)} liked videos -> {VIDEOS}")

def dump_takeout(yt, csv_path):
    ids = []
    for row in csv.reader(open(csv_path, encoding="utf-8-sig")):
        ids += [c.strip() for c in row if re.fullmatch(r"[A-Za-z0-9_-]{11}", c.strip())]
    ids, vids = list(dict.fromkeys(ids)), []
    for i in range(0, len(ids), 50):
        resp = yt.videos().list(part="snippet", id=",".join(ids[i:i + 50])).execute()
        vids += [slim(v["id"], v["snippet"]) for v in resp.get("items", [])]
    save(VIDEOS, vids); print(f"saved {len(vids)} of {len(ids)} watch-later videos -> {VIDEOS} (missing ones are deleted/private)")

def is_quota(e): return e.resp.status == 403 and b"quota" in e.content

def apply(yt):
    assign, playlists, added = load(ASSIGN, {}), load(PLAYLISTS, {}), set(load(ADDED, []))
    if not assign: sys.exit(f"{ASSIGN} is missing or empty - classify the videos first")
    try:
        for topic in sorted(set(assign.values())):
            if topic not in playlists:
                body = {"snippet": {"title": topic}, "status": {"privacyStatus": "private"}}
                playlists[topic] = yt.playlists().insert(part="snippet,status", body=body).execute()["id"]
                save(PLAYLISTS, playlists); print(f"created private playlist '{topic}'")
        todo = [(v, t) for v, t in assign.items() if v not in added]
        for n, (vid, topic) in enumerate(todo, 1):
            body = {"snippet": {"playlistId": playlists[topic], "resourceId": {"kind": "youtube#video", "videoId": vid}}}
            try: yt.playlistItems().insert(part="snippet", body=body).execute()
            except HttpError as e:
                if is_quota(e): raise
                print(f"skipped {vid} (HTTP {e.resp.status}, probably deleted or private)")
            added.add(vid); save(ADDED, sorted(added))
            print(f"[{n}/{len(todo)}] {vid} -> {topic}")
    except HttpError as e:
        if is_quota(e): sys.exit("Daily YouTube API quota used up. Run 'apply' again tomorrow - progress is saved and resumes automatically.")
        raise
    print("done - every assigned video is in its topic playlist")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:2] == ["dump", "liked"]: dump_liked(youtube())
    elif a[:2] == ["dump", "takeout"] and len(a) == 3: dump_takeout(youtube(), a[2])
    elif a == ["apply"]: apply(youtube())
    else: sys.exit(__doc__)
