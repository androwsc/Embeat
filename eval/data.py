# -*- coding: utf-8 -*-
# Written by GD Studio
# Date: 2026-09-12

import datasets
import json
import os
import random
import re
import time
import traceback
import tqdm
from collections import Counter
from typing import Union
from zhconv import convert
from .config import DATASET_DIR, ENGENREMAP_FILE, ENGENREMAP_X_METADATA_FILE, ENGENREMAP_X_NETEASE_FILE, EVAL_RESULT_INPUT_DIR, EVAL_RESULT_OUTPUT_DIR, PROXY_URL
from .api import get_netease_search, get_musicbrainz_track_info


# Fetch preview tracks from engenremap
def get_preview_tracks():
    result = []
    if os.path.isfile(ENGENREMAP_X_METADATA_FILE) and os.path.getsize(ENGENREMAP_X_METADATA_FILE) > 0:
        with open(ENGENREMAP_X_METADATA_FILE, "r", encoding="utf-8") as f:
            result = json.load(f)
        print(f"Loaded {len(result)} preview track items.")
        return result
    print("-> Reading Embeat HF dataset...")
    ds = datasets.load_from_disk(DATASET_DIR)
    try:
        ds = ds['train']
    except Exception:
        pass
    print("-> Reading EveryNoise engenremap.json...")
    with open(ENGENREMAP_FILE, "r", encoding="utf-8") as f:
        engenremap = json.loads(f.read())
    print("-> Filtering HF dataset with engenremap preview_track_id...")
    preview_tracks = [item['preview_track_id'] for item in engenremap if item['preview_track_id']]
    ds = ds.remove_columns(list(set(ds.column_names) - {"track_id", "track_name", "artist_name", "album_name", "isrc", "popularity", "duration", "artist_genre_idx"}))
    ds = ds.filter(lambda x: x['track_id'] in preview_tracks, num_proc=32)
    print(f"-> Combining {len(ds)} intersection items...")
    for ds_item in tqdm.tqdm(ds, total=len(ds)):
        item = {}
        for genre_item in engenremap:
            if ds_item['track_id'] == genre_item['preview_track_id'] and ds_item['artist_genre_idx'] > 0:
                item['index'] = genre_item['index']
                item['genre'] = genre_item['genre']
                item['artist_genre_idx'] = ds_item['artist_genre_idx']
                item['popularity'] = ds_item['popularity']
                item['isrc'] = ds_item['isrc']
                item['spotify_track_id'] = ds_item['track_id']
                item['spotify_track_name'] = ds_item['track_name']
                item['spotify_artist_name'] = ds_item['artist_name']
                item['spotify_album_name'] = ds_item['album_name']
                item['spotify_duration'] = ds_item['duration']
                if item:
                    result.append(item)
                break
    result = sorted(result, key=lambda x: x['index'])
    print(f"Final preview track items: {len(result)}")
    with open(ENGENREMAP_X_METADATA_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2))
    return result


# Basic clean
def clean_name(name: str):
    name = name.strip()
    name = name.split(" (")[0].strip()
    if len(name.split(" - ")) == 2:
        name = name.split(" - ")[0].strip()
    return name


# Deep clean
def normalize_name(name: Union[str, list]):
    result = []
    if isinstance(name, str):
        names = [name]
        is_batch = False
    else:
        names = name
        is_batch = True
    for name in names:
        name = clean_name(name)
        name = convert(name, locale="zh-hans")
        name = name.lower().strip()
        if name and name not in result:
            result.append(name)
    if is_batch:
        return result
    return result[0] if result else ""


