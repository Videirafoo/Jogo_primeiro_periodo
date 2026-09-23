extends CharacterBody3D

const WALK_SPEED := 3.7
const RUN_SPEED := 6.4
const DODGE_SPEED := 10.5
const ACCEL := 22.0
const MODEL_ROTATE_SPEED := 12.0
const MOUSE_SENSITIVITY := 0.00235

const MAX_STAMINA := 100.0
const RUN_DRAIN := 17.0
const STAMINA_REGEN := 23.0
const DODGE_COST := 25.0
const HEAVY_COST := 34.0
const LOCK_RANGE := 15.0
const LIGHT_COSTS: Array[float] = [6.0, 7.0, 9.0]
const LIGHT_DAMAGE: Array[int] = [24, 30, 40]
const LIGHT_DURATION: Array[float] = [0.34, 0.39, 0.48]
const LIGHT_HIT_DELAY: Array[float] = [0.10, 0.12, 0.16]
const LIGHT_ANIM_RATE: Array[float] = [1.34, 1.16, 0.96]

const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")
const AXE := preload("res://assets/weapons/SimpleAxe.obj")

var health := 120
var stamina := MAX_STAMINA
var attack_time := 0.0
var dodge_time := 0.0
var invuln_time := 0.0
var combo_window := 0.0
var combo_step := 0
var stamina_regen_delay := 0.0
var facing := Vector3.FORWARD
var dodge_direction := Vector3.FORWARD
var lock_target: Node3D
var current_interactable: Node

var model_root: Node3D
var anim_player: AnimationPlayer
var animation_tree: AnimationTree
var weapon_pivot: Node3D
var skeleton: Skeleton3D
var camera_yaw := 0.0
var camera_pitch := deg_to_rad(-12.0)
var camera_manual_timer := 0.0
var motion_phase := 0.0

@onready var camera_rig: Node3D = $CameraRig
@onready var spring_arm: SpringArm3D = $CameraRig/SpringArm3D
@onready var camera: Camera3D = $CameraRig/SpringArm3D/Camera3D

func _ready() -> void:
	add_to_group("player")
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	_build_collision()
	_build_viking()
	_build_weapon()
	_build_animation_tree()
	spring_arm.add_excluded_object(get_rid())
	_apply_camera_rotation()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED and not lock_target:
			camera_manual_timer = 0.75
			camera_yaw -= event.relative.x * MOUSE_SENSITIVITY
			camera_pitch -= event.relative.y * MOUSE_SENSITIVITY
			camera_pitch = clampf(
				camera_pitch,
				deg_to_rad(-42.0),
				deg_to_rad(18.0)
			)
			_apply_camera_rotation()

	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
				_light_attack()

	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_ESCAPE:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		elif event.keycode == KEY_TAB:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _physics_process(delta: float) -> void:
	attack_time = maxf(0.0, attack_time - delta)
	dodge_time = maxf(0.0, dodge_time - delta)
	invuln_time = maxf(0.0, invuln_time - delta)
	combo_window = maxf(0.0, combo_window - delta)
	stamina_regen_delay = maxf(0.0, stamina_regen_delay - delta)
	camera_manual_timer = maxf(0.0, camera_manual_timer - delta)

	if combo_window <= 0.0 and attack_time <= 0.0:
		combo_step = 0

	_validate_lock_target()
	_update_lock_camera(delta)
	var input := Input.get_vector(
		"move_left", "move_right",
		"move_forward", "move_back"
	)
	var direction := _camera_relative_direction(input)
	var wants_run := Input.is_action_pressed("run")
	var running := (
		wants_run
		and direction.length_squared() > 0.01
		and stamina > 0.5
		and attack_time <= 0.0
	)

	if running:
		_spend_stamina(RUN_DRAIN * delta, 0.20)
	elif stamina_regen_delay <= 0.0:
		stamina = minf(MAX_STAMINA, stamina + STAMINA_REGEN * delta)

	if is_instance_valid(lock_target):
		var to_target := lock_target.global_position - global_position
		to_target.y = 0.0
		if to_target.length_squared() > 0.01:
			facing = to_target.normalized()
	elif direction.length_squared() > 0.01:
		facing = direction.normalized()
		dodge_direction = facing

	_auto_follow_camera(delta, direction)

	var speed := RUN_SPEED if running else WALK_SPEED
	var target_velocity := direction * speed
	if dodge_time > 0.0:
		target_velocity = dodge_direction * DODGE_SPEED

	velocity.x = move_toward(
		velocity.x,
		target_velocity.x,
		ACCEL * delta
	)
	velocity.z = move_toward(
		velocity.z,
		target_velocity.z,
		ACCEL * delta
	)
	velocity.y = -1.0
	move_and_slide()

	_rotate_model(delta)
	_update_locomotion(direction.length(), running)
	_visual_motion(delta, direction.length(), running)

	if Input.is_action_just_pressed("attack"):
		_light_attack()
	if Input.is_action_just_pressed("heavy"):
		_heavy_attack()
	if Input.is_action_just_pressed("dodge"):
		_dodge()
	if Input.is_action_just_pressed("lock_on"):
		_toggle_lock()
	if Input.is_action_just_pressed("interact"):
		_interact()

