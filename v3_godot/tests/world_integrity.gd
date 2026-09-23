extends SceneTree

var failures: Array[String] = []

func check(condition: bool, label: String) -> void:
	if condition:
		print("PASS ", label)
	else:
		print("FAIL ", label)
		failures.append(label)

func near(a: Vector3, b: Vector3, tolerance: float) -> bool:
	return a.distance_to(b) <= tolerance

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	var scene := packed.instantiate()
	root.add_child(scene)
	current_scene = scene
	await process_frame
	await process_frame
	await physics_frame

	var player = scene.get_node("Player")
	var director = scene.get_node("GameDirector")
	var forge = scene.find_child("ForgeDoor", true, false)
	var forge_exit = scene.find_child("ForgeExit", true, false)
	var lost_door = scene.find_child("LostStudentDoor", true, false)
	var recovery_bed = scene.find_child("RecoveryBed", true, false)
	var recovery_house = scene.find_child(
		"RecoveryHouseExterior",
		true,
		false
	)
	var arena_entry = scene.find_child("ArenaEntry", true, false)
	var boss = scene.get_node("JarlBoss")

	var laptop = scene.find_child("BedroomLaptop", true, false)
	var tv = scene.find_child("BedroomTV", true, false)
	var bedroom_door = scene.find_child(
		"BedroomDoor",
		true,
		false
	)

	check(laptop != null, "bedroom_has_laptop")
	check(tv != null, "bedroom_has_tv")
	check(bedroom_door != null, "bedroom_has_real_door")
	check(recovery_house != null, "recovery_house_exists_outside")
	check(lost_door != null, "recovery_house_has_access")
	check(recovery_bed != null, "recovery_house_has_bed")
	check(arena_entry != null, "boss_arena_has_entry_trigger")
	check(boss != null, "jarl_vorun_exists")

	director.phase_index = 0
	director.objective_id = "enter_forge"
	forge.interact(player)
	await create_timer(0.72).timeout
	check(
		near(
			player.global_position,
			Vector3(0, 18.08, 85.55),
			0.35
		),
		"forge_entry_is_safe"
	)

	forge_exit.interact(player)
	await create_timer(0.72).timeout
	check(
		near(
			player.global_position,
			Vector3(10.3, 0.08, 7.85),
			0.40
		),
		"forge_exit_spawn_is_safe"
	)
	await create_timer(0.55).timeout
	check(
		player.global_position.y > -0.15,
		"forge_exit_does_not_fall"
	)

	director.phase_index = 1
	player.health = 1
	player.invuln_time = 0.0
	player.take_hit(999)
	await create_timer(0.72).timeout
	check(
		near(
			player.global_position,
			Vector3(48.0, 18.08, 85.25),
			0.45
		),
		"death_wakes_in_recovery_house"
	)
	check(
		player.health == 120,
		"death_restores_health"
	)

	player.last_safe_position = Vector3(48.0, 18.08, 85.25)
	player.global_position = Vector3(48.0, 10.0, 85.25)
	await physics_frame
	await physics_frame
	check(
		player.global_position.y > 17.5,
		"interior_fall_guard_recovers_player"
	)

	director.phase_index = 1
	director.objective_id = "reach_gate"
	director.handle_event("eternal_gate")
	check(
		director.phase_index == 2
		and director.objective_id == "defeat_boss",
		"eternal_gate_opens_boss_phase"
	)

	director.handle_event("arena_entry")
	await create_timer(0.72).timeout
	check(
		near(
			player.global_position,
			Vector3(0, 0.18, -27.4),
			0.45
		),
		"boss_arena_entry_is_reachable"
	)
	check(
		player.global_position.distance_to(
			boss.global_position
		) < 8.0,
		"player_reaches_boss_combat_radius"
	)

	player.health = 1
	player.invuln_time = 0.0
	player.take_hit(999)
	await create_timer(0.72).timeout
	check(
		near(
			player.global_position,
			Vector3(48.0, 18.08, 85.25),
			0.45
		),
		"boss_death_returns_to_recovery_house"
	)

	if failures.is_empty():
		print("QA_WORLD_INTEGRITY=PASS")
		quit(0)
	else:
		print("QA_WORLD_INTEGRITY=FAIL ", failures)
		quit(1)
