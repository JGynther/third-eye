from pathlib import Path

CACHE = Path.home() / ".cache/third-eye"
CARDS = CACHE / "cards.json"
IMAGES = CACHE / "images"
INDEX = CACHE / "cards.faiss"
IDS = CACHE / "ids.txt"

LOCAL = Path.home() / ".local/share/third-eye"
OBJECTS = LOCAL / "objects"
DB = LOCAL / "collection.db"

TMP = Path(".tmp")

# Make sure dirs exist
CACHE.mkdir(parents=True, exist_ok=True)
LOCAL.mkdir(parents=True, exist_ok=True)
OBJECTS.mkdir(parents=True, exist_ok=True)
TMP.mkdir(exist_ok=True)
