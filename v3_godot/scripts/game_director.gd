extends Node

signal objective_changed(
	chapter: String,
	title: String,
	detail: String,
	progress: String
)
signal story_message(
	speaker: String,
	text: String,
	duration: float
)
signal phase_changed(index: int, name: String)
signal game_completed()

const PROLOGUE := [
	["MEMÓRIA", "Fui dormir num dia comum. Quando abri os olhos, a chuva fria de Valdrak batia no meu rosto."],
	["MEMÓRIA", "Pinheiros cercavam uma estrada de lama. Ao longe: fumaça, ferro e o som de uma guerra."],
	["SISTEMA", "PODER DESPERTADO // TECNOLOGIA. Scanner de Runas, Mapa Holográfico e Pulso de Código disponíveis."],
	["MEMÓRIA", "Outros sonhadores estão presos aqui. Para acordar, preciso encontrar a última porta."]
]

var phase_index := 0
var chapter_name := "CAPÍTULO I // A CHEGADA"
var objective_id := "reach_bonfire"
var objective_title := "Siga a fumaça"
var objective_detail := "Alcance a fogueira no centro de Valdrak."
var objective_progress := "0 / 1"
var completed := false

func _ready() -> void:
	add_to_group("game_director")
	call_deferred("_bootstrap")

func _bootstrap() -> void:
	await get_tree().process_frame
	_bind_enemies()
	_emit_objective()
	call_deferred("_play_prologue")
func _bind_enemies() -> void:
	for node in get_tree().get_nodes_in_group("enemies"):
		if node.has_signal("died"):
			var callback := Callable(self, "_on_enemy_died")
			if not node.died.is_connected(callback):
				node.died.connect(callback)

func handle_event(event_id: String) -> void:
	match event_id:
		"bonfire_arrival":
			if objective_id == "reach_bonfire":
				_set_objective(
					"enter_forge",
					"Procure respostas",
					"Entre na ferraria de Eirik. O símbolo azul marca a entrada.",
					"0 / 1"
				)
				show_story(
					"VOZ DISTANTE",
					"Se ainda houver alguém vivo, estará perto da forja.",
					4.0
				)
		"forge_enter":
			if objective_id == "enter_forge":
				_set_objective(
					"talk_eirik",
					"O último ferreiro",
					"Encontre Eirik dentro da ferraria e fale com ele.",
					"0 / 1"
				)
		"blacksmith_talk":
			if objective_id == "talk_eirik":
				phase_index = 1
				chapter_name = "CAPÍTULO II // SANGUE NAS RUNAS"
				phase_changed.emit(phase_index, chapter_name)
				_set_objective(
					"collect_rune",
					"A Runa Partida",
					"Recupere a runa brilhante escondida na ferraria.",
					"0 / 1"
				)
				show_story(
					"EIRIK",
					"Vorun abriu o Portão dos Eternos. Sem a runa, ninguém o fecha.",
					6.0
				)
			elif objective_id == "collect_rune":
				show_story(
					"EIRIK",
					"A runa está sobre o pedestal da forja. Ela pulsa quando você se aproxima.",
					5.0
				)
			elif objective_id == "clear_village":
				show_story(
					"EIRIK",
					"Não deixe nenhum invasor de pé. Depois siga para o portão ao norte.",
					5.0
				)
			elif objective_id == "reach_gate":
				show_story(
					"EIRIK",
					"O Portão dos Eternos responde à runa. Atravesse-o e não olhe para trás.",
					5.0
				)
			elif objective_id == "defeat_boss":
				show_story(
					"EIRIK",
					"Vorun está na arena. Quebre o juramento dele e Valdrak respirará de novo.",
					5.0
				)
			elif objective_id == "complete":
				show_story(
					"EIRIK",
					"Você libertou Valdrak. Mas este foi apenas o primeiro juramento.",
					5.0
				)
		"rune_collect":
			if objective_id == "collect_rune":
				_set_objective(
					"clear_village",
					"Retome Valdrak",
					"Elimine os invasores que ocupam a aldeia.",
					"0 / 4"
				)
				show_story(
					"EIRIK",
					"Agora eles sentirão a runa despertar. Prepare-se.",
					4.0
				)
				var profile := _profile()
				if profile:
					profile.unlock_codex("runas")
					profile.add_item({
						"name": "Runa do Código",
						"slot": "rune",
						"rarity": "Raro",
						"stat": "energy",
						"value": 10
					})
				call_deferred("_evaluate_regular_enemies")
		"eternal_gate":
			if objective_id == "reach_gate":
				phase_index = 2
				chapter_name = "CAPÍTULO III // O JARL ETERNO"
				phase_changed.emit(phase_index, chapter_name)
				_set_objective(
					"defeat_boss",
					"Quebre o juramento",
					"Entre na arena e derrote JARL VORUN.",
					"0 / 1"
				)
				show_story(
					"JARL VORUN",
					"Você trouxe a runa até mim. Agora traga também o seu nome.",
					6.0
				)
		"bonfire_rest":
			var player := get_tree().get_first_node_in_group("player")
			if player:
				player.health = 120
				player.stamina = 100.0
			var profile := _profile()
			if profile:
				profile.save_game()
			show_story(
				"FOGUEIRA",
				"O calor devolve suas forças. O sonho registra este momento.",
				4.0
			)
		"loot_forge_chest":
			var profile := _profile()
			if profile and profile.open_chest("forge_chest"):
				profile.add_coins(35)
				profile.add_item({
					"name": "Machado de Valdrak",
					"slot": "weapon",
					"rarity": "Raro",
					"stat": "attack",
					"value": 9
				})
				show_story(
					"TESOURO",
					"Você encontrou um Machado de Valdrak e 35 moedas.",
					4.0
				)
		"loot_archive_chest":
			var profile := _profile()
			if profile and profile.open_chest("archive_chest"):
				profile.add_coins(22)
				profile.add_item({
					"name": "Olho de Aurel",
					"slot": "amulet",
					"rarity": "Raro",
					"stat": "crit",
					"value": 5
				})
				profile.unlock_codex("eternos")
				show_story(
					"TESOURO",
					"Você encontrou o Olho de Aurel e um registro sobre os Eternos.",
					4.5
				)
		"quest_board":
			var quests := get_tree().get_first_node_in_group(
				"quest_manager"
			)
			if quests:
				quests.interact_board()
		"lore_house":
			var profile := _profile()
			if profile:
				profile.unlock_codex("eternos")
			show_story(
				"CRÔNICA DE VALDRAK",
				"Os Eternos não eram deuses. Eram guerreiros que se recusaram a morrer.",
				6.0
			)
		_:
			pass

