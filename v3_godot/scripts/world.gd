extends Node3D

const HOUSE := preload("res://assets/environment/village/House_1.obj")
const BLACKSMITH := preload("res://assets/environment/village/Blacksmith.obj")
const BONFIRE := preload("res://assets/environment/village/Bonfire_Lit.obj")
const FENCE := preload("res://assets/environment/village/Fence.obj")

var wood_material: StandardMaterial3D
var leaf_material: StandardMaterial3D
var trunk_material: StandardMaterial3D
var stone_material: StandardMaterial3D

func _ready() -> void:
	_build_shared_materials()
	_environment()
	_lighting()
	_authored_village()
	_village_props()
	_forest_edge()
	_landmark()
	_boss_arena()

func _build_shared_materials() -> void:
	leaf_material = StandardMaterial3D.new()
	leaf_material.albedo_color = Color("173d34")
	leaf_material.roughness = 0.92

	trunk_material = StandardMaterial3D.new()
	trunk_material.albedo_color = Color("493525")
	trunk_material.roughness = 0.94

	stone_material = StandardMaterial3D.new()
	stone_material.albedo_color = Color("444d52")
	stone_material.metallic = 0.04
	stone_material.roughness = 0.84

	wood_material = StandardMaterial3D.new()
	wood_material.albedo_color = Color("4a3327")
	wood_material.roughness = 0.88

func _environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("06111a")
	sky_mat.sky_horizon_color = Color("617476")
	sky_mat.ground_bottom_color = Color("060a0c")
	sky_mat.ground_horizon_color = Color("2f403d")
	sky_mat.sun_angle_max = 12.0
	sky_mat.sun_curve = 0.12
	sky.sky_material = sky_mat
	env.sky = sky

	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.54
	env.ambient_light_sky_contribution = 0.88
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.fog_enabled = true
	env.fog_light_color = Color("6f8585")
	env.fog_light_energy = 0.58
	env.fog_density = 0.009
	env.fog_height = 0.6
	env.fog_height_density = 0.055
	env.adjustment_enabled = true
	env.adjustment_brightness = 1.03
	env.adjustment_contrast = 1.12
	env.adjustment_saturation = 0.88
	$WorldEnvironment.environment = env

func _lighting() -> void:
	$Sun.light_color = Color("ffe2b8")
	$Sun.light_energy = 1.52
	$Sun.shadow_enabled = true
	$Sun.directional_shadow_max_distance = 68.0

	var rim := DirectionalLight3D.new()
	rim.name = "ColdRim"
	rim.rotation_degrees = Vector3(-28, 138, 0)
	rim.light_color = Color("76b9cb")
	rim.light_energy = 0.34
	rim.shadow_enabled = false
	add_child(rim)

func _authored_village() -> void:
	_mesh(HOUSE, Vector3(-11.5, 0, -11.5), 0.38, 1.55)
	_mesh(HOUSE, Vector3(11.5, 0, -11.0), -0.42, 1.48)
	_mesh(HOUSE, Vector3(-13.2, 0, 3.5), 1.08, 1.38)
	_mesh(BLACKSMITH, Vector3(12.5, 0, 4.5), -0.82, 1.35)
	_mesh(BONFIRE, Vector3(0, 0.02, -6.0), 0.0, 2.55)

	for i in range(6):
		var x := -8.0 + float(i) * 3.2
		_mesh(FENCE, Vector3(x, 0, 8.8), 0.0, 1.25)

	for i in range(4):
		_mesh(
			FENCE,
			Vector3(-17.0, 0, -7.0 + float(i) * 3.0),
			PI * 0.5,
			1.2
		)

	_bonfire_light()
	_bonfire_particles()
	_banner_posts()

func _mesh(
	mesh: Mesh,
	pos: Vector3,
	yaw: float,
	scale_value: float
) -> void:
	var body := StaticBody3D.new()
	body.position = pos
	body.rotation.y = yaw
	body.scale = Vector3.ONE * scale_value
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	body.add_child(instance)

	var collision := CollisionShape3D.new()
	var shape := mesh.create_trimesh_shape()
	if shape is ConcavePolygonShape3D:
		shape.backface_collision = true
	collision.shape = shape
	body.add_child(collision)
	add_child(body)

func _bonfire_light() -> void:
	var light := OmniLight3D.new()
	light.position = Vector3(0, 1.4, -6.0)
	light.light_color = Color("ff9a45")
	light.light_energy = 4.2
	light.omni_range = 12.0
	light.shadow_enabled = true
	add_child(light)

