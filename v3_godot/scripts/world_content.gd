extends Node3D

const INTERACTION := preload("res://scripts/interaction_area.gd")
const EIRIK := preload("res://assets/characters/npcs/Eirik.glb")
const ASTRID := preload("res://assets/characters/npcs/Astrid.glb")
const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")
const LONG_SWORD := preload("res://assets/weapons/LongSword.obj")
const SIMPLE_AXE := preload("res://assets/weapons/SimpleAxe.obj")

const FORGE_ORIGIN := Vector3(0, 18, 82)
const ARCHIVE_ORIGIN := Vector3(24, 18, 82)
const TAVERN_ORIGIN := Vector3(-24, 18, 82)
const LOST_ROOM_ORIGIN := Vector3(48, 18, 82)
const CROW_DUNGEON_ORIGIN := Vector3(72, 18, 82)
const REAL_ROOM_ORIGIN := Vector3(120, 30, 120)

var wood := StandardMaterial3D.new()
var stone := StandardMaterial3D.new()
var metal := StandardMaterial3D.new()
var rune := StandardMaterial3D.new()

var story_npc_roots: Array[Node3D] = []
var story_npc_areas: Array[Area3D] = []
var last_story_phase := -999

func _ready() -> void:
	_build_materials()
	_build_real_world_room()
	_build_story_zones()
	_build_forge_interior()
	_build_archive_interior()
	_build_tavern_interior()
	_build_lost_student_house()
	_build_six_echoes()
	_build_crowwood_access()
	_build_crow_dungeon()
	call_deferred("_refresh_story_npc_visibility")

func _process(_delta: float) -> void:
	var director := get_tree().get_first_node_in_group(
		"game_director"
	)
	if not director:
		return
	var phase := int(director.phase_index)
	if phase == last_story_phase:
		return
	last_story_phase = phase
	_refresh_story_npc_visibility()

func _refresh_story_npc_visibility() -> void:
	var director := get_tree().get_first_node_in_group(
		"game_director"
	)
	var enabled := (
		director != null
		and int(director.phase_index) >= 3
	)
	for root in story_npc_roots:
		if is_instance_valid(root):
			root.visible = enabled
	for area in story_npc_areas:
		if is_instance_valid(area):
			area.set_deferred("monitoring", enabled)
			area.set_deferred("monitorable", enabled)

func _build_materials() -> void:
	wood.albedo_color = Color("4b3022")
	wood.roughness = 0.91

	stone.albedo_color = Color("343c40")
	stone.roughness = 0.86

	metal.albedo_color = Color("30383e")
	metal.metallic = 0.72
	metal.roughness = 0.35

	rune.albedo_color = Color("72f2ff")
	rune.emission_enabled = true
	rune.emission = Color("2bd8ff")
	rune.metallic = 0.12
	rune.roughness = 0.28
func _build_story_zones() -> void:
	_make_interaction(
		"BonfireArrival",
		Vector3(0, 0.8, -6.0),
		3.2,
		"",
		"bonfire_arrival",
		true,
		true
	)

	_make_interaction(
		"BonfireRest",
		Vector3(0, 0.8, -6.0),
		2.2,
		"Descansar na fogueira",
		"bonfire_rest"
	)

	_make_interaction(
		"ForgeDoor",
		Vector3(10.3, 1.0, 6.7),
		1.5,
		"Entrar na Ferraria de Eirik",
		"forge_enter",
		false,
		false,
		true,
		FORGE_ORIGIN + Vector3(0, 0.08, 3.55)
	)
	_make_marker(
		Vector3(10.3, 2.8, 6.7),
		"FERRARIA  //  R PARA ENTRAR",
		Color("6fefff")
	)

	_make_interaction(
		"EternalGate",
		Vector3(0, 1.0, -22.0),
		2.5,
		"",
		"eternal_gate",
		true,
		false
	)
	_make_interaction(
		"ArenaEntry",
		Vector3(0, 1.0, -25.1),
		2.3,
		"",
		"arena_entry",
		true,
		false
	)

	_make_interaction(
		"ArchiveDoor",
		Vector3(-10.8, 1.0, -10.2),
		1.5,
		"Entrar no Salão das Crônicas",
		"",
		false,
		false,
		true,
		ARCHIVE_ORIGIN + Vector3(0, 0.08, 2.7)
	)
	_make_marker(
		Vector3(-10.8, 2.8, -10.2),
		"SALÃO DAS CRÔNICAS",
		Color("d4b6ff")
	)

	_make_quest_board(Vector3(-5.8, 0.0, -4.2))

	_make_interaction(
		"TavernDoor",
		Vector3(-12.8, 1.0, 4.4),
		1.55,
		"Entrar na Taverna do Corvo",
		"tavern_enter",
		false,
		false,
		true,
		TAVERN_ORIGIN + Vector3(0, 0.08, 4.2)
	)
	_make_marker(
		Vector3(-12.8, 2.7, 4.4),
		"TAVERNA DO CORVO",
		Color("efc778")
	)

	_make_interaction(
		"LostStudentDoor",
		Vector3(18.7, 1.0, 10.25),
		1.75,
		"Entrar na Casa do Desperto",
		"lost_student_enter",
		false,
		false,
		true,
		LOST_ROOM_ORIGIN + Vector3(0, 0.08, 3.25)
	)
	_make_marker(
		Vector3(18.7, 2.65, 10.35),
		"CASA DO DESPERTO",
		Color("8ae8ff")
	)

