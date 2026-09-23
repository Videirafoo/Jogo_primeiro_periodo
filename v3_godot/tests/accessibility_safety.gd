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

func _point_blocked(
	space: PhysicsDirectSpaceState3D,
	point: Vector3
) -> bool:
	var params := PhysicsPointQueryParameters3D.new()
	params.position = point
	params.collision_mask = 1
	params.collide_with_areas = false
	params.collide_with_bodies = true
	var hits := space.intersect_point(params, 32)
	for hit in hits:
		var collider = hit.get("collider")
		if collider is StaticBody3D:
			return true
	return false

func _run() -> void:
	var scene := (load("res://main.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	current_scene = scene
	await process_frame
	await process_frame
	await physics_frame

	var space: PhysicsDirectSpaceState3D = (
		scene.get_world_3d().direct_space_state
	)

	var forge_door = scene.find_child("ForgeDoor", true, false)
	var lost_door = scene.find_child("LostStudentDoor", true, false)
	var arena_entry = scene.find_child("ArenaEntry", true, false)

	check(
		not _point_blocked(space, forge_door.global_position),
		"forge_door_interaction_not_inside_wall"
	)
	check(
		not _point_blocked(space, lost_door.global_position),
		"recovery_house_interaction_not_inside_wall"
	)
	check(
		not _point_blocked(space, arena_entry.global_position),
		"arena_entry_not_inside_blocker"
	)

	var boss = scene.get_node("JarlBoss")
	check(
		boss.global_position.distance_to(
			Vector3(0, 0.18, -27.4)
		) < 8.0,
		"boss_is_reachable_from_safe_entry"
	)

	for enemy in get_nodes_in_group("enemies"):
		if enemy.global_position.y > 10.0:
			continue
		if enemy.name == "JarlBoss":
			continue
		var pos: Vector3 = enemy.global_position
		if pos.length() < 27.0:
			check(
				absf(pos.y) < 0.8,
				"enemy_spawn_grounded_%s" % enemy.name
			)

	if failures.is_empty():
		print("QA_ACCESSIBILITY=PASS")
		quit(0)
	else:
		print("QA_ACCESSIBILITY=FAIL ", failures)
		quit(1)