func _bonfire_particles() -> void:
	var particles := GPUParticles3D.new()
	particles.position = Vector3(0, 0.72, -6.0)
	particles.amount = 32
	particles.lifetime = 1.25
	particles.randomness = 0.46

	var process := ParticleProcessMaterial.new()
	process.direction = Vector3(0, 1, 0)
	process.spread = 24.0
	process.initial_velocity_min = 0.8
	process.initial_velocity_max = 2.25
	process.gravity = Vector3(0, 0.65, 0)
	process.color = Color("ffad55")
	particles.process_material = process

	var quad := QuadMesh.new()
	quad.size = Vector2(0.06, 0.06)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color("ffe1b2")
	material.emission_enabled = true
	material.emission = Color("ff7a25")
	quad.material = material
	particles.draw_pass_1 = quad
	particles.emitting = true
	add_child(particles)

func _forest_edge() -> void:
	for i in range(42):
		var angle := TAU * float(i) / 42.0
		var radius := 25.0 + float((i * 5) % 8) * 1.15
		var pos := Vector3(
			cos(angle) * radius,
			0,
			sin(angle) * radius
		)
		if pos.z < -28.0 and absf(pos.x) < 11.0:
			continue
		_pine(pos, 0.85 + float(i % 5) * 0.08)

func _pine(pos: Vector3, size: float) -> void:
	var root := StaticBody3D.new()
	root.position = pos
	root.scale = Vector3.ONE * size

	var trunk := MeshInstance3D.new()
	var cylinder := CylinderMesh.new()
	cylinder.top_radius = 0.13
	cylinder.bottom_radius = 0.23
	cylinder.height = 3.1
	trunk.mesh = cylinder
	trunk.position.y = 1.55
	trunk.material_override = trunk_material
	root.add_child(trunk)

	var trunk_collision := CollisionShape3D.new()
	var trunk_shape := CylinderShape3D.new()
	trunk_shape.radius = 0.28
	trunk_shape.height = 3.0
	trunk_collision.shape = trunk_shape
	trunk_collision.position.y = 1.5
	root.add_child(trunk_collision)

	for tier in range(4):
		var leaves := MeshInstance3D.new()
		var cone := CylinderMesh.new()
		cone.top_radius = 0.0
		cone.bottom_radius = 1.45 - tier * 0.19
		cone.height = 2.15
		leaves.mesh = cone
		leaves.position.y = 2.65 + tier * 0.76
		leaves.material_override = leaf_material
		root.add_child(leaves)
	add_child(root)

func _banner_posts() -> void:
	for x in [-3.2, 3.2]:
		var post := StaticBody3D.new()
		post.position = Vector3(x, 0, -15.5)

		var mesh_instance := MeshInstance3D.new()
		var mesh := CylinderMesh.new()
		mesh.top_radius = 0.10
		mesh.bottom_radius = 0.13
		mesh.height = 3.2
		mesh_instance.mesh = mesh
		mesh_instance.position.y = 1.6
		mesh_instance.material_override = wood_material
		post.add_child(mesh_instance)

		var collision := CollisionShape3D.new()
		var shape := CylinderShape3D.new()
		shape.radius = 0.14
		shape.height = 3.2
		collision.shape = shape
		collision.position.y = 1.6
		post.add_child(collision)
		add_child(post)
func _landmark() -> void:
	for side in [-1.0, 1.0]:
		var pillar := StaticBody3D.new()
		pillar.position = Vector3(side * 3.7, 3.4, -22.5)

		var mesh_instance := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = Vector3(1.4, 6.8, 1.4)
		mesh_instance.mesh = mesh
		mesh_instance.material_override = stone_material
		pillar.add_child(mesh_instance)

		var collision := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = mesh.size
		collision.shape = shape
		pillar.add_child(collision)
		add_child(pillar)

	var lintel := StaticBody3D.new()
	lintel.position = Vector3(0, 6.35, -22.5)
	var lintel_mesh_instance := MeshInstance3D.new()
	var lintel_mesh := BoxMesh.new()
	lintel_mesh.size = Vector3(8.8, 1.2, 1.55)
	lintel_mesh_instance.mesh = lintel_mesh
	lintel_mesh_instance.material_override = stone_material
	lintel.add_child(lintel_mesh_instance)
	var lintel_collision := CollisionShape3D.new()
	var lintel_shape := BoxShape3D.new()
	lintel_shape.size = lintel_mesh.size
	lintel_collision.shape = lintel_shape
	lintel.add_child(lintel_collision)
	add_child(lintel)

	var rune := OmniLight3D.new()
	rune.position = Vector3(0, 5.45, -21.7)
	rune.light_color = Color("67e8f9")
	rune.light_energy = 3.4
	rune.omni_range = 8.0
	add_child(rune)