func _build_forge_interior() -> void:
	_build_room(
		FORGE_ORIGIN,
		Vector2(13.0, 10.0),
		"FERRARIA DE EIRIK"
	)

	_make_interaction(
		"ForgeExit",
		FORGE_ORIGIN + Vector3(0, 1.0, 4.15),
		2.15,
		"Sair para Valdrak",
		"",
		false,
		false,
		true,
		Vector3(10.3, 0.08, 7.85)
	)

	# Porta de saída visível e proporcional. O vão da sala continua livre.
	var forge_door_mat := StandardMaterial3D.new()
	forge_door_mat.albedo_color = Color("4b2f20")
	forge_door_mat.roughness = 0.90
	var forge_frame_mat := StandardMaterial3D.new()
	forge_frame_mat.albedo_color = Color("241a14")
	forge_frame_mat.roughness = 0.86
	for x in [-0.72, 0.72]:
		_make_box(
			FORGE_ORIGIN + Vector3(x, 1.22, 4.78),
			Vector3(0.14, 2.44, 0.16),
			forge_frame_mat
		)
	_make_box(
		FORGE_ORIGIN + Vector3(0, 2.38, 4.78),
		Vector3(1.58, 0.16, 0.16),
		forge_frame_mat
	)
	var forge_door := _make_box(
		FORGE_ORIGIN + Vector3(0.92, 1.10, 4.55),
		Vector3(1.18, 2.20, 0.11),
		forge_door_mat
	)
	forge_door.name = "ForgeVisibleDoor"
	forge_door.rotation_degrees.y = -68.0

	var exit_glow_mat := StandardMaterial3D.new()
	exit_glow_mat.albedo_color = Color("ffd073")
	exit_glow_mat.emission_enabled = true
	exit_glow_mat.emission = Color("ffb54e")
	exit_glow_mat.emission_energy_multiplier = 2.4
	exit_glow_mat.roughness = 0.42
	_make_box(
		FORGE_ORIGIN + Vector3(0, 0.035, 4.25),
		Vector3(1.65, 0.06, 0.85),
		exit_glow_mat
	)
	var exit_light := OmniLight3D.new()
	exit_light.position = FORGE_ORIGIN + Vector3(0, 1.45, 4.20)
	exit_light.light_color = Color("ffc36d")
	exit_light.light_energy = 1.55
	exit_light.omni_range = 3.5
	exit_light.shadow_enabled = false
	add_child(exit_light)

	_make_marker(
		FORGE_ORIGIN + Vector3(0, 2.72, 4.58),
		"SAÍDA // VALDRAK",
		Color("f2c978")
	)

	_build_blacksmith(
		FORGE_ORIGIN + Vector3(-2.1, 0.0, -0.3)
	)

	_make_rune_relic(
		FORGE_ORIGIN + Vector3(2.25, 1.0, -1.2)
	)

	_make_anvil(FORGE_ORIGIN + Vector3(0.2, 0.55, -1.4))
	_make_table(
		FORGE_ORIGIN + Vector3(3.8, 0.65, 1.8),
		Vector3(2.4, 0.18, 1.0)
	)
	for z in [-2.8, -1.8, -0.8]:
		_make_weapon_rack(
			FORGE_ORIGIN + Vector3(-5.2, 1.15, z)
		)

	_make_hearth(
		FORGE_ORIGIN + Vector3(4.4, 0.35, -3.2)
	)

	_make_chest(
		"ForgeChest",
		FORGE_ORIGIN + Vector3(-3.7, 0.45, 2.4),
		"loot_forge_chest",
		"Abrir baú da ferraria"
	)

func _build_archive_interior() -> void:
	_build_room(
		ARCHIVE_ORIGIN,
		Vector2(12.0, 9.0),
		"SALÃO DAS CRÔNICAS"
	)

	_make_interaction(
		"ArchiveExit",
		ARCHIVE_ORIGIN + Vector3(0, 1.0, 3.65),
		1.3,
		"Sair para Valdrak",
		"",
		false,
		false,
		true,
		Vector3(-10.4, 0.08, -8.3)
	)

	var pedestal := _make_box(
		ARCHIVE_ORIGIN + Vector3(0, 0.65, -1.0),
		Vector3(1.2, 1.3, 1.2),
		stone
	)
	pedestal.rotation.y = 0.35

	var lore_area := _make_interaction(
		"LoreStone",
		ARCHIVE_ORIGIN + Vector3(0, 1.1, -1.0),
		1.5,
		"Ler a Crônica dos Eternos",
		"lore_house"
	)
	var crystal := MeshInstance3D.new()
	var crystal_mesh := PrismMesh.new()
	crystal_mesh.size = Vector3(0.45, 0.9, 0.45)
	crystal.mesh = crystal_mesh
	crystal.position.y = 0.8
	crystal.material_override = rune
	lore_area.add_child(crystal)

	for x in [-4.3, 4.3]:
		for z in [-2.6, -0.7, 1.2]:
			_make_shelf(
				ARCHIVE_ORIGIN + Vector3(x, 1.25, z)
			)

	_make_chest(
		"ArchiveChest",
		ARCHIVE_ORIGIN + Vector3(3.1, 0.45, -2.9),
		"loot_archive_chest",
		"Abrir cofre das crônicas"
	)

func _build_room(
	origin: Vector3,
	size: Vector2,
	title: String
) -> void:
	_make_box(
		origin + Vector3(0, -0.18, 0),
		Vector3(size.x, 0.35, size.y),
		stone,
		true
	)

	var wall_h := 4.4
	var thickness := 0.35
	_make_box(
		origin + Vector3(0, wall_h * 0.5, -size.y * 0.5),
		Vector3(size.x, wall_h, thickness),
		stone,
		true
	)
	_make_box(
		origin + Vector3(-size.x * 0.5, wall_h * 0.5, 0),
		Vector3(thickness, wall_h, size.y),
		stone,
		true
	)
	_make_box(
		origin + Vector3(size.x * 0.5, wall_h * 0.5, 0),
		Vector3(thickness, wall_h, size.y),
		stone,
		true
	)

	var front_z := size.y * 0.5
	_make_box(
		origin + Vector3(-4.1, wall_h * 0.5, front_z),
		Vector3(size.x * 0.34, wall_h, thickness),
		stone,
		true
	)
	_make_box(
		origin + Vector3(4.1, wall_h * 0.5, front_z),
		Vector3(size.x * 0.34, wall_h, thickness),
		stone,
		true
	)
	_make_box(
		origin + Vector3(0, wall_h - 0.45, front_z),
		Vector3(3.3, 0.9, thickness),
		wood,
		true
	)

	_make_box(
		origin + Vector3(0, wall_h + 0.18, 0),
		Vector3(size.x, 0.28, size.y),
		wood,
		true
	)

	_make_marker(
		origin + Vector3(0, 3.3, -size.y * 0.5 + 0.25),
		title,
		Color("dffcff")
	)
	_make_interior_light(origin + Vector3(-3.5, 2.7, 0))
	_make_interior_light(origin + Vector3(3.5, 2.7, 0))
