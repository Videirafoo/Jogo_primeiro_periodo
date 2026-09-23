extends Node

var ambient: AudioStreamPlayer
var fire: AudioStreamPlayer
var sfx: AudioStreamPlayer
var director: Node
var player: Node3D
var current_mode := ""
var update_timer := 0.0

var room_stream: AudioStream
var wind_stream: AudioStream
var fire_stream: AudioStream
var phone_stream: AudioStream
var sleep_stream: AudioStream
var swing_stream: AudioStream
var impact_stream: AudioStream

func _ready() -> void:
	add_to_group("audio_manager")
	AudioServer.set_bus_mute(0, false)
	AudioServer.set_bus_volume_db(0, -2.0)
	_build_streams()

	ambient = AudioStreamPlayer.new()
	ambient.name = "Ambient"
	add_child(ambient)
	ambient.finished.connect(_restart_ambient)

	fire = AudioStreamPlayer.new()
	fire.name = "Bonfire"
	fire.stream = fire_stream
	fire.volume_db = -60.0
	add_child(fire)
	fire.finished.connect(
		func():
			if current_mode == "valdrak":
				fire.play()
	)

	sfx = AudioStreamPlayer.new()
	sfx.name = "SFX"
	add_child(sfx)
	call_deferred("_bind_world")

func _build_streams() -> void:
	# Use real imported WAV assets. Generating PCM at startup was wasteful
	# on the Intel iGPU machine and could cause a silent/laggy first boot.
	room_stream = load("res://assets/audio/room_night.wav")
	wind_stream = load("res://assets/audio/valdrak_wind.wav")
	fire_stream = load("res://assets/audio/bonfire.wav")
	phone_stream = load("res://assets/audio/phone_chime.wav")
	sleep_stream = load("res://assets/audio/sleep_whoosh.wav")
	swing_stream = load("res://assets/audio/weapon_swing.wav")
	impact_stream = load("res://assets/audio/impact.wav")

func _bind_world() -> void:
	director = get_tree().get_first_node_in_group(
		"game_director"
	)
	player = get_tree().get_first_node_in_group(
		"player"
	) as Node3D
	if director:
		var cb := Callable(self, "_on_phase_changed")
		if not director.phase_changed.is_connected(cb):
			director.phase_changed.connect(cb)
	_apply_mode()

func _process(delta: float) -> void:
	update_timer -= delta
	if update_timer > 0.0:
		return
	update_timer = 0.20
	if not is_instance_valid(director):
		director = get_tree().get_first_node_in_group(
			"game_director"
		)
	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group(
			"player"
		) as Node3D
	_apply_mode()
	_update_fire()

func _on_phase_changed(
	_index: int,
	_chapter: String
) -> void:
	_apply_mode()

func _apply_mode() -> void:
	if not director:
		return
	var mode := (
		"room"
		if int(director.phase_index) < 0
		else "valdrak"
	)
	if mode == current_mode and ambient.playing:
		return
	current_mode = mode
	ambient.stop()
	ambient.stream = (
		room_stream
		if mode == "room"
		else wind_stream
	)
	ambient.volume_db = -12.0 if mode == "room" else -9.0
	ambient.play()

	if mode == "valdrak":
		if not fire.playing:
			fire.play()
	else:
		fire.stop()

func _restart_ambient() -> void:
	if ambient.stream:
		ambient.play()

func _update_fire() -> void:
	if (
		current_mode != "valdrak"
		or not is_instance_valid(player)
	):
		fire.volume_db = -60.0
		return
	var distance := player.global_position.distance_to(
		Vector3(0, 0, -6)
	)
	var level := clampf(
		1.0 - distance / 18.0,
		0.0,
		1.0
	)
	fire.volume_db = (
		linear_to_db(maxf(level, 0.001)) - 3.0
	)

func play_sfx(id: String) -> void:
	match id:
		"phone":
			sfx.stream = phone_stream
			sfx.volume_db = -4.0
		"sleep":
			sfx.stream = sleep_stream
			sfx.volume_db = -5.0
		"swing":
			sfx.stream = swing_stream
			sfx.volume_db = -6.0
		"impact":
			sfx.stream = impact_stream
			sfx.volume_db = -5.0
		_:
			return
	sfx.play()
