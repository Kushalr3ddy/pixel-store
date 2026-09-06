"""
full youtube round-trip test for pixel-store.

encodes a file into a video, uploads it to youtube, waits for youtube to finish
chewing on it (thats where the lossy re-encode happens), pulls it back down and
decodes it, then checks the bytes are still byte-for-byte the original.

this is the REAL test. the local ffmpeg simulation is nice but youtube does its
own thing to the video, this proves the ecc actually holds up against the real deal.

uses its OWN oauth creds, not borrowed from anywhere else:
  - drop a client_secrets.json (Desktop app oauth client) next to this file
  - first run pops a browser to log in, after that it caches token.pickle here

deps this needs on top of the normal pixel-store ones:
  pip install google-api-python-client google-auth-oauthlib yt-dlp

usage:
  python roundtrip_youtube.py                 # tests dummy.pdf
  python roundtrip_youtube.py myfile.zip       # test any file
  python roundtrip_youtube.py myfile.zip --privacy unlisted --pix-size 16 --parity 32
"""

import os
import sys
import time
import pickle
import shutil
import hashlib
import argparse
import subprocess

from pixelstore.encoder import Encoder
from pixelstore.decodr import Decoder

# ---- paths, all relative to this file so it works from anywhere ----
HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS = os.path.join(HERE, "client_secrets.json")
TOKEN_PICKLE = os.path.join(HERE, "token.pickle")

