extends Node3D

const HOUSE := preload("res://assets/environment/village/House_1.obj")
const BLACKSMITH := preload("res://assets/environment/village/Blacksmith.obj")
const BONFIRE := preload("res://assets/environment/village/Bonfire_Lit.obj")
const FENCE := preload("res://assets/environment/village/Fence.obj")

func _ready() -> void:
    _environment()
    _ground()
    _authored_village()
    _forest_edge()
    _landmark()

func _environment() -> void:
    var env := Environment.new()
    env.background_mode = Environment.BG_SKY
    var sky := Sky.new()
    var sky_mat := ProceduralSkyMaterial.new()
    sky_mat.sky_top_color = Color("07131c")
    sky_mat.sky_horizon_color = Color("5c6f73")
    sky_mat.ground_bottom_color = Color("070b0d")
    sky_mat.ground_horizon_color = Color("33413f")
    sky.sky_material = sky_mat
    env.sky = sky

    env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
    env.ambient_light_energy = 0.58
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    env.glow_enabled = true
    env.fog_enabled = true
    env.fog_light_color = Color("718081")
    env.fog_light_energy = 0.65
    env.fog_density = 0.012
    env.fog_height = 0.0
    env.fog_height_density = 0.08
    env.adjustment_enabled = true
    env.adjustment_brightness = 1.02
    env.adjustment_contrast = 1.08
    env.adjustment_saturation = 0.92
    $WorldEnvironment.environment = env

func _ground() -> void:
    var ground := StaticBody3D.new()
    ground.name = "Ground"
    var mesh := MeshInstance3D.new()
    var plane := BoxMesh.new()
    plane.size = Vector3(80, 0.35, 80)
    mesh.mesh = plane
    mesh.position.y = -0.18
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color("263832")
    mat.roughness = 0.96
    mesh.material_override = mat
    ground.add_child(mesh)

    var shape := CollisionShape3D.new()
    var box := BoxShape3D.new()
    box.size = Vector3(80, 0.35, 80)
    shape.shape = box
    shape.position.y = -0.18
    ground.add_child(shape)
    add_child(ground)

func _authored_village() -> void:
    _mesh(HOUSE, Vector3(-8, 0, -9), 0.30, 1.55)
    _mesh(HOUSE, Vector3(-13, 0, -2), -0.65, 1.35)
    _mesh(HOUSE, Vector3(11, 0, -3), 2.45, 1.45)
    _mesh(BLACKSMITH, Vector3(7.5, 0, -11), -0.25, 1.35)
    _mesh(BONFIRE, Vector3(0, 0, -5), 0.0, 2.4)
    for i in range(8):
        var x := -8.5 + float(i) * 2.4
        _mesh(FENCE, Vector3(x, 0, 4.8), 0.0, 1.2)
    _bonfire_light()
    _bonfire_particles()

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
    collision.shape = mesh.create_trimesh_shape()
    body.add_child(collision)
    add_child(body)

func _bonfire_light() -> void:
    var light := OmniLight3D.new()
    light.position = Vector3(0, 1.3, -5)
    light.light_color = Color("ff9c4a")
    light.light_energy = 3.8
    light.omni_range = 11.0
    light.shadow_enabled = true
    add_child(light)

func _forest_edge() -> void:
    for i in range(26):
        var angle := TAU * float(i) / 26.0
        var radius := 24.0 + float(i % 5) * 1.4
        _pine(Vector3(
            cos(angle) * radius,
            0,
            sin(angle) * radius
        ))

func _pine(pos: Vector3) -> void:
    var root := Node3D.new()
    root.position = pos
    var trunk := MeshInstance3D.new()
    var cylinder := CylinderMesh.new()
    cylinder.top_radius = 0.14
    cylinder.bottom_radius = 0.24
    cylinder.height = 2.8
    trunk.mesh = cylinder
    trunk.position.y = 1.4
    root.add_child(trunk)

    for tier in range(4):
        var leaves := MeshInstance3D.new()
        var cone := CylinderMesh.new()
        cone.top_radius = 0.0
        cone.bottom_radius = 1.35 - tier * 0.18
        cone.height = 2.0
        leaves.mesh = cone
        leaves.position.y = 2.4 + tier * 0.72
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color("183d34").lightened(tier * 0.025)
        mat.roughness = 0.92
        leaves.material_override = mat
        root.add_child(leaves)
    add_child(root)

func _landmark() -> void:
    var stone := StandardMaterial3D.new()
    stone.albedo_color = Color("48545a")
    stone.metallic = 0.08
    stone.roughness = 0.78
    for side in [-1.0, 1.0]:
        var pillar := MeshInstance3D.new()
        var mesh := BoxMesh.new()
        mesh.size = Vector3(1.5, 7.2, 1.5)
        pillar.mesh = mesh
        pillar.position = Vector3(side * 3.4, 3.6, -19.0)
        pillar.material_override = stone
        add_child(pillar)

    var lintel := MeshInstance3D.new()
    var lintel_mesh := BoxMesh.new()
    lintel_mesh.size = Vector3(8.3, 1.25, 1.7)
    lintel.mesh = lintel_mesh
    lintel.position = Vector3(0, 6.7, -19.0)
    lintel.material_override = stone
    add_child(lintel)

    var rune := OmniLight3D.new()
    rune.position = Vector3(0, 5.5, -18.2)
    rune.light_color = Color("67e8f9")
    rune.light_energy = 2.8
    rune.omni_range = 7.0
    add_child(rune)

func _bonfire_particles() -> void:
    var particles := GPUParticles3D.new()
    particles.position = Vector3(0, 0.65, -5)
    particles.amount = 28
    particles.lifetime = 1.2
    particles.randomness = 0.45

    var process := ParticleProcessMaterial.new()
    process.direction = Vector3(0, 1, 0)
    process.spread = 24.0
    process.initial_velocity_min = 0.7
    process.initial_velocity_max = 2.1
    process.gravity = Vector3(0, 0.55, 0)
    process.color = Color("ffb15c")
    particles.process_material = process

    var quad := QuadMesh.new()
    quad.size = Vector2(0.055, 0.055)
    var material := StandardMaterial3D.new()
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.albedo_color = Color("ffd7a0")
    material.emission_enabled = true
    material.emission = Color("ff7f2a")
    quad.material = material
    particles.draw_pass_1 = quad
    particles.emitting = true
    add_child(particles)
