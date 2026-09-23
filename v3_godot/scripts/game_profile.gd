extends Node

signal profile_changed()
signal toast_requested(text: String)

const SAVE_PATH := "user://os_eternos_v3_slot_1.json"

const REGION_NAMES := {
	1: "Estrada de Valdrak",
	2: "Portão dos Ossos",
	3: "Vila dos Despertos",
	4: "Bosque dos Corvos",
	5: "Terras dos Lobos de Ferro",
	6: "Forja Morta",
	7: "Última Porta"
}

const CODEX := {
	"valdrak": {
		"title": "Valdrak",
		"body": "Um mundo de sonho que reage às escolhas, memórias e marcas do jogador."
	},
	"eternos": {
		"title": "Os Eternos",
		"body": "Guerreiros, sonhadores e poderes presos entre sonho, magia e destino."
	},
	"runas": {
		"title": "Runas",
		"body": "Símbolos que ligam tecnologia, sonho e magia em Valdrak."
	},
	"guardioes": {
		"title": "Os Sete Guardiões",
		"body": "Cada grande região possui um guardião ligado ao juramento dos Eternos."
	},
	"sonhadores": {
		"title": "Os Despertos",
		"body": "Pessoas do mundo real que adormeceram e acordaram em Valdrak. Alguns estão presos há anos."
	},
	"telefone": {
		"title": "Telefone Desperto",
		"body": "O celular do estudante atravessou o sonho. Sem rede, ele recebe sinais, mapas e mensagens que ainda não aconteceram."
	}
}
var level := 1
var xp := 0
var coins := 0
var inventory: Array[Dictionary] = []
var equipped := {
	"weapon": {},
	"armor": {},
	"amulet": {},
	"rune": {}
}
var codex: Array[String] = ["valdrak"]
var visited_regions: Array[int] = [1]
var discoveries: Array[String] = []
var opened_chests: Array[String] = []
var reputation := {
	"Clãs Livres": 0,
	"Círculo Rúnico": 0,
	"Errantes do Vazio": 0
}

func _ready() -> void:
	add_to_group("game_profile")

func add_item(item: Dictionary) -> void:
	inventory.append(item.duplicate(true))
	var slot := str(item.get("slot", ""))
	if equipped.has(slot):
		var current: Dictionary = equipped[slot]
		if current.is_empty() or float(item.get("value", 0)) > float(current.get("value", 0)):
			equipped[slot] = item.duplicate(true)
	profile_changed.emit()
	toast_requested.emit(
		"%s obtido" % str(item.get("name", "Item"))
	)

func add_coins(amount: int) -> void:
	coins += maxi(0, amount)
	profile_changed.emit()

func add_xp(amount: int) -> void:
	xp += maxi(0, amount)
	while xp >= level * 100:
		xp -= level * 100
		level += 1
		toast_requested.emit("NÍVEL %d" % level)
	profile_changed.emit()
func unlock_codex(entry: String) -> void:
	if CODEX.has(entry) and not codex.has(entry):
		codex.append(entry)
		profile_changed.emit()
		toast_requested.emit(
			"Códice atualizado: %s" % str(CODEX[entry].title)
		)

func register_discovery(id: String) -> void:
	if not discoveries.has(id):
		discoveries.append(id)
		profile_changed.emit()

func open_chest(id: String) -> bool:
	if opened_chests.has(id):
		return false
	opened_chests.append(id)
	profile_changed.emit()
	return true

func save_game() -> bool:
	var player := get_tree().get_first_node_in_group("player")
	var director := get_tree().get_first_node_in_group("game_director")
	if not player or not director:
		return false

	var quest_manager := get_tree().get_first_node_in_group(
		"quest_manager"
	)
	var relationships := get_tree().get_first_node_in_group(
		"relationships"
	)
	var data := {
		"version": 1,
		"level": level,
		"xp": xp,
		"coins": coins,
		"inventory": inventory,
		"equipped": equipped,
		"codex": codex,
		"visited_regions": visited_regions,
		"discoveries": discoveries,
		"opened_chests": opened_chests,
		"reputation": reputation,
		"relationships": (
			relationships.export_state()
			if relationships
			else {}
		),
		"optional_quests": (
			quest_manager.export_state()
			if quest_manager
			else []
		),
		"player": {
			"x": player.global_position.x,
			"y": player.global_position.y,
			"z": player.global_position.z,
			"health": player.health,
			"stamina": player.stamina,
			"weapon_unlocked": player.weapon_unlocked,
			"weapon_index": player.weapon_index,
			"checkpoint_x": player.respawn_position.x,
			"checkpoint_y": player.respawn_position.y,
			"checkpoint_z": player.respawn_position.z
		},
		"story": {
			"phase_index": director.phase_index,
			"chapter_name": director.chapter_name,
			"objective_id": director.objective_id,
			"objective_title": director.objective_title,
			"objective_detail": director.objective_detail,
			"objective_progress": director.objective_progress,
			"completed": director.completed
		}
	}

	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if not file:
		return false
	file.store_string(JSON.stringify(data, "	"))
	file.close()
	toast_requested.emit("JOGO SALVO")
	return true

