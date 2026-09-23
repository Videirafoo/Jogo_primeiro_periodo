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

	var expected_exits := [
		"ForgeExit",
		"ArchiveExit",
		"TavernExit",
		"LostHouseExit",
		"CrowDungeonExit"
	]

	var door_leaves: Array[Node] = []
	for node in scene.find_children(
		"*",
		"Node3D",
		true,
		false
	):
		if str(node.name).ends_with("DoorLeaf"):
			door_leaves.append(node)

	check(
		door_leaves.size() >= expected_exits.size(),
		"generated_interiors_have_physical_door_leaves"
	)

	for exit_name in expected_exits:
		var exit_area := scene.find_child(
			exit_name,
			true,
			false
		) as Area3D
		check(
			exit_area != null,
			"%s_exists" % exit_name
		)
		if not exit_area:
			continue

		var nearest := INF
		for leaf in door_leaves:
			var distance := exit_area.global_position.distance_to(
				(leaf as Node3D).global_position
			)
			nearest = minf(nearest, distance)

		check(
			nearest <= 3.2,
			"%s_has_nearby_physical_door" % exit_name
		)

	var bedroom_door := scene.find_child(
		"BedroomDoor",
		true,
		false
	) as Node3D
	check(
		bedroom_door != null,
		"real_world_bedroom_has_physical_door"
	)

	if failures.is_empty():
		print("QA_INTERIOR_DOORS=PASS")
		quit(0)
	else:
		print("QA_INTERIOR_DOORS=FAIL ", failures)
		quit(1)