func _build_blacksmith(pos: Vector3) -> void:
	var root := Node3D.new()
	root.position = pos
	add_child(root)

	var model := EIRIK.instantiate()
	model.scale = Vector3.ONE * 0.50
	model.rotation.y = PI
	root.add_child(model)
	_fix_npc_materials(model, "eirik")

	var anim := model.find_child(
		"AnimationPlayer",
		true,
		false
	) as AnimationPlayer
	if anim:
		anim.play("CharacterArmature|CharacterArmature|Idle")

	var label := Label3D.new()
	label.text = "EIRIK // FERREIRO"
	label.position = Vector3(0, 2.08, 0)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 28
	label.outline_size = 8
	label.modulate = Color("7fefff")
	root.add_child(label)

	_make_interaction(
		"TalkEirik",
		pos + Vector3(0, 0.9, 0),
		1.45,
		"Falar com Eirik",
		"blacksmith_talk"
	)

func _make_rune_relic(pos: Vector3) -> void:
	var area := _make_interaction(
		"BrokenRune",
		pos,
		1.25,
		"Recuperar a Runa Partida",
		"rune_collect",
		false,
		true
	)
	var crystal := MeshInstance3D.new()
	var mesh := PrismMesh.new()
	mesh.size = Vector3(0.62, 1.25, 0.62)
	crystal.mesh = mesh
	crystal.rotation_degrees = Vector3(0, 22, 18)
	crystal.material_override = rune
	area.add_child(crystal)

	var light := OmniLight3D.new()
	light.light_color = Color("5be7ff")
	light.light_energy = 2.7
	light.omni_range = 4.8
	area.add_child(light)

func _make_interaction(
	node_name: String,
	pos: Vector3,
	radius: float,
	prompt := "Interagir",
	event := "",
	auto := false,
	once := false,
	teleport := false,
	target := Vector3.ZERO
) -> Area3D:
	var area := Area3D.new()
	area.name = node_name
	area.position = pos
	area.set_script(INTERACTION)
	area.prompt_text = prompt
	area.event_id = event
	area.auto_trigger = auto
	area.one_shot = once
	area.teleport_enabled = teleport
	area.target_position = target

	var collision := CollisionShape3D.new()
	var shape := SphereShape3D.new()
	shape.radius = radius
	collision.shape = shape
	area.add_child(collision)
	add_child(area)
	return area
func _make_marker(
	pos: Vector3,
	text: String,
	color: Color
) -> void:
	var label := Label3D.new()
	label.position = pos
	label.text = text
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 26
	label.outline_size = 8
	label.modulate = color
	add_child(label)

func _make_box(
	pos: Vector3,
	size: Vector3,
	material: Material,
	collidable := false
) -> Node3D:
	var root: Node3D
	if collidable:
		root = StaticBody3D.new()
	else:
		root = Node3D.new()
	root.position = pos

	var mesh_instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mesh_instance.mesh = mesh
	mesh_instance.material_override = material
	root.add_child(mesh_instance)

	if collidable:
		var collision := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = size
		collision.shape = shape
		root.add_child(collision)
	add_child(root)
	return root
func _make_table(pos: Vector3, size: Vector3) -> void:
	_make_box(pos, size, wood)
	for x in [-0.95, 0.95]:
		for z in [-0.32, 0.32]:
			_make_box(
				pos + Vector3(x, -0.55, z),
				Vector3(0.14, 1.1, 0.14),
				wood
			)

func _make_anvil(pos: Vector3) -> void:
	_make_box(pos, Vector3(1.4, 0.35, 0.55), metal)
	_make_box(
		pos + Vector3(0, -0.55, 0),
		Vector3(0.55, 0.9, 0.45),
		metal
	)

func _make_weapon_rack(pos: Vector3) -> void:
	_make_box(pos, Vector3(0.16, 2.1, 0.16), wood)
	_make_box(
		pos + Vector3(0.85, 0, 0),
		Vector3(0.16, 2.1, 0.16),
		wood
	)
	_make_box(
		pos + Vector3(0.42, 0.45, 0),
		Vector3(1.0, 0.10, 0.12),
		wood
	)

func _make_shelf(pos: Vector3) -> void:
	_make_box(pos, Vector3(1.6, 2.5, 0.35), wood)
	for y in [-0.75, 0.0, 0.75]:
		_make_box(
			pos + Vector3(0, y, -0.22),
			Vector3(1.75, 0.08, 0.55),
			wood
		)

func _make_hearth(pos: Vector3) -> void:
	_make_box(pos, Vector3(2.2, 0.55, 1.4), stone)
	var light := OmniLight3D.new()
	light.position = pos + Vector3(0, 1.0, 0)
	light.light_color = Color("ff7f32")
	light.light_energy = 3.5
	light.omni_range = 5.5
	add_child(light)

func _make_interior_light(pos: Vector3) -> void:
	var light := OmniLight3D.new()
	light.position = pos
	light.light_color = Color("ffc77d")
	light.light_energy = 2.2
	light.omni_range = 7.0
	light.shadow_enabled = false
	add_child(light)

func _make_chest(
	node_name: String,
	pos: Vector3,
	event_id: String,
	prompt: String
) -> void:
	var area := _make_interaction(
		node_name,
		pos + Vector3(0, 0.65, 0),
		1.35,
		prompt,
		event_id,
		false,
		true
	)

	var chest := Node3D.new()
	chest.position = Vector3(0, -0.38, 0)
	area.add_child(chest)

	var base := MeshInstance3D.new()
	var base_mesh := BoxMesh.new()
	base_mesh.size = Vector3(1.2, 0.6, 0.75)
	base.mesh = base_mesh
	base.material_override = wood
	chest.add_child(base)

	var lid := MeshInstance3D.new()
	var lid_mesh := BoxMesh.new()
	lid_mesh.size = Vector3(1.25, 0.22, 0.8)
	lid.mesh = lid_mesh
	lid.position.y = 0.42
	lid.material_override = metal
	chest.add_child(lid)

	var rune_mark := MeshInstance3D.new()
	var rune_mesh := BoxMesh.new()
	rune_mesh.size = Vector3(0.18, 0.32, 0.82)
	rune_mark.mesh = rune_mesh
	rune_mark.position = Vector3(0, 0.02, -0.39)
	rune_mark.material_override = rune
	chest.add_child(rune_mark)

