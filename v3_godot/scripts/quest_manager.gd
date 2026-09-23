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
	var character_text := character_journal_text()
	if character_text != "":
		lines.append("")
		lines.append("MISSÕES DE PERSONAGEM")
		lines.append(character_text)
	return "
".join(lines)
func export_state() -> Dictionary:
	return {
		"board": quests.duplicate(true),
		"characters": character_quests.duplicate(true)
	}

func import_state(value) -> void:
	if value is Array:
		_import_board_state(value)
		quests_changed.emit()
		return
	if not value is Dictionary:
		return
	_import_board_state(value.get("board", []))
	var loaded_characters = value.get("characters", {})
	if loaded_characters is Dictionary:
		for character in character_quests.keys():
			if not loaded_characters.has(character):
				continue
			var source = loaded_characters[character]
			if not source is Dictionary:
				continue
			var target: Dictionary = character_quests[character]
			for key in ["accepted", "complete"]:
				if source.has(key):
					target[key] = source[key]
			character_quests[character] = target
	quests_changed.emit()

func _import_board_state(value) -> void:
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


var character_quests := {
	"Thorvald": {
		"id": "char_thorvald_oath",
		"title": "O Juramento de Thorvald",
		"detail": "Descanse na fogueira depois de aceitar ouvir o juramento dos Clãs Livres.",
		"trigger": "bonfire_rest",
		"accepted": false,
		"complete": false,
		"reward": 55
	},
	"Aurel": {
		"id": "char_aurel_archive",
		"title": "As Margens do Códice",
		"detail": "Investigue o Salão das Crônicas e leia o registro dos Eternos.",
		"trigger": "lore_house",
		"accepted": false,
		"complete": false,
		"reward": 60
	},
	"Kaion": {
		"id": "char_kaion_crows",
		"title": "Pegadas Entre Corvos",
		"detail": "Chegue ao Bosque dos Corvos seguindo a rota de Kaion.",
		"trigger": "crowwood_gate",
		"accepted": false,
		"complete": false,
		"reward": 65
	},
	"Brenor": {
		"id": "char_brenor_rune",
		"title": "Ferro que Lembra",
		"detail": "Leve a Runa do Código até a forja e prove que ela responde a você.",
		"trigger": "rune_collect",
		"accepted": false,
		"complete": false,
		"reward": 58
	},
	"Eiran": {
		"id": "char_eiran_echo",
		"title": "O Sonho de Outro",
		"detail": "Encontre uma memória de outro Desperto.",
		"trigger": "lost_student_phone",
		"accepted": false,
		"complete": false,
		"reward": 62
	},
	"Noctar": {
		"id": "char_noctar_depths",
		"title": "A Porta Debaixo da Pedra",
		"detail": "Entre na masmorra escondida sob o Bosque dos Corvos.",
		"trigger": "crow_dungeon",
		"accepted": false,
		"complete": false,
		"reward": 75
	}
}

func accept_character_quest(character: String) -> void:
	if not character_quests.has(character):
		return
	var quest: Dictionary = character_quests[character]
	if bool(quest.accepted) or bool(quest.complete):
		_announce(
			"%s // %s" % [
				str(quest.title),
				"CONCLUÍDA" if bool(quest.complete) else "ATIVA"
			]
		)
		return
	quest.accepted = true
	character_quests[character] = quest
	quests_changed.emit()
	_announce(
		"MISSÃO DE %s // %s — %s" % [
			character.to_upper(),
			str(quest.title),
			str(quest.detail)
		]
	)

func notify_event(event_id: String) -> void:
	for character in character_quests.keys():
		var quest: Dictionary = character_quests[character]
		if not bool(quest.accepted) or bool(quest.complete):
			continue
		if str(quest.trigger) != event_id:
			continue
		quest.complete = true
		character_quests[character] = quest
		var profile := get_tree().get_first_node_in_group(
			"game_profile"
		)
		if profile:
			profile.add_coins(int(quest.reward))
			profile.add_xp(55)
		var relationships := get_tree().get_first_node_in_group(
			"relationships"
		)
		if relationships:
			relationships.add_affinity(character, 2)
		_announce(
			"MISSÃO DE %s CONCLUÍDA // %s  +%d moedas" % [
				character.to_upper(),
				str(quest.title),
				int(quest.reward)
			]
		)
		quests_changed.emit()

func character_journal_text() -> String:
	var lines: Array[String] = []
	for character in character_quests.keys():
		var quest: Dictionary = character_quests[character]
		if not bool(quest.accepted) and not bool(quest.complete):
			continue
		var state := "CONCLUÍDA" if bool(quest.complete) else "ATIVA"
		lines.append(
			"• %s — %s — %s" % [
				character,
				state,
				str(quest.title)
			]
		)
	return "\n".join(lines)
