# -*- coding: utf-8 -*-
# Written by GD Studio
# Date: 2026-09-09

import base64
import binascii
import json
import re
import requests
import time
import unicodedata
from Crypto.Cipher import AES
from .config import NONCE, PUB_KEY, MODULUS, IV, SECOND_KEY


# AES-128-CBC encryption with PKCS7 padding
def aes_encrypt(text: bytes, key: bytes):
    result = b""
    pad_len = 16 - len(text) % 16
    text = text + bytes([pad_len] * pad_len)
    cipher = AES.new(key, AES.MODE_CBC, IV)
    encrypted = cipher.encrypt(text)
    result = base64.b64encode(encrypted)
    return result


# RSA encryption (no padding) for the second key
def rsa_encrypt(text: bytes):
    result = ""
    text_reversed = text[::-1]
    text_int = int(binascii.hexlify(text_reversed), 16)
    encrypted_int = pow(text_int, int(PUB_KEY, 16), int(MODULUS, 16))
    result = format(encrypted_int, "x").zfill(256)
    return result


# Two-pass AES encryption used by Netease weapi
def encrypt_params(plain_text: str):
    result = {
        "params": "",
        "encSecKey": ""
    }
    # First pass: encrypt with nonce
    first_pass = aes_encrypt(plain_text.encode("utf-8"), NONCE)
    # Second pass: encrypt with fixed second key
    params = aes_encrypt(first_pass, SECOND_KEY).decode("utf-8")
    # RSA encrypt the second key
    enc_sec_key = rsa_encrypt(SECOND_KEY)
    result['params'] = params
    result['encSecKey'] = enc_sec_key
    return result