func _make_quest_board(pos: Vector3) -> void:
	var area := _make_interaction(
		"QuestBoard",
		pos + Vector3(0, 1.2, 0),
		1.8,
		"Ver quadro de caçadas",
		"quest_board"
	)

	var board := Node3D.new()
	board.position = Vector3(0, -0.25, 0)
	area.add_child(board)

	for x in [-0.95, 0.95]:
		var post := MeshInstance3D.new()
		var post_mesh := BoxMesh.new()
		post_mesh.size = Vector3(0.14, 2.2, 0.16)
		post.mesh = post_mesh
		post.position = Vector3(x, 0.0, 0)
		post.material_override = wood
		board.add_child(post)

	var plank := MeshInstance3D.new()
	var plank_mesh := BoxMesh.new()
	plank_mesh.size = Vector3(2.35, 1.25, 0.14)
	plank.mesh = plank_mesh
	plank.position = Vector3(0, 0.35, 0)
	plank.material_override = wood
	board.add_child(plank)

	var label := Label3D.new()
	label.text = "CAÇADAS"
	label.position = Vector3(0, 0.45, -0.12)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 24
	label.outline_size = 6
	label.modulate = Color("f2c879")
	board.add_child(label)

func _build_tavern_interior() -> void:
	_build_room(
		TAVERN_ORIGIN,
		Vector2(15.0, 11.0),
		"TAVERNA DO CORVO"
	)

	_make_interaction(
		"TavernExit",
		TAVERN_ORIGIN + Vector3(0, 1.0, 4.65),
		1.35,
		"Sair para Valdrak",
		"",
		false,
		false,
		true,
		Vector3(-12.6, 0.08, 6.2)
	)

	_make_box(
		TAVERN_ORIGIN + Vector3(-4.8, 0.78, -2.4),
		Vector3(4.0, 0.18, 1.0),
		wood
	)
	for pos in [
		Vector3(-2.8, 0.65, 0.7),
		Vector3(1.0, 0.65, 1.4),
		Vector3(3.4, 0.65, -1.3)
	]:
		_make_table(
			TAVERN_ORIGIN + pos,
			Vector3(2.1, 0.16, 1.15)
		)
		_make_bench(
			TAVERN_ORIGIN + pos + Vector3(0, -0.22, 0.95)
		)
		_make_bench(
			TAVERN_ORIGIN + pos + Vector3(0, -0.22, -0.95)
		)

	_build_innkeeper(
		TAVERN_ORIGIN + Vector3(-4.4, 0.0, -1.6)
	)
	_make_dream_phone_echo(
		TAVERN_ORIGIN + Vector3(2.6, 0.95, -3.5)
	)
	_make_hearth(
		TAVERN_ORIGIN + Vector3(5.6, 0.35, -3.7)
	)
func _make_bench(pos: Vector3) -> void:
	_make_box(
		pos,
		Vector3(1.75, 0.16, 0.42),
		wood
	)
	for x in [-0.62, 0.62]:
		_make_box(
			pos + Vector3(x, -0.34, 0),
			Vector3(0.12, 0.68, 0.12),
			wood
		)

func _build_innkeeper(pos: Vector3) -> void:
	var root := Node3D.new()
	root.position = pos
	add_child(root)

	var model := ASTRID.instantiate()
	model.scale = Vector3.ONE * 0.55
	model.rotation.y = PI
	root.add_child(model)
	_fix_npc_materials(model, "astrid")

	var anim := model.find_child(
		"AnimationPlayer",
		true,
		false
	) as AnimationPlayer
	if anim:
		anim.play(
			"CharacterArmature|CharacterArmature|Idle"
		)

	var label := Label3D.new()
	label.text = "ASTRID // HOSPEDEIRA"
	label.position = Vector3(0, 2.02, 0)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 26
	label.outline_size = 7
	label.modulate = Color("efc778")
	root.add_child(label)

	_make_interaction(
		"TalkAstrid",
		pos + Vector3(0, 0.88, 0),
		1.45,
		"Falar com Astrid",
		"astrid_talk"
	)

func _make_dream_phone_echo(pos: Vector3) -> void:
	var area := _make_interaction(
		"DreamPhoneEcho",
		pos,
		1.35,
		"Ler notificação impossível",
		"dream_echo_1",
		false,
		false
	)

	var phone := MeshInstance3D.new()
	var phone_mesh := BoxMesh.new()
	phone_mesh.size = Vector3(0.18, 0.035, 0.34)
	phone.mesh = phone_mesh
	phone.position = Vector3(0, -0.08, 0)
	var phone_mat := StandardMaterial3D.new()
	phone_mat.albedo_color = Color("121a20")
	phone_mat.metallic = 0.7
	phone_mat.roughness = 0.24
	phone.material_override = phone_mat
	area.add_child(phone)

	var screen := MeshInstance3D.new()
	var screen_mesh := BoxMesh.new()
	screen_mesh.size = Vector3(0.15, 0.008, 0.29)
	screen.mesh = screen_mesh
	screen.position = Vector3(0, -0.057, 0)
	var screen_mat := StandardMaterial3D.new()
	screen_mat.albedo_color = Color("66efff")
	screen_mat.emission_enabled = true
	screen_mat.emission = Color("27d9ee")
	screen_mat.emission_energy_multiplier = 3.0
	screen.material_override = screen_mat
	area.add_child(screen)

	var light := OmniLight3D.new()
	light.light_color = Color("66efff")
	light.light_energy = 1.8
	light.omni_range = 2.6
	light.position = Vector3(0, 0.25, 0)
	area.add_child(light)

