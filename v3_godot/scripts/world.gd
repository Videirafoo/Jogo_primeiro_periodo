extends Node3D

func _ready() -> void:
    _environment()
    _ground()
    _village()
    _landmark()

func _environment() -> void:
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("111a1d")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("8aa0a0")
    env.ambient_light_energy = 0.55
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    env.glow_enabled = true
    $WorldEnvironment.environment = env

func _ground() -> void:
    var ground := StaticBody3D.new()
    ground.name = "Ground"
    var mesh := MeshInstance3D.new()
    var plane := BoxMesh.new()
    plane.size = Vector3(70, 0.4, 70)
    mesh.mesh = plane
    mesh.position.y = -0.2
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color("263832")
    mat.roughness = 0.92
    mesh.material_override = mat
    ground.add_child(mesh)
    var shape := CollisionShape3D.new()
    var box := BoxShape3D.new()
    box.size = Vector3(70, 0.4, 70)
    shape.shape = box
    shape.position.y = -0.2
    ground.add_child(shape)
    add_child(ground)

func _village() -> void:
    for i in range(12):
        var angle := TAU * float(i) / 12.0
        var radius := 12.0 + float(i % 3) * 3.5
        var pos := Vector3(cos(angle) * radius, 0, sin(angle) * radius)
        _house(pos, angle)
    for i in range(24):
        var angle := TAU * float(i) / 24.0
        var radius := 21.0 + float(i % 4)
        _pine(Vector3(cos(angle) * radius, 0, sin(angle) * radius))

func _house(pos: Vector3, angle: float) -> void:
    var root := Node3D.new()
    root.position = pos
    root.rotation.y = -angle
    var wall := MeshInstance3D.new()
    var box := BoxMesh.new()
    box.size = Vector3(4.2, 2.6, 3.5)
    wall.mesh = box
    wall.position.y = 1.3
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color("59483a")
    mat.roughness = 0.88
    wall.material_override = mat
    root.add_child(wall)
    var roof := MeshInstance3D.new()
    var roof_mesh := PrismMesh.new()
    roof_mesh.size = Vector3(4.9, 1.6, 4.1)
    roof.mesh = roof_mesh
    roof.position.y = 3.2
    var roof_mat := StandardMaterial3D.new()
    roof_mat.albedo_color = Color("211f20")
    roof_mat.roughness = 0.95
    roof.material_override = roof_mat
    root.add_child(roof)
    add_child(root)

func _pine(pos: Vector3) -> void:
    var root := Node3D.new()
    root.position = pos
    var trunk := MeshInstance3D.new()
    var cylinder := CylinderMesh.new()
    cylinder.top_radius = 0.16
    cylinder.bottom_radius = 0.24
    cylinder.height = 2.3
    trunk.mesh = cylinder
    trunk.position.y = 1.15
    root.add_child(trunk)
    for tier in range(3):
        var leaves := MeshInstance3D.new()
        var cone := CylinderMesh.new()
        cone.top_radius = 0.0
        cone.bottom_radius = 1.25 - tier * 0.2
        cone.height = 2.1
        leaves.mesh = cone
        leaves.position.y = 2.2 + tier * 0.85
        var leaf_mat := StandardMaterial3D.new()
        leaf_mat.albedo_color = Color("173b32").lightened(tier * 0.04)
        leaf_mat.roughness = 0.9
        leaves.material_override = leaf_mat
        root.add_child(leaves)
    add_child(root)

func _landmark() -> void:
    for side in [-1.0, 1.0]:
        var pillar := MeshInstance3D.new()
        var mesh := BoxMesh.new()
        mesh.size = Vector3(1.3, 6.5, 1.3)
        pillar.mesh = mesh
        pillar.position = Vector3(side * 3.0, 3.25, -16.0)
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color("48545a")
        mat.metallic = 0.18
        mat.roughness = 0.72
        pillar.material_override = mat
        add_child(pillar)
    var lintel := MeshInstance3D.new()
    var lintel_mesh := BoxMesh.new()
    lintel_mesh.size = Vector3(7.3, 1.1, 1.5)
    lintel.mesh = lintel_mesh
    lintel.position = Vector3(0, 6.1, -16)
    add_child(lintel)
