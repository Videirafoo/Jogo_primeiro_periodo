import json
from copy import deepcopy
from pathlib import Path


SAVE_VERSION = 1
SAVE_PATH = Path(__file__).with_name("save_os_eternos.json")


def build_snapshot(
    engine,
    rpg_profile,
    phase,
    opening_index,
    scene_index,
):
    resume_phase = phase

    if phase not in {"opening", "chapter", "explore"}:
        resume_phase = (
            "chapter"
            if engine.current_chapter is not None
            else "opening"
        )

    return {
        "version": SAVE_VERSION,
        "resume_phase": resume_phase,
        "opening_index": opening_index,
        "scene_index": scene_index,
        "engine": {
            "state": deepcopy(engine.state),
            "allies": list(engine.allies),
            "history": deepcopy(engine.history),
            "chapter_index": engine.chapter_index,
        },
        "rpg_profile": deepcopy(rpg_profile),
    }


def save_game(
    engine,
    rpg_profile,
    phase,
    opening_index,
    scene_index,
    path=SAVE_PATH,
):
    snapshot = build_snapshot(
        engine,
        rpg_profile,
        phase,
        opening_index,
        scene_index,
    )

    try:
        path.write_text(
            json.dumps(
                snapshot,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def load_game(path=SAVE_PATH):
    if not path.exists():
        return None

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return None

    if data.get("version") != SAVE_VERSION:
        return None

    engine_data = data.get("engine")
    profile = data.get("rpg_profile")

    if not isinstance(engine_data, dict):
        return None
    if not isinstance(profile, dict):
        return None

    required = {
        "state",
        "allies",
        "history",
        "chapter_index",
    }
    if not required.issubset(engine_data):
        return None

    return data

def slot_path(slot=1):
    slot = max(1, min(3, int(slot)))
    if slot == 1:
        return SAVE_PATH
    return Path(__file__).with_name(
        f"save_os_eternos_slot_{slot}.json"
    )


def available_slots():
    return [
        slot
        for slot in range(1, 4)
        if slot_path(slot).exists()
    ]