func _fix_npc_materials(
	model: Node3D,
	variant: String
) -> void:
	var palette := {
		"Skin": Color("855942"),
		"Shirt": (
			Color("5a2f2b")
			if variant == "eirik"
			else Color("385748")
		),
		"Pants": Color("292e32"),
		"Belt": Color("593827"),
		"Face": Color("f1f1e8"),
		"Hair": (
			Color("3a2922")
			if variant == "eirik"
			else Color("6a3a2a")
		)
	}

	for node in model.find_children(
		"*",
		"MeshInstance3D",
		true,
		false
	):
		var mesh_instance := node as MeshInstance3D
		if not mesh_instance.mesh:
			continue
		for surface in range(
			mesh_instance.mesh.get_surface_count()
		):
			var source := mesh_instance.get_active_material(
				surface
			)
			if not source is StandardMaterial3D:
				continue
			var material := source.duplicate() as StandardMaterial3D
			material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
			var color := material.albedo_color
			var mat_name := str(material.resource_name)
			if palette.has(mat_name):
				color = palette[mat_name]
			color.a = 1.0
			material.albedo_color = color
			material.roughness = 0.76
			mesh_instance.set_surface_override_material(
				surface,
				material
			)

	var npc_skeleton := model.find_child(
		"Skeleton3D",
		true,
		false
	) as Skeleton3D
	if npc_skeleton:
		var head := npc_skeleton.find_bone("Head")
		if head >= 0:
			npc_skeleton.set_bone_pose_scale(
				head,
				Vector3(0.72, 0.72, 0.72)
			)