func _camera_relative_direction(input: Vector2) -> Vector3:
	if input.length_squared() <= 0.01:
		return Vector3.ZERO
	var forward := -camera.global_transform.basis.z
	var right := camera.global_transform.basis.x
	forward.y = 0.0
	right.y = 0.0
	forward = forward.normalized()
	right = right.normalized()
	return (right * input.x + forward * -input.y).normalized()

func _apply_camera_rotation() -> void:
	camera_rig.rotation.y = camera_yaw
	spring_arm.rotation.x = camera_pitch

func _update_lock_camera(delta: float) -> void:
	if not is_instance_valid(lock_target):
		return
	var direction := lock_target.global_position - global_position
	direction.y = 0.0
	if direction.length_squared() <= 0.01:
		return
	var desired_yaw := atan2(-direction.x, -direction.z)
	camera_yaw = lerp_angle(
		camera_yaw,
		desired_yaw,
		clampf(delta * 4.0, 0.0, 1.0)
	)
	_apply_camera_rotation()

func _auto_follow_camera(delta: float, direction: Vector3) -> void:
	if is_instance_valid(lock_target):
		return
	if camera_manual_timer > 0.0:
		return
	if direction.length_squared() <= 0.05:
		return

	var desired_yaw := atan2(-facing.x, -facing.z)
	camera_yaw = lerp_angle(
		camera_yaw,
		desired_yaw,
		clampf(delta * 2.9, 0.0, 1.0)
	)
	_apply_camera_rotation()

func _visual_motion(
	delta: float,
	move_amount: float,
	running: bool
) -> void:
	var amount := clampf(move_amount, 0.0, 1.0)
	var speed_scale := 1.45 if running else 1.0
	motion_phase += delta * lerpf(2.0, 8.6 * speed_scale, amount)

	var bob := sin(motion_phase * 2.0) * 0.018 * amount
	var sway := sin(motion_phase) * 0.012 * amount
	if model_root:
		model_root.position.y = bob
		model_root.rotation.z = sway
		model_root.rotation.x = -0.035 * amount * speed_scale

	var target_fov := 69.0 if running and amount > 0.1 else 64.0
	camera.fov = lerpf(
		camera.fov,
		target_fov,
		clampf(delta * 4.5, 0.0, 1.0)
	)
	camera.position.x = 0.52 + sin(motion_phase) * 0.018 * amount
	camera.position.y = 0.10 + absf(sin(motion_phase * 2.0)) * 0.012 * amount

func _rotate_model(delta: float) -> void:
	if not model_root or facing.length_squared() <= 0.01:
		return
	var target_yaw := atan2(facing.x, facing.z)
	model_root.rotation.y = lerp_angle(
		model_root.rotation.y,
		target_yaw,
		MODEL_ROTATE_SPEED * delta
	)

func _light_attack() -> void:
	if attack_time > 0.12 or dodge_time > 0.0:
		return

	if combo_window > 0.0:
		combo_step = (combo_step + 1) % 3
	else:
		combo_step = 0

	if stamina < LIGHT_COSTS[combo_step]:
		return

	var damage: int = LIGHT_DAMAGE[combo_step]
	var duration: float = LIGHT_DURATION[combo_step]
	var hit_delay: float = LIGHT_HIT_DELAY[combo_step]
	var anim_rate: float = LIGHT_ANIM_RATE[combo_step]

	_spend_stamina(LIGHT_COSTS[combo_step], 0.52)
	attack_time = duration
	combo_window = 0.68
	_face_lock_target()
	_set_attack_rate(anim_rate)
	_fire_one_shot("AttackShot")
	_queue_attack_hit(damage, hit_delay, 2.55, false)
func _heavy_attack() -> void:
	if attack_time > 0.0 or dodge_time > 0.0:
		return
	if stamina < HEAVY_COST:
		return

	_spend_stamina(HEAVY_COST, 0.82)
	attack_time = 0.74
	combo_window = 0.0
	combo_step = 0
	_face_lock_target()
	_set_attack_rate(0.70)
	_fire_one_shot("AttackShot")
	_queue_attack_hit(62, 0.29, 2.9, true)

func _queue_attack_hit(
	damage: int,
	delay: float,
	reach: float,
	cleave: bool
) -> void:
	await get_tree().create_timer(delay).timeout
	if not is_inside_tree():
		return
	_deal_attack_hit(damage, reach, cleave)

