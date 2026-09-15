# -*- coding: utf-8 -*-
# Written by GD Studio
# Date: 2026-09-15

import json
import os
import random
import tqdm
import sys
import uuid
from typing import Literal
from .config import EVAL_RESULT_INPUT_DIR, EVAL_RESULT_OUTPUT_DIR, PROXY_URL, SYSTEM_PROMPT, RESPONSE_SCHEMA, client
from .api import get_netease_recommendation, get_musicbrainz_track_info, normalize_display
from .data import get_preview_tracks, netease_search_preview_tracks, build_eval_set

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/").rstrip("/")
sys.path.insert(0, parent_dir)
from infer.Embeat import EmbeatDatabase


# Get Embeat and Netease recommendation result for eval data sets
def get_both_recommendation():
    ed = EmbeatDatabase(verbose_log=False, same_artist_ratio_range=[0.0, 0.0])
    eval_sources = [os.path.join(EVAL_RESULT_INPUT_DIR, str(file)) for file in os.listdir(EVAL_RESULT_INPUT_DIR) if str(file).endswith(".json")]
    for eval_source in eval_sources:
        eval_file_name = os.path.splitext(os.path.basename(eval_source))[0]
        output_question_json = f"{EVAL_RESULT_OUTPUT_DIR}/{eval_file_name}.json"
        output_answer_json = f"{EVAL_RESULT_OUTPUT_DIR}/{eval_file_name}_ab.json"
        with open(eval_source, "r", encoding="utf-8") as f:
            candidates = json.load(f)
        question_result, question_result_json = [], []
        answer_result, answer_result_json = {}, {}
        if os.path.isfile(output_question_json) and os.path.getsize(output_question_json) > 0:
            with open(output_question_json, "r", encoding="utf-8") as f:
                question_result_json = json.load(f)
        if os.path.isfile(output_answer_json) and os.path.getsize(output_answer_json) > 0:
            with open(output_answer_json, "r", encoding="utf-8") as f:
                answer_result_json = json.load(f)
        for item in question_result_json:
            if not item:
                continue
            item_id = item['id']
            if item['id'] in answer_result_json:
                question_result.append(item)
                answer_result[item_id] = answer_result_json[item_id]
        for candidate in tqdm.tqdm(candidates, total=len(candidates)):
            question_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(candidate['index'])).hex)
            if question_id in answer_result:
                continue
            spotify_track_id = candidate['spotify_track_id']
            netease_track_id = candidate['netease_track_id']
            if not spotify_track_id or not netease_track_id:
                print(f"Missing query track ID. Skip.")
                continue
            query_isrc = candidate.get("isrc") or ""
            if not query_isrc:
                print(candidate)
                print(f"Missing query ISRC. Use query track name instead.")
            mb_result = get_musicbrainz_track_info(track_name=candidate['spotify_track_name'], artist_name=candidate['spotify_artist_name'], isrc=query_isrc, proxy_url=PROXY_URL)
            query_track_name = normalize_display(mb_result['track_name'])
            query_artist_name = normalize_display(mb_result['artist_name'])
            print(f"Query song: {query_track_name} - {query_artist_name}")
            netease_result = get_netease_recommendation(track_id=netease_track_id)
            embeat_result = ed.search_entry(track_id=spotify_track_id, top_k=max(len(netease_result), 5))
            question_item = {
                "id": question_id,
                "query_song": f"{query_track_name} - {query_artist_name}",
                "a_recs": [],
                "b_recs": []
            }
            netease_key = random.choice(["a_recs", "b_recs"])
            embeat_key = list({"a_recs", "b_recs"} - {netease_key})[0]
            for i in range(len(netease_result)):
                netease_track_name = netease_result[i]['track_name'].strip()
                netease_artist_name = netease_result[i]['artist_name'].split(", ")[0].strip()
                mb_netease_item = get_musicbrainz_track_info(track_name=netease_track_name, artist_name=netease_artist_name, proxy_url=PROXY_URL)
                netease_track_clean = normalize_display(mb_netease_item['track_name'])
                netease_artist_clean = normalize_display(mb_netease_item['artist_name'])
                question_item[netease_key].append(f"{netease_track_clean} - {netease_artist_clean}")
            for i in range(len(embeat_result)):
                embeat_track_name = embeat_result[i]['track_name'].strip()
                embeat_artist_name = embeat_result[i]['artist_name'].split(", ")[0].strip()
                embeat_isrc = embeat_result[i]['isrc'].replace("-", "").strip()
                mb_embeat_item = get_musicbrainz_track_info(track_name=embeat_track_name, artist_name=embeat_artist_name, isrc=embeat_isrc, proxy_url=PROXY_URL)
                embeat_track_clean = normalize_display(mb_embeat_item['track_name'])
                embeat_artist_clean = normalize_display(mb_embeat_item['artist_name'])
                question_item[embeat_key].append(f"{embeat_track_clean} - {embeat_artist_clean}")
            question_result.append(question_item)
            if netease_key == "a_recs":
                answer_result[question_id] = {"a": "netease", "b": "embeat"}
            else:
                answer_result[question_id] = {"a": "embeat", "b": "netease"}
            with open(output_question_json, "w", encoding="utf-8") as f:
                f.write(json.dumps(question_result, ensure_ascii=False, indent=2))
            with open(output_answer_json, "w", encoding="utf-8") as f:
                f.write(json.dumps(answer_result, ensure_ascii=False, indent=2))
            print(f"======= Embeat Top {len(question_item[embeat_key])} items =======")
            print("index\ttrack_name - artist_name")
            for i, item in enumerate(question_item[embeat_key]):
                print(f"{i + 1} \t{item}")
            print(f"======= Netease Top {len(question_item[netease_key])} items =======")
            print("index\ttrack_name - artist_name")
            for i, item in enumerate(question_item[netease_key]):
                print(f"{i + 1} \t{item}")
            print("")
    print(f"DONE! Output folder: {EVAL_RESULT_OUTPUT_DIR}")


