import math

DIRECTIONS_8 = (
    "E", "SE", "S", "SW", "W", "NW", "N", "NE",
)

STATE_FPS = {
    "idle": 2,
    "walk": 8,
    "run": 11,
    "attack1": 12,
    "attack2": 14,
    "heavy": 10,
    "dash": 16,
    "hurt": 8,
    "death": 6,
    "power": 10,
    "pulse": 10,
}


def direction8(vector):
    if vector is None or vector.length_squared() == 0:
        return "S"
    angle = (math.degrees(math.atan2(vector.y, vector.x)) + 360) % 360
    index = int((angle + 22.5) // 45) % 8
    return DIRECTIONS_8[index]


def frame_index(state, seconds, frame_count=4):
    fps = STATE_FPS.get(state, 6)
    return int(seconds * fps) % max(1, frame_count)


def pose(state, seconds):
    frame = frame_index(state, seconds, 6)
    swing = math.sin((frame / 6) * math.tau)
    if state == "idle":
        return {"bob": abs(swing) * 1.2, "lean": 0, "weapon": 0}
    if state in {"walk", "run"}:
        return {
            "bob": abs(swing) * (2 if state == "walk" else 3),
            "lean": swing * 2,
            "weapon": swing * 5,
        }
    if state == "attack1":
        return {"bob": 0, "lean": 3, "weapon": -55 + swing * 32}
    if state == "attack2":
        return {"bob": 0, "lean": -3, "weapon": 45 - swing * 34}
    if state == "heavy":
        return {"bob": 1, "lean": 5, "weapon": -95 + swing * 55}
    if state == "dash":
        return {"bob": 0, "lean": 7, "weapon": -145}
    if state in {"power", "pulse"}:
        return {"bob": -2, "lean": 0, "weapon": -20}
    if state == "hurt":
        return {"bob": 1, "lean": -6, "weapon": 12}
    if state == "death":
        return {"bob": 8, "lean": 18, "weapon": 90}
    return {"bob": 0, "lean": 0, "weapon": 0}
