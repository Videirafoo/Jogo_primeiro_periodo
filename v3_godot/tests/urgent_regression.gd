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
	var audio = scene.get_node("AudioManager")
	var content = scene.get_node("NarrativeContent")

	check(director.phase_index == -1, "starts_in_real_room")
	check(player.global_position.x > 100.0, "player_starts_in_bedroom")
	check(absf(player.camera_yaw) < 0.05, "camera_faces_room_not_door")
	check(content.find_child("BedroomLaptop", true, false) != null, "bedroom_has_laptop")
	check(content.find_child("BedroomTV", true, false) != null, "bedroom_has_tv")
	check(audio.room_stream != null, "room_audio_loaded")
	check(audio.wind_stream != null, "valdrak_audio_loaded")
	check(audio.ambient.playing, "ambient_audio_playing")

	director.handle_event("real_phone")
	await process_frame
	check(player.phone_owned, "phone_pickup_works")
	director.handle_event("dream_begin")
	await create_timer(2.05).timeout
	check(director.phase_index == 0, "sleep_transitions_to_valdrak")
	check(player.weapon_unlocked, "starting_sword_unlocked_in_valdrak")
	check(player.unlocked_weapon_count >= 1, "at_least_one_weapon_available")
	check(player.weapon_roots[0].visible, "sword_visible_after_waking")

	director.phase_index = 0
	director.objective_id = "enter_forge"
	var forge = content.find_child("ForgeDoor", true, false)
	forge.interact(player)
	await create_timer(0.25).timeout
	var forge_exit = content.find_child("ForgeExit", true, false)
	check(forge_exit != null, "forge_exit_exists")
	check(forge_exit.monitoring, "forge_exit_is_active")
	forge_exit.interact(player)
	await create_timer(0.80).timeout
	print("FORGE_EXIT_ACTUAL=", player.global_position)
	check(player.global_position.distance_to(Vector3(10.3,0.08,7.85)) < 0.8, "forge_exit_returns_to_valdrak")

	print("QA_URGENT=", "PASS" if failures.is_empty() else "FAIL")
	if not failures.is_empty():
		print(failures)
	quit(0 if failures.is_empty() else 1)