func _boss_arena() -> void:
	var arena := StaticBody3D.new()
	arena.name = "BossArena"
	arena.position = Vector3(0, -0.06, -34.0)

	var floor_mesh := MeshInstance3D.new()
	var cylinder := CylinderMesh.new()
	cylinder.top_radius = 9.0
	cylinder.bottom_radius = 9.4
	cylinder.height = 0.32
	floor_mesh.mesh = cylinder
	floor_mesh.material_override = stone_material
	arena.add_child(floor_mesh)

	var floor_collision := CollisionShape3D.new()
	var floor_shape := CylinderShape3D.new()
	floor_shape.radius = 9.0
	floor_shape.height = 0.32
	floor_collision.shape = floor_shape
	arena.add_child(floor_collision)
	add_child(arena)

	for i in range(10):
		var angle := TAU * float(i) / 10.0
		var rock := StaticBody3D.new()
		rock.position = Vector3(
			cos(angle) * 8.2,
			1.4,
			-34.0 + sin(angle) * 8.2
		)
		rock.rotation.y = -angle

		var mesh_instance := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = Vector3(0.85, 2.8, 0.9)
		mesh_instance.mesh = mesh
		mesh_instance.material_override = stone_material
		rock.add_child(mesh_instance)

		var collision := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = mesh.size
		collision.shape = shape
		rock.add_child(collision)
		add_child(rock)

func _village_props() -> void:
	var crate_positions := [
		Vector3(-8.4, 0.45, -6.5),
		Vector3(-7.4, 0.45, -6.8),
		Vector3(8.2, 0.45, -7.4),
		Vector3(9.1, 0.45, -7.0),
		Vector3(-10.0, 0.45, 5.8),
		Vector3(10.8, 0.45, 6.2),
		Vector3(-5.8, 0.45, 9.8),
		Vector3(6.0, 0.45, 10.0)
	]
	for pos in crate_positions:
		_make_crate(pos)

	var torch_positions := [
		Vector3(-3.2, 0, -2.0),
		Vector3(3.2, 0, -2.0),
		Vector3(-4.8, 0, -12.8),
		Vector3(4.8, 0, -12.8),
		Vector3(-3.8, 0, -20.0),
		Vector3(3.8, 0, -20.0)
	]
	for pos in torch_positions:
		_make_torch(pos)

	var rune_positions := [
		Vector3(-14.5, 0, -15.0),
		Vector3(14.5, 0, -15.5),
		Vector3(-11.5, 0, -28.5),
		Vector3(11.5, 0, -28.5)
	]
	for pos in rune_positions:
		_make_rune_stone(pos)

func _make_crate(pos: Vector3) -> void:
	var body := StaticBody3D.new()
	body.position = pos
	body.rotation.y = pos.x * 0.08

	var mesh_instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.9, 0.9, 0.9)
	mesh_instance.mesh = mesh
	mesh_instance.material_override = wood_material
	body.add_child(mesh_instance)

	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = mesh.size
	collision.shape = shape
	body.add_child(collision)
	add_child(body)

func _make_torch(pos: Vector3) -> void:
	var root := Node3D.new()
	root.position = pos

	var pole := MeshInstance3D.new()
	var pole_mesh := CylinderMesh.new()
	pole_mesh.top_radius = 0.06
	pole_mesh.bottom_radius = 0.08
	pole_mesh.height = 1.7
	pole.mesh = pole_mesh
	pole.position.y = 0.85
	pole.material_override = wood_material
	root.add_child(pole)

	var flame := OmniLight3D.new()
	flame.position.y = 1.82
	flame.light_color = Color("ff9a45")
	flame.light_energy = 2.1
	flame.omni_range = 5.2
	flame.shadow_enabled = false
	root.add_child(flame)

	var glow := MeshInstance3D.new()
	var glow_mesh := SphereMesh.new()
	glow_mesh.radius = 0.11
	glow_mesh.height = 0.22
	glow.mesh = glow_mesh
	glow.position.y = 1.82
	var glow_mat := StandardMaterial3D.new()
	glow_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	glow_mat.albedo_color = Color("ffd08a")
	glow_mat.emission_enabled = true
	glow_mat.emission = Color("ff7a24")
	glow.material_override = glow_mat
	root.add_child(glow)
	add_child(root)

func _make_rune_stone(pos: Vector3) -> void:
	var root := StaticBody3D.new()
	root.position = pos
	root.rotation.y = pos.z * 0.03

	var stone := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.8, 2.2, 0.55)
	stone.mesh = mesh
	stone.position.y = 1.1
	stone.material_override = stone_material
	root.add_child(stone)

	var rune := MeshInstance3D.new()
	var rune_mesh := BoxMesh.new()
	rune_mesh.size = Vector3(0.08, 0.95, 0.62)
	rune.mesh = rune_mesh
	rune.position = Vector3(0, 1.18, -0.31)
	var rune_mat := StandardMaterial3D.new()
	rune_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rune_mat.albedo_color = Color("7fefff")
	rune_mat.emission_enabled = true
	rune_mat.emission = Color("38d9ff")
	rune.material_override = rune_mat
	root.add_child(rune)

	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = mesh.size
	collision.shape = shape
	collision.position.y = 1.1
	root.add_child(collision)
	add_child(root)
