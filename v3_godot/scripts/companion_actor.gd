extends CharacterBody3D

@export var companion_name := "Thorvald"
@export var model_key := 0
@export var accent := Color("e8c27a")
@export var follow_distance := 2.2
@export var combat_range := 6.5
@export var attack_damage := 18
@export var attack_cooldown := 1.15

const EIRIK := preload("res://assets/characters/npcs/Eirik.glb")
const ASTRID := preload("res://assets/characters/npcs/Astrid.glb")
const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")

var player: Node3D
var attack_timer := 0.0
var model_root: Node3D
var anim: AnimationPlayer

func _ready() -> void:
	add_to_group("companions")
	player = get_tree().get_first_node_in_group(
		"player"
	) as Node3D
	_build_model()

func _physics_process(delta: float) -> void:
	attack_timer = maxf(0.0, attack_timer - delta)
	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group(
			"player"
		) as Node3D
		return

	var enemy := _nearest_enemy()
	if is_instance_valid(enemy):
		var dist := global_position.distance_to(
			enemy.global_position
		)
		if dist <= 2.15:
			velocity.x = 0.0
			velocity.z = 0.0
			_face(enemy.global_position)
			_play("CharacterArmature|Punch")
			if attack_timer <= 0.0:
				attack_timer = attack_cooldown
				if enemy.has_method("take_hit"):
					var direction := (
						enemy.global_position
						- global_position
					).normalized()
					enemy.take_hit(
						attack_damage,
						direction
					)
		else:
			_move_toward(
				enemy.global_position,
				3.8,
				delta
			)
		return

	var offset := player.global_position - global_position
	offset.y = 0.0
	var distance := offset.length()
	if distance > 10.0:
		global_position = (
			player.global_position
			+ player.global_transform.basis.x * 1.6
			+ player.global_transform.basis.z * 1.9
		)
		return

	if distance > follow_distance:
		_move_toward(
			player.global_position
			- player.global_transform.basis.z * 1.7,
			4.1,
			delta
		)
	else:
		velocity.x = move_toward(
			velocity.x,
			0.0,
			12.0 * delta
		)
		velocity.z = move_toward(
			velocity.z,
			0.0,
			12.0 * delta
		)
		velocity.y = -1.0
		move_and_slide()
		_play("CharacterArmature|Idle")

func _move_toward(
	target: Vector3,
	speed: float,
	delta: float
) -> void:
	var offset := target - global_position
	offset.y = 0.0
	if offset.length_squared() <= 0.01:
		return
	var direction := offset.normalized()
	velocity.x = move_toward(
		velocity.x,
		direction.x * speed,
		14.0 * delta
	)
	velocity.z = move_toward(
		velocity.z,
		direction.z * speed,
		14.0 * delta
	)
	velocity.y = -1.0
	_face(global_position + direction)
	move_and_slide()
	_play("CharacterArmature|Walk")

func _face(target: Vector3) -> void:
	var flat := target
	flat.y = global_position.y
	if global_position.distance_squared_to(flat) > 0.01:
		look_at(flat, Vector3.UP)

func _nearest_enemy() -> Node3D:
	var best: Node3D = null
	var best_distance := combat_range
	for node in get_tree().get_nodes_in_group(
		"enemies"
	):
		if not node is Node3D:
			continue
		if int(node.health) <= 0:
			continue
		var distance := global_position.distance_to(
			node.global_position
		)
		if distance < best_distance:
			best = node
			best_distance = distance
	return best

func _build_model() -> void:
	var packed: PackedScene
	match model_key:
		1:
			packed = ASTRID
		2:
			packed = VIKING
		_:
			packed = EIRIK
	model_root = packed.instantiate()
	model_root.scale = Vector3.ONE * (
		0.49 if model_key == 2
		else (0.55 if model_key == 1 else 0.50)
	)
	model_root.rotation.y = PI
	add_child(model_root)
	_tint_model()

	anim = model_root.find_child(
		"AnimationPlayer",
		true,
		false
	) as AnimationPlayer
	if anim:
		for animation_name in [
			"CharacterArmature|Idle",
			"CharacterArmature|Walk"
		]:
			var animation := anim.get_animation(
				animation_name
			)
			if animation:
				animation.loop_mode = (
					Animation.LOOP_LINEAR
				)
		_play("CharacterArmature|Idle")

	var shape := CapsuleShape3D.new()
	shape.radius = 0.32
	shape.height = 1.75
	var collision := CollisionShape3D.new()
	collision.shape = shape
	collision.position.y = 0.88
	add_child(collision)

	var label := Label3D.new()
	label.text = companion_name.to_upper()
	label.position = Vector3(0, 2.0, 0)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 22
	label.outline_size = 7
	label.modulate = accent
	add_child(label)

func _tint_model() -> void:
	var overlay := StandardMaterial3D.new()
	overlay.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	overlay.albedo_color = Color(
		accent.r,
		accent.g,
		accent.b,
		0.10
	)
	overlay.emission_enabled = true
	overlay.emission = accent.darkened(0.78)
	for node in model_root.find_children(
		"*",
		"MeshInstance3D",
		true,
		false
	):
		(node as MeshInstance3D).material_overlay = overlay

func _play(name: String) -> void:
	if not anim:
		return
	if anim.has_animation(name):
		if anim.current_animation != name:
			anim.play(name, 0.12)
