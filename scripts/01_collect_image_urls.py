"""Step 1. Collect traffic camera image links from the data.gov.sg Traffic Images API.

The API returns, for a given time stamp, a link to the latest image of every LTA camera.
The study queried it every five minutes from 04:50 to 23:50 for cameras 2703, 2705, 2706,
2707 and 2708 (Bukit Timah Expressway). The API also answers historical queries, so the
links of the study weeks can be recovered with this script.

Usage
    python scripts/01_collect_image_urls.py --start 2022-06-20 --end 2022-06-26 --out data/image_urls
    python scripts/01_collect_image_urls.py --start 2022-06-20 --end 2022-06-20 --out data/image_urls --download

Output: one CSV per day with columns Cam_ID, Timestamp_sg_time (query time), Image_timestamp
(time the image was taken), URL. With --download the JPEG files are also saved.

Images contain information from the Traffic Images dataset accessed from data.gov.sg, made
available under the Singapore Open Data Licence version 1.0. They may show identifiable
vehicles; check the licence (it grants no rights over personal data) before redistributing them.

Adapted from Filter_by_camera.py (project website, 2020). The Dropbox upload was removed.
"""
import argparse
import datetime as dt
import os
import time

import pandas as pd
import requests

API = "https://api.data.gov.sg/v1/transport/traffic-images"
CAMERAS = ["2703", "2705", "2706", "2707", "2708"]


def query(ts, retries=3):
    for k in range(retries):
        try:
            r = requests.get(API, params={"date_time": ts.strftime("%Y-%m-%dT%H:%M:%S")}, timeout=30)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(2 * (k + 1))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="first day, YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="last day, YYYY-MM-DD")
    ap.add_argument("--out", default="data/image_urls")
    ap.add_argument("--first", default="04:50", help="first time stamp of the day")
    ap.add_argument("--last", default="23:50", help="last time stamp of the day")
    ap.add_argument("--step", type=int, default=5, help="minutes between queries")
    ap.add_argument("--cameras", nargs="+", default=CAMERAS)
    ap.add_argument("--download", action="store_true", help="also save the images")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    day = dt.date.fromisoformat(a.start)
    while day <= dt.date.fromisoformat(a.end):
        h0, m0 = map(int, a.first.split(":"))
        h1, m1 = map(int, a.last.split(":"))
        ts = dt.datetime.combine(day, dt.time(h0, m0))
        stop = dt.datetime.combine(day, dt.time(h1, m1))
        rows = []
        while ts <= stop:
            data = query(ts)
            if data is None:
                print("no response for", ts)
            else:
                for item in data.get("items", []):
                    for cam in item.get("cameras", []):
                        if cam["camera_id"] in a.cameras:
                            rows.append(dict(Cam_ID=cam["camera_id"], Timestamp_sg_time=ts,
                                             Image_timestamp=cam.get("timestamp"), URL=cam["image"]))
            ts += dt.timedelta(minutes=a.step)
            time.sleep(0.2)
        df = pd.DataFrame(rows)
        f = os.path.join(a.out, f"image_urls_{day.isoformat()}.csv")
        df.to_csv(f, index=False)
        print(f"{f}: {len(df)} links, {df['URL'].nunique() if len(df) else 0} distinct images")
        if a.download and len(df):
            img_dir = os.path.join(a.out, "images", day.isoformat())
            os.makedirs(img_dir, exist_ok=True)
            for url in df["URL"].unique():
                target = os.path.join(img_dir, url.rsplit("/", 1)[-1])
                if not os.path.exists(target):
                    r = requests.get(url, timeout=60)
                    if r.status_code == 200:
                        with open(target, "wb") as fh:
                            fh.write(r.content)
        day += dt.timedelta(days=1)


if __name__ == "__main__":
    main()
