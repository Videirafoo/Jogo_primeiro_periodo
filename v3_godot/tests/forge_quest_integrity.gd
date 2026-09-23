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
	var scene := (load("res://main.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	current_scene = scene
	await process_frame
	await process_frame

	var player = scene.get_node("Player")
	var director = scene.get_node("GameDirector")
	var rune_area = scene.find_child("BrokenRune", true, false)
	var sword_area = scene.find_child("ForgeWeapon_0", true, false)
	var axe_area = scene.find_child("ForgeWeapon_1", true, false)
	var hammer_area = scene.find_child("ForgeWeapon_2", true, false)

	check(rune_area != null, "rune_interaction_exists")
	check(sword_area != null, "sword_display_exists")
	check(axe_area != null, "axe_display_exists")
	check(hammer_area != null, "hammer_display_exists")

	director.phase_index = 0
	director.objective_id = "talk_eirik"
	await process_frame
	check(not rune_area.visible, "rune_hidden_before_eirik")

	rune_area.interact(player)
	await process_frame
	check(not rune_area.consumed, "rune_cannot_be_consumed_early")
	check(director.objective_id == "talk_eirik", "early_rune_does_not_skip_story")

	director.handle_event("blacksmith_talk")
	await process_frame
	check(director.objective_id == "collect_rune", "eirik_unlocks_rune_objective")
	check(rune_area.visible, "rune_becomes_visible_for_mission")
	check(rune_area.monitoring, "rune_becomes_interactive")

	rune_area.interact(player)
	await process_frame
	check(rune_area.consumed, "rune_consumes_after_valid_pickup")
	check(director.objective_id == "clear_village", "rune_advances_story")
	check(player.unlocked_weapon_count == 3, "rune_unlocks_three_weapons")
	check(player.weapon_unlocked, "weapon_system_active")

	sword_area.interact(player)
	await process_frame
	check(player.weapon_index == 0, "forge_equips_sword")

	axe_area.interact(player)
	await process_frame
	check(player.weapon_index == 1, "forge_equips_axe")

	hammer_area.interact(player)
	await process_frame
	check(player.weapon_index == 2, "forge_equips_hammer")

	var exits := [
		"ForgeExit",
		"ArchiveExit",
		"TavernExit",
		"LostHouseExit",
		"CrowDungeonExit"
	]
	for exit_name in exits:
		var exit_area = scene.find_child(exit_name, true, false)
		check(exit_area != null, "%s_exists" % exit_name)
		if exit_area:
			check(exit_area.teleport_enabled, "%s_is_teleport_exit" % exit_name)

	var exit_labels := 0
	for node in scene.find_children("*", "Label3D", true, false):
		if str(node.text) == "SAÍDA":
			exit_labels += 1
	check(exit_labels >= 5, "all_generated_interiors_have_exit_labels")

	if failures.is_empty():
		print("QA_FORGE_QUEST=PASS")
		quit(0)
	else:
		print("QA_FORGE_QUEST=FAIL ", failures)
		quit(1)