func _build_real_world_room() -> void:
	var wall := StandardMaterial3D.new()
	wall.albedo_color = Color("d8d1c4")
	wall.roughness = 0.90

	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color("5b402f")
	floor_mat.roughness = 0.88

	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color("20252c")
	dark.roughness = 0.78

	var fabric := StandardMaterial3D.new()
	fabric.albedo_color = Color("334c62")
	fabric.roughness = 0.96

	var paper := StandardMaterial3D.new()
	paper.albedo_color = Color("e8e2d2")
	paper.roughness = 0.98

	var screen := StandardMaterial3D.new()
	screen.albedo_color = Color("73efff")
	screen.emission_enabled = true
	screen.emission = Color("29d7ee")
	screen.emission_energy_multiplier = 2.2
	screen.roughness = 0.12

	var o := REAL_ROOM_ORIGIN
	_make_box(
		o + Vector3(0, -0.18, 0),
		Vector3(9.0, 0.35, 7.0),
		floor_mat,
		true
	)
	_make_box(
		o + Vector3(0, 2.0, -3.5),
		Vector3(9.0, 4.0, 0.28),
		wall,
		true
	)
	_make_box(
		o + Vector3(-4.5, 2.0, 0),
		Vector3(0.28, 4.0, 7.0),
		wall,
		true
	)
	_make_box(
		o + Vector3(4.5, 2.0, 0),
		Vector3(0.28, 4.0, 7.0),
		wall,
		true
	)
	_make_box(
		o + Vector3(0, 4.05, 0),
		Vector3(9.0, 0.22, 7.0),
		wall,
		true
	)

	# Parede frontal fechada com porta real. A câmera não pode sair do quarto.
	_make_box(
		o + Vector3(-2.85, 2.0, 3.5),
		Vector3(3.30, 4.0, 0.28),
		wall,
		true
	)
	_make_box(
		o + Vector3(2.45, 2.0, 3.5),
		Vector3(4.10, 4.0, 0.28),
		wall,
		true
	)
	_make_box(
		o + Vector3(-0.55, 3.55, 3.5),
		Vector3(1.30, 0.90, 0.28),
		wall,
		true
	)

	var door_mat := StandardMaterial3D.new()
	door_mat.albedo_color = Color("4a3327")
	door_mat.roughness = 0.84
	var real_door := _make_box(
		o + Vector3(-0.55, 1.45, 3.42),
		Vector3(1.18, 2.90, 0.16),
		door_mat,
		true
	)
	real_door.name = "BedroomDoor"

	var frame_mat := StandardMaterial3D.new()
	frame_mat.albedo_color = Color("2a211d")
	frame_mat.roughness = 0.76
	for x in [-1.18, 0.08]:
		_make_box(
			o + Vector3(x, 1.55, 3.32),
			Vector3(0.10, 3.10, 0.12),
			frame_mat
		)
	_make_box(
		o + Vector3(-0.55, 3.08, 3.32),
		Vector3(1.36, 0.12, 0.12),
		frame_mat
	)

	var knob := MeshInstance3D.new()
	var knob_mesh := SphereMesh.new()
	knob_mesh.radius = 0.055
	knob_mesh.height = 0.11
	knob.mesh = knob_mesh
	knob.position = o + Vector3(-0.12, 1.35, 3.29)
	var knob_mat := StandardMaterial3D.new()
	knob_mat.albedo_color = Color("a78b57")
	knob_mat.metallic = 0.72
	knob_mat.roughness = 0.28
	knob.material_override = knob_mat
	add_child(knob)

	_make_interaction(
		"RealBedroomDoor",
		o + Vector3(-0.55, 1.15, 2.82),
		1.10,
		"Verificar a porta",
		"real_room_door"
	)

	# Cama do estudante.
	_make_box(
		o + Vector3(-2.75, 0.35, 0.85),
		Vector3(2.05, 0.42, 3.45),
		dark
	)
	_make_box(
		o + Vector3(-2.75, 0.62, 0.78),
		Vector3(1.9, 0.28, 3.1),
		fabric
	)
	_make_box(
		o + Vector3(-2.75, 0.86, -0.48),
		Vector3(1.72, 0.18, 0.72),
		paper
	)

	_make_interaction(
		"RealBed",
		o + Vector3(-2.75, 0.85, 0.9),
		1.55,
		"Dormir",
		"dream_begin"
	)

	# Escrivaninha e cadeira.
	_make_box(
		o + Vector3(2.65, 0.78, -1.75),
		Vector3(3.1, 0.16, 1.05),
		dark
	)
	for x in [-1.25, 1.25]:
		_make_box(
			o + Vector3(2.65 + x, 0.38, -1.75),
			Vector3(0.14, 0.78, 0.14),
			dark
		)

	_make_box(
		o + Vector3(2.45, 0.47, -0.55),
		Vector3(0.72, 0.16, 0.72),
		dark
	)
	_make_box(
		o + Vector3(2.45, 0.95, -0.85),
		Vector3(0.72, 0.88, 0.12),
		dark
	)
	# Quarto normal do mundo real: notebook na mesa e televisão.
	var laptop := Node3D.new()
	laptop.name = "BedroomLaptop"
	laptop.position = o + Vector3(2.30, 0.90, -1.72)
	add_child(laptop)

	var laptop_base := MeshInstance3D.new()
	var laptop_base_mesh := BoxMesh.new()
	laptop_base_mesh.size = Vector3(0.78, 0.045, 0.52)
	laptop_base.mesh = laptop_base_mesh
	laptop_base.material_override = dark
	laptop.add_child(laptop_base)

	var laptop_screen := MeshInstance3D.new()
	var laptop_screen_mesh := BoxMesh.new()
	laptop_screen_mesh.size = Vector3(0.78, 0.48, 0.04)
	laptop_screen.mesh = laptop_screen_mesh
	laptop_screen.position = Vector3(0, 0.27, -0.23)
	laptop_screen.rotation_degrees.x = -10.0
	var laptop_glow := StandardMaterial3D.new()
	laptop_glow.albedo_color = Color("1f87bb")
	laptop_glow.emission_enabled = true
	laptop_glow.emission = Color("126d9d")
	laptop_glow.emission_energy_multiplier = 1.45
	laptop_glow.roughness = 0.20
	laptop_screen.material_override = laptop_glow
	laptop.add_child(laptop_screen)

	var keyboard := MeshInstance3D.new()
	var keyboard_mesh := BoxMesh.new()
	keyboard_mesh.size = Vector3(0.62, 0.018, 0.24)
	keyboard.mesh = keyboard_mesh
	keyboard.position = Vector3(0, 0.035, 0.04)
	keyboard.material_override = dark
	laptop.add_child(keyboard)

	# TV de parede, desligada para manter a cena noturna.
	var tv_frame := _make_box(
		o + Vector3(-0.1, 2.05, -3.28),
		Vector3(2.15, 1.22, 0.10),
		dark
	)
	tv_frame.name = "BedroomTV"
	var tv_screen_mat := StandardMaterial3D.new()
	tv_screen_mat.albedo_color = Color("111820")
	tv_screen_mat.metallic = 0.15
	tv_screen_mat.roughness = 0.18
	_make_box(
		o + Vector3(-0.1, 2.05, -3.215),
		Vector3(1.98, 1.06, 0.025),
		tv_screen_mat
	)

	# Criado-mudo e luminária simples.
	_make_box(
		o + Vector3(-3.78, 0.42, 1.55),
		Vector3(0.72, 0.84, 0.72),
		dark
	)
	var lamp := OmniLight3D.new()
	lamp.position = o + Vector3(-3.78, 1.28, 1.55)
	lamp.light_color = Color("ffd0a0")
	lamp.light_energy = 0.68
	lamp.omni_range = 2.9
	lamp.shadow_enabled = false
	add_child(lamp)

	# Livros/cadernos.
	for i in range(4):
		_make_box(
			o + Vector3(
				3.15,
				0.91 + float(i) * 0.045,
				-1.76
			),
			Vector3(
				0.58 - float(i) * 0.03,
				0.04,
				0.42
			),
			paper
		)

	var phone_area := _make_interaction(
		"RealPhone",
		o + Vector3(2.85, 1.0, -1.55),
		1.25,
		"Pegar celular",
		"real_phone",
		false,
		true
	)
	_make_phone_prop(phone_area, Vector3(0, -0.16, 0))
	# Estante com materiais da faculdade.
	for y in [0.55, 1.25, 1.95]:
		_make_box(
			o + Vector3(-3.9, y, -2.75),
			Vector3(1.0, 0.10, 0.48),
			dark
		)
	for x in [-0.42, 0.42]:
		_make_box(
			o + Vector3(-3.9 + x, 1.25, -2.75),
			Vector3(0.08, 2.5, 0.45),
			dark
		)

	# Janela fechada: cidade real do lado de fora.
	var glass := StandardMaterial3D.new()
	glass.albedo_color = Color(0.08, 0.14, 0.20, 0.55)
	glass.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glass.metallic = 0.15
	glass.roughness = 0.12
	_make_box(
		o + Vector3(0.2, 2.15, -3.32),
		Vector3(2.7, 1.55, 0.035),
		glass
	)

	for i in range(10):
		var light_box := MeshInstance3D.new()
		var light_mesh := BoxMesh.new()
		light_mesh.size = Vector3(0.16, 0.10, 0.02)
		light_box.mesh = light_mesh
		light_box.position = o + Vector3(
			-0.9 + float(i % 5) * 0.48,
			1.75 + float(i / 5) * 0.58,
			-3.39
		)
		var city_mat := StandardMaterial3D.new()
		city_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		city_mat.albedo_color = Color("ffd98a")
		city_mat.emission_enabled = true
		city_mat.emission = Color("ffc66d")
		light_box.material_override = city_mat
		add_child(light_box)

	var room_light := OmniLight3D.new()
	room_light.position = o + Vector3(0, 2.75, 0)
	room_light.light_color = Color("ffd6aa")
	room_light.light_energy = 1.45
	room_light.omni_range = 7.0
	room_light.shadow_enabled = false
	add_child(room_light)

