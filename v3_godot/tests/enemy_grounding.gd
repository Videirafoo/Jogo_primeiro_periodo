extends SceneTree

var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	if ok:
		print("PASS ", label)
	else:
		print("FAIL ", label)
		failures.append(label)

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
	await physics_frame
	await physics_frame

	var director = scene.get_node("GameDirector")
	director.phase_index = 1
	director._set_objective(
		"clear_village",
		"Retome Valdrak",
		"Elimine os quatro invasores.",
		"0 / 4"
	)
	await physics_frame
	await physics_frame

	var enemies: Array[Node] = []
	for node in get_nodes_in_group("enemies"):
		if str(node.encounter_id) == "valdrak_village":
			enemies.append(node)

	check(enemies.size() == 4, "four_village_enemies_present")

	var space: PhysicsDirectSpaceState3D = scene.get_world_3d().direct_space_state
	for enemy in enemies:
		var from: Vector3 = enemy.global_position + Vector3.UP * 2.0
		var to: Vector3 = enemy.global_position + Vector3.DOWN * 4.0
		var query := PhysicsRayQueryParameters3D.create(
			from,
			to
		)
		query.exclude = [enemy.get_rid()]
		var hit: Dictionary = space.intersect_ray(query)
		check(
			not hit.is_empty(),
			"%s_has_floor" % enemy.name
		)
		if not hit.is_empty():
			var floor_y: float = hit.position.y
			var offset: float = enemy.global_position.y - floor_y
			print(
				enemy.name,
				" y=",
				enemy.global_position.y,
				" floor=",
				floor_y,
				" offset=",
				offset
			)
			check(
				offset >= 0.0 and offset <= 0.16,
				"%s_grounded" % enemy.name
			)

	if failures.is_empty():
		print("QA_ENEMY_GROUNDING=PASS")
		quit(0)
	else:
		print("QA_ENEMY_GROUNDING=FAIL ", failures)
		quit(1)
