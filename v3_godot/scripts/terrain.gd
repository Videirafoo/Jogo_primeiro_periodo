extends Node3D

const SIZE := 190.0
const SEGMENTS := 56
const UV_SCALE := 14.0
const HALF := SIZE * 0.5

var terrain_mesh: ArrayMesh
var ground_material: ShaderMaterial
var rock_material: StandardMaterial3D
var shrub_material: StandardMaterial3D
var water_material: StandardMaterial3D

func _ready() -> void:
	_build_materials()
	_build_terrain()
	_build_paths()
	_build_road_details()
	_build_rocks()
	_build_shrubs()
	_build_stream()
	_build_distant_mountains()
	_build_world_boundary()

func _build_materials() -> void:
	ground_material = _terrain_material()

	rock_material = StandardMaterial3D.new()
	rock_material.albedo_color = Color("3d4749")
	rock_material.roughness = 0.90
	rock_material.metallic = 0.025

	shrub_material = StandardMaterial3D.new()
	shrub_material.albedo_color = Color("254837")
	shrub_material.roughness = 0.96

	water_material = StandardMaterial3D.new()
	water_material.albedo_color = Color(0.08, 0.20, 0.24, 0.78)
	water_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water_material.metallic = 0.08
	water_material.roughness = 0.18

func _height_at(x: float, z: float) -> float:
	var radius := Vector2(x, z).length()
	if radius < 27.0:
		return 0.0

	var blend := smoothstep(27.0, 72.0, radius)
	var hills := (
		sin(x * 0.105) * 1.45
		+ cos(z * 0.092) * 1.15
		+ sin((x + z) * 0.047) * 0.85
		+ cos((x - z) * 0.071) * 0.55
	)
	var edge_rise := smoothstep(72.0, 94.0, radius) * 8.5
	var height := hills * blend + edge_rise

	var road_x := 1.0 - smoothstep(4.2, 10.5, absf(x))
	var road_z_start := smoothstep(-8.0, 4.0, z)
	var road_z_end := 1.0 - smoothstep(65.0, 79.0, z)
	var road_flat := road_x * road_z_start * road_z_end
	height *= 1.0 - road_flat * 0.88

	return height

func _normal_at(x: float, z: float) -> Vector3:
	var e := 0.34
	var dx := _height_at(x + e, z) - _height_at(x - e, z)
	var dz := _height_at(x, z + e) - _height_at(x, z - e)
	return Vector3(-dx, e * 2.0, -dz).normalized()
func _build_terrain() -> void:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	var row := SEGMENTS + 1

	for z_i in range(row):
		var z := -HALF + SIZE * float(z_i) / float(SEGMENTS)
		for x_i in range(row):
			var x := -HALF + SIZE * float(x_i) / float(SEGMENTS)
			var y := _height_at(x, z)
			vertices.append(Vector3(x, y, z))
			normals.append(_normal_at(x, z))
			uvs.append(
				Vector2(
					float(x_i) / float(SEGMENTS),
					float(z_i) / float(SEGMENTS)
				) * UV_SCALE
			)

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
	mesh_instance.material_override = ground_material
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