# Get search result from Netease Music
def get_netease_search(keyword: str, count: int = 5):
    result = []
    url = "https://music.163.com/weapi/cloudsearch/pc"
    payload = json.dumps({
        "s": keyword.strip(),
        "type": 1,
        "offset": 0,
        "limit": count,
        "total": "true"
    })
    encrypted = encrypt_params(payload)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.16 (KHTML, like Gecko) Mobile/15E149 CloudMusic/0.1.2 NeteaseMusic/8.6.40",
        "Referer": "https://music.163.com/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://music.163.com"
    }
    response = requests.post(url, data=encrypted, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Netease API error: code={data.get('code')}, msg={data.get('msg', 'unknown')}")
    items = data.get("result", {}).get("songs", [])
    for item in items:
        artist_alias = []
        for artist in item.get("ar", []):
            for a in artist.get("tns", []):
                if a.strip():
                    artist_alias.append(a.strip())
            for a in artist.get("alias", []):
                if a.strip():
                    artist_alias.append(a.strip())
        result.append({
            "track_id": str(item.get("id", "")),
            "track_name": str(item.get("name", "")),
            "artist_names": [artist.get("name", "") for artist in item.get("ar", [])],
            "album_name": str(item.get("al", {}).get("name", "")),
            "duration": int(int(item.get("dt") or 0) / 1000),
            "artist_alias": artist_alias,
            "source": "netease"
        })
    return result


# Get similar song recommendations from Netease Music
def get_netease_recommendation(track_id: int, count: int = 5):
    result = []
    url = "https://music.163.com/weapi/discovery/simiSong"
    payload = json.dumps({
        "songid": track_id,
        "limit": count,
        "offset": 0
    })
    encrypted = encrypt_params(payload)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.16 (KHTML, like Gecko) Mobile/15E149 CloudMusic/0.1.2 NeteaseMusic/8.6.40",
        "Referer": "https://music.163.com/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://music.163.com"
    }
    response = requests.post(url, data=encrypted, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Netease API error: code={data.get('code')}, msg={data.get('msg', 'unknown')}")
    items = data.get("songs", [])
    for song in items[:count]:
        artist_names = ", ".join(ar.get("name", "") for ar in song.get("artists", []))
        item = {
            "track_id": song.get("id"),
            "track_name": song.get("name", ""),
            "artist_name": artist_names,
            "album_name": song.get("album", {}).get("name", "")
        }
        result.append(item)
    return result


# Get normalized name from MusicBrainz
def get_musicbrainz_track_info(track_name: str = "", artist_name: str = "", isrc: str = "", proxy_url: str = "", retry: int = 5):
    result = {
        "mbid": "",
        "track_name": "",
        "artist_name": "",
        "artists": [],
        "isrc": ""
    }
    track_name = track_name.strip()
    artist_name = artist_name.strip()
    url = "https://musicbrainz.org/ws/2/recording/"
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    #     "Content-Type": "application/json; charset=utf-8",
    #     "Referer": "https://musicbrainz.org/"
    # }
    headers = {"User-Agent": "NeteaseMusic/1.0 ( neteasemusic@163.com )"}
    if proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    else:
        proxies = None
    if isrc:
        query = f"isrc:{isrc.upper()}"
    else:
        query = f'"{track_name}" AND artistname:{artist_name}'
    params = {
        "query": query,
        "limit": 10,
        "fmt": "json"
    }
    try:
        for i in range(retry):
            req = requests.get(url=url, params=params, headers=headers, proxies=proxies, timeout=30)
            if req.status_code == 200:
                break
            # print(f"Failed to request API from MusicBrainz (code {req.status_code}). Retry: {i + 1}")
            time.sleep(5)
        req.raise_for_status()
        items = req.json().get("recordings", [])
        if not items:
            raise ValueError("Result field `recordings` is empty.")
    except Exception as e:
        print(f"Failed to get track info ({track_name} - {artist_name}) from MusicBrainz and skip: {e}")
        result['track_name'] = track_name
        result['artist_name'] = artist_name
        return result
    chosen_item = {}
    isrc = ""
    for item in items:
        isrcs = list(item.get("isrcs") or [])
        if len(isrcs) > 0:
            chosen_item = item
            isrc = isrcs[0]
            break
    if not chosen_item:
        chosen_item = items[0]
    mbid = chosen_item.get("id", "")
    track_name_clean = ""
    artist_name_clean = ""
    track_name_clean = chosen_item.get("title", "")
    artist_credit = chosen_item.get("artist-credit", [])
    if artist_credit:
        artist_name_clean = artist_credit[0].get("artist", {}).get("name", "")
    if track_name_clean and artist_name_clean:
        track_name = track_name_clean
        artist_name = artist_name_clean
    artist_names = [artist_name]
    for credit in artist_credit:
        aliases = credit.get("artist", {}).get("aliases", [])
        if not aliases:
            continue
        for alias in aliases:
            artist_alias_name = alias.get("name", "")
            if artist_alias_name and artist_alias_name not in artist_names:
                artist_names.append(artist_alias_name)
    result['mbid'] = mbid
    result['track_name'] = track_name
    result['artist_name'] = artist_name
    result['artists'] = artist_names
    result['isrc'] = isrc
    return result


# Normalize display name for track/artist (extracted from get_both_recommendation)
def normalize_display(s: str):
    noise = (
        r"remaster(ed)?(\s+\d{4})?|\d{4}\s+remaster(ed)?|digital(ly)?\s+remaster(ed)?"
        r"|radio\s+edit|single\s+(version|edit)|album\s+version|original\s+version"
        r"|bonus\s+track|deluxe(\s+edition)?|expanded(\s+edition)?"
        r"|mono(\s+version)?|stereo(\s+version)?"
        r"|\d+(st|nd|rd|th)\s+anniversary(\s+edition)?"
    )
    keep = (
        r"live|remix|acoustic|instrumental|demo|cover|karaoke|edit|mix"
        r"|reprise|unplugged|extended|club\s+mix|radio\s+mix|version"
    )
    dashes = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uff0d"), "-")
    brackets = str.maketrans({
        "\uff08": "(", "\uff09": ")", "\uff3b": "[", "\uff3d": "]", "\u3010": "(", "\u3011": ")",
        "\u3014": "(", "\u3015": ")", "\uff1a": ":", "\uff0c": ",", "\u3001": ",", "\uff01": "!", "\uff1f": "?",
        "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'", "\u2032": "'", "\u2033": '"',
        "\u2026": "...", "\u3000": " ", "\u00a0": " ",
    })
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s).translate(brackets).translate(dashes)
    s = re.sub(rf"\s*[\(\[]\s*({noise})[^)\]]*[)\]]", "", s, flags=re.I)
    s = re.sub(rf"\s*-\s*({noise})\b.*$", "", s, flags=re.I)
    s = re.sub(r"\s*[\(\[]\s*(feat|ft|featuring|with)\.?\s+[^)\]]*[)\]]", "", s, flags=re.I)
    s = re.sub(r"\s*-\s*(feat|ft|featuring)\.?\s+.*$", "", s, flags=re.I)
    s = re.sub(r"\s+(feat|ft|featuring)\.?\s+.*$", "", s, flags=re.I)
    s = re.sub(rf"\s*-\s*([^-]*\b(?:{keep})\b[^-]*)$", r" (\1)", s, flags=re.I)
    s = re.sub(r"[\(\[]\s*[)\]]", "", s)
    s = re.sub(r"\s*:\s*", ": ", s)
    s = re.sub(r"\s*,\s*", ", ", s)
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" -,;:\u00b7\u30fb/|").strip()
    return s
