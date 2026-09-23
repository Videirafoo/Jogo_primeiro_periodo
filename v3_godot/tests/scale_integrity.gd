extends SceneTree

var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	if ok:
		print("PASS ", label)
	else:
		print("FAIL ", label)
		failures.append(label)

func _find_character_model(root_node: Node) -> Node3D:
	for child in root_node.get_children():
		if not child is Node3D:
			continue
		var node := child as Node3D
		if node.find_child(
			"Skeleton3D",
			true,
			false
		):
			return node
	return null

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

	var player := scene.get_node("Player")
	var player_shape := (
		player.get_node("CollisionShape3D")
		as CollisionShape3D
	).shape as CapsuleShape3D
	check(
		player_shape != null,
		"player_has_capsule"
	)
	if player_shape:
		check(
			player_shape.height >= 1.65
			and player_shape.height <= 2.05,
			"player_is_human_scale"
		)

	for enemy in get_nodes_in_group("enemies"):
		if bool(enemy.boss):
			check(
				float(enemy.body_height) >= 2.50
				and float(enemy.body_height) <= 3.80,
				"%s_boss_scale_is_intentional"
				% enemy.name
			)
		else:
			check(
				float(enemy.body_height) >= 1.65
				and float(enemy.body_height) <= 2.15,
				"%s_is_human_scale" % enemy.name
			)

	var npc_names := [
		"Thorvald",
		"Aurel",
		"Kaion",
		"Brenor",
		"Eiran",
		"Noctar"
	]
	for npc_name in npc_names:
		var npc := scene.find_child(
			npc_name,
			true,
			false
		) as Node3D
		check(
			npc != null,
			"%s_exists" % npc_name
		)
		if not npc:
			continue
		var model := _find_character_model(npc)
		check(
			model != null,
			"%s_has_character_model" % npc_name
		)
		if model:
			var scale_value := model.scale.x
			check(
				scale_value >= 0.45
				and scale_value <= 0.60,
				"%s_is_human_scale" % npc_name
			)

	var door_count := 0
	for node in scene.find_children(
		"*DoorLeaf",
		"Node3D",
		true,
		false
	):
		for child in node.get_children():
			if not child is MeshInstance3D:
				continue
			var mesh_instance := child as MeshInstance3D
			if not mesh_instance.mesh:
				continue
			var size := mesh_instance.mesh.get_aabb().size
			if (
				size.y >= 2.35
				and size.y <= 2.75
			):
				door_count += 1
				break

	check(
		door_count >= 5,
		"interior_doors_use_human_scale"
	)

	if failures.is_empty():
		print("QA_SCALE=PASS")
		quit(0)
	else:
		print("QA_SCALE=FAIL ", failures)
		quit(1)
