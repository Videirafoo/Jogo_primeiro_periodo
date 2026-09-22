import random


class CombatV25:
    def __init__(self, profile):
        self.profile = profile
        self.profile.setdefault("max_stamina", 100)
        self.profile.setdefault("stamina", self.profile["max_stamina"])
        self.profile.setdefault("parries", 0)
        self.profile.setdefault("perfect_dodges", 0)
        self.profile.setdefault("executions", 0)
        self.parry_window = 0.0
        self.dodge_window = 0.0
        self.combo_timer = 0.0
        self.combo_index = 0
        self.statuses = {}
        self.rng = random.Random(31337)

    @property
    def stamina(self):
        return self.profile["stamina"]

    @stamina.setter
    def stamina(self, value):
        self.profile["stamina"] = max(
            0,
            min(self.profile["max_stamina"], value),
        )

    def update(self, dt, moving=False):
        self.parry_window = max(0.0, self.parry_window - dt)
        self.dodge_window = max(0.0, self.dodge_window - dt)
        self.combo_timer = max(0.0, self.combo_timer - dt)
        if self.combo_timer <= 0:
            self.combo_index = 0

        regen = 20 if not moving else 13
        self.stamina += regen * dt

    def activate_parry(self):
        if self.stamina < 18:
            return False
        self.stamina -= 18
        self.parry_window = 0.28
        return True

    def activate_dodge(self):
        if self.stamina < 15:
            return False
        self.stamina -= 15
        self.dodge_window = 0.24
        return True

    def spend_heavy(self):
        if self.stamina < 30:
            return False
        self.stamina -= 30
        return True

    def next_combo(self):
        if self.combo_timer > 0:
            self.combo_index = (self.combo_index + 1) % 3
        else:
            self.combo_index = 0
        self.combo_timer = 0.62
        return (1.0, 1.18, 1.38)[self.combo_index]

    def incoming(self, damage):
        if self.parry_window > 0:
            self.parry_window = 0
            self.profile["parries"] += 1
            self.stamina += 12
            return 0, "PARRY PERFEITO"
        if self.dodge_window > 0:
            self.dodge_window = 0
            self.profile["perfect_dodges"] += 1
            self.stamina += 8
            return 0, "ESQUIVA PERFEITA"
        return damage, ""

    def apply_status(self, enemy, kind, duration=3.2):
        key = id(enemy)
        self.statuses[key] = {
            "enemy": enemy,
            "kind": kind,
            "remaining": duration,
            "tick": 0.45,
        }

    def update_statuses(self, dt):
        defeated = []
        expired = []
        for key, data in list(self.statuses.items()):
            enemy = data["enemy"]
            if enemy.dead:
                expired.append(key)
                continue
            data["remaining"] -= dt
            data["tick"] -= dt
            if data["tick"] <= 0:
                data["tick"] += 0.45
                damage = {
                    "burn": 3,
                    "bleed": 2,
                    "frost": 1,
                }.get(data["kind"], 2)
                if enemy.hit(damage):
                    defeated.append(enemy)
                    expired.append(key)
            if data["remaining"] <= 0:
                expired.append(key)
        for key in set(expired):
            self.statuses.pop(key, None)
        return defeated

    def execution_available(self, boss_controller, distance):
        return (
            boss_controller.stunned > 0
            and distance <= 105
            and self.stamina >= 25
        )

    def execute(self):
        self.stamina -= 25
        self.profile["executions"] += 1
