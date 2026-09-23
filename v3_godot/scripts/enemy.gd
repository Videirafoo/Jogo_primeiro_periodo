extends CharacterBody3D

const SPEED := 2.7
const ATTACK_RANGE := 1.75
const ATTACK_COOLDOWN := 1.15
const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")
const SWORD := preload("res://assets/weapons/LongSword.obj")

var health := 100
var attack_cd := 0.0
var swing_time := 0.0
var knockback := Vector3.ZERO
var player: Node3D
var anim_player: AnimationPlayer
var weapon_pivot: Node3D

func _ready() -> void:
    add_to_group("enemies")
    player = get_tree().get_first_node_in_group("player") as Node3D
    _build_collision()
    _build_raider()

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
    if planar.length() > 0.05:
        look_at(global_position + planar, Vector3.UP)

    var movement := Vector3.ZERO
    if planar.length() > ATTACK_RANGE:
        movement = planar.normalized() * SPEED
        if swing_time <= 0.0:
            _play_loop("CharacterArmature|Walk")
    elif attack_cd <= 0.0:
        _attack_player()
    elif swing_time <= 0.0:
        _play_loop("CharacterArmature|Idle")

    velocity.x = movement.x + knockback.x
    velocity.z = movement.z + knockback.z
    velocity.y = -1.0
    move_and_slide()

func _attack_player() -> void:
    attack_cd = ATTACK_COOLDOWN
    swing_time = 0.42
    if anim_player:
        anim_player.play("CharacterArmature|Punch", 0.05, 1.1)

    if weapon_pivot:
        weapon_pivot.rotation_degrees = Vector3(-14, 0, -18)
        var tween := create_tween()
        tween.tween_property(
            weapon_pivot,
            "rotation_degrees",
            Vector3(-18, 82, 58),
            0.16
        )
        tween.tween_property(
            weapon_pivot,
            "rotation_degrees",
            Vector3(-14, 0, -18),
            0.18
        )

    if player and player.has_method("take_hit"):
        player.take_hit(16)

func take_hit(amount: int, direction: Vector3) -> void:
    health -= amount
    knockback += direction * 5.2
    if anim_player and health > 0:
        anim_player.play("CharacterArmature|RecieveHit", 0.03, 1.1)
    if health <= 0:
        queue_free()

func _build_collision() -> void:
    var shape := CapsuleShape3D.new()
    shape.radius = 0.4
    shape.height = 1.75
    $CollisionShape3D.shape = shape
    $CollisionShape3D.position.y = 0.88

func _build_raider() -> void:
    var model := VIKING.instantiate()
    model.name = "RaiderModel"
    model.scale = Vector3.ONE * 1.22
    model.rotation.y = PI
    add_child(model)

    anim_player = model.find_child(
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
        _play_loop("CharacterArmature|Idle")

    weapon_pivot = Node3D.new()
    weapon_pivot.position = Vector3(0.46, 1.0, -0.08)
    weapon_pivot.rotation_degrees = Vector3(-14, 0, -18)
    add_child(weapon_pivot)

    var sword := MeshInstance3D.new()
    sword.mesh = SWORD
    sword.scale = Vector3.ONE * 0.26
    sword.position = Vector3(0, -0.18, 0)
    sword.rotation_degrees = Vector3(0, 0, -8)
    weapon_pivot.add_child(sword)

func _play_loop(name: String) -> void:
    if not anim_player:
        return
    if anim_player.current_animation == name:
        return
    anim_player.play(name, 0.12)