# Recommendation result counter and generate final eval json
def recs_result_filter():
    seed_region_map = {}
    eval_sources = [os.path.join(EVAL_RESULT_INPUT_DIR, f) for f in os.listdir(EVAL_RESULT_INPUT_DIR) if f.endswith(".json")]
    for eval_source in eval_sources:
        with open(eval_source, "r", encoding="utf-8") as f:
            for seed in json.load(f):
                seed_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(seed['index'])).hex)
                seed_region_map[seed_id] = seed['region']
    final_question_items = []
    final_answer_dict = {}
    result = {
        "embeat_normal_recs_count": 0,
        "embeat_short_recs_count": 0,
        "embeat_zero_recs_count": 0,
        "embeat_problem_regions": {"zh": 0, "ja": 0, "ko": 0, "other": 0},
        "netease_normal_recs_count": 0,
        "netease_short_recs_count": 0,
        "netease_zero_recs_count": 0,
        "netease_problem_regions": {"zh": 0, "ja": 0, "ko": 0, "other": 0}
    }
    for eval_source in eval_sources:
        eval_file_name = os.path.splitext(os.path.basename(eval_source))[0]
        output_question_json = f"{EVAL_RESULT_OUTPUT_DIR}/{eval_file_name}.json"
        output_answer_json = f"{EVAL_RESULT_OUTPUT_DIR}/{eval_file_name}_ab.json"
        with open(output_question_json, "r", encoding="utf-8") as f:
            question_items = json.load(f)
        with open(output_answer_json, "r", encoding="utf-8") as f:
            answer_items = json.load(f)
        for item in question_items:
            question_id = item['id']
            region = seed_region_map.get(question_id, "unk")
            answer_item = answer_items[question_id]
            for side in ["a", "b"]:
                system = answer_item[side]
                recs_count = len(item[f'{side}_recs'])
                if recs_count == 0:
                    result[f'{system}_zero_recs_count'] = result[f'{system}_zero_recs_count'] + 1
                    if region in result[f'{system}_problem_regions']:
                        result[f'{system}_problem_regions'][region] = result[f'{system}_problem_regions'][region] + 1
                elif recs_count < 5:
                    result[f'{system}_short_recs_count'] = result[f'{system}_short_recs_count'] + 1
                    if region in result[f'{system}_problem_regions']:
                        result[f'{system}_problem_regions'][region] = result[f'{system}_problem_regions'][region] + 1
                else:
                    result[f'{system}_normal_recs_count'] = result[f'{system}_normal_recs_count'] + 1
            if len(item['a_recs']) == len(item['b_recs']) == 5:
                final_question_items.append(item)
                final_answer_dict[question_id] = {"a": answer_item['a'], "b": answer_item['b']}
    print(result)
    final_question_json = f"{EVAL_RESULT_OUTPUT_DIR}/eval.json"
    with open(final_question_json, "w", encoding="utf-8") as f:
        f.write(json.dumps(final_question_items, ensure_ascii=False, indent=2))
    final_answer_json = f"{EVAL_RESULT_OUTPUT_DIR}/eval_ab.json"
    with open(final_answer_json, "w", encoding="utf-8") as f:
        f.write(json.dumps(final_answer_dict, ensure_ascii=False, indent=2))


