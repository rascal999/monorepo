import luigi
import random
import json
from datetime import datetime

class GeneratePlaylist(luigi.Task):
    """Task to generate a mock playlist"""
    user_id = luigi.Parameter()
    playlist_name = luigi.Parameter(default="My Awesome Mix")
    
    def output(self):
        return luigi.LocalTarget(f"data/{self.user_id}_playlist.json")
    
    def run(self):
        # Simulate playlist generation
        songs = [
            {"id": f"track_{i}", "title": f"Song {i}", "artist": f"Artist {i%5}"}
            for i in range(10)
        ]
        
        playlist = {
            "name": self.playlist_name,
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "songs": songs
        }
        
        with self.output().open('w') as f:
            json.dump(playlist, f, indent=2)

class CalculateListeningStats(luigi.Task):
    """Task to calculate listening statistics"""
    user_id = luigi.Parameter()
    
    def requires(self):
        return GeneratePlaylist(user_id=self.user_id)
    
    def output(self):
        return luigi.LocalTarget(f"data/{self.user_id}_stats.json")
    
    def run(self):
        # Read playlist
        with self.input().open('r') as f:
            playlist = json.load(f)
        
        # Generate mock listening stats
        stats = {
            "user_id": self.user_id,
            "total_songs": len(playlist["songs"]),
            "favorite_artist": f"Artist {random.randint(0, 4)}",
            "listening_time": random.randint(100, 1000),
            "generated_at": datetime.now().isoformat()
        }
        
        with self.output().open('w') as f:
            json.dump(stats, f, indent=2)

class GenerateRecommendations(luigi.Task):
    """Task to generate song recommendations"""
    user_id = luigi.Parameter()
    
    def requires(self):
        return CalculateListeningStats(user_id=self.user_id)
    
    def output(self):
        return luigi.LocalTarget(f"data/{self.user_id}_recommendations.json")
    
    def run(self):
        # Read stats
        with self.input().open('r') as f:
            stats = json.load(f)
        
        # Generate mock recommendations
        recommendations = {
            "user_id": self.user_id,
            "based_on_artist": stats["favorite_artist"],
            "recommended_songs": [
                {
                    "id": f"rec_track_{i}",
                    "title": f"Recommended Song {i}",
                    "artist": f"Artist {random.randint(0, 9)}"
                }
                for i in range(5)
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        with self.output().open('w') as f:
            json.dump(recommendations, f, indent=2)

if __name__ == '__main__':
    luigi.build([
        GenerateRecommendations(user_id="demo_user_123")
    ], local_scheduler=True)