func load_game() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		toast_requested.emit("Nenhum save encontrado")
		return false

	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not file:
		return false
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	if not parsed is Dictionary:
		return false

	level = int(parsed.get("level", 1))
	xp = int(parsed.get("xp", 0))
	coins = int(parsed.get("coins", 0))
	inventory = _dict_array(parsed.get("inventory", []))
	equipped = parsed.get("equipped", equipped)
	codex = _string_array(parsed.get("codex", ["valdrak"]))
	visited_regions = _int_array(parsed.get("visited_regions", [1]))
	discoveries = _string_array(parsed.get("discoveries", []))
	opened_chests = _string_array(parsed.get("opened_chests", []))
	var loaded_rep = parsed.get("reputation", {})
	if loaded_rep is Dictionary:
		reputation = loaded_rep
	var relationships := get_tree().get_first_node_in_group(
		"relationships"
	)
	if relationships:
		relationships.import_state(
			parsed.get("relationships", {})
		)
	var quest_manager := get_tree().get_first_node_in_group(
		"quest_manager"
	)
	if quest_manager:
		quest_manager.import_state(
			parsed.get("optional_quests", [])
		)
	var player := get_tree().get_first_node_in_group("player")
	var director := get_tree().get_first_node_in_group("game_director")
	var player_data: Dictionary = parsed.get("player", {})
	if player and not player_data.is_empty():
		player.teleport_to(Vector3(
			float(player_data.get("x", 0.0)),
			float(player_data.get("y", 0.25)),
			float(player_data.get("z", 3.0))
		))
		player.health = int(player_data.get("health", 120))
		player.stamina = float(player_data.get("stamina", 100.0))
		if player.has_method("set_checkpoint"):
			player.set_checkpoint(Vector3(
				float(player_data.get("checkpoint_x", player.global_position.x)),
				float(player_data.get("checkpoint_y", player.global_position.y)),
				float(player_data.get("checkpoint_z", player.global_position.z))
			))
		if bool(player_data.get("weapon_unlocked", false)):
			player.unlock_weapons()
			player.equip_weapon(
				int(player_data.get("weapon_index", 0))
			)

	var story: Dictionary = parsed.get("story", {})
	if director and not story.is_empty():
		director.phase_index = int(story.get("phase_index", -1))
		director.chapter_name = str(story.get(
			"chapter_name",
			"PRÓLOGO // UMA NOITE COMUM"
		))
		director.objective_id = str(story.get(
			"objective_id",
			"check_phone"
		))
		director.objective_title = str(story.get(
			"objective_title",
			"Amanhã tem prova"
		))
		director.objective_detail = str(story.get(
			"objective_detail",
			"Veja as mensagens no celular antes de dormir."
		))
		director.objective_progress = str(story.get(
			"objective_progress",
			"0 / 1"
		))
		director.completed = bool(story.get("completed", false))
		director._emit_objective()

	profile_changed.emit()
	toast_requested.emit("SAVE CARREGADO")
	return true
func inventory_text() -> String:
	if inventory.is_empty():
		return "Nenhum equipamento encontrado ainda."
	var lines: Array[String] = []
	for item in inventory:
		lines.append(
			"• %s [%s]  +%s %s" % [
				str(item.get("name", "Item")),
				str(item.get("rarity", "Comum")),
				str(item.get("value", 0)),
				str(item.get("stat", ""))
			]
		)
	return "
".join(lines)

func codex_text() -> String:
	var lines: Array[String] = []
	for key in codex:
		if not CODEX.has(key):
			continue
		lines.append(
			"%s
%s" % [
				str(CODEX[key].title),
				str(CODEX[key].body)
			]
		)
	return "

".join(lines)

func map_text() -> String:
	var lines: Array[String] = []
	for number in range(1, 8):
		var status := "DESCONHECIDA"
		if visited_regions.has(number):
			status = "ATUAL" if number == 1 else "VISITADA"
		lines.append(
			"%d. %s  —  %s" % [
				number,
				REGION_NAMES[number],
				status
			]
		)
	return "
".join(lines)

func _dict_array(value) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if value is Array:
		for entry in value:
			if entry is Dictionary:
				result.append(entry)
	return result
func _string_array(value) -> Array[String]:
	var result: Array[String] = []
	if value is Array:
		for entry in value:
			result.append(str(entry))
	return result

func _int_array(value) -> Array[int]:
	var result: Array[int] = []
	if value is Array:
		for entry in value:
			result.append(int(entry))
	return result
