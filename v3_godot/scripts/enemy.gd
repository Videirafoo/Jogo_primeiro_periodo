extends CharacterBody3D

const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")
const SWORD := preload("res://assets/weapons/LongSword.obj")

@export var display_name := "VALDRAK RAIDER"
@export var max_health := 100
@export var move_speed := 2.7
@export var attack_range := 1.75
@export var attack_cooldown := 1.15
@export var attack_damage := 16
@export var aggro_range := 14.0
@export var model_scale := 1.22
@export var archetype := 0
@export var boss := false

var health := 100
var home_position := Vector3.ZERO
var attack_cd := 0.0
var swing_time := 0.0
var knockback := Vector3.ZERO
var player: Node3D
var anim_player: AnimationPlayer
var weapon_pivot: Node3D
var status_label: Label3D
var marker: MeshInstance3D
func _ready() -> void:
	add_to_group("enemies")
	if boss:
		add_to_group("bosses")
	health = max_health
	home_position = global_position
	player = get_tree().get_first_node_in_group("player") as Node3D
	_build_collision()
	_build_raider()
	_build_marker()
	_update_status()

func _physics_process(delta: float) -> void:
	attack_cd = maxf(0.0, attack_cd - delta)
	swing_time = maxf(0.0, swing_time - delta)
	knockback = knockback.move_toward(
		Vector3.ZERO,
		18.0 * delta
	)

	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group("player") as Node3D
		return

	var offset := player.global_position - global_position
	var planar := Vector3(offset.x, 0.0, offset.z)
	var distance := planar.length()

	if distance > aggro_range:
		_return_home()
		return

	if distance > 0.05:
		look_at(global_position + planar, Vector3.UP)

	var movement := Vector3.ZERO
	if distance > attack_range:
		movement = planar.normalized() * move_speed
		if swing_time <= 0.0:
			_play_loop("CharacterArmature|Walk")
	elif attack_cd <= 0.0:
		_attack_player()
	elif swing_time <= 0.0:
		_play_loop("CharacterArmature|Idle")

	_apply_movement(movement)

func _attack_player() -> void:
	attack_cd = attack_cooldown
	swing_time = 0.46 if boss else 0.40
	if anim_player:
		anim_player.play(
			"CharacterArmature|Punch",
			0.05,
			0.88 if boss else 1.08
		)
	if weapon_pivot:
		weapon_pivot.rotation_degrees = Vector3(0, 90, -92)
		var tween := create_tween()
		tween.tween_property(
			weapon_pivot,
			"rotation_degrees",
			Vector3(-8, 32, -48),
			0.16 if boss else 0.13
		)
		tween.tween_property(
			weapon_pivot,
			"rotation_degrees",
			Vector3(0, 90, -92),
			0.22
		)

	await get_tree().create_timer(
		0.18 if boss else 0.13
	).timeout
	if player and player.has_method("take_hit"):
		if global_position.distance_to(player.global_position) <= attack_range + 0.45:
			player.take_hit(attack_damage)

func take_hit(amount: int, direction: Vector3) -> void:
	health = maxi(0, health - amount)
	knockback += direction * (3.6 if boss else 5.2)
	_spawn_hit_vfx(direction)
	_hit_pulse()
	_update_status()
	if anim_player and health > 0:
		anim_player.play(
			"CharacterArmature|RecieveHit",
			0.03,
			0.88 if boss else 1.1
		)
	if health <= 0:
		_die()

func _die() -> void:
	if anim_player:
		anim_player.play("CharacterArmature|Defeat", 0.08, 1.0)
	set_physics_process(false)
	collision_layer = 0
	collision_mask = 0
	var tween := create_tween()
	tween.tween_interval(0.85)
	tween.tween_property(self, "scale", Vector3.ZERO, 0.35)
	tween.tween_callback(queue_free)

func _build_collision() -> void:
	var shape := CapsuleShape3D.new()
	shape.radius = 0.52 if boss else 0.40
	shape.height = 2.15 if boss else 1.75
	$CollisionShape3D.shape = shape
	$CollisionShape3D.position.y = 1.05 if boss else 0.88
func _build_raider() -> void:
	var model := VIKING.instantiate()
	model.name = "EnemyModel"
	model.scale = Vector3.ONE * model_scale
	model.rotation.y = PI
	add_child(model)

	anim_player = model.find_child(
		"AnimationPlayer",
		true,
		false
	) as AnimationPlayer

	if anim_player:
		for anim_name in [
			"CharacterArmature|Idle",
			"CharacterArmature|Walk"
		]:
			var anim := anim_player.get_animation(anim_name)
			if anim:
				anim.loop_mode = Animation.LOOP_LINEAR
		_play_loop("CharacterArmature|Idle")

	_apply_character_proportions(model)
	_apply_archetype_overlay(model)
	_attach_weapon(model)