# Run LLM evaluation for each item in final eval json
def batch_llm_eval(model: Literal["gemini", "gpt", "claude", "kimi"], retry: int = 3):
    result = []
    model_cards = {
        "gemini": {
            "model_id": "google/gemini-3.1-pro-preview",
            "extra_body": {
                "reasoning": {"effort": "minimal", "exclude": True},
                "usage": {"include": True}
            }
        },
        "gpt": {
            "model_id": "openai/gpt-5.6-sol",
            "extra_body": {
                "reasoning": {"effort": "none"},
                "usage": {"include": True}
            }
        },
        "claude": {
            "model_id": "anthropic/claude-opus-5",
            "extra_body": {
                "reasoning": {"max_tokens": 1024, "exclude": True},
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
                "usage": {"include": True}
            }
        },
        "kimi": {
            "model_id": "moonshotai/kimi-k3",
            "extra_body": {
                "reasoning": {"effort": "minimal", "exclude": True},
                "usage": {"include": True}
            }
        }
    }
    if model not in model_cards:
        raise ValueError(f"Value of `model` should be: {list(model_cards.keys())}")
    final_question_json = f"{EVAL_RESULT_OUTPUT_DIR}/eval.json"
    llm_result_json = f"{EVAL_RESULT_OUTPUT_DIR}/{model}_result.json"
    question_items = []
    with open(final_question_json, "r", encoding="utf-8") as f:
        question_items = json.load(f)
    if os.path.isfile(llm_result_json) and os.path.getsize(llm_result_json) > 0:
        with open(llm_result_json, "r", encoding="utf-8") as f:
            result = json.load(f)
    result_ids = [r['id'] for r in result if r['id']]
    items = [question for question in question_items if question['id'] not in result_ids]
    print(f"Evaluating {len(items)} items using LLM: {model_cards[model]['model_id']}")
    for item in tqdm.tqdm(items, total=len(question_items), initial=len(result_ids)):
        item = {key: item[key] for key in ("id", "query_song", "a_recs", "b_recs")}
        current_retry = 0
        for _ in range(retry):
            llm_text = ""
            try:
                response = client.chat.completions.create(
                    model=model_cards[model]['model_id'],
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": json.dumps(item, ensure_ascii=False, indent=2)}
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "rating",
                            "strict": True,
                            "schema": RESPONSE_SCHEMA
                        }
                    },
                    extra_body=model_cards[model]['extra_body'],
                    temperature=0,
                    max_tokens=8192,
                    timeout=120.0
                )
                res = response.choices[0].message.content
                if not res:
                    current_retry = current_retry + 1
                    raise ValueError(f"LLM returns empty. Retry: {current_retry}")
                llm_text = res.strip()
                llm_dict = json.loads(llm_text)
                llm_dict['model'] = response.model
                llm_dict['usage'] = response.usage.model_dump() if response.usage else None
                result.append(llm_dict)
                with open(llm_result_json, "w", encoding="utf-8") as f:
                    f.write(json.dumps(result, ensure_ascii=False, indent=2))
                break
            except Exception as e:
                print(llm_text)
                print(e)
    print(f"DONE! Output {len(result)} eval result to: {llm_result_json}")