float hash21(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	float n1 = sin(world_pos.x * 0.22) * cos(world_pos.z * 0.19);
	float n2 = sin((world_pos.x + world_pos.z) * 0.075);
	float cell = hash21(floor(world_pos.xz * 0.42));
	float noise = n1 * 0.36 + n2 * 0.34 + (cell - 0.5) * 0.30;
	float slope = clamp(1.0 - world_normal.y, 0.0, 1.0);
	float altitude = smoothstep(2.0, 9.0, world_pos.y);

	vec3 moss = vec3(0.055, 0.125, 0.095);
	vec3 grass = vec3(0.105, 0.235, 0.145);
	vec3 wet_grass = vec3(0.075, 0.170, 0.125);
	vec3 earth = vec3(0.205, 0.150, 0.095);
	vec3 stone = vec3(0.245, 0.285, 0.295);

	vec3 ground = mix(wet_grass, grass, smoothstep(-0.45, 0.45, noise));
	ground = mix(ground, moss, smoothstep(0.36, 0.92, -noise));
	ground = mix(ground, earth, smoothstep(0.48, 0.92, noise));
	ground = mix(ground, stone, smoothstep(0.18, 0.56, slope));
	ground = mix(ground, stone * 0.88, altitude * 0.55);

	ALBEDO = ground;
	ROUGHNESS = 0.94;
	METALLIC = 0.015;
	SPECULAR = 0.22;
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	return material
func _build_paths() -> void:
	var road := StandardMaterial3D.new()
	road.albedo_color = Color("47382a")
	road.roughness = 0.98

	_make_path(
		Vector3(0, 0.055, 20.0),
		Vector3(4.8, 0.075, 88.0),
		0.0,
		road
	)
	_make_path(
		Vector3(0, 0.058, -5.5),
		Vector3(34.0, 0.075, 3.3),
		0.0,
		road
	)
	_make_path(
		Vector3(-8.0, 0.06, 5.5),
		Vector3(18.0, 0.075, 2.7),
		deg_to_rad(-18.0),
		road
	)
	_make_path(
		Vector3(9.0, 0.06, 7.0),
		Vector3(20.0, 0.075, 2.7),
		deg_to_rad(20.0),
		road
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

func _build_road_details() -> void:
	var pebble_mat := StandardMaterial3D.new()
	pebble_mat.albedo_color = Color("58534a")
	pebble_mat.roughness = 0.92

	for i in range(32):
		var side := -1.0 if i % 2 == 0 else 1.0
		var z := 62.0 - float(i) * 1.2
		var x := side * (2.8 + float((i * 7) % 9) * 0.18)
		if z < -22.0:
			break
		var pebble := MeshInstance3D.new()
		var mesh := SphereMesh.new()
		mesh.radius = 0.12 + float(i % 4) * 0.025
		mesh.height = 0.12
		mesh.radial_segments = 7
		mesh.rings = 3
		pebble.mesh = mesh
		pebble.position = Vector3(x, 0.10, z)
		pebble.scale = Vector3(1.25, 0.42, 0.9)
		pebble.material_override = pebble_mat
		add_child(pebble)
func _build_rocks() -> void:
	for i in range(42):
		var angle := TAU * float(i) / 42.0 + float(i % 7) * 0.17
		var radius := 30.0 + float((i * 13) % 52)
		if i % 9 == 0:
			radius *= 0.72
		var x := cos(angle) * radius
		var z := sin(angle) * radius
		if absf(x) < 7.0 and z > -30.0 and z < 70.0:
			continue
		var y := _height_at(x, z)

		var root := StaticBody3D.new()
		root.position = Vector3(x, y + 0.28, z)
		root.rotation = Vector3(
			0.0,
			angle * 0.73,
			0.10 * sin(float(i))
		)
		var scale_value := 0.45 + float(i % 7) * 0.16
		root.scale = Vector3(
			scale_value * 1.18,
			scale_value * (0.62 + float(i % 3) * 0.12),
			scale_value
		)

		var rock := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = 0.72
		sphere.height = 1.15
		sphere.radial_segments = 9
		sphere.rings = 5
		rock.mesh = sphere
		rock.material_override = rock_material
		root.add_child(rock)

		if i % 3 == 0:
			var collision := CollisionShape3D.new()
			var shape := SphereShape3D.new()
			shape.radius = 0.62
			collision.shape = shape
			root.add_child(collision)

		add_child(root)

func _build_shrubs() -> void:
	var mesh := SphereMesh.new()
	mesh.radius = 0.48
	mesh.height = 0.62
	mesh.radial_segments = 7
	mesh.rings = 4

	var multi := MultiMesh.new()
	multi.transform_format = MultiMesh.TRANSFORM_3D
	multi.instance_count = 72
	multi.mesh = mesh

	var written := 0
	for i in range(170):
		if written >= multi.instance_count:
			break
		var angle := float(i) * 2.399963
		var radius := 23.0 + float((i * 17) % 67)
		var x := cos(angle) * radius
		var z := sin(angle) * radius
		if absf(x) < 9.0 and z > -32.0 and z < 74.0:
			continue
		if Vector2(x, z).length() > 91.0:
			continue
		var y := _height_at(x, z)
		var scale_value := 0.45 + float(i % 5) * 0.10
		var basis := Basis()
		basis = basis.scaled(
			Vector3(
				scale_value,
				scale_value * 0.72,
				scale_value
			)
		)
		var transform := Transform3D(
			basis,
			Vector3(x, y + 0.22, z)
		)
		multi.set_instance_transform(written, transform)
		written += 1

	if written < multi.instance_count:
		multi.instance_count = written

	var instance := MultiMeshInstance3D.new()
	instance.name = "ValdrakShrubs"
	instance.multimesh = multi
	instance.material_override = shrub_material
	add_child(instance)
func _build_stream() -> void:
	for i in range(9):
		var z := -58.0 + float(i) * 8.0
		var x := -42.0 + sin(float(i) * 0.58) * 4.2
		var y := _height_at(x, z) + 0.035
		var water := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = Vector3(7.0, 0.045, 8.4)
		water.mesh = mesh
		water.position = Vector3(x, y, z)
		water.rotation.y = sin(float(i) * 0.43) * 0.08
		water.material_override = water_material
		add_child(water)

func _build_distant_mountains() -> void:
	var mountain_material := StandardMaterial3D.new()
	mountain_material.albedo_color = Color("253337")
	mountain_material.roughness = 1.0

	for i in range(14):
		var angle := TAU * float(i) / 14.0
		var radius := 103.0 + float(i % 4) * 4.5
		var height := 24.0 + float((i * 7) % 14)
		var width := 9.0 + float(i % 5) * 2.2

		var mountain := MeshInstance3D.new()
		var cone := CylinderMesh.new()
		cone.top_radius = 0.0
		cone.bottom_radius = width
		cone.height = height
		cone.radial_segments = 7
		mountain.mesh = cone
		mountain.position = Vector3(
			cos(angle) * radius,
			height * 0.5 - 2.0,
			sin(angle) * radius
		)
		mountain.rotation.y = angle
		mountain.material_override = mountain_material
		add_child(mountain)

func _build_world_boundary() -> void:
	var body := StaticBody3D.new()
	body.name = "WorldBoundary"
	add_child(body)

	var thickness := 2.0
	var wall_height := 22.0
	var length := SIZE + 12.0

	for entry in [
		[Vector3(HALF, wall_height * 0.5, 0), Vector3(thickness, wall_height, length)],
		[Vector3(-HALF, wall_height * 0.5, 0), Vector3(thickness, wall_height, length)],
		[Vector3(0, wall_height * 0.5, HALF), Vector3(length, wall_height, thickness)],
		[Vector3(0, wall_height * 0.5, -HALF), Vector3(length, wall_height, thickness)]
	]:
		var collision := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = entry[1]
		collision.shape = shape
		collision.position = entry[0]
		body.add_child(collision)
