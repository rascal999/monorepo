# Spotify Luigi Demo

This is a demonstration of using Luigi for building data pipelines, simulating Spotify-like operations.

## Overview

The demo includes three main tasks that form a pipeline:

1. `GeneratePlaylist`: Creates a mock playlist for a user
2. `CalculateListeningStats`: Analyzes the playlist to generate listening statistics
3. `GenerateRecommendations`: Uses the statistics to create song recommendations

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Demo

To run the complete pipeline:

```bash
python spotify_tasks.py
```

This will:
1. Generate a playlist for a demo user
2. Calculate their listening statistics
3. Generate song recommendations

The results will be stored in JSON files in the `data/` directory:
- `data/demo_user_123_playlist.json`
- `data/demo_user_123_stats.json`
- `data/demo_user_123_recommendations.json`

## Task Details

### GeneratePlaylist
- Creates a mock playlist with 10 songs
- Each song has an ID, title, and artist
- Output: JSON file with playlist data

### CalculateListeningStats
- Depends on: GeneratePlaylist
- Analyzes the playlist to generate mock statistics
- Calculates total songs, favorite artist, and listening time
- Output: JSON file with listening statistics

### GenerateRecommendations
- Depends on: CalculateListeningStats
- Uses the statistics to generate song recommendations
- Recommends 5 new songs based on the user's favorite artist
- Output: JSON file with recommended songs

## Visualizing the Pipeline

Luigi provides a built-in visualization tool. To use it:

1. Run the Luigi scheduler:
```bash
luigid
```

2. Run the pipeline with the central scheduler:
```bash
python spotify_tasks.py --local-scheduler=false
```

3. Open http://localhost:8082 in your browser to see the task graph