func _deal_attack_hit(
	damage: int,
	reach: float,
	cleave: bool
) -> void:
	var hits: Array[Node3D] = []
	for node in get_tree().get_nodes_in_group("enemies"):
		if not node is Node3D:
			continue
		var enemy := node as Node3D
		var offset := enemy.global_position - global_position
		var planar := Vector3(offset.x, 0.0, offset.z)
		var distance := planar.length()
		if distance <= 0.01 or distance > reach:
			continue
		var direction := planar.normalized()
		if facing.dot(direction) < 0.32:
			continue
		hits.append(enemy)

	if hits.is_empty():
		return

	hits.sort_custom(
		func(a: Node3D, b: Node3D) -> bool:
			return global_position.distance_to(a.global_position) < global_position.distance_to(b.global_position)
	)

	var count := hits.size() if cleave else 1
	for i in range(count):
		var target := hits[i]
		if target.has_method("take_hit"):
			target.take_hit(damage, facing.normalized())

func take_hit(amount: int) -> void:
	if invuln_time > 0.0 or dodge_time > 0.0:
		return
	invuln_time = 0.45
	health -= amount
	_fire_one_shot("HitShot")
	if health <= 0:
		health = 120
		stamina = MAX_STAMINA
		global_position = Vector3.ZERO
		velocity = Vector3.ZERO

func _dodge() -> void:
	if dodge_time > 0.0 or attack_time > 0.25:
		return
	if stamina < DODGE_COST:
		return
	_spend_stamina(DODGE_COST, 0.72)
	dodge_time = 0.30
	invuln_time = maxf(invuln_time, 0.34)
	if facing.length_squared() > 0.01:
		dodge_direction = facing.normalized()

func _spend_stamina(amount: float, regen_delay: float) -> void:
	stamina = maxf(0.0, stamina - amount)
	stamina_regen_delay = maxf(
		stamina_regen_delay,
		regen_delay
	)

func _toggle_lock() -> void:
	if is_instance_valid(lock_target):
		lock_target = null
		return
	lock_target = _find_nearest_enemy()
func _find_nearest_enemy() -> Node3D:
	var best: Node3D = null
	var best_score := LOCK_RANGE
	for node in get_tree().get_nodes_in_group("enemies"):
		if not node is Node3D:
			continue
		var enemy := node as Node3D
		var distance := global_position.distance_to(enemy.global_position)
		if distance < best_score:
			best = enemy
			best_score = distance
	return best

func _validate_lock_target() -> void:
	if not is_instance_valid(lock_target):
		lock_target = null
		return
	if global_position.distance_to(lock_target.global_position) > LOCK_RANGE * 1.35:
		lock_target = null

func _face_lock_target() -> void:
	if not is_instance_valid(lock_target):
		return
	var offset := lock_target.global_position - global_position
	offset.y = 0.0
	if offset.length_squared() > 0.01:
		facing = offset.normalized()

func _build_collision() -> void:
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.38
	capsule.height = 1.75
	$CollisionShape3D.shape = capsule
	$CollisionShape3D.position.y = 0.88

func _build_viking() -> void:
	model_root = VIKING.instantiate()
	model_root.name = "VikingModel"
	model_root.scale = Vector3.ONE * 1.28
	model_root.rotation.y = PI
	add_child(model_root)

	anim_player = model_root.find_child(
		"AnimationPlayer",
		true,
		false
	) as AnimationPlayer
	skeleton = model_root.find_child(
		"Skeleton3D",
		true,
		false
	) as Skeleton3D
	_apply_character_proportions()

	if anim_player:
		for anim_name in [
			"CharacterArmature|Idle",
			"CharacterArmature|Walk"
		]:
			var anim := anim_player.get_animation(anim_name)
			if anim:
				anim.loop_mode = Animation.LOOP_LINEAR

func _build_weapon() -> void:
	var weapon_rig := model_root.find_child(
		"Skeleton3D",
		true,
		false
	) as Skeleton3D
	if not weapon_rig:
		return

	var attachment := BoneAttachment3D.new()
	attachment.name = "RightHandWeapon"
	attachment.bone_name = "Fist.R"
	weapon_rig.add_child(attachment)

	weapon_pivot = Node3D.new()
	weapon_pivot.name = "WeaponPivot"
	var inherited_scale := attachment.global_basis.get_scale().x
	inherited_scale = maxf(inherited_scale, 0.001)
	weapon_pivot.scale = Vector3.ONE / inherited_scale
	weapon_pivot.position = Vector3(0.0, -0.03, 0.02) / inherited_scale
	weapon_pivot.rotation_degrees = Vector3(0, 90, -92)
	attachment.add_child(weapon_pivot)

	var axe := MeshInstance3D.new()
	axe.name = "VikingAxe"
	axe.mesh = AXE
	axe.scale = Vector3.ONE * 0.24
	axe.position = Vector3(0.0, -0.17, 0.0)
	weapon_pivot.add_child(axe)

