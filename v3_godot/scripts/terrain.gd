extends Node3D

const SIZE := 92.0
const SEGMENTS := 48
const UV_SCALE := 8.0

var terrain_mesh: ArrayMesh

func _ready() -> void:
	_build_terrain()
	_build_paths()
	_build_rocks()

func _height_at(x: float, z: float) -> float:
	var radius := Vector2(x, z).length()
	if radius < 16.0:
		return 0.0

	var blend := smoothstep(16.0, 34.0, radius)
	var hills := (
		sin(x * 0.17) * 0.58
		+ cos(z * 0.15) * 0.48
		+ sin((x + z) * 0.085) * 0.36
	)
	return hills * blend

func _normal_at(x: float, z: float) -> Vector3:
	var e := 0.28
	var dx := _height_at(x + e, z) - _height_at(x - e, z)
	var dz := _height_at(x, z + e) - _height_at(x, z - e)
	return Vector3(-dx, e * 2.0, -dz).normalized()

func _build_terrain() -> void:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	var row := SEGMENTS + 1
	var half := SIZE * 0.5

	for z_i in range(row):
		var z := -half + SIZE * float(z_i) / float(SEGMENTS)
		for x_i in range(row):
			var x := -half + SIZE * float(x_i) / float(SEGMENTS)
			var y := _height_at(x, z)
			vertices.append(Vector3(x, y, z))
			normals.append(_normal_at(x, z))
			uvs.append(Vector2(
				float(x_i) / float(SEGMENTS),
				float(z_i) / float(SEGMENTS)
			) * UV_SCALE)

	for z_i in range(SEGMENTS):
		for x_i in range(SEGMENTS):
			var i := z_i * row + x_i
			indices.append_array([
				i,
				i + row,
				i + 1,
				i + 1,
				i + row,
				i + row + 1
			])

	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices

	terrain_mesh = ArrayMesh.new()
	terrain_mesh.add_surface_from_arrays(
		Mesh.PRIMITIVE_TRIANGLES,
		arrays
	)

	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = "ValdrakTerrain"
	mesh_instance.mesh = terrain_mesh
	mesh_instance.material_override = _terrain_material()
	add_child(mesh_instance)

	var body := StaticBody3D.new()
	body.name = "TerrainCollision"
	var collision := CollisionShape3D.new()
	var shape := terrain_mesh.create_trimesh_shape()
	if shape is ConcavePolygonShape3D:
		shape.backface_collision = true
	collision.shape = shape
	body.add_child(collision)
	add_child(body)
func _terrain_material() -> ShaderMaterial:
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
render_mode cull_back, depth_draw_opaque;

varying vec3 world_pos;
varying vec3 world_normal;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	float noise_a = sin(world_pos.x * 0.36) * cos(world_pos.z * 0.31);
	float noise_b = sin((world_pos.x + world_pos.z) * 0.14);
	float noise = noise_a * 0.5 + noise_b * 0.5;
	float slope = clamp(1.0 - world_normal.y, 0.0, 1.0);

	vec3 moss = vec3(0.105, 0.175, 0.145);
	vec3 grass = vec3(0.185, 0.285, 0.225);
	vec3 earth = vec3(0.255, 0.205, 0.145);
	vec3 stone = vec3(0.255, 0.285, 0.295);

	float dry_mix = smoothstep(0.1, 0.8, noise);
	vec3 ground = mix(moss, grass, dry_mix);
	ground = mix(ground, earth, smoothstep(0.42, 0.9, noise));
	ground = mix(ground, stone, smoothstep(0.14, 0.55, slope));

	ALBEDO = ground;
	ROUGHNESS = 0.92;
	METALLIC = 0.02;
	SPECULAR = 0.28;
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	return material
func _build_paths() -> void:
	var path_material := StandardMaterial3D.new()
	path_material.albedo_color = Color("38322d")
	path_material.roughness = 0.96

	_make_path(
		Vector3(0, 0.045, -11.0),
		Vector3(2.75, 0.07, 28.0),
		0.0,
		path_material
	)
	_make_path(
		Vector3(0, 0.05, -4.0),
		Vector3(24.0, 0.07, 2.15),
		0.0,
		path_material
	)

func _make_path(
	pos: Vector3,
	size: Vector3,
	yaw: float,
	material: Material
) -> void:
	var mesh_instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mesh_instance.mesh = mesh
	mesh_instance.position = pos
	mesh_instance.rotation.y = yaw
	mesh_instance.material_override = material
	add_child(mesh_instance)
func _build_rocks() -> void:
	var rock_material := StandardMaterial3D.new()
	rock_material.albedo_color = Color("434b4d")
	rock_material.roughness = 0.88
	rock_material.metallic = 0.035

	for i in range(30):
		var angle := TAU * float(i) / 30.0 + float(i % 4) * 0.11
		var radius := 19.0 + float((i * 7) % 13)
		var x := cos(angle) * radius
		var z := sin(angle) * radius
		var y := _height_at(x, z)

		var root := StaticBody3D.new()
		root.position = Vector3(x, y + 0.32, z)
		root.rotation = Vector3(
			0.0,
			angle * 0.63,
			0.12 * sin(float(i))
		)
		var scale_value := 0.55 + float(i % 5) * 0.13
		root.scale = Vector3(
			scale_value,
			scale_value * (0.75 + float(i % 3) * 0.1),
			scale_value * 1.15
		)
		var rock := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = 0.62
		sphere.height = 1.0
		sphere.radial_segments = 8
		sphere.rings = 4
		rock.mesh = sphere
		rock.material_override = rock_material
		root.add_child(rock)

		if i % 2 == 0:
			var collision := CollisionShape3D.new()
			var shape := SphereShape3D.new()
			shape.radius = 0.58
			collision.shape = shape
			root.add_child(collision)

		add_child(root)