func _attach_weapon(model: Node3D) -> void:
	var skeleton := model.find_child(
		"Skeleton3D",
		true,
		false
	) as Skeleton3D
	if not skeleton:
		return

	var attachment := BoneAttachment3D.new()
	attachment.name = "RightHandWeapon"
	attachment.bone_name = "Fist.R"
	skeleton.add_child(attachment)

	weapon_pivot = Node3D.new()
	var inherited_scale := attachment.global_basis.get_scale().x
	inherited_scale = maxf(inherited_scale, 0.001)
	weapon_pivot.scale = Vector3.ONE / inherited_scale
	weapon_pivot.position = Vector3(0.0, -0.03, 0.02) / inherited_scale
	weapon_pivot.rotation_degrees = Vector3(0, 90, -92)
	attachment.add_child(weapon_pivot)

	var sword := MeshInstance3D.new()
	sword.mesh = SWORD
	sword.scale = Vector3.ONE * (0.29 if boss else 0.23)
	sword.position = Vector3(0, -0.18, 0)
	weapon_pivot.add_child(sword)
func _apply_archetype_overlay(model: Node3D) -> void:
	var color := _archetype_color()
	var overlay := StandardMaterial3D.new()
	overlay.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	overlay.albedo_color = Color(color.r, color.g, color.b, 0.16)
	overlay.emission_enabled = true
	overlay.emission = color.darkened(0.62)
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := node as MeshInstance3D
		mesh_instance.material_overlay = overlay

func _build_marker() -> void:
	marker = MeshInstance3D.new()
	var ring := TorusMesh.new()
	ring.inner_radius = 0.76 if boss else 0.48
	ring.outer_radius = 1.02 if boss else 0.68
	ring.rings = 16
	ring.ring_segments = 8
	marker.mesh = ring
	marker.position.y = 0.035

	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = _archetype_color()
	mat.emission_enabled = true
	mat.emission = _archetype_color()
	marker.material_override = mat
	add_child(marker)

	status_label = Label3D.new()
	status_label.position = Vector3(
		0,
		3.05 if boss else 2.38,
		0
	)
	status_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	status_label.font_size = 30 if boss else 24
	status_label.outline_size = 8
	status_label.modulate = _archetype_color().lightened(0.18)
	add_child(status_label)

func _update_status() -> void:
	if not status_label:
		return
	status_label.text = "%s  %d/%d" % [
		display_name,
		health,
		max_health
	]

func _archetype_color() -> Color:
	if boss:
		return Color("d86cff")
	if archetype == 1:
		return Color("ff9f43")
	return Color("ff5d67")
func _hit_pulse() -> void:
	if not marker:
		return
	var base := Vector3.ONE
	marker.scale = base * 1.35
	var tween := create_tween()
	tween.tween_property(marker, "scale", base, 0.16)

func _play_loop(animation_name: String) -> void:
	if not anim_player:
		return
	if anim_player.current_animation == animation_name:
		return
	anim_player.play(animation_name, 0.12)

func _spawn_hit_vfx(direction: Vector3) -> void:
	var particles := GPUParticles3D.new()
	particles.amount = 18 if boss else 14
	particles.lifetime = 0.42
	particles.one_shot = true
	particles.explosiveness = 0.95

	var process := ParticleProcessMaterial.new()
	process.direction = Vector3(
		direction.x,
		0.85,
		direction.z
	).normalized()
	process.spread = 62.0
	process.initial_velocity_min = 2.4
	process.initial_velocity_max = 5.6
	process.gravity = Vector3(0, -7.5, 0)
	process.color = _archetype_color().lightened(0.16)
	particles.process_material = process

	var quad := QuadMesh.new()
	quad.size = Vector2(0.065, 0.065)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color("e5fcff")
	material.emission_enabled = true
	material.emission = _archetype_color()
	quad.material = material
	particles.draw_pass_1 = quad

	get_parent().add_child(particles)
	particles.global_position = global_position + Vector3.UP * 1.0
	particles.finished.connect(particles.queue_free)
	particles.emitting = true

	var flash := OmniLight3D.new()
	flash.light_color = _archetype_color()
	flash.light_energy = 3.2
	flash.omni_range = 3.2
	get_parent().add_child(flash)
	flash.global_position = particles.global_position
	var fade := get_tree().create_tween()
	fade.tween_property(flash, "light_energy", 0.0, 0.14)
	fade.tween_callback(flash.queue_free)

func _return_home() -> void:
	var home_offset := home_position - global_position
	home_offset.y = 0.0
	var movement := Vector3.ZERO

	if home_offset.length() > 0.55:
		look_at(
			global_position + home_offset.normalized(),
			Vector3.UP
		)
		movement = home_offset.normalized() * move_speed * 0.72
		if swing_time <= 0.0:
			_play_loop("CharacterArmature|Walk")
	elif swing_time <= 0.0:
		_play_loop("CharacterArmature|Idle")

	_apply_movement(movement)

func _apply_movement(movement: Vector3) -> void:
	velocity.x = movement.x + knockback.x
	velocity.z = movement.z + knockback.z
	velocity.y = -1.0
	move_and_slide()

func _apply_character_proportions(model: Node3D) -> void:
	var rig := model.find_child(
		"Skeleton3D",
		true,
		false
	) as Skeleton3D
	if not rig:
		return

	var head := rig.find_bone("Head")
	if head >= 0:
		var head_scale := 0.54 if boss else 0.58
		rig.set_bone_pose_scale(
			head,
			Vector3.ONE * head_scale
		)

	var neck := rig.find_bone("Neck")
	if neck >= 0:
		rig.set_bone_pose_scale(
			neck,
			Vector3(0.93, 1.02, 0.93)
		)
