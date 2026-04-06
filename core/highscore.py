import os
import sys

def get_highscore_path():
    """
    Platform-independent path for user data.
    Mirrors the logic in utils.pas and highscoreunit.pas.
    """
    if sys.platform == "win32":
        # Windows: %APPDATA%/thesheepkiller/
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
        data_dir = os.path.join(base_dir, "thesheepkiller")
    else:
        # Linux/macOS: ~/.thesheepkiller/
        data_dir = os.path.join(os.path.expanduser("~"), ".thesheepkiller")
    
    return os.path.join(data_dir, "highscores.txt")

class Highscore:
    def __init__(self, filename=None):
        self.filename = filename if filename else get_highscore_path()
        self.scores = []

    def load(self):
        if not os.path.exists(self.filename):
            self.scores = [(0, "No One")] * 10
            return

        try:
            with open(self.filename, "r") as f:
                self.scores = []
                for line in f:
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2:
                        self.scores.append((int(parts[0]), parts[1]))
        except Exception:
            self.scores = [(0, "No One")] * 10

    def save(self):
        # Ensure the directory exists (equivalent to ForceDirectories in Pascal)
        dir_name = os.path.dirname(self.filename)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with open(self.filename, "w") as f:
            for score, name in self.scores:
                f.write(f"{score} {name}\n")

    def add_score(self, score: int, name: str):
        found_user = False
        for i, (existing_score, existing_name) in enumerate(self.scores):
            if existing_name == name:
                found_user = True
                if score > existing_score:
                    # Update existing score if new score is higher
                    self.scores[i] = (score, name)
                break # User found, no need to check further
        
        if not found_user:
            # If user doesn't exist, add a new entry
            self.scores.append((score, name))

        # Sort descending by score
        self.scores.sort(key=lambda x: x[0], reverse=True)
        # Keep top 10
        self.scores = self.scores[:10]

    @property
    def count(self):
        return len(self.scores)

    def get_entry(self, index: int):
        if index < len(self.scores):
            return self.scores[index]
        return (0, "")