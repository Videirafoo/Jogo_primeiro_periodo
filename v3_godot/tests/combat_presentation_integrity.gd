extends SceneTree

var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	if ok:
		print("PASS ", label)
	else:
		print("FAIL ", label)
		failures.append(label)

func approx(a: float, b: float, eps := 0.08) -> bool:
	return absf(a - b) <= eps

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

	var player = scene.get_node("Player")
	var director = scene.get_node("GameDirector")

	player.unlock_weapons()
	player.equip_weapon(2)
	player.phone_action_time = 0.0
	player._update_offhand_pose(1.0)

	check(
		player.weapon_index == 2,
		"hammer_equips"
	)
	check(
		player.phone_ik.influence >= 0.60,
		"hammer_uses_two_hand_ik"
	)
	check(
		player.weapon_roots[2].visible,
		"hammer_visible_when_equipped"
	)

	player.phone_owned = true
	player._present_phone(2.0)
	player._update_offhand_pose(1.0)
	check(
		player.phone_root.visible,
		"phone_visible_when_presented"
	)
	player._update_phone_pose()
	var screen_forward: Vector3 = (
		-player.phone_root.global_basis.z
	).normalized()
	var to_camera: Vector3 = (
		player.camera.global_position
		- player.phone_root.global_position
	).normalized()
	check(
		screen_forward.dot(to_camera) >= 0.82,
		"phone_screen_faces_camera"
	)
	check(
		player.phone_ik.influence <= 0.05,
		"phone_releases_hammer_offhand"
	)
	var weapons_hidden := true
	for root in player.weapon_roots:
		if root.visible:
			weapons_hidden = false
	check(
		weapons_hidden,
		"phone_temporarily_sheathes_weapon"
	)

	player.phone_action_time = 0.0
	player.phone_root.visible = false
	player._refresh_weapon_visibility()
	player._update_offhand_pose(1.0)
	check(
		player.phone_ik.influence >= 0.60,
		"hammer_recovers_two_hand_grip_after_phone"
	)

	director.phase_index = 1
	director._set_objective(
		"clear_village",
		"QA",
		"QA",
		"0 / 4"
	)
	await process_frame

	player.global_position = Vector3(
		-3.8,
		0.2,
		-9.5
	)
	var target = player._find_nearest_enemy()
	check(
		target != null,
		"lock_finds_active_enemy"
	)

	if target:
		target.visible = false
		target.set_physics_process(false)
		var replacement = player._find_nearest_enemy()
		check(
			replacement != target,
			"lock_ignores_hidden_enemy"
		)
		target.visible = true
		target.set_physics_process(true)

	player.lock_target = null
	director.phase_index = -1
	player.global_position = Vector3(
		120.0,
		30.2,
		120.85
	)
	player._update_zone_safety_and_camera(1.0)
	check(
		approx(player.spring_arm.spring_length, 2.08),
		"real_room_uses_close_camera"
	)
	check(
		approx(player.camera.fov, 58.0),
		"real_room_uses_indoor_fov"
	)

	director.phase_index = 1
	player.global_position = Vector3(
		0.0,
		0.3,
		-5.0
	)
	player.last_safe_position = player.global_position
	player._update_zone_safety_and_camera(1.0)
	check(
		approx(player.spring_arm.spring_length, 4.15),
		"outdoor_uses_exploration_camera"
	)
	check(
		approx(player.camera.fov, 64.0),
		"outdoor_uses_exploration_fov"
	)

	director.phase_index = 1
	director._set_objective(
		"clear_village",
		"QA",
		"QA",
		"0 / 4"
	)
	await process_frame
	if target and is_instance_valid(target):
		target.visible = true
		target.set_physics_process(true)
		player.lock_target = target
		player._update_zone_safety_and_camera(1.0)
		check(
			approx(
				player.spring_arm.spring_length,
				3.65
			),
			"lock_on_uses_combat_camera"
		)
		check(
			approx(player.camera.fov, 61.0),
			"lock_on_uses_combat_fov"
		)
	else:
		check(false, "combat_target_available")

	if failures.is_empty():
		print("QA_COMBAT_PRESENTATION=PASS")
		quit(0)
	else:
		print(
			"QA_COMBAT_PRESENTATION=FAIL ",
			failures
		)
		quit(1)
