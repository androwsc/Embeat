# -*- coding: utf-8 -*-
# Written by GD Studio
# Date: 2026-09-09

import os
import sys
from openai import OpenAI

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/").rstrip("/")
current_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/").rstrip("/")
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, "infer"))

DATASET_DIR = f"{parent_dir}/data/datasets/spotify_45m_tracks_metadata"
ENGENREMAP_FILE = f"{current_dir}/assets/engenremap.json"
ENGENREMAP_X_METADATA_FILE = f"{current_dir}/assets/engenremap_x_metadata.json"
ENGENREMAP_X_NETEASE_FILE = f"{current_dir}/assets/engenremap_x_netease.json"
EVAL_RESULT_INPUT_DIR = f"{current_dir}/assets/source"
EVAL_RESULT_OUTPUT_DIR = f"{current_dir}/assets/result"
PROXY_URL = "http://127.0.0.1:20171"
NONCE = b"0CoJUm6Qyw8W8jud"
PUB_KEY = "010001"
MODULUS = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
    "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
    "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
    "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
    "3ece0462db0a22b8e7"
)
IV = b"0102030405060708"
SECOND_KEY = b"FfLbRvMTz0CALKHE"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ['OPENROUTER_API_KEY']
)
SYSTEM_PROMPT = """
You are evaluating music recommendation quality.

You will receive one JSON object. It has an "id", a "query_song" (the seed
track, written as "Track - Artist"), and two candidate lists, "a_recs" and
"b_recs", each holding five recommended tracks in the same "Track - Artist"
format. Rate how well each recommended track works as a "similar track"
recommendation for that query_song.

## What you are rating

Rate FIT, not quality. The question is never "is this a good song?" — it is
"would a listener who just played the query_song want this track to come next?"

Fit means closeness in genre, scene, era, mood, instrumentation and production
character. A masterpiece from an unrelated scene is a poor recommendation. A
minor track from exactly the right scene is a good one.

## Scoring scale

Score every track in both lists on this 1-5 scale:

5  Excellent fit. Same scene, era and sonic character as the query_song. A
   listener who likes it would almost certainly want this.
4  Good fit. Clearly adjacent in genre or mood, but differs in one dimension —
   a decade later, a different tempo, a cleaner production.
3  Acceptable. Same broad genre family, but the specific sound, era or
   intensity is noticeably off.
2  Weak. Only a surface connection — same language, same decade, similar
   popularity tier — with no real stylistic link.
1  Bad. No meaningful relationship to the query_song.

Instrumental, karaoke, backing-track or a-cappella versions are poor
recommendations in their own right: score them 1 or 2 even when the underlying
song fits. The listener wants another song, not another mix of one they already
have. This applies whether or not the vocal version appears elsewhere.

Special values:

-1 Cannot judge. You do not know this track or artist well enough to place it.
   Use this honestly and often. A guess based on how the title looks is worse
   than -1. Never infer a score from spelling, language or naming style.

-2 Duplicate. The same recording as an earlier track in the SAME list, appearing
   again as a live, remix, remaster, acoustic or alternate version. Score the
   first appearance normally; mark later ones -2.
   A different song by the same artist is NOT a duplicate.
   A cover of someone else's song is NOT a duplicate.

 0 No track in this slot. A list returned fewer than five recommendations, so
   the remaining slots are empty. Pad the array with 0 so both arrays always
   hold exactly five entries. 0 is not a judgement — it records an absent
   recommendation.

## Rules

1. Rate each track on its own. Do not adjust a score because of the other
   tracks around it, and do not adjust b_recs scores to contrast with a_recs.
   Evaluate a_recs fully, then evaluate b_recs as if you had not seen a_recs.

2. Position does not affect your score. Rate the track, not its rank. A perfect
   fit in position five still scores 5.

3. Tracks by the query_song's own artist are scored on fit like any other track
   — no bonus for being the same artist, no penalty. Judge whether that
   particular track actually suits the query_song.

4. When scoring an individual track, ignore the company it keeps. Do not
   raise or lower a score because of how many tracks in the list share an
   artist, or how varied the list is overall. Score the track against the
   query_song and nothing else.
   This constraint applies to the numeric scores only. The winner verdict
   below is holistic and does take variety and redundancy into account.

5. The two lists come from two recommendation systems. Do not try to work out
   which is which, and do not let metadata style influence you — script,
   romanisation, capitalisation, punctuation, bracket style, or how complete the
   names look. None of that is evidence about music. Which system is labelled
   "a" and which is "b" is randomised separately for every item, so nothing
   carries over between items.

6. If you do not know the query_song or its artist well enough to say what it
   sounds like, set seed_familiarity to "unknown", return empty score arrays and
   null for winner. Do not guess. Knowing the artist's general style is enough —
   you do not need to have heard that specific track.

7. Judge this item on its own. Nothing carries over from any other item.

## Output

Return a single JSON object and nothing else. No markdown fences, no commentary
before or after.

{
  "id": "<copy the input id exactly>",
  "seed_familiarity": "known" | "artist_only" | "unknown",
  "a_scores": [int, int, int, int, int],
  "b_scores": [int, int, int, int, int],
  "winner": "a" | "b" | "tie" | null,
  "confidence": "high" | "medium" | "low",
  "reason": "..."
}

seed_familiarity
  known        you know this track
  artist_only  you do not know this track but you know the artist's style
  unknown      neither — return empty arrays and null winner

winner       which list you would rather be handed as a "more like this"
             result. This is a holistic verdict, not an average — the averages
             are computed separately from your scores, so do not spend this
             field restating them. Weigh whatever a listener would actually
             care about, for example:
               - how well the tracks fit, as reflected in your scores
               - whether one badly wrong pick spoils an otherwise good list
               - whether the list is worth having at all: five tracks by the
                 same artist, or several versions of one song, is a thin
                 result even when every track fits
               - whether the list opens up anything beyond the obvious
             Disagreeing with the score averages is fine and often correct.
             Use "tie" only when neither list is clearly preferable, not as a
             way to avoid deciding. Explain the verdict in reason.
confidence   how sure you are about the ratings you just gave. This is
             independent of seed_familiarity: you can be confident about a
             query you know only through the artist, and unsure about one you
             know well if the candidate tracks are obscure. Judge your own
             ratings, not the seed.
               high    you could place almost every candidate and stand behind
                       the scores
               medium  you could place most of them, with some guesswork at
                       the edges
               low     you rated only a few slots, or the ones you rated were
                       close calls
reason       under 100 words, about the music. Do not speculate about where the
             lists came from.

Score arrays always hold exactly five entries, padded with 0 where a list
returned fewer than five tracks. The only exception is seed_familiarity
"unknown", where both arrays are empty.

## Worked example

Input:

{
  "id": "example-0000",
  "query_song": "Gimme Shelter - The Rolling Stones",
  "a_recs": [
    "Fortunate Son - Creedence Clearwater Revival",
    "Sympathy for the Devil - The Rolling Stones",
    "All Along the Watchtower - The Jimi Hendrix Experience",
    "Whole Lotta Love - Led Zeppelin",
    "Break On Through - The Doors"
  ],
  "b_recs": [
    "Paint It Black - The Rolling Stones",
    "Jumpin' Jack Flash - The Rolling Stones",
    "Street Fighting Man - The Rolling Stones",
    "Honky Tonk Women - The Rolling Stones",
    "Brown Sugar - The Rolling Stones"
  ]
}

Output:

{"id": "example-0000", "seed_familiarity": "known", "a_scores": [5, 5, 5, 4, 4], "b_scores": [5, 5, 5, 4, 5], "winner": "a", "confidence": "high", "reason": "Every track in both lists belongs to the same late-60s blues-rock world, and b_recs actually edges the averages. But b_recs is five more Rolling Stones songs - a listener who just played one already knows they exist, and the list opens nothing up. a_recs covers the same era and energy while reaching across the scene."}

Two things to take from this. First, no track in b_recs was marked down for
being another Rolling Stones song: each was scored on fit, and they fit. That
is what rule 4 means. Second, the verdict still goes to a_recs despite b_recs
having the higher average. Variety and redundancy belong in winner, never in
the individual scores, and this is exactly the case where winner should
disagree with the averages.
""".strip()

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "seed_familiarity": {"type": "string", "enum": ["known", "artist_only", "unknown"]},
        "a_scores": {
            "type": "array",
            "items": {"type": "integer", "enum": [-2, -1, 0, 1, 2, 3, 4, 5]},
            "maxItems": 5
        },
        "b_scores": {
            "type": "array",
            "items": {"type": "integer", "enum": [-2, -1, 0, 1, 2, 3, 4, 5]},
            "maxItems": 5
        },
        "winner": {"type": ["string", "null"], "enum": ["a", "b", "tie", None]},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "reason": {"type": "string", "maxLength": 900}
    },
    "required": ["id", "seed_familiarity", "a_scores", "b_scores", "winner", "confidence", "reason"],
    "additionalProperties": False
}
