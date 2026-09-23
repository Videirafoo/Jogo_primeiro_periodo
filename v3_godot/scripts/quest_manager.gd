extends Node

signal quests_changed()
signal quest_message(text: String)

var quests := [
	{
		"id": "optional_1_hunt",
		"title": "Caçada da Fronteira",
		"target_archetype": 0,
		"target_name": "raider",
		"need": 2,
		"kills": 0,
		"reward": 39,
		"accepted": false,
		"complete": false
	},
	{
		"id": "optional_1_elite",
		"title": "Ameaça de Elite",
		"target_archetype": 1,
		"target_name": "berserker",
		"need": 2,
		"kills": 0,
		"reward": 60,
		"accepted": false,
		"complete": false
	}
]

func _ready() -> void:
	add_to_group("quest_manager")
	call_deferred("_bind_enemies")

func _bind_enemies() -> void:
	await get_tree().process_frame
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if not enemy.has_signal("died"):
			continue
		var cb := Callable(self, "_on_enemy_died")
		if not enemy.died.is_connected(cb):
			enemy.died.connect(cb)
func interact_board() -> void:
	for quest in quests:
		if not bool(quest.accepted):
			quest.accepted = true
			quests_changed.emit()
			_announce(
				"MISSÃO OPCIONAL ACEITA // %s — %d %s" % [
					str(quest.title),
					int(quest.need),
					str(quest.target_name)
				]
			)
			return

	var active_lines: Array[String] = []
	for quest in quests:
		var status := "CONCLUÍDA" if bool(quest.complete) else "%d/%d" % [
			int(quest.kills),
			int(quest.need)
		]
		active_lines.append("%s: %s" % [str(quest.title), status])
	_announce("QUADRO DE CAÇADAS // " + "  •  ".join(active_lines))

func _on_enemy_died(enemy: Node) -> void:
	if bool(enemy.boss):
		return

	for quest in quests:
		if not bool(quest.accepted) or bool(quest.complete):
			continue
		if int(enemy.archetype) != int(quest.target_archetype):
			continue

		quest.kills = mini(int(quest.need), int(quest.kills) + 1)
		quests_changed.emit()

		if int(quest.kills) >= int(quest.need):
			_complete_quest(quest)
		else:
			_announce(
				"%s // %d/%d" % [
					str(quest.title),
					int(quest.kills),
					int(quest.need)
				]
			)
func _complete_quest(quest: Dictionary) -> void:
	quest.complete = true
	var profile := get_tree().get_first_node_in_group("game_profile")
	if profile:
		profile.add_coins(int(quest.reward))
		profile.add_xp(40)
		if profile.reputation.has("Clãs Livres"):
			profile.reputation["Clãs Livres"] += 2
			profile.profile_changed.emit()

	_announce(
		"OPCIONAL CONCLUÍDA // %s  +%d moedas" % [
			str(quest.title),
			int(quest.reward)
		]
	)
	quests_changed.emit()

func _announce(text: String) -> void:
	quest_message.emit(text)
	var director := get_tree().get_first_node_in_group("game_director")
	if director:
		director.show_story("QUADRO DE CAÇADAS", text, 4.5)

func journal_text() -> String:
	var lines: Array[String] = []
	for quest in quests:
		var status := "DISPONÍVEL"
		if bool(quest.complete):
			status = "CONCLUÍDA"
		elif bool(quest.accepted):
			status = "ATIVA %d/%d" % [
				int(quest.kills),
				int(quest.need)
			]
		lines.append(
			"• %s — %s — recompensa %d" % [
				str(quest.title),
				status,
				int(quest.reward)
			]
		)
	return "
".join(lines)
func export_state() -> Array:
	return quests.duplicate(true)

func import_state(value) -> void:
	if not value is Array:
		return
	if value.size() != quests.size():
		return
	for i in range(quests.size()):
		if value[i] is Dictionary:
			for key in [
				"kills",
				"accepted",
				"complete"
			]:
				if value[i].has(key):
					quests[i][key] = value[i][key]
	quests_changed.emit()
