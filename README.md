<p align="center">
  <img src="assets/banner.png" alt="Embeat Banner" width="100%">
</p>

<p align="center">
  <b>English</b> | <a href="README_zh.md">简体中文</a>
</p>

<p align="center">
  <a href="https://github.com/gdstudio-org/Embeat">Homepage</a> •
  <a href="https://www.bilibili.com/opus/1218087093501165591">Blog</a> •
  <a href="https://huggingface.co/GD-Studio/embeat-track2vec">Model</a> •
  <a href="https://huggingface.co/datasets/GD-Studio/embeat_45m_spotify_tracks">Dataset</a> •
  <a href="https://pan.baidu.com/s/1CWFzgM75Z4YjP1tZnGCZKg?pwd=0616">Database</a>
</p>

<p align="center">
  <a href="https://github.com/gdstudio-org/Embeat"><img src="https://img.shields.io/github/stars/gdstudio-org/Embeat?style=social" alt="Stars"></a>
  <a href="https://github.com/gdstudio-org/Embeat/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC--BY--NC%204.0-blue" alt="License"></a>
</p>

---

# Embeat: A Music Recommendation System Based on Acoustic Features

## Introduction

Embeat is a music recommendation system built on Spotify acoustic feature data. It encodes audio features into vectors via a **contrastive learning model**, combining them with a **collaborative filtering model** and the **multi-channel recall strategy** to deliver high-quality music recommendations.

**Key Features:**

- **In-house models**: EmbeatMLP encodes Spotify Audio Features (key, tempo, energy, mood, etc.) into 64-dimensional acoustic vectors, responsible for "sounding like"; Track2Vec learns co-occurrence patterns from millions of playlists, responsible for "what the public likes"
- **Genre-aware**: 6,291 micro-genre tags covering over 2 million artists are deeply integrated into the recommendation system, ensuring exceptionally stable performance for niche songs
- **Blind-evaluated**: Compared to Netease Cloud Music, it leads by a wide margin with an 84~95% win rate across 157 cross-language samples
- **Multi-channel recall**: 5 recall channels (Acoustic Similarity / Same-Genre Popular / Same Artist / Similar Artists / Playlist Collaborative Filtering), merged and scored for final output
- **Flexible lookup**: Supports retrieving seed tracks via Spotify track ID, ISRC, track title + artist name, or artist name alone
- **Low-RAM support**: Can be deployed on a VPS with 2GB+ RAM, responds in 30–200 ms, with multiple versions of the open-source database available


## Roadmap

> If you find this project helpful, please give it a ⭐️. It means a lot to a personal project, thanks!

