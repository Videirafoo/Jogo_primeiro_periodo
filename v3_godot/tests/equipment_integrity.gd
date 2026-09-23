extends SceneTree

var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	if ok:
		print("PASS ", label)
	else:
		print("FAIL ", label)
		failures.append(label)

func _bounds_for(root_node: Node3D) -> AABB:
	var first := true
	var min_v := Vector3.ZERO
	var max_v := Vector3.ZERO
	for node in root_node.find_children(
		"*",
		"MeshInstance3D",
		true,
		false
	):
		var mi := node as MeshInstance3D
		if not mi.mesh:
			continue
		var box := mi.get_aabb()
		for x in [0.0, 1.0]:
			for y in [0.0, 1.0]:
				for z in [0.0, 1.0]:
					var local := box.position + Vector3(
						box.size.x * x,
						box.size.y * y,
						box.size.z * z
					)
					var world := mi.global_transform * local
					if first:
						min_v = world
						max_v = world
						first = false
					else:
						min_v = min_v.min(world)
						max_v = max_v.max(world)
	return AABB(min_v, max_v - min_v)

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
	director.phase_index = 1
	director.objective_id = "clear_village"

	player.teleport_to(Vector3(0, 0.30, 8.0))
	player.unlock_weapons()
	await process_frame

	var hand_r: Vector3 = player._bone_world_position(
		"Fist.R"
	)
	check(
		player.weapon_pivot.global_position.distance_to(
			hand_r
		) < 0.18,
		"weapon_pivot_attached_to_right_hand"
	)

	for index in range(3):
		player.equip_weapon(index)
		await process_frame
		for visible_index in range(3):
			check(
				player.weapon_roots[visible_index].visible
				== (visible_index == index),
				"weapon_%d_visibility_%d" % [
					index,
					visible_index
				]
			)
		var bounds := _bounds_for(
			player.weapon_roots[index]
		)
		var largest := maxf(
			bounds.size.x,
			maxf(bounds.size.y, bounds.size.z)
		)
		check(
			largest >= 0.55 and largest <= 1.65,
			"weapon_%d_human_scale" % index
		)

	player.phone_owned = true
	player._present_phone(2.0)
	await process_frame
	var phone_target: Vector3 = (
		player.left_hand_target.global_position
	)
	print(
		"PHONE_TARGET_DISTANCE=",
		player.phone_root.global_position.distance_to(
			phone_target
		)
	)
	check(
		player.phone_root.global_position.distance_to(
			phone_target
		) < 0.16,
		"phone_follows_left_hand_ik_target"
	)
	check(
		player.phone_root.visible,
		"phone_visible_when_presented"
	)
	check(
		player.phone_holo_root.visible,
		"runic_phone_hologram_visible_in_valdrak"
	)

	if failures.is_empty():
		print("QA_EQUIPMENT=PASS")
		quit(0)
	else:
		print("QA_EQUIPMENT=FAIL ", failures)
		quit(1)