func _build_animation_tree() -> void:
	if not anim_player:
		return

	animation_tree = AnimationTree.new()
	animation_tree.name = "RuntimeAnimationTree"
	model_root.add_child(animation_tree)
	animation_tree.anim_player = animation_tree.get_path_to(anim_player)

	var blend_tree := AnimationNodeBlendTree.new()
	var locomotion := AnimationNodeBlendSpace1D.new()
	locomotion.min_space = 0.0
	locomotion.max_space = 1.0

	var idle := AnimationNodeAnimation.new()
	idle.animation = &"CharacterArmature|Idle"
	var walk := AnimationNodeAnimation.new()
	walk.animation = &"CharacterArmature|Walk"
	locomotion.add_blend_point(idle, 0.0, -1, &"Idle")
	locomotion.add_blend_point(walk, 1.0, -1, &"Walk")

	var locomotion_rate := AnimationNodeTimeScale.new()
	var attack_anim := AnimationNodeAnimation.new()
	attack_anim.animation = &"CharacterArmature|Punch"
	var attack_rate := AnimationNodeTimeScale.new()
	var attack_shot := AnimationNodeOneShot.new()
	var hit_anim := AnimationNodeAnimation.new()
	hit_anim.animation = &"CharacterArmature|RecieveHit"
	var hit_shot := AnimationNodeOneShot.new()
	blend_tree.add_node("Locomotion", locomotion, Vector2(0, 0))
	blend_tree.add_node("LocomotionRate", locomotion_rate, Vector2(210, 0))
	blend_tree.add_node("AttackAnim", attack_anim, Vector2(190, 150))
	blend_tree.add_node("AttackRate", attack_rate, Vector2(390, 150))
	blend_tree.add_node("AttackShot", attack_shot, Vector2(570, 60))
	blend_tree.add_node("HitAnim", hit_anim, Vector2(560, 220))
	blend_tree.add_node("HitShot", hit_shot, Vector2(780, 100))

	blend_tree.connect_node("LocomotionRate", 0, "Locomotion")
	blend_tree.connect_node("AttackRate", 0, "AttackAnim")
	blend_tree.connect_node("AttackShot", 0, "LocomotionRate")
	blend_tree.connect_node("AttackShot", 1, "AttackRate")
	blend_tree.connect_node("HitShot", 0, "AttackShot")
	blend_tree.connect_node("HitShot", 1, "HitAnim")
	blend_tree.connect_node("output", 0, "HitShot")

	animation_tree.tree_root = blend_tree
	animation_tree.active = true
	animation_tree.set(
		"parameters/Locomotion/blend_position",
		0.0
	)
	_set_attack_rate(1.0)
func _update_locomotion(amount: float, running: bool) -> void:
	if not animation_tree:
		return
	var blend := clampf(amount, 0.0, 1.0)
	animation_tree.set(
		"parameters/Locomotion/blend_position",
		blend
	)
	animation_tree.set(
		"parameters/LocomotionRate/scale",
		1.42 if running and blend > 0.1 else 1.0
	)

func _set_attack_rate(rate: float) -> void:
	if not animation_tree:
		return
	animation_tree.set(
		"parameters/AttackRate/scale",
		rate
	)

func _fire_one_shot(node_name: String) -> void:
	if not animation_tree:
		return
	animation_tree.set(
		"parameters/%s/request" % node_name,
		AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE
	)

func _apply_character_proportions() -> void:
	if not skeleton:
		return

	var head := skeleton.find_bone("Head")
	if head >= 0:
		skeleton.set_bone_pose_scale(
			head,
			Vector3(0.58, 0.58, 0.58)
		)

	var neck := skeleton.find_bone("Neck")
	if neck >= 0:
		skeleton.set_bone_pose_scale(
			neck,
			Vector3(0.93, 1.02, 0.93)
		)

func set_interactable(node: Node) -> void:
	current_interactable = node

func clear_interactable(node: Node) -> void:
	if current_interactable == node:
		current_interactable = null

func _interact() -> void:
	if not is_instance_valid(current_interactable):
		current_interactable = null
		return
	if current_interactable.has_method("interact"):
		current_interactable.interact(self)

func get_interaction_prompt() -> String:
	if not is_instance_valid(current_interactable):
		return ""
	if current_interactable.has_method("get_prompt"):
		return current_interactable.get_prompt()
	return "Interagir"

func teleport_to(target: Vector3) -> void:
	global_position = target
	velocity = Vector3.ZERO
	lock_target = null
	current_interactable = null
	camera_manual_timer = 0.0
	camera_pitch = deg_to_rad(-12.0)
	_apply_camera_rotation()
