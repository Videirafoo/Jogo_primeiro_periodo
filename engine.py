from copy import deepcopy


class StoryEngine:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.state = deepcopy(self.game["initial_state"])
        self.state.setdefault("tools", [])
        self.allies = []
        self.history = []
        self.chapter_index = 0

    @property
    def current_chapter(self):
        if self.chapter_index >= len(self.game["chapters"]):
            return None
        return self.game["chapters"][self.chapter_index]

    def choice_available(self, choice):
        required_ally = choice.get("requires_ally")
        if required_ally and required_ally not in self.allies:
            return False

        required_tool = choice.get("requires_tool")
        if required_tool and required_tool not in self.state["tools"]:
            return False

        required_count = choice.get("requires_any_ally_count")
        if required_count and len(self.allies) < required_count:
            return False

        return True

    def availability_reason(self, choice):
        required_ally = choice.get("requires_ally")
        if required_ally and required_ally not in self.allies:
            ally = self.game["allies"].get(required_ally, {})
            return f"Requer {ally.get('name', required_ally)}"

        required_tool = choice.get("requires_tool")
        if required_tool and required_tool not in self.state["tools"]:
            return f"Requer {required_tool}"

        required_count = choice.get("requires_any_ally_count")
        if required_count and len(self.allies) < required_count:
            return f"Requer {required_count} aliados"

        return ""

    def available_choices(self, chapter=None):
        chapter = chapter or self.current_chapter
        if chapter is None:
            return []
        return [
            choice
            for choice in chapter.get("choices", [])
            if self.choice_available(choice)
        ]

    def apply_choice(self, choice):
        if not self.choice_available(choice):
            return {
                "ok": False,
                "reason": self.availability_reason(choice),
                "result": [],
                "new_ally": None,
                "new_tool": None,
            }

        chapter = self.current_chapter
        self.history.append(
            {
                "chapter": chapter["number"],
                "title": chapter["title"],
                "choice": choice["text"],
            }
        )

        for key, value in choice.get("effects", {}).items():
            self.state[key] = self.state.get(key, 0) + value

        new_ally = None
        ally_id = choice.get("unlock_ally")
        if ally_id and ally_id not in self.allies:
            self.allies.append(ally_id)
            new_ally = self.game["allies"][ally_id]

        new_tool = None
        tool = choice.get("unlock_tool")
        if tool and tool not in self.state["tools"]:
            self.state["tools"].append(tool)
            new_tool = tool

        return {
            "ok": True,
            "reason": "",
            "result": choice.get("result", []),
            "sfx_sequence": choice.get("sfx_sequence", []),
            "new_ally": new_ally,
            "new_tool": new_tool,
        }

    def advance_chapter(self):
        self.chapter_index += 1
        return self.current_chapter

    def ending_matches(self, ending):
        condition = ending.get("condition", {})
        if not condition:
            return True

        for key, minimum in condition.items():
            if key == "allies_min":
                if len(self.allies) < minimum:
                    return False
                continue

            if key.endswith("_min"):
                state_key = key[:-4]
                if self.state.get(state_key, 0) < minimum:
                    return False
                continue

            if self.state.get(key, 0) < minimum:
                return False

        return True

    def choose_ending(self):
        for ending in self.game["endings"]:
            if self.ending_matches(ending):
                return ending
        return self.game["endings"][-1]

    def ally_names(self):
        return [
            self.game["allies"][ally_id]["name"]
            for ally_id in self.allies
        ]

    def status_snapshot(self):
        keys = [
            "coragem",
            "sabedoria",
            "tecnologia",
            "amizade",
            "caos",
            "marcas",
        ]
        return {key: self.state.get(key, 0) for key in keys}
