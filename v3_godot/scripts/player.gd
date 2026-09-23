extends CharacterBody3D

const SPEED := 5.8
const ACCEL := 20.0
const ROTATE_SPEED := 9.0
const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")
const AXE := preload("res://assets/weapons/SimpleAxe.obj")

var attack_time := 0.0
var dodge_time := 0.0
var facing := Vector3.FORWARD
var health := 120
var invuln_time := 0.0
var anim_player: AnimationPlayer
var model_root: Node3D
var weapon_pivot: Node3D

func _ready() -> void:
    add_to_group("player")
    _build_collision()
    _build_viking()
    _build_weapon()
    _play_loop("CharacterArmature|Idle")

func _physics_process(delta: float) -> void:
    attack_time = maxf(0.0, attack_time - delta)
    dodge_time = maxf(0.0, dodge_time - delta)
    invuln_time = maxf(0.0, invuln_time - delta)

    var input := Input.get_vector(
        "move_left", "move_right",
        "move_forward", "move_back"
    )
    var dir := Vector3(input.x, 0.0, input.y)

    if dir.length_squared() > 0.01:
        dir = dir.normalized()
        facing = dir
        rotation.y = lerp_angle(
            rotation.y,
            atan2(dir.x, dir.z),
            delta * ROTATE_SPEED
        )

    var target_velocity := dir * SPEED
    if dodge_time > 0.0:
        target_velocity += facing * 7.5

    velocity.x = move_toward(
        velocity.x, target_velocity.x, ACCEL * delta
    )
    velocity.z = move_toward(
        velocity.z, target_velocity.z, ACCEL * delta
    )
    velocity.y = -1.0
    move_and_slide()

    if attack_time <= 0.0:
        _play_locomotion(dir.length_squared() > 0.01)

    if Input.is_action_just_pressed("attack"):
        _attack()
    if Input.is_action_just_pressed("dodge"):
        _dodge()

func _attack() -> void:
    if attack_time > 0.0:
        return
    attack_time = 0.42

    if anim_player:
        anim_player.play(
            "CharacterArmature|Punch",
            0.06,
            1.25
        )

    if weapon_pivot:
        weapon_pivot.rotation_degrees = Vector3(-18, 0, -28)
        var tween := create_tween()
        tween.set_trans(Tween.TRANS_QUAD)
        tween.set_ease(Tween.EASE_OUT)
        tween.tween_property(
            weapon_pivot,
            "rotation_degrees",
            Vector3(-18, -90, 72),
            0.13
        )

        tween.tween_property(
            weapon_pivot,
            "rotation_degrees",
            Vector3(-18, 0, -28),
            0.18
        )

    _deal_attack_hit()

func _deal_attack_hit() -> void:
    var best: Node3D = null
    var best_distance := 2.35
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
        if facing.dot(direction) < 0.05:
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
    if anim_player:
        anim_player.play("CharacterArmature|RecieveHit", 0.03, 1.15)
    if health <= 0:
        health = 120
        global_position = Vector3.ZERO

func _dodge() -> void:
    if dodge_time > 0.0:
        return
    dodge_time = 0.28
    if anim_player:
        anim_player.play(
            "CharacterArmature|Walk",
            0.03,
            2.0
        )

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
    weapon_pivot = Node3D.new()
    weapon_pivot.name = "WeaponPivot"
    weapon_pivot.position = Vector3(0.48, 1.02, -0.08)
    weapon_pivot.rotation_degrees = Vector3(-18, 0, -28)
    add_child(weapon_pivot)

    var axe := MeshInstance3D.new()
    axe.name = "VikingAxe"
    axe.mesh = AXE
    axe.scale = Vector3.ONE * 0.27
    axe.position = Vector3(0.0, -0.18, 0.0)
    axe.rotation_degrees = Vector3(0, 0, -12)
    weapon_pivot.add_child(axe)

func _play_locomotion(moving: bool) -> void:
    if moving:
        _play_loop("CharacterArmature|Walk")
    else:
        _play_loop("CharacterArmature|Idle")

func _play_loop(name: String) -> void:
    if not anim_player:
        return
    if anim_player.current_animation == name:
        return
    anim_player.play(name, 0.12)
