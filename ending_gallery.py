import json
from pathlib import Path

GALLERY_PATH = Path(__file__).with_name("gallery_os_eternos.json")


class EndingGallery:
    def __init__(self, endings):
        self.endings = list(endings)
        self.unlocked = set()
        self._load()

    def _load(self):
        if not GALLERY_PATH.exists():
            return
        try:
            data = json.loads(GALLERY_PATH.read_text(encoding="utf-8"))
            self.unlocked = set(data.get("unlocked", []))
        except (OSError, json.JSONDecodeError):
            self.unlocked = set()

    def unlock(self, ending_id):
        if not ending_id:
            return
        self.unlocked.add(ending_id)
        try:
            GALLERY_PATH.write_text(
                json.dumps(
                    {"unlocked": sorted(self.unlocked)},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass

    def entries(self):
        return [
            {
                "id": ending["id"],
                "title": ending["title"],
                "unlocked": ending["id"] in self.unlocked,
            }
            for ending in self.endings
        ]
