extends SceneTree

var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	if ok:
		print("PASS ", label)
	else:
		print("FAIL ", label)
		failures.append(label)

func _set_objective(
	director: Node,
	id: String
) -> void:
	director._set_objective(
		id,
		"QA",
		"QA encounter state",
		"0 / 1"
	)

func _encounter_nodes(
	scene: Node,
	id: String
) -> Array[Node]:
	var result: Array[Node] = []
	for node in scene.get_tree().get_nodes_in_group(
		"enemies"
	):
		if str(node.encounter_id) == id:
			result.append(node)
	return result

func _visible_alive_count(nodes: Array[Node]) -> int:
	var count := 0
	for node in nodes:
		if (
			is_instance_valid(node)
			and int(node.health) > 0
			and node.visible
			and node.is_physics_processing()
		):
			count += 1
	return count

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var scene := (
		load("res://main.tscn") as PackedScene
	).instantiate()
	root.add_child(scene)
	current_scene = scene
	await process_frame
	await process_frame
	await process_frame

	var director = scene.get_node("GameDirector")
	var village := _encounter_nodes(
		scene,
		"valdrak_village"
	)
	var jarl := _encounter_nodes(scene, "jarl_vorun")
	var crowwood := _encounter_nodes(
		scene,
		"crowwood_patrol"
	)
	var warden := _encounter_nodes(
		scene,
		"raven_warden"
	)

	check(village.size() == 4, "village_has_four_enemies")
	check(jarl.size() == 1, "jarl_encounter_has_boss")
	check(crowwood.size() == 2, "crowwood_has_two_patrols")
	check(warden.size() == 3, "warden_encounter_has_three_enemies")

	director.phase_index = 1
	_set_objective(director, "collect_rune")
	await process_frame
	check(
		_visible_alive_count(village) == 0,
		"village_hidden_before_rune"
	)

	_set_objective(director, "clear_village")
	await process_frame
	check(
		_visible_alive_count(village) == 4,
		"village_spawns_four_on_objective"
	)
	for node in village:
		check(
			int(node.health) == int(node.max_health),
			"%s_full_health" % node.name
		)

	_set_objective(director, "reach_gate")
	await process_frame
	check(
		_visible_alive_count(village) == 0,
		"village_deactivates_after_encounter"
	)

	director.phase_index = 2
	_set_objective(director, "defeat_boss")
	await process_frame
	check(
		_visible_alive_count(jarl) == 1,
		"jarl_activates_only_for_boss_objective"
	)

	director.phase_index = 4
	_set_objective(director, "enter_crow_dungeon")
	await process_frame
	check(
		_visible_alive_count(crowwood) == 2,
		"crowwood_patrol_activates"
	)
	check(
		_visible_alive_count(jarl) == 0,
		"jarl_deactivates_after_boss_objective"
	)

	director.phase_index = 5
	_set_objective(director, "defeat_raven_warden")
	await process_frame
	check(
		_visible_alive_count(warden) == 3,
		"warden_encounter_activates_three"
	)
	check(
		_visible_alive_count(crowwood) == 0,
		"crowwood_patrol_deactivates_in_dungeon"
	)

	if failures.is_empty():
		print("QA_ENCOUNTERS=PASS")
		quit(0)
	else:
		print("QA_ENCOUNTERS=FAIL ", failures)
		quit(1)