- [x] **2026-06-26**: Open-source initial codebase + [EmbeatMLP model weights](checkpoints/EmbeatMLP/)
- [x] **2026-06-26**: Open-source [45M tracks dataset](https://huggingface.co/datasets/GD-Studio/embeat_45m_spotify_tracks) + [Technical blog](https://www.bilibili.com/opus/1218087093501165591)
- [x] **2026-07-02**: Open-source Qdrant database V1 [[Google Drive](https://drive.google.com/drive/folders/1dFdueTmcWgGZXhJXs7c7YOjeniZsSW9x?usp=sharing)] [[Baidu Netdisk](https://pan.baidu.com/s/1CWFzgM75Z4YjP1tZnGCZKg?pwd=0616)]
- [x] **2026-09-06**: Open-source Qdrant database V2 (same link above, 2GB+ RAM can deploy)
- [x] **2026-09-06**: Open-source [Track2Vec model weights](https://huggingface.co/GD-Studio/embeat-track2vec)
- [x] **2026-09-16**: Open-source [Evaluation data](eval/assets/)


## Demo

> Below are example recommendation results from Embeat (please unmute before playing)

<details open>
<summary><b>Uptown Funk - Bruno Mars [dance pop, pop]</b></summary>
<table>
<tr>
<th width="25%">Seed Track</th>
<th width="25%">Embeat #1</th>
<th width="25%">Embeat #2</th>
<th width="25%">Embeat #3</th>
</tr>
<tr>
<td>Uptown Funk - Bruno Mars</td>
<td>CAN'T STOP THE FEELING! - Justin Timberlake</td>
<td>Happy - Pharrell Williams</td>
<td>I Like to Move It - will.i.am</td>
</tr>
<tr>
<td>
<video src="https://github.com/user-attachments/assets/e22f726e-eb61-49c1-ab17-91cda503293d" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/a571d075-1527-4d57-8ca7-a2f285e04de6" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/8ba236f0-f28e-4083-8561-00fcbfb49a98" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/1758195d-34c0-485c-b627-5b6d26e00b17" controls width="100%" preload="none"></video>
</td>
</tr>
</table>
</details>

<details>
<summary><b>杀死那个石家庄人 - 万能青年旅店 [chinese indie rock]</b></summary>
<table>
<tr>
<th width="25%">Seed Track</th>
<th width="25%">Embeat #1</th>
<th width="25%">Embeat #2</th>
<th width="25%">Embeat #3</th>
</tr>
<tr>
<td>杀死那个石家庄人 - 万能青年旅店</td>
<td>大石碎胸口 - 万能青年旅店</td>
<td>凄美地 - 郭顶</td>
<td>不要停止我的音乐 - 痛仰乐队</td>
</tr>
<tr>
<td>
<video src="https://github.com/user-attachments/assets/48eb51b0-0796-42e1-a54f-8a46a49d2916" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/e98e555f-8ac9-4fd0-9254-f440a6e0008e" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/535fec8c-3da1-4ba0-8bfa-bb0889cd698d" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/857666db-45f8-47df-86d2-32e51a679855" controls width="100%" preload="none"></video>
</td>
</tr>
</table>
</details>

<details>
<summary><b>Sis puella magica! - 梶浦由記 [anime score, japanese vgm]</b></summary>
<table>
<tr>
<th width="25%">Seed Track</th>
<th width="25%">Embeat #1</th>
<th width="25%">Embeat #2</th>
<th width="25%">Embeat #3</th>
</tr>
<tr>
<td>Sis puella magica! - 梶浦由記</td>
<td>Decretum - 梶浦由記</td>
<td>Zoltraak - Evan Call</td>
<td>Arrietty's Song - Cécile Corbel</td>
</tr>
<tr>
<td>
<video src="https://github.com/user-attachments/assets/caa287b2-d477-443b-84e6-2135c8b2b4be" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/f8caff21-35e3-4620-958e-a2ea1ed4eec5" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/bc3048e6-279d-4010-bc7d-81b705dc2b2c" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/7b197556-9ea6-4c1b-a04b-6221975a9273" controls width="100%" preload="none"></video>
</td>
</tr>
</table>
</details>

<details>
<summary><b>Gizeh - Oskar Schuster [compositional ambient]</b></summary>
<table>
<tr>
<th width="25%">Seed Track</th>
<th width="25%">Embeat #1</th>
<th width="25%">Embeat #2</th>
<th width="25%">Embeat #3</th>
</tr>
<tr>
<td>Gizeh - Oskar Schuster</td>
<td>Vleurgat - Oskar Schuster</td>
<td>Sleeping Lotus - Joep Beving</td>
<td>Travelling - James Spiteri</td>
</tr>
<tr>
<td>
<video src="https://github.com/user-attachments/assets/f10fad24-0f7b-43e3-ad11-879a7961a86a" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/1ce856b6-0e40-4d42-98a1-af458480e89f" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/b1413a46-243d-480c-a3d7-890789ff34f2" controls width="100%" preload="none"></video>
</td>
<td>
<video src="https://github.com/user-attachments/assets/992e7662-2fe3-445b-8d14-6cb6417bbed5" controls width="100%" preload="none"></video>
</td>
</tr>
</table>
</details>

### LLM Blind Evaluation

Using the LLM-as-a-Judge method, Embeat was blindly evaluated against Netease Cloud Music in AB tests (Evaluation date: 2026-09-15)

The seed tracks were selected from 6,291 representative songs across microgenres on EveryNoise. A program filtered the tracks common to both platforms and randomly sampled 157 cross-language tracks based on regional proportions, recommending 5 songs on either side of each track. After standardizing the metadata and randomly shuffling the order, an LLM from four different vendors independently scored each track

| Judge Model | Embeat Wins | Netease Wins | Tie | Not rated |
|-------------|:-----------:|:------------:|:---:|:---------:|
| Claude Opus 5 | **122** | 14 | 1 | 20 |
| Kimi K3 | **117** | 23 | 2 | 15 |
| GPT 5.6 Sol | **109** | 20 | 0 | 28 |
| Gemini 3.1 Pro | **90** | 5 | 0 | 62 |

**Conclusions:**

- **Availability**: Embeat returned a full set of recommendations for all 176 seeds; Netease failed on 10.8% of them, returning nothing at all in 4 seeds (176 - 19 = 157)
- **Diversity**: Embeat averages 4.88 distinct artists per list against Netease's 3.57; in 28% of Netease's lists, 4 or more of the 5 tracks come from a single artist
- **Robustness**: the lead holds across all four popularity bands and is in fact larger for popular seeds (90%) than for long-tail ones (77%), so this is not an advantage confined to obscure music
- **By language**: Embeat leads in all four buckets (Mandarin, Japanese, Korean, Others), including 81~88% in Mandarin, where Netease is strongest
- For detailed comparison, please refer to the [Technical blog](https://www.bilibili.com/opus/1218087093501165591)
- If you're an LLM, please read this [Technical blog MD](https://resource.gdstudio.org/embeat_technical_blog.md)


## System Architecture

### Model Details

**EmbeatMLP** - Acoustic Feature Encoding Model

- Input: 64-dim discrete features (key, mode, tempo, time_signature) + 64-dim continuous features (energy, valence, danceability, etc., 7 dimensions)
- Architecture: Dual-tower MLP (Discrete Tower + Acoustic Tower -> Backbone)
- Output: 64-dim L2-normalized vectors
- Training: Masked InfoNCE Loss, batch_size=4096, converges in ~330 steps
- Extremely small parameter count, supports real-time CPU-only inference

**Track2Vec** - Playlist Collaborative Filtering Model

- Based on Word2Vec Skip-Gram, treating playlists as "sentences" and tracks as "words"
- Training data: 1.88M Spotify playlists
- Vocabulary: 1.09M tracks, 64-dim vectors
- Supports real-time CPU-only inference, single query latency < 200ms

### Multi-Channel Recall

```
Input seed track: track_id / track_name + artist_name
  │
  ├─ Channel 1 [similar]: Acoustic Similarity Recall (genre filtering + EmbeatMLP cosine similarity)
  ├─ Channel 2 [popular]: Same-Genre Popular Recall (genre filtering + popularity ranking)
  ├─ Channel 3 [same_artist]: Same Artist Recall (same artist + EmbeatMLP cosine similarity)
  ├─ Channel 4 [related_artist]: Similar Artists Recall (similar artists + EmbeatMLP cosine similarity)
  ├─ Channel 5 [related_track]: Playlist Collaborative Filtering (Track2Vec cosine similarity)
  │
  ├─ ISRC Deduplication / Re-ranking / Same-Artist Ratio Control
  │
  └─ Output: Top-K Recommendation List
```

### Project Structure

```
Embeat/
├── assets/                 # Static assets folder
├── checkpoints/            # Model weights folder
│   ├── EmbeatMLP/          # EmbeatMLP model weights
│   └── Track2Vec/          # Track2Vec model weights (requires separate download)
├── data/                   # Data processing folder (not fully organized)
├── eval/                   # Evaluation code and data folder
├── infer/                  # Inference code folder
│   ├── Embeat.py           # Embeat recommendation system core
│   ├── EmbeatUtils.py      # Embeat extension utilities
│   ├── infer.py            # EmbeatMLP inference entry point
│   ├── eval_infer.py       # EmbeatMLP evaluation utilities
│   └── hf_to_qdrant.py     # Convert HF Dataset to Qdrant database
├── train/                  # Training code folder
│   ├── model.py            # EmbeatMLP model definition
│   ├── dataset.py          # HF Dataset processing
│   ├── sampler.py          # Positive/negative sample sampler
│   ├── loss.py             # Masked InfoNCE Loss
│   ├── trainer.py          # EmbeatMLP trainer
│   ├── train.py            # EmbeatMLP training entry point
│   └── train_track2vec.py  # Track2Vec training entry point
├── .env.example            # Environment variables example for .env
├── requirements.txt
└── LICENSE
```


## Getting Started

### Requirements (recommended)

- Python >= 3.10
- PyTorch >= 2.6, < 2.7 (required for training)
- CUDA >= 12.0 (required for training)
- [Qdrant](https://github.com/qdrant/qdrant/releases) >= 1.18 (required for inference)

### Installation

```bash
conda create -n embeat python=3.10
conda activate embeat

# Install PyTorch (CUDA 12.x), see https://pytorch.org/get-started/previous-versions/
pip install "torch>=2.6,<2.7" --index-url https://download.pytorch.org/whl/cu126

pip install -r requirements.txt
```

### Train EmbeatMLP

```bash
# 1. Download the HuggingFace tracks dataset to `data/datasets/`, then rename it to `spotify_45m_tracks_metadata`
# 2. If you want to make more detailed adjustments to the training parameters, please review the code
cd train
python train.py
```

### Train Track2Vec

```bash
# 1. Prepare the playlist training data (txt format, one playlist per line, space-separated track_ids)
# 2. Rename it to `spotify_playlists.txt`, and place it in the `train` folder
# 3. If you want to make more detailed adjustments to the training parameters, please review the code
cd train
python train_track2vec.py
```

### Inference: Compute Acoustic Similarity Between Two Tracks

```python
# 1. Get the acoustic feature data from HuggingFace tracks dataset
# 2. Or you can find some existed examples from infer/eval_infer.py
from infer.infer import infer

# 晴天 - Jay Chou (G major with fast tempo)
song_a = {"key": 7, "mode": 1, "tempo": 137, "time_signature": 4,
          "danceability": 0.54, "energy": 0.56, "speechiness": 0.02,
          "instrumentalness": 0.0, "valence": 0.41, "acousticness": 0.23,
          "liveness": 0.1}

# 夜曲 - Jay Chou (F minor with slow tempo)
song_b = {"key": 5, "mode": 0, "tempo": 87, "time_signature": 4,
          "danceability": 0.67, "energy": 0.65, "speechiness": 0.05,
          "instrumentalness": 0.03, "valence": 0.57, "acousticness": 0.27,
          "liveness": 0.19}

# Compute acoustic similarity via EmbeatMLP
similarity = infer(sample_a=song_a, sample_b=song_b,
                   checkpoint_path="checkpoints/EmbeatMLP/model.pt")

# Similarity: 0.6944
print(f"Similarity: {similarity:.4f}")
```

### Inference: Qdrant-Based Music Recommendation

```bash
# 1. Start the Qdrant service and import the database
# 2. Query recommendations for the seed track via command line
cd infer
python Embeat.py -t 5pIcwtJYNJx93l420oR2Vm   # Query by Spotify Track ID
python Embeat.py -t TWK970300503   # Query by ISRC
python Embeat.py -s "晴天 - Jay Chou"   # Query by track name and artist
python Embeat.py -a "Jay Chou"   # Query by artist name


# Output result for "晴天 - Jay Chou":
Query track_id: 5pIcwtJYNJx93l420oR2Vm
Query track info: 晴天 - Jay Chou
Query artist genres: ['mandopop', 'taiwan pop', 'c-pop', 'zhongguo feng']
-> Find query record used time: 21ms
-> Similar recall used time: 48ms
-> Popular recall used time: 24ms
-> Same artist recall used time: 4ms
-> Related artist recall used time: 5ms
-> Related track recall used time: 123ms
-> Re-ranking used time: 2ms
Result artist genres: ['taiwan indie', 'mandopop', 'chinese viral pop', 'cantopop']
======= Top 20 items =======
index   track_id                track_name      artist_name     album_name      sources         score
1       3Qj9Fy8BPbWmICTiNkuqB7  珊瑚海  Jay Chou        11月的蕭邦      ['same_artist', 'related_track']        1.0
2       10VuSw48iPN2UK2xX9Y6P0  青花瓷  Jay Chou        我很忙  ['same_artist', 'related_track']        1.0
3       0IAgufC1FlOg1nZMmRZxRr  突然好想你      Mayday  後 青春期的詩   ['popular', 'related_artist']   1.0
4       2zB7NKVnzRh7xSUSPLErFr  明明就  Jay Chou        十二新作        ['same_artist', 'related_track']        1.0
5       5WtMlbTDNZlbN8xZ5zfXva  Our Singapore   JJ Lin  My August 9th - 50 Wonderful Years (2016 Edition)       ['similar', 'related_artist']   1.0
6       5cU1O9P0EDA0rPkPDykhIm  怎麼了  Eric Chou       終於了解自由 (Deluxe)   ['popular', 'related_track']    1.0
7       4daA20tBusVX29bUWgd8Dw  交換餘生        JJ Lin  交換餘生        ['popular', 'related_track']    1.0
8       1EgGTmmFGtlWuqgXFLrp9x  溫柔    Mayday  愛情萬歲        ['related_artist']      0.87
9       3ZuyyfGJqx9qhWTVtdMCWz  生命線 - 電視劇《院長爸爸》片頭曲       Bii     生命線 (電視劇《院長爸爸》片頭曲)       ['similar']     0.85
10      3p4UTiSIIpP4LFn0KEyEOj  十面埋伏        Eason Chan      Live For Today  ['related_artist']      0.85
11      4lhbajK3dvUcJ0UNEeCdMn  飞鸟和蝉        Ren Ran         Ren然   ['related_track']       0.84
12      3e8uw7YMiKVcIakItBENqm  天天晴朗（蘇打綠版）    sodagreen       秋：故事（蘇打綠版）    ['similar']     0.83
13      26O8PmJ32hwAbZnIhbJJwZ  天使    Mayday  為愛而生        ['related_artist']      0.82
14      3LgoekU3dE5ZMLvuL3NIt9  清醒 (戲劇《淺情人不知》片尾曲)         Ariel Tsai      清醒 (戲劇《淺情人不知》片尾曲)         ['similar']     0.81
15      1WnTw4Tzpc5q9dHMjs4aHu  陰天快樂        Eason Chan      rice & shine    ['related_artist']      0.8
16      14GFYAUxkeXranhS2qrYIZ  我想要佔據你    告五人  帶你飛  ['related_track']       0.8
17      1ylx8p71GKQy5g1t4gzuEz  抱歉    Sam Lee         原諒我沒有說    ['similar']     0.79
18      7fAdinC2UTc0Y9GiKrkTtu  字字句句        卢卢快闭嘴      字字句句        ['related_track']       0.78
19      1VG8o5rUZQZ0wjs7Bi4siU  最熟悉的陌生人  Elva Hsiao      蕭亞軒 (最熟悉的)       ['similar']     0.77
20      1lM4cYuhJHSsDRfD0ZCRN7  你的背包        Eason Chan      陳奕迅 國語精選 (HQCDII)        ['related_artist']      0.77

Query used time: 0.229s
```


## Related Links

<p align="center">
  <img src="assets/gdmusic_embeat.png" alt="GDMusic Embeat" width="100%">
</p>

- GD Music (Live Demo): [https://music.gdstudio.xyz](https://music.gdstudio.xyz)
- Embeat UI Web: [https://github.com/lkwodp/embeat-ui-refactor](https://github.com/lkwodp/embeat-ui-refactor)
- Bilibili: [https://space.bilibili.com/13715770](https://space.bilibili.com/13715770)
- Telegram: [https://t.me/gdstudio_music](https://t.me/gdstudio_music)


## Acknowledgements

- [Anna's Archive](https://annas-archive.org)
- [Every Noise at Once](https://everynoise.com)


## License

| Scope | License |
|-------|---------|
| Code, Model Weights | MIT |
| Datasets, Database | CC-BY-NC 4.0 |

> Made with ❤️ by [GD Studio](https://github.com/gdstudio-org)