# Get Netease recommendation result and clean track info
def netease_search_preview_tracks():
    def run_netease_search(spotify_track_name: str, spotify_artist_name: str, spotify_duration: int, match_track_name_only: bool = False, count: int = 5):
        if match_track_name_only:
            keyword = spotify_track_name.strip()
        else:
            keyword = f"{spotify_artist_name} {spotify_track_name}".strip()
        if not keyword:
            return
        try:
            netease_items = get_netease_search(keyword=keyword, count=count)
        except Exception:
            print(f"Error in `run_netease_search`: {keyword}")
            traceback.print_exc()
            return
        spotify_track_name = normalize_name(spotify_track_name)
        spotify_artist_name = normalize_name(spotify_artist_name)
        for i, netease_item in enumerate(netease_items):
            netease_track_name = normalize_name(netease_item['track_name'])
            netease_artist_names = normalize_name(netease_item['artist_names'])
            netease_artist_alias = normalize_name(netease_item['artist_alias'])
            if match_track_name_only:
                artist_ok = any(spotify_artist_name in artist or artist in spotify_artist_name for artist in netease_artist_names + netease_artist_alias)
                if i == 0 and netease_item['duration'] == spotify_duration and artist_ok:
                    return netease_item
                if netease_track_name == spotify_track_name and netease_item['duration'] == spotify_duration:
                    if artist_ok or len(spotify_track_name) >= 4:
                        return netease_item
            else:
                if (netease_track_name in spotify_track_name or spotify_track_name in netease_track_name) and (spotify_artist_name in netease_artist_names or spotify_artist_name in netease_artist_alias):
                    if abs(netease_item['duration'] - spotify_duration) <= 1:
                        return netease_item

    def save_json(result: list):
        result = sorted(result, key=lambda x: x['index'])
        with open(ENGENREMAP_X_NETEASE_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"Saved items: {len(result)}")

    def run_patch(result: list):
        spotify_items = []
        if os.path.isfile(ENGENREMAP_X_METADATA_FILE) and os.path.getsize(ENGENREMAP_X_METADATA_FILE) > 0:
            with open(ENGENREMAP_X_METADATA_FILE, "r", encoding="utf-8") as f:
                spotify_items = json.load(f)
        result = [item for item in result if item['artist_genre_idx'] > 0]
        for item in result:
            if "popularity" not in item:
                for spotify_item in spotify_items:
                    if item['spotify_track_id'] == spotify_item['spotify_track_id']:
                        item['popularity'] = spotify_item['popularity']
            if "genre" not in item:
                for spotify_item in spotify_items:
                    if item['spotify_track_id'] == spotify_item['spotify_track_id']:
                        item['genre'] = spotify_item['genre']
        return result

    result = []
    if os.path.isfile(ENGENREMAP_X_NETEASE_FILE) and os.path.getsize(ENGENREMAP_X_NETEASE_FILE) > 0:
        with open(ENGENREMAP_X_NETEASE_FILE, "r", encoding="utf-8") as f:
            result = json.load(f)
        result = run_patch(result)
        save_json(result)
    matched_ids = [item['spotify_track_id'] for item in result]
    preview_tracks = get_preview_tracks()
    for i, spotify_item in enumerate(tqdm.tqdm(preview_tracks, total=len(preview_tracks))):
        if i > 0 and i % 100 == 0:
            save_json(result)
        if spotify_item['spotify_track_id'] in matched_ids:
            continue
        time.sleep(max(1.0, round(random.uniform(2, 3) * random.random(), 3)))
        result_item = {}
        netease_item = {}
        spotify_track_name = clean_name(spotify_item['spotify_track_name'])
        spotify_artist_name = clean_name(spotify_item['spotify_artist_name'])
        spotify_duration = spotify_item['spotify_duration']
        netease_item = run_netease_search(spotify_track_name=spotify_track_name, spotify_artist_name=spotify_artist_name, spotify_duration=spotify_duration, count=5)
        if not netease_item:
            print(f"Failed to get `{spotify_track_name} - {spotify_artist_name}` from Netease Music. Try to clean song info via MusicBrainz...")
            if spotify_item['isrc']:
                mb_result = get_musicbrainz_track_info(isrc=spotify_item['isrc'], proxy_url=PROXY_URL)
            else:
                mb_result = get_musicbrainz_track_info(track_name=spotify_track_name, artist_name=spotify_artist_name, proxy_url=PROXY_URL)
            if mb_result:
                mb_track_name = mb_result['track_name']
                mb_artist_name = mb_result['artist_name']
                netease_item = run_netease_search(spotify_track_name=mb_track_name, spotify_artist_name=mb_artist_name, spotify_duration=spotify_duration, count=5)
        if not netease_item:
            print(f"Failed to get `{spotify_track_name} - {spotify_artist_name}` from Netease Music. Try to search by track_name only...")
            netease_item = run_netease_search(spotify_track_name=spotify_track_name, spotify_artist_name=spotify_artist_name, spotify_duration=spotify_duration, match_track_name_only=True, count=20)
        if not netease_item:
            print(f"Failed and skip.")
            continue
        result_item.update(spotify_item)
        result_item.update({
            "netease_track_id": netease_item['track_id'],
            "netease_track_name": netease_item['track_name'],
            "netease_artist_name": ", ".join(netease_item['artist_names']),
            "netease_album_name": netease_item['album_name'],
            "netease_duration": netease_item['duration']
        })
        result.append(result_item)
    save_json(result)
    return result