# youtube.upload to push the video, force-ssl so we can poll processing AND delete
# it afterwards for cleanup (readonly alone cant delete)
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def md5(path):
    """plain md5 of a file, so we can compare original vs what came back out."""
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def get_youtube():
    """oauth dance. caches token.pickle so it only nags for a browser login once."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        # refresh silently if we can, otherwise fall back to the browser login
        if creds and creds.expired and creds.refresh_token:
            print("[auth] refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS):
                sys.exit(f"[auth] no client_secrets.json at {CLIENT_SECRETS}. cant login without it.")
            print("[auth] no valid token, opening browser to login...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            # port=0 = grab any free loopback port, works for Desktop oauth clients
            creds = flow.run_local_server(port=0, prompt="consent")
        with open(TOKEN_PICKLE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload(youtube, video_path, title, privacy):
    """resumable upload of the encoded video. returns the youtube video id."""
    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {
            "title": title,
            "description": "pixel-store round-trip test. this is a file stored as a video, not actual footage.",
            "categoryId": "22",  # People & Blogs, doesnt really matter
        },
        "status": {
            "privacyStatus": privacy,          # unlisted by default so we can pull it back with just the link
            "selfDeclaredMadeForKids": False,
        },
    }
    # 5MB chunks, resumable so a flaky connection doesnt nuke the whole upload
    media = MediaFileUpload(video_path, mimetype="video/*", chunksize=5 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"[upload] pushing {video_path} ({os.path.getsize(video_path)//1024} KB)...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[upload] {int(status.progress() * 100)}%", end="\r")
    vid = response["id"]
    print(f"\n[upload] done -> https://youtu.be/{vid}")
    return vid


def wait_until_processed(youtube, video_id, timeout, interval=20):
    """
    poll youtube till its done processing the upload. thats when the lossy re-encode
    is baked in and the video is actually downloadable. bails after `timeout` seconds.
    """
    print("[wait] waiting for youtube to finish processing (this is where it compresses it)...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = youtube.videos().list(part="status,processingDetails", id=video_id).execute()
        items = resp.get("items")
        if not items:
            print("[wait] video not visible yet...")
        else:
            status = items[0].get("status", {})
            upload_status = status.get("uploadStatus")
            proc = items[0].get("processingDetails", {}).get("processingStatus")
            print(f"[wait] uploadStatus={upload_status} processing={proc}", end="\r")
            if upload_status == "processed":
                print("\n[wait] processed.")
                return True
            if upload_status in ("failed", "rejected"):
                sys.exit(f"\n[wait] youtube {upload_status} the video, cant continue.")
        time.sleep(interval)
    print("\n[wait] timed out waiting for processing.")
    return False


def _yt_dlp_cmd():
    """prefer the venv yt-dlp, and wire in node as the js runtime if we can (newer yt-dlp needs it)."""
    venv_bin = os.path.join(os.path.dirname(sys.executable), "yt-dlp")
    ytdlp = venv_bin if os.path.exists(venv_bin) else "yt-dlp"
    args = [ytdlp]
    node = shutil.which("node")
    if node:
        try:
            helptxt = subprocess.run([ytdlp, "--help"], capture_output=True, text=True).stdout
            if "--js-runtimes" in helptxt:
                args += ["--js-runtimes", f"node:{node}"]
        except Exception:
            pass
    return args


def download(video_id, out_dir, retries=6):
    """
    pull the processed video back down with yt-dlp. retries a bit cause the transcode
    sometimes isnt ready the exact second uploadStatus flips to processed.
    """
    os.makedirs(out_dir, exist_ok=True)
    out_tmpl = os.path.join(out_dir, "%(id)s.%(ext)s")
    url = f"https://www.youtube.com/watch?v={video_id}"
    base = _yt_dlp_cmd()

    for attempt in range(1, retries + 1):
        print(f"[download] attempt {attempt}/{retries}...")
        # grab a single mp4 file (progressive) so theres one clean file to decode
        cmd = base + ["-f", "best[ext=mp4]/best", "-o", out_tmpl, "--no-playlist", url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            for f in os.listdir(out_dir):
                if f.startswith(video_id):
                    path = os.path.join(out_dir, f)
                    print(f"[download] got {path} ({os.path.getsize(path)//1024} KB)")
                    return path
        print(f"[download] not ready ({r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'unknown'}), waiting...")
        time.sleep(30)
    return None


def decode_and_check(video_path, original_path):
    """
    decode the downloaded video and compare md5 against the original file.
    wipes extracted_frames first cause the decoder counts frames in there and
    stale frames from an old run will wreck the decode.
    """
    if os.path.exists("extracted_frames"):
        shutil.rmtree("extracted_frames")

    print("[decode] decoding downloaded video...")
    Decoder(video_path).decode_data()  # prints its own checksum OK/MISMATCH too

    decoded = os.path.join("decoded_files", os.path.basename(original_path))
    if not os.path.exists(decoded):
        print(f"[decode] expected output {decoded} never got written.")
        return False

    same = md5(decoded) == md5(original_path)
    print(f"[decode] original md5: {md5(original_path)}")
    print(f"[decode] decoded  md5: {md5(decoded)}")
    return same


def main():
    ap = argparse.ArgumentParser(description="pixel-store youtube round-trip test")
    ap.add_argument("file", nargs="?", default="dummy.pdf", help="file to round-trip (default: dummy.pdf)")
    ap.add_argument("--privacy", default="unlisted", choices=["unlisted", "private", "public"],
                    help="youtube privacy (default unlisted so the link is enough to download)")
    ap.add_argument("--pix-size", type=int, default=16, help="bit cell size, 16 = 4x4 (default)")
    ap.add_argument("--parity", type=int, default=None, help="reed-solomon parity bytes (default: encoder default)")
    ap.add_argument("--poll-timeout", type=int, default=900, help="seconds to wait for youtube processing (default 900)")
    ap.add_argument("--keep-video", action="store_true", help="dont delete the uploaded video after (default deletes it)")
    args = ap.parse_args()

    src = args.file
    if not os.path.exists(src):
        sys.exit(f"file not found: {src}")

    print("=" * 60)
    print(f"round-tripping {src} through youtube")
    print("=" * 60)
    original_md5 = md5(src)
    print(f"[encode] source md5: {original_md5}")

    # 1. file -> video
    enc_kwargs = {"pix_size": args.pix_size}
    if args.parity is not None:
        enc_kwargs["parity"] = args.parity
    Encoder(src, **enc_kwargs).encode()
    avi = os.path.join("output", os.path.splitext(os.path.basename(src))[0] + ".avi")
    if not os.path.exists(avi):
        sys.exit(f"[encode] expected {avi} but it wasnt written")

    youtube = get_youtube()

    # 2. video -> youtube
    title = f"pixelstore-roundtrip-{os.path.basename(src)}-{int(time.time())}"
    video_id = upload(youtube, avi, title, args.privacy)

    ok = False
    try:
        # 3. wait for the lossy re-encode to finish
        if not wait_until_processed(youtube, video_id, args.poll_timeout):
            sys.exit("giving up, youtube took too long to process.")

        # 4. youtube -> video file
        downloaded = download(video_id, "downloaded")
        if not downloaded:
            sys.exit("[download] couldnt pull the video back down.")

        # 5. video -> file + integrity check
        ok = decode_and_check(downloaded, src)
    finally:
        # clean up the uploaded video unless told to keep it. deleting needs the
        # broader youtube scope, so this can fail on readonly+upload tokens - no biggie.
        if not args.keep_video:
            try:
                youtube.videos().delete(id=video_id).execute()
                print(f"[cleanup] deleted uploaded video {video_id}")
            except Exception as e:
                print(f"[cleanup] couldnt delete {video_id} ({e}). delete it by hand if you care.")

    print("=" * 60)
    if ok:
        print("PASS - data survived the youtube round-trip byte-for-byte")
        sys.exit(0)
    else:
        print("FAIL - data came back corrupted, bump --pix-size or --parity and retry")
        sys.exit(1)


if __name__ == "__main__":
    main()
