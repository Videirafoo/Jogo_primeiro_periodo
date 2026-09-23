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
signal transition_requested(
	title: String,
	subtitle: String,
	duration: float
)
signal game_completed()

const VALDRAK_ARRIVAL := [
	["MEMÓRIA", "O chão desapareceu. Eu não estava mais no quarto."],
	["MEMÓRIA", "Acordei numa estrada molhada cercada por pinheiros e montanhas."],
	["CELULAR", "SEM REDE // ambiente desconhecido detectado: VALDRAK."],
	["MEMÓRIA", "Se isto é um sonho, ele sabe coisas demais sobre mim."]
]

var phase_index := -1
var chapter_name := "PRÓLOGO // UMA NOITE COMUM"
var objective_id := "check_phone"
var objective_title := "Amanhã tem prova"
var objective_detail := "Veja as mensagens no celular antes de dormir."
var objective_progress := "0 / 1"
var completed := false

func _ready() -> void:
	add_to_group("game_director")
	call_deferred("_bootstrap")

func _bootstrap() -> void:
	await get_tree().process_frame
	_bind_enemies()
	_bind_relationships()
	_emit_objective()
	show_story(
		"23:18 // QUARTO",
		"Livros abertos, mochila pronta e uma prova amanhã. Só falta responder as mensagens e dormir.",
		5.5
	)
func _bind_relationships() -> void:
	var relationships := get_tree().get_first_node_in_group(
		"relationships"
	)
	if not relationships:
		return
	var cb := Callable(self, "_on_choice_recorded")
	if not relationships.choice_recorded.is_connected(cb):
		relationships.choice_recorded.connect(cb)

func _bind_enemies() -> void:
	for node in get_tree().get_nodes_in_group("enemies"):
		if node.has_signal("died"):
			var callback := Callable(self, "_on_enemy_died")
			if not node.died.is_connected(callback):
				node.died.connect(callback)

