extends SceneTree

var failures: Array[String] = []

func check(condition: bool, label: String) -> void:
	if condition:
		print("PASS ", label)
	else:
		print("FAIL ", label)
		failures.append(label)

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var scene := (load("res://main.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	current_scene = scene
	await process_frame
	await process_frame
	await physics_frame

	var director = scene.get_node("GameDirector")
	var player = scene.get_node("Player")

	director.handle_event("real_phone")
	check(
		director.objective_id == "sleep",
		"phone_advances_prologue"
	)

	director.handle_event("dream_begin")
	await create_timer(2.1).timeout
	check(
		director.phase_index == 0
		and director.objective_id == "reach_bonfire",
		"dream_enters_valdrak"
	)

	director.handle_event("bonfire_arrival")
	check(
		director.objective_id == "enter_forge",
		"bonfire_points_to_forge"
	)

	director.handle_event("forge_enter")
	check(
		director.objective_id == "talk_eirik",
		"forge_requires_eirik"
	)

	director.handle_event("blacksmith_talk")
	check(
		director.phase_index == 1
		and director.objective_id == "collect_rune",
		"eirik_opens_rune_objective"
	)

	director.handle_event("rune_collect")
	await process_frame
	check(
		director.objective_id == "clear_village",
		"rune_opens_village_combat"
	)
	check(
		player.weapon_unlocked,
		"rune_unlocks_weapons"
	)

	for enemy in get_nodes_in_group("enemies"):
		if bool(enemy.boss):
			continue
		if int(enemy.active_phase) > 1:
			continue
		enemy.take_hit(9999, Vector3.FORWARD)

	await create_timer(0.15).timeout
	await process_frame
	check(
		director.objective_id == "reach_gate",
		"clearing_village_opens_gate"
	)

	director.handle_event("eternal_gate")
	check(
		director.phase_index == 2
		and director.objective_id == "defeat_boss",
		"gate_opens_jarl_chapter"
	)

	var jarl = scene.get_node("JarlBoss")
	jarl.take_hit(120, Vector3.FORWARD)
	check(
		jarl.health < jarl.max_health,
		"boss_can_take_damage"
	)

	player.health = 1
	player.invuln_time = 0.0
	player.take_hit(999)
	await create_timer(0.30).timeout
	check(
		jarl.health == jarl.max_health,
		"player_death_resets_boss_attempt"
	)
	check(
		jarl.global_position.distance_to(
			jarl.home_position
		) < 0.15,
		"boss_returns_home_after_player_death"
	)

	director.handle_event("arena_entry")
	await create_timer(0.72).timeout
	jarl.take_hit(9999, Vector3.FORWARD)
	await process_frame
	check(
		director.phase_index == 3
		and director.objective_id == "choose_ally",
		"jarl_defeat_opens_six_echoes"
	)

	director._on_choice_recorded(
		"Thorvald",
		"trust"
	)
	check(
		director.objective_id == "reach_crowwood",
		"ally_choice_opens_crowwood"
	)

	director.handle_event("crowwood_gate")
	check(
		director.phase_index == 4
		and director.objective_id == "enter_crow_dungeon",
		"crowwood_gate_advances_story"
	)

	director.handle_event("crow_dungeon")
	check(
		director.phase_index == 5
		and director.objective_id == "defeat_raven_warden",
		"crow_dungeon_opens_warden"
	)

	var warden = scene.get_node("RavenWarden")
	warden.take_hit(9999, Vector3.FORWARD)
	await process_frame
	check(
		director.phase_index == 6
		and director.objective_id == "region_two_gate",
		"warden_defeat_opens_region_two"
	)

	director.handle_event("region_two_gate")
	check(
		director.phase_index == 7
		and director.objective_id == "region_two_arrival",
		"region_two_transition_completes_current_arc"
	)

	if failures.is_empty():
		print("QA_STORY_FLOW=PASS")
		quit(0)
	else:
		print("QA_STORY_FLOW=FAIL ", failures)
		quit(1)