func show_story(
	speaker: String,
	text: String,
	duration := 4.5
) -> void:
	story_message.emit(speaker, text, duration)

func _on_enemy_died(enemy: Node) -> void:
	if bool(enemy.boss):
		if objective_id == "defeat_boss":
			_complete_story()
		return
	if objective_id == "clear_village":
		call_deferred("_evaluate_regular_enemies")
func _evaluate_regular_enemies() -> void:
	await get_tree().process_frame
	var alive := 0
	for node in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(node):
			continue
		if bool(node.boss):
			continue
		if int(node.health) > 0:
			alive += 1

	var total := 4
	var defeated := clampi(total - alive, 0, total)
	objective_progress = "%d / %d" % [defeated, total]
	_emit_objective()

	if alive <= 0 and objective_id == "clear_village":
		_set_objective(
			"reach_gate",
			"O Portão dos Eternos",
			"Aldeia segura. Atravesse o grande portão ao norte.",
			"0 / 1"
		)
		show_story(
			"MEMÓRIA",
			"Além do portão está a arena de Vorun. Não há retorno fácil.",
			5.0
		)

func _complete_story() -> void:
	completed = true
	chapter_name = "EPÍLOGO // VALDRAK RESPIRA"
	objective_id = "complete"
	objective_title = "Valdrak está livre"
	objective_detail = "Vertical slice concluído. Novas regiões serão abertas a partir daqui."
	objective_progress = "CONCLUÍDO"
	_emit_objective()
	var profile := _profile()
	if profile:
		profile.add_xp(250)
		profile.add_coins(100)
		profile.unlock_codex("guardioes")
	show_story(
		"EIRIK",
		"Um Jarl caiu. Seis regiões ainda carregam o mesmo juramento.",
		7.0
	)
	game_completed.emit()
func _set_objective(
	id: String,
	title: String,
	detail: String,
	progress: String
) -> void:
	objective_id = id
	objective_title = title
	objective_detail = detail
	objective_progress = progress
	_emit_objective()

func _emit_objective() -> void:
	objective_changed.emit(
		chapter_name,
		objective_title,
		objective_detail,
		objective_progress
	)

func _play_prologue() -> void:
	for entry in PROLOGUE:
		if objective_id != "reach_bonfire":
			return
		show_story(str(entry[0]), str(entry[1]), 4.2)
		await get_tree().create_timer(4.35).timeout

func _profile() -> Node:
	return get_tree().get_first_node_in_group("game_profile")
