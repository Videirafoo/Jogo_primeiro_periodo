extends CharacterBody3D

const WALK_SPEED := 3.7
const RUN_SPEED := 6.4
const DODGE_SPEED := 10.5
const ACCEL := 22.0
const MODEL_ROTATE_SPEED := 12.0
const MOUSE_SENSITIVITY := 0.0024
const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")
const AXE := preload("res://assets/weapons/SimpleAxe.obj")

var attack_time := 0.0
var dodge_time := 0.0
var invuln_time := 0.0
var health := 120
var facing := Vector3.FORWARD
var dodge_direction := Vector3.FORWARD

var model_root: Node3D
var anim_player: AnimationPlayer
var animation_tree: AnimationTree
var weapon_pivot: Node3D
var camera_yaw := 0.0
var camera_pitch := deg_to_rad(-14.0)

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
        if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
            camera_yaw -= event.relative.x * MOUSE_SENSITIVITY
            camera_pitch -= event.relative.y * MOUSE_SENSITIVITY
            camera_pitch = clampf(
                camera_pitch,
                deg_to_rad(-48.0),
                deg_to_rad(24.0)
            )
            _apply_camera_rotation()

    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
            if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
                _attack()

    if event is InputEventKey and event.pressed:
        if event.keycode == KEY_ESCAPE:
            Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
        elif event.keycode == KEY_TAB:
            Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
func _physics_process(delta: float) -> void:
    attack_time = maxf(0.0, attack_time - delta)
    dodge_time = maxf(0.0, dodge_time - delta)
    invuln_time = maxf(0.0, invuln_time - delta)

    var input := Input.get_vector(
        "move_left", "move_right",
        "move_forward", "move_back"
    )
    var direction := _camera_relative_direction(input)
    var running := Input.is_action_pressed("run")

    if direction.length_squared() > 0.01:
        facing = direction.normalized()
        dodge_direction = facing

    var speed := RUN_SPEED if running else WALK_SPEED
    var target_velocity := direction * speed
    if dodge_time > 0.0:
        target_velocity = dodge_direction * DODGE_SPEED

    velocity.x = move_toward(
        velocity.x, target_velocity.x, ACCEL * delta
    )
    velocity.z = move_toward(
        velocity.z, target_velocity.z, ACCEL * delta
    )
    velocity.y = -1.0
    move_and_slide()
    _rotate_model(delta)
    _update_locomotion(direction.length(), running)

    if Input.is_action_just_pressed("attack"):
        _attack()
    if Input.is_action_just_pressed("dodge"):
        _dodge()

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

func _rotate_model(delta: float) -> void:
    if not model_root or facing.length_squared() <= 0.01:
        return
    var target_yaw := atan2(facing.x, facing.z)
    model_root.rotation.y = lerp_angle(
        model_root.rotation.y,
        target_yaw,
        MODEL_ROTATE_SPEED * delta
    )
func _attack() -> void:
    if attack_time > 0.0 or dodge_time > 0.0:
        return
    attack_time = 0.44
    _fire_one_shot("AttackShot")
    _deal_attack_hit_deferred()

func _deal_attack_hit_deferred() -> void:
    await get_tree().create_timer(0.13).timeout
    if not is_inside_tree():
        return
    _deal_attack_hit()

func _deal_attack_hit() -> void:
    var best: Node3D = null
    var best_distance := 2.45
    for node in get_tree().get_nodes_in_group("enemies"):
        if not node is Node3D:
            continue
        var enemy := node as Node3D
        var offset := enemy.global_position - global_position
        var planar := Vector3(offset.x, 0.0, offset.z)
        var distance := planar.length()
        if distance <= 0.01 or distance > best_distance:
            continue
        var direction := planar.normalized()
        if facing.dot(direction) < 0.32:
            continue
        best = enemy
        best_distance = distance

    if best and best.has_method("take_hit"):
        best.take_hit(34, facing.normalized())
func take_hit(amount: int) -> void:
    if invuln_time > 0.0 or dodge_time > 0.0:
        return
    invuln_time = 0.45
    health -= amount
    _fire_one_shot("HitShot")
    if health <= 0:
        health = 120
        global_position = Vector3.ZERO
        velocity = Vector3.ZERO

func _dodge() -> void:
    if dodge_time > 0.0 or attack_time > 0.25:
        return
    dodge_time = 0.28
    invuln_time = maxf(invuln_time, 0.30)
    if facing.length_squared() > 0.01:
        dodge_direction = facing.normalized()

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

    if anim_player:
        for name in [
            "CharacterArmature|Idle",
            "CharacterArmature|Walk"
        ]:
            var anim := anim_player.get_animation(name)
            if anim:
                anim.loop_mode = Animation.LOOP_LINEAR

func _build_weapon() -> void:
    var skeleton := model_root.find_child(
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
    weapon_pivot.name = "WeaponPivot"
    weapon_pivot.position = Vector3(0.0, -0.03, 0.02)
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
    var attack_shot := AnimationNodeOneShot.new()
    var hit_anim := AnimationNodeAnimation.new()
    hit_anim.animation = &"CharacterArmature|RecieveHit"
    var hit_shot := AnimationNodeOneShot.new()

    blend_tree.add_node("Locomotion", locomotion, Vector2(0, 0))
    blend_tree.add_node("LocomotionRate", locomotion_rate, Vector2(220, 0))
    blend_tree.add_node("AttackAnim", attack_anim, Vector2(220, 150))
    blend_tree.add_node("AttackShot", attack_shot, Vector2(440, 60))
    blend_tree.add_node("HitAnim", hit_anim, Vector2(440, 190))
    blend_tree.add_node("HitShot", hit_shot, Vector2(650, 90))

    blend_tree.connect_node("LocomotionRate", 0, "Locomotion")
    blend_tree.connect_node("AttackShot", 0, "LocomotionRate")
    blend_tree.connect_node("AttackShot", 1, "AttackAnim")
    blend_tree.connect_node("HitShot", 0, "AttackShot")
    blend_tree.connect_node("HitShot", 1, "HitAnim")
    blend_tree.connect_node("output", 0, "HitShot")

    animation_tree.tree_root = blend_tree
    animation_tree.active = true
    animation_tree.set("parameters/Locomotion/blend_position", 0.0)
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

func _fire_one_shot(node_name: String) -> void:
    if not animation_tree:
        return
    animation_tree.set(
        "parameters/%s/request" % node_name,
        AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE
    )
