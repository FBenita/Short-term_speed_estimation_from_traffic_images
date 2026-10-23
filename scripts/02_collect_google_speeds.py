"""Step 2. Collect reference travel times from the Google Maps Directions API.

For each camera-direction pair, a driving route between a fixed origin and destination near the
camera (data/cameras/google_od_pairs.csv) is requested every five minutes, with the departure
time set to the time of the request. The route length and the travel time in traffic are stored,
and speed is computed as length / travel time. Google returns travel times for the present
only, so this script can collect new data but cannot recover past weeks.

Usage
    export GOOGLE_MAPS_API_KEY="your-key"           (Windows: set GOOGLE_MAPS_API_KEY=your-key)
    python scripts/02_collect_google_speeds.py --out data/google_speeds
    python scripts/02_collect_google_speeds.py --out data/google_speeds --once     (single round, for testing)

Output: one CSV per day with columns Route, Camera_id, TimeStamp, Distance_text, Distance_value (m),
Duration_text, Duration_value (s, in traffic) and Speed_kmh. These are the columns of the files
collected in 2022, plus the speed.

Requires: pip install googlemaps pandas. Usage is billed by Google and subject to the Google Maps
Platform Terms of Service. Never write the API key into this file or commit it to the repository.

Adapted from googleMaps_aws_s3_combined.py (2022). The S3 upload and the logging of the key were removed.
"""
import argparse
import datetime as dt
import os
import time

import googlemaps
import pandas as pd


def latlon(s):
    lat, lon = (float(x) for x in str(s).split(","))
    return lat, lon


def one_round(client, od, now):
    rows = []
    for _, r in od.iterrows():
        row = dict(Route=r["Route"], Camera_id=r["Cam_id"], TimeStamp=now, Distance_text=None,
                   Distance_value=None, Duration_text=None, Duration_value=None, Speed_kmh=None)
        try:
            res = client.directions(latlon(r["origin_lat_lon"]), latlon(r["destination_lat_lon"]),
                                    mode="driving", departure_time=now)
            leg = res[0]["legs"][0]
            row.update(Distance_text=leg["distance"]["text"], Distance_value=leg["distance"]["value"],
                       Duration_text=leg["duration_in_traffic"]["text"],
                       Duration_value=leg["duration_in_traffic"]["value"])
            if row["Duration_value"]:
                # m/s to km/h, truncated to whole km/h as in the study
                row["Speed_kmh"] = int(row["Distance_value"] / row["Duration_value"] * 3.6)
        except Exception as e:                       # keep the time stamp with empty values
            print(now, r["Route"], r["Cam_id"], "request failed:", e)
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--od", default="data/cameras/google_od_pairs.csv")
    ap.add_argument("--out", default="data/google_speeds")
    ap.add_argument("--first", default="04:50")
    ap.add_argument("--last", default="23:50")
    ap.add_argument("--step", type=int, default=5, help="minutes between rounds")
    ap.add_argument("--once", action="store_true", help="run a single round now and stop")
    a = ap.parse_args()

    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        raise SystemExit("Set the environment variable GOOGLE_MAPS_API_KEY first.")
    client = googlemaps.Client(key=key)
    od = pd.read_csv(a.od)
    os.makedirs(a.out, exist_ok=True)

    def save(rows, day):
        f = os.path.join(a.out, f"google_speeds_{day.isoformat()}.csv")
        pd.DataFrame(rows).to_csv(f, mode="a", header=not os.path.exists(f), index=False)

    if a.once:
        now = dt.datetime.now().replace(second=0, microsecond=0)
        save(one_round(client, od, now), now.date())
        return

    h0, m0 = map(int, a.first.split(":"))
    h1, m1 = map(int, a.last.split(":"))
    while True:
        now = dt.datetime.now().replace(second=0, microsecond=0)
        start = now.replace(hour=h0, minute=m0)
        end = now.replace(hour=h1, minute=m1)
        if now < start:
            time.sleep((start - dt.datetime.now()).total_seconds())
            continue
        if now > end:                                 # wait for the next day
            time.sleep((start + dt.timedelta(days=1) - dt.datetime.now()).total_seconds())
            continue
        # align to the five-minute grid that starts at the first time stamp
        steps = int((now - start).total_seconds() // (60 * a.step))
        slot = start + dt.timedelta(minutes=a.step * steps)
        save(one_round(client, od, slot), slot.date())
        nxt = slot + dt.timedelta(minutes=a.step)
        time.sleep(max(0.0, (nxt - dt.datetime.now()).total_seconds()))


if __name__ == "__main__":
    main()