func _build_lost_student_house() -> void:
	_build_room(
		LOST_ROOM_ORIGIN,
		Vector2(11.5, 8.5),
		"CASA DO DESPERTO"
	)

	_make_interaction(
		"LostHouseExit",
		LOST_ROOM_ORIGIN + Vector3(0, 1.0, 3.35),
		1.35,
		"Sair para Valdrak",
		"",
		false,
		false,
		true,
		Vector3(18.7, 0.08, 10.0)
	)

	_make_box(
		LOST_ROOM_ORIGIN + Vector3(-3.3, 0.42, -1.6),
		Vector3(1.8, 0.46, 3.0),
		wood
	)
	_make_interaction(
		"RecoveryBed",
		LOST_ROOM_ORIGIN + Vector3(-3.3, 1.0, -1.15),
		1.45,
		"Descansar e registrar despertar",
		"recovery_bed"
	)
	var old_fabric := StandardMaterial3D.new()
	old_fabric.albedo_color = Color("384c5b")
	old_fabric.roughness = 0.97
	_make_box(
		LOST_ROOM_ORIGIN + Vector3(-3.3, 0.72, -1.6),
		Vector3(1.65, 0.22, 2.72),
		old_fabric
	)

	_make_table(
		LOST_ROOM_ORIGIN + Vector3(2.65, 0.66, -1.8),
		Vector3(2.2, 0.16, 1.0)
	)

	var echo := _make_interaction(
		"LostPhoneEcho",
		LOST_ROOM_ORIGIN + Vector3(2.65, 0.95, -1.8),
		1.25,
		"Examinar celular quebrado",
		"lost_student_phone"
	)
	_make_phone_prop(echo, Vector3(0, -0.18, 0))

	var note := _make_interaction(
		"LostNotebook",
		LOST_ROOM_ORIGIN + Vector3(1.5, 0.9, 1.2),
		1.35,
		"Ler caderno do Desperto",
		"lost_notebook"
	)
	var paper_mat := StandardMaterial3D.new()
	paper_mat.albedo_color = Color("d9d1b8")
	paper_mat.roughness = 1.0
	var note_mesh := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.55, 0.04, 0.72)
	note_mesh.mesh = mesh
	note_mesh.material_override = paper_mat
	note.add_child(note_mesh)

	_make_box(
		LOST_ROOM_ORIGIN + Vector3(-0.4, 0.62, 2.0),
		Vector3(0.55, 1.15, 0.30),
		metal
	)
func _make_phone_prop(
	parent: Node3D,
	offset: Vector3
) -> void:
	var shell := MeshInstance3D.new()
	var shell_mesh := BoxMesh.new()
	shell_mesh.size = Vector3(0.17, 0.035, 0.32)
	shell.mesh = shell_mesh
	shell.position = offset
	var shell_mat := StandardMaterial3D.new()
	shell_mat.albedo_color = Color("12171d")
	shell_mat.metallic = 0.72
	shell_mat.roughness = 0.24
	shell.material_override = shell_mat
	parent.add_child(shell)

	var display := MeshInstance3D.new()
	var display_mesh := BoxMesh.new()
	display_mesh.size = Vector3(0.145, 0.010, 0.285)
	display.mesh = display_mesh
	display.position = offset + Vector3(0, -0.023, 0)
	var display_mat := StandardMaterial3D.new()
	display_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	display_mat.albedo_color = Color("65efff")
	display_mat.emission_enabled = true
	display_mat.emission = Color("2cdff2")
	display_mat.emission_energy_multiplier = 2.8
	display.material_override = display_mat
	parent.add_child(display)

	var light := OmniLight3D.new()
	light.position = offset + Vector3(0, 0.20, 0)
	light.light_color = Color("65efff")
	light.light_energy = 1.0
	light.omni_range = 1.8
	parent.add_child(light)

func _build_six_echoes() -> void:
	var configs := [
		{
			"name":"Thorvald",
			"role":"GUARDIÃO DOS CLÃS",
			"pos":Vector3(4.8, 0.0, -2.8),
			"model":2,
			"scale":0.49,
			"color":Color("e8c27a")
		},
		{
			"name":"Aurel",
			"role":"CRONISTA RÚNICO",
			"pos":Vector3(-8.8, 0.0, -8.8),
			"model":0,
			"scale":0.50,
			"color":Color("a98cff")
		},
		{
			"name":"Kaion",
			"role":"BATEDOR",
			"pos":Vector3(-16.2, 0.0, 9.8),
			"model":2,
			"scale":0.49,
			"color":Color("6fe6b2")
		},
		{
			"name":"Brenor",
			"role":"FERREIRO DE GUERRA",
			"pos":Vector3(14.4, 0.0, 5.8),
			"model":0,
			"scale":0.51,
			"color":Color("f49a61")
		},
		{
			"name":"Eiran",
			"role":"CURANDEIRA DOS DESPERTOS",
			"pos":Vector3(-5.8, 0.0, 7.2),
			"model":1,
			"scale":0.55,
			"color":Color("80d8ff")
		},
		{
			"name":"Noctar",
			"role":"EXILADO DO VAZIO",
			"pos":Vector3(22.0, 0.0, -15.0),
			"model":2,
			"scale":0.50,
			"color":Color("d66cff")
		}
	]
	for cfg in configs:
		_build_story_npc(cfg)

func _build_story_npc(cfg: Dictionary) -> void:
	var root := Node3D.new()
	root.name = str(cfg.name)
	root.position = cfg.pos
	add_child(root)
	story_npc_roots.append(root)

	var packed: PackedScene
	match int(cfg.model):
		1:
			packed = ASTRID
		2:
			packed = VIKING
		_:
			packed = EIRIK

	var model := packed.instantiate()
	model.scale = Vector3.ONE * float(cfg.scale)
	model.rotation.y = PI
	root.add_child(model)
	_apply_story_npc_accent(
		model,
		cfg.color
	)

	var anim := model.find_child(
		"AnimationPlayer",
		true,
		false
	) as AnimationPlayer
	if anim and anim.has_animation(
		"CharacterArmature|CharacterArmature|Idle"
	):
		anim.play(
			"CharacterArmature|CharacterArmature|Idle"
		)
	elif anim and anim.has_animation(
		"CharacterArmature|Idle"
	):
		anim.play("CharacterArmature|Idle")

	var label := Label3D.new()
	label.text = "%s // %s" % [
		str(cfg.name).to_upper(),
		str(cfg.role)
	]
	label.position = Vector3(0, 2.02, 0)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 20
	label.outline_size = 7
	label.modulate = cfg.color
	root.add_child(label)

	_add_npc_signature(
		root,
		cfg.color,
		int(cfg.model)
	)

	var talk_area := _make_interaction(
		"Talk%s" % str(cfg.name),
		root.position + Vector3(0, 0.92, 0),
		1.6,
		"Falar com %s" % str(cfg.name),
		"npc_%s" % str(cfg.name).to_lower()
	)
	story_npc_areas.append(talk_area)