func handle_event(event_id: String) -> void:
	var quest_manager := get_tree().get_first_node_in_group(
		"quest_manager"
	)
	if quest_manager and quest_manager.has_method("notify_event"):
		quest_manager.notify_event(event_id)

	if event_id.begins_with("npc_"):
		var character := event_id.trim_prefix("npc_")
		character = character.capitalize()
		var dialogue := get_tree().get_first_node_in_group(
			"dialogue_manager"
		)
		if dialogue:
			dialogue.start(character)
		return

	match event_id:
		"real_room_door":
			show_story(
				"MEMÓRIA",
				"É tarde. A porta está fechada e amanhã tem prova. Melhor olhar o celular e dormir.",
				4.5
			)
		"real_phone":
			var audio := get_tree().get_first_node_in_group(
				"audio_manager"
			)
			if audio and audio.has_method("play_sfx"):
				audio.play_sfx("phone")
			var player := get_tree().get_first_node_in_group(
				"player"
			)
			if player and player.has_method("pickup_phone"):
				player.pickup_phone()
			if objective_id == "check_phone":
				_set_objective(
					"sleep",
					"Desligue por hoje",
					"A cama está pronta. Durma antes da prova de amanhã.",
					"0 / 1"
				)
				show_story(
					"CELULAR // GRUPO DA TURMA",
					"23:19 — 'Não esquece a prova amanhã.'  23:20 — 'Você terminou o trabalho?'",
					6.0
				)
		"dream_begin":
			if objective_id == "sleep":
				var audio := get_tree().get_first_node_in_group(
					"audio_manager"
				)
				if audio and audio.has_method("play_sfx"):
					audio.play_sfx("sleep")
				transition_requested.emit(
					"ADORMECENDO",
					"O quarto desaparece no escuro. Quando você abre os olhos, o ar está gelado.",
					4.0
				)
				show_story(
					"CELULAR // 00:03",
					"NOVA REDE ENCONTRADA: VALDRAK // intensidade impossível.",
					3.4
				)
				await get_tree().create_timer(1.8).timeout
				var player := get_tree().get_first_node_in_group("player")
				if player and player.has_method("teleport_to"):
					player.teleport_to(Vector3(0, 0.28, 58.0))
					if player.has_method("set_checkpoint"):
						player.set_checkpoint(Vector3(0, 0.28, 58.0))
					if player.has_method("unlock_starting_sword"):
						player.unlock_starting_sword()
				phase_index = 0
				chapter_name = "CAPÍTULO I // A CHEGADA"
				phase_changed.emit(phase_index, chapter_name)
				_set_objective(
					"reach_bonfire",
					"Siga a fumaça",
					"Você acordou numa estrada desconhecida. Alcance a fogueira de Valdrak.",
					"0 / 1"
				)
				var profile := _profile()
				if profile:
					profile.register_discovery("first_dream")
					profile.unlock_codex("telefone")
				await get_tree().create_timer(0.8).timeout
				call_deferred("_play_valdrak_arrival")
		"lost_student_enter":
			var profile := _profile()
			if profile and not profile.discoveries.has("lost_student_house"):
				profile.register_discovery("lost_student_house")
				profile.unlock_codex("sonhadores")
				show_story(
					"MEMÓRIA",
					"Há um carregador moderno sobre a mesa. Alguém do meu mundo viveu aqui antes de mim.",
					5.5
				)
		"lost_student_phone":
			var profile := _profile()
			if profile:
				profile.register_discovery("lost_phone")
				profile.unlock_codex("telefone")
				profile.add_xp(20)
			show_story(
				"CELULAR QUEBRADO",
				"Última gravação: 'Dia 43. Aqui passam semanas. Minha mãe ainda manda mensagens do mesmo domingo.'",
				7.0
			)
		"lost_notebook":
			var profile := _profile()
			if profile:
				profile.register_discovery("lost_notebook")
				profile.add_xp(25)
			show_story(
				"CADERNO DO DESPERTO",
				"'Não confie no tempo de Valdrak. A Última Porta não leva todos para o mesmo lugar.'",
				7.0
			)
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
				var player := get_tree().get_first_node_in_group(
					"player"
				)
				if player and player.has_method("unlock_weapons"):
					player.unlock_weapons()
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
		"arena_entry":
			var player := get_tree().get_first_node_in_group(
				"player"
			)
			if objective_id == "defeat_boss":
				if player and player.has_method(
					"transition_teleport_to"
				):
					player.transition_teleport_to(
						Vector3(0, 0.18, -27.4),
						"ARENA DE VORUN"
					)
			elif phase_index < 2:
				show_story(
					"PORTÃO DOS ETERNOS",
					"A runa ainda não abriu o caminho para a arena.",
					3.5
				)
		"player_death":
			for enemy in get_tree().get_nodes_in_group(
				"enemies"
			):
				if enemy.has_method(
					"reset_after_player_death"
				):
					enemy.reset_after_player_death()

			var profile := _profile()
			if profile:
				profile.register_discovery(
					"recovery_house"
				)
			show_story(
				"CASA DO DESPERTO",
				"Você abre os olhos em outra cama. Alguém em Valdrak já sabia que você voltaria.",
				5.2
			)
		"recovery_bed":
			var player := get_tree().get_first_node_in_group(
				"player"
			)
			if player:
				player.health = 120
				player.stamina = 100.0
				if player.has_method("set_checkpoint"):
					player.set_checkpoint(
						player.global_position
					)
			var profile := _profile()
			if profile:
				profile.save_game()
			show_story(
				"CASA DO DESPERTO",
				"O sonho registra este quarto como abrigo seguro.",
				4.0
			)
		"bonfire_rest":
			var player := get_tree().get_first_node_in_group("player")
			if player:
				player.health = 120
				player.stamina = 100.0
				if player.has_method("set_checkpoint"):
					player.set_checkpoint(player.global_position)
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
		"tavern_enter":
			var profile := _profile()
			if profile and not profile.discoveries.has("tavern_corvo"):
				profile.register_discovery("tavern_corvo")
				profile.unlock_codex("sonhadores")
				show_story(
					"CELULAR // 03:17",
					"SEM REDE. Mesmo assim, uma notificação surgiu: 'Você vai para a aula amanhã?'",
					5.5
				)
		"astrid_talk":
			var profile := _profile()
			if profile:
				profile.unlock_codex("sonhadores")
			show_story(
				"ASTRID",
				"Vocês chegam com roupas estranhas e objetos que brilham. Todos dizem a mesma coisa: estavam dormindo antes de Valdrak.",
				6.5
			)
		"dream_echo_1":
			var profile := _profile()
			if profile and not profile.discoveries.has("phone_echo_faculdade"):
				profile.register_discovery("phone_echo_faculdade")
				profile.unlock_codex("telefone")
				profile.add_xp(25)
			show_story(
				"CELULAR // GRUPO DA FACULDADE",
				"07:42 — 'A prova começa em vinte minutos. Você está vindo?' A mensagem está datada de amanhã.",
				6.5
			)
		"lore_house":
			var profile := _profile()
			if profile:
				profile.unlock_codex("eternos")
			show_story(
				"CRÔNICA DE VALDRAK",
				"Os Eternos não eram deuses. Eram guerreiros que se recusaram a morrer.",
				6.0
			)
		"crowwood_gate":
			if phase_index >= 3:
				phase_index = maxi(phase_index, 4)
				chapter_name = "CAPÍTULO V // BOSQUE DOS CORVOS"
				phase_changed.emit(phase_index, chapter_name)
				_set_objective(
					"enter_crow_dungeon",
					"A voz sob as raízes",
					"Explore o Bosque dos Corvos e encontre a entrada da masmorra sob as ruínas.",
					"0 / 1"
				)
				var profile := _profile()
				if profile:
					if not profile.visited_regions.has(4):
						profile.visited_regions.append(4)
					profile.register_discovery("crowwood")
					profile.profile_changed.emit()
				transition_requested.emit(
					"BOSQUE DOS CORVOS",
					"A luz muda. Até o celular perde sinal entre as árvores negras.",
					3.2
				)
		"crow_dungeon":
			if phase_index >= 4:
				phase_index = maxi(phase_index, 5)
				chapter_name = "CAPÍTULO VI // SOB AS RAÍZES"
				phase_changed.emit(phase_index, chapter_name)
				_set_objective(
					"defeat_raven_warden",
					"O Guardião Corvino",
					"Derrote o guardião que protege a câmara sob o Bosque dos Corvos.",
					"0 / 1"
				)
				transition_requested.emit(
					"MASMORRA DOS CORVOS",
					"Runas antigas acendem quando o telefone atravessa o limiar.",
					3.0
				)
		"region_two_gate":
			if phase_index >= 6:
				phase_index = 7
				chapter_name = "CAPÍTULO VII // ALÉM DE VALDRAK"
				phase_changed.emit(phase_index, chapter_name)
				_set_objective(
					"region_two_arrival",
					"Região II",
					"A nova fronteira foi aberta. O próximo arco começa além das montanhas.",
					"DESBLOQUEADA"
				)
				var profile := _profile()
				if profile and not profile.visited_regions.has(5):
					profile.visited_regions.append(5)
					profile.profile_changed.emit()
				transition_requested.emit(
					"REGIÃO II DESBLOQUEADA",
					"O mapa do celular desenha uma área que não existia antes.",
					4.0
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
			_complete_region_one()
		elif objective_id == "defeat_raven_warden":
			_complete_crowwood()
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
		if int(node.active_phase) > 1:
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

func _complete_region_one() -> void:
	completed = false
	phase_index = 3
	chapter_name = "CAPÍTULO IV // OS SEIS ECOS"
	phase_changed.emit(phase_index, chapter_name)
	_set_objective(
		"choose_ally",
		"Quem você vai ouvir?",
		"Fale com Thorvald, Aurel, Kaion, Brenor, Eiran ou Noctar. Sua resposta terá consequência.",
		"0 / 1"
	)
	var profile := _profile()
	if profile:
		profile.add_xp(250)
		profile.add_coins(100)
		profile.unlock_codex("guardioes")
	show_story(
		"EIRIK",
		"Vorun caiu, mas o juramento continua. Seis pessoas esperam por você na aldeia. Escolha com cuidado quem ouvir primeiro.",
		7.0
	)

func _on_choice_recorded(
	character: String,
	choice_id: String
) -> void:
	if phase_index != 3 or objective_id != "choose_ally":
		return
	_set_objective(
		"reach_crowwood",
		"Bosque dos Corvos",
		"%s marcou no seu mapa uma passagem a oeste. Siga até o bosque." % character,
		"0 / 1"
	)
	show_story(
		"CELULAR // MAPA",
		"Novo ponto detectado: BOSQUE DOS CORVOS. A rota apareceu sem conexão de rede.",
		5.0
	)

func _complete_crowwood() -> void:
	completed = false
	phase_index = 6
	chapter_name = "CAPÍTULO VI // O ECO QUE SOBROU"
	phase_changed.emit(phase_index, chapter_name)
	_set_objective(
		"region_two_gate",
		"Além das montanhas",
		"O Guardião Corvino caiu. O celular detectou um novo caminho no extremo leste.",
		"0 / 1"
	)
	var profile := _profile()
	if profile:
		profile.add_xp(320)
		profile.add_coins(160)
		profile.register_discovery("raven_warden")
	show_story(
		"CELULAR // SINAL",
		"Uma nova região apareceu no mapa. A mensagem é curta: 'Você já esteve aqui.'",
		7.0
	)
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

func _play_valdrak_arrival() -> void:
	for entry in VALDRAK_ARRIVAL:
		if phase_index < 0:
			return
		show_story(str(entry[0]), str(entry[1]), 4.0)
		await get_tree().create_timer(4.15).timeout

func _profile() -> Node:
	return get_tree().get_first_node_in_group("game_profile")
