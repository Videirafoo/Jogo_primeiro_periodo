extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var scene := (load("res://main.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	current_scene = scene
	await process_frame
	await process_frame
	await physics_frame

	var player = scene.get_node("Player")
	var director = scene.get_node("GameDirector")
	director.phase_index = 7
	director.objective_id = "region_two_arrival"

	var teleports: Array = []
	for node in get_nodes_in_group("interactables"):
		if bool(node.teleport_enabled):
			teleports.append(node)

	print("TELEPORT_COUNT=", teleports.size())
	for area in teleports:
		var target: Vector3 = area.target_position
		player.teleport_to(target)
		await create_timer(0.32).timeout
		var drift := absf(player.global_position.y - target.y)
		var ok := drift < 0.45
		print(
			"TELEPORT ",
			area.name,
			" target=",
			target,
			" actual=",
			player.global_position,
			" drift=",
			drift,
			" ",
			"PASS" if ok else "FAIL"
		)
		if not ok:
			failures.append(str(area.name))

	if failures.is_empty():
		print("QA_INTERACTION_SAFETY=PASS")
		quit(0)
	else:
		print("QA_INTERACTION_SAFETY=FAIL ", failures)
		quit(1)