func _apply_story_npc_accent(
	model: Node3D,
	color: Color
) -> void:
	var overlay := StandardMaterial3D.new()
	overlay.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	overlay.albedo_color = Color(
		color.r,
		color.g,
		color.b,
		0.10
	)
	overlay.emission_enabled = true
	overlay.emission = color.darkened(0.78)
	for node in model.find_children(
		"*",
		"MeshInstance3D",
		true,
		false
	):
		(node as MeshInstance3D).material_overlay = overlay

	var npc_skeleton := model.find_child(
		"Skeleton3D",
		true,
		false
	) as Skeleton3D
	if npc_skeleton:
		var head := npc_skeleton.find_bone("Head")
		if head >= 0:
			npc_skeleton.set_bone_pose_scale(
				head,
				Vector3.ONE * 0.72
			)
func _add_npc_signature(
	root: Node3D,
	color: Color,
	model_key: int
) -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color.darkened(0.28)
	mat.metallic = 0.28
	mat.roughness = 0.46
	mat.emission_enabled = true
	mat.emission = color.darkened(0.72)

	if model_key == 1:
		var staff := MeshInstance3D.new()
		var staff_mesh := CylinderMesh.new()
		staff_mesh.top_radius = 0.035
		staff_mesh.bottom_radius = 0.045
		staff_mesh.height = 1.72
		staff.mesh = staff_mesh
		staff.position = Vector3(0.42, 0.86, 0.05)
		staff.material_override = mat
		root.add_child(staff)

		var orb := MeshInstance3D.new()
		var orb_mesh := SphereMesh.new()
		orb_mesh.radius = 0.10
		orb_mesh.height = 0.20
		orb.mesh = orb_mesh
		orb.position = Vector3(0.42, 1.76, 0.05)
		orb.material_override = mat
		root.add_child(orb)
	elif model_key == 2:
		var mantle := MeshInstance3D.new()
		var mantle_mesh := BoxMesh.new()
		mantle_mesh.size = Vector3(0.72, 0.12, 0.22)
		mantle.mesh = mantle_mesh
		mantle.position = Vector3(0, 1.45, 0.08)
		mantle.material_override = mat
		root.add_child(mantle)
	else:
		var rune_plate := MeshInstance3D.new()
		var plate_mesh := BoxMesh.new()
		plate_mesh.size = Vector3(0.30, 0.38, 0.06)
		rune_plate.mesh = plate_mesh
		rune_plate.position = Vector3(0, 1.28, -0.18)
		rune_plate.material_override = mat
		root.add_child(rune_plate)

func _build_crowwood_access() -> void:
	_make_interaction(
		"CrowwoodGate",
		Vector3(-44.0, 1.45, -8.0),
		3.2,
		"Entrar no Bosque dos Corvos",
		"crowwood_gate"
	)
	_make_marker(
		Vector3(-44.0, 3.65, -8.0),
		"BOSQUE DOS CORVOS",
		Color("79d6b0")
	)

	_make_interaction(
		"CrowDungeonDoor",
		Vector3(-72.0, -0.05, -24.0),
		2.2,
		"Descer para a masmorra",
		"crow_dungeon",
		false,
		false,
		true,
		CROW_DUNGEON_ORIGIN + Vector3(
			0,
			0.08,
			6.4
		)
	)
	_make_marker(
		Vector3(-72.0, 1.85, -24.0),
		"RUÍNAS SOB AS RAÍZES",
		Color("b38aff")
	)

	_make_interaction(
		"RegionTwoGate",
		Vector3(72.0, 5.0, 42.0),
		2.8,
		"Atravessar para a Região II",
		"region_two_gate"
	)
	_make_marker(
		Vector3(72.0, 7.4, 42.0),
		"PASSAGEM DAS MONTANHAS",
		Color("7fefff")
	)
func _build_crow_dungeon() -> void:
	_build_room(
		CROW_DUNGEON_ORIGIN,
		Vector2(20.0, 16.0),
		"MASMORRA DOS CORVOS"
	)

	_make_interaction(
		"CrowDungeonExit",
		CROW_DUNGEON_ORIGIN + Vector3(
			0,
			1.0,
			6.9
		),
		1.6,
		"Voltar ao Bosque dos Corvos",
		"",
		false,
		false,
		true,
		Vector3(-69.5, 0.08, -21.5)
	)

	for x in [-7.2, -3.6, 0.0, 3.6, 7.2]:
		_make_box(
			CROW_DUNGEON_ORIGIN + Vector3(
				x,
				1.5,
				-4.8
			),
			Vector3(0.75, 3.0, 0.75),
			stone,
			true
		)

	for z in [-2.5, 1.0, 4.0]:
		var light := OmniLight3D.new()
		light.position = (
			CROW_DUNGEON_ORIGIN
			+ Vector3(0, 2.4, z)
		)
		light.light_color = Color("7957ff")
		light.light_energy = 2.0
		light.omni_range = 7.0
		add_child(light)

	var altar := _make_box(
		CROW_DUNGEON_ORIGIN + Vector3(
			0,
			0.45,
			-5.8
		),
		Vector3(3.2, 0.9, 1.8),
		stone,
		true
	)
	var rune_mark := MeshInstance3D.new()
	var rune_mesh := BoxMesh.new()
	rune_mesh.size = Vector3(1.8, 0.08, 0.55)
	rune_mark.mesh = rune_mesh
	rune_mark.position = Vector3(0, 0.52, 0)
	rune_mark.material_override = rune
	altar.add_child(rune_mark)