# Collect LLMs evaluation result and generate combined result (final production)
def collect_eval_result():
    result = []
    eval_result_json = f"{EVAL_RESULT_OUTPUT_DIR}/eval_result.json"
    final_question_json = f"{EVAL_RESULT_OUTPUT_DIR}/eval.json"
    final_answer_json = f"{EVAL_RESULT_OUTPUT_DIR}/eval_ab.json"
    llm_keys = ["gemini", "gpt", "claude", "kimi"]
    with open(final_question_json, "r", encoding="utf-8") as f:
        question_items = json.load(f)
    with open(final_answer_json, "r", encoding="utf-8") as f:
        answer_items = json.load(f)
    seed_items = []
    eval_sources = [os.path.join(EVAL_RESULT_INPUT_DIR, str(file)) for file in os.listdir(EVAL_RESULT_INPUT_DIR) if str(file).endswith(".json")]
    for eval_source in eval_sources:
        with open(eval_source, "r", encoding="utf-8") as f:
            seed_items.extend(json.load(f))
    llm_result = {}
    for llm_key in llm_keys:
        llm_result_json = f"{EVAL_RESULT_OUTPUT_DIR}/{llm_key}_result.json"
        if os.path.isfile(llm_result_json) and os.path.getsize(llm_result_json) > 0:
            with open(llm_result_json, "r", encoding="utf-8") as f:
                llm_result[llm_key] = json.load(f)
    for question_item in question_items:
        result_item = {
            "index": 0,
            "genre": "",
            "isrc": "",
            "popularity": 0.0,
            "region": "",
            "query_song": "",
            "embeat_recs": [],
            "netease_recs": [],
            "claude_winner": "",
            "claude_reason": "",
            "gpt_winner": "",
            "gpt_reason": "",
            "gemini_winner": "",
            "gemini_reason": "",
            "kimi_winner": "",
            "kimi_reason": ""
        }
        question_id = question_item['id']
        embeat_label = "a" if answer_items[question_id]['a'] == "embeat" else "b"
        netease_label = "a" if answer_items[question_id]['a'] == "netease" else "b"
        for seed_item in seed_items:
            seed_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(seed_item['index'])).hex)
            if seed_id == question_id:
                result_item['index'] = seed_item['index']
                result_item['genre'] = seed_item['genre']
                result_item['isrc'] = seed_item['isrc']
                result_item['popularity'] = seed_item['popularity']
                result_item['region'] = seed_item['region']
                break
        result_item['query_song'] = question_item['query_song']
        result_item['embeat_recs'] = question_item[f'{embeat_label}_recs']
        result_item['netease_recs'] = question_item[f'{netease_label}_recs']
        for llm_key in llm_keys:
            for llm_item in llm_result[llm_key]:
                if llm_item['id'] != question_id:
                    continue
                if llm_item['winner'] == embeat_label:
                    result_item[f'{llm_key}_winner'] = "embeat"
                elif llm_item['winner'] == netease_label:
                    result_item[f'{llm_key}_winner'] = "netease"
                elif llm_item['winner'] and llm_item['winner'].lower() == "tie":
                    result_item[f'{llm_key}_winner'] = "tie"
                else:
                    result_item[f'{llm_key}_winner'] = ""
                result_item[f'{llm_key}_reason'] = llm_item['reason'].strip()
        result.append(result_item)
    result = sorted(result, key=lambda x: x['index'])
    with open(eval_result_json, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Saved {len(result)} collected eval items to: {eval_result_json}")


if __name__ == "__main__":
    # get_preview_tracks()
    # netease_search_preview_tracks()
    # build_eval_set()
    # get_both_recommendation()
    # recs_result_filter()
    # batch_llm_eval(model="claude")
    # collect_eval_result()
    pass