# Build eval data sets by rules
def build_eval_set():
    RE_ZH = re.compile(
        r"(chinese|mandopop|cantopop|c-pop|taiwan|hong kong|cantonese"
        r"|sichuan|shanghai|southern china|xinyao|sinogaze|fo jing|macau)", re.I)
    RE_KO = re.compile(r"(k-pop|korean|joseon|dong-yo)", re.I)
    RE_JA = re.compile(
        r"(j-pop|j-rock|j-rap|j-idol|j-indie|j-division|japanese|vocaloid|anime"
        r"|seiyu|doujin|kayo|denpa|48g|ryukyu|ryukoka|okinawan|shojo|oshare"
        r"|jirai|visual kei|city pop|otacore|kawaii)", re.I)
    RE_EXCLUDE = re.compile(
        r"(classical|romanticism|baroque|chamber choir|opera\b|operetta"
        r"|asmr|meditation|lullab|white noise|sleep|background|bgm|karaoke"
        r"|nursery|children's music|focus)", re.I)
    RE_EXCLUDE_ESCAPE = re.compile(
        r"(pop|rock|jazz|drill|psych|folk|metal|punk|rap|hip hop|house|techno"
        r"|trance|indie|soul|funk|disco|wave)", re.I)
    OUTPUT_BY = "window"  # window / region
    TARGET_ZH = 44
    TARGET_JA = 25
    TARGET_KO = 19
    TARGET_NON_CJK = 88
    WINDOW_COUNT = 1
    SHUFFLE_SEED = 616
    DROP_GENRES = ["new rave", "anadolu rock", "pet calming", "phonk"]

    def classify_country_by_genre(genre: str):
        if RE_ZH.search(genre):
            return "zh"
        if RE_KO.search(genre):
            return "ko"
        if RE_JA.search(genre):
            return "ja"
        return "other"

    def is_genre_excluded(genre: str):
        if not RE_EXCLUDE.search(genre):
            return False
        return not RE_EXCLUDE_ESCAPE.search(genre)

    def systematic_sampling(rows: list, target_count: int):
        rows = sorted(rows, key=lambda r: r['index'])
        if len(rows) <= target_count:
            return rows
        stride = len(rows) // target_count
        samples = rows[::stride][:target_count]
        return samples

    def build_seeds(all_rows: list):
        kept_rows = []
        dropped_count = 0
        excluded_count = 0
        for row in all_rows:
            if row['genre'] in DROP_GENRES:
                dropped_count = dropped_count + 1
                continue
            # if is_genre_excluded(row['genre']):
            #     excluded_count = excluded_count + 1
            #     continue
            kept_rows.append(row)
        print(f"Dropped {dropped_count} rows for spotify-netease mismatching. Dropped {excluded_count} rows for low quality metadata genre.")
        pools = {
            "zh": [],
            "ja": [],
            "ko": [],
            "other": []
        }
        for row in kept_rows:
            genre_country = classify_country_by_genre(row['genre'])
            pools[genre_country].append(row)
        target_counts = {
            "zh": TARGET_ZH,
            "ja": TARGET_JA,
            "ko": TARGET_KO,
            "other": TARGET_NON_CJK
        }
        seeds = {}
        for region, pool in pools.items():
            seeds[region] = []
            rows = systematic_sampling(rows=pool, target_count=target_counts[region])
            for row in rows:
                seeds[region].append({
                    "index": row["index"],
                    "genre": row["genre"],
                    "popularity": row["popularity"],
                    "isrc": row["isrc"],
                    "spotify_track_id": row["spotify_track_id"],
                    "spotify_track_name": row["spotify_track_name"],
                    "spotify_artist_name": row["spotify_artist_name"],
                    "netease_track_id": row["netease_track_id"],
                    "netease_track_name": row["netease_track_name"],
                    "netease_artist_name": row["netease_artist_name"],
                    "duration": row["spotify_duration"],
                    "region": region
                })
            print(f"{region}: {len(pool)} -> {len(seeds[region])}")
        return seeds

    def write_by_region(seeds: list):
        groups = {
            "zh": seeds['zh'],
            "ja_ko": seeds['ja'] + seeds['ko'],
            "non_cjk": seeds['other']
        }
        for region, rows in groups.items():
            rows = sorted(rows, key=lambda r: r['index'])
            path = os.path.join(EVAL_RESULT_INPUT_DIR, f"eval_region_{region}.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(rows, ensure_ascii=False, indent=2))
            print(f"[region={region}] Write {len(rows)} items to: {path}")

    def write_by_window(seeds: list):
        rng = random.Random(SHUFFLE_SEED)
        buckets = [[] for _ in range(WINDOW_COUNT)]
        for region in ["zh", "ja", "ko", "other"]:
            rows = list(seeds[region])
            rng.shuffle(rows)
            for i, row in enumerate(rows):
                rr_chosen_bucket = i % WINDOW_COUNT
                buckets[rr_chosen_bucket].append(row)
        for i, bucket in enumerate(buckets):
            rng.shuffle(bucket)
            path = os.path.join(EVAL_RESULT_INPUT_DIR, f"eval_window_{i}.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(bucket, ensure_ascii=False, indent=2))
            region_distribution = Counter(row['region'] for row in bucket)
            print(f"[window={i + 1}]: Write {len(bucket)} items {dict(region_distribution)}: {path}")

    with open(ENGENREMAP_X_NETEASE_FILE, encoding="utf-8") as f:
        all_rows = json.load(f)
    print(f"Loaded {len(all_rows)} spotify-netease matched tracks.")
    os.makedirs(EVAL_RESULT_INPUT_DIR, exist_ok=True)
    os.makedirs(EVAL_RESULT_OUTPUT_DIR, exist_ok=True)
    seeds = build_seeds(all_rows)
    if OUTPUT_BY == "window":
        write_by_window(seeds)
    elif OUTPUT_BY == "region":
        write_by_region(seeds)
    else:
        raise ValueError(f"Error in func `{build_eval_set}`: Unknown OUTPUT_BY: {OUTPUT_BY}")
