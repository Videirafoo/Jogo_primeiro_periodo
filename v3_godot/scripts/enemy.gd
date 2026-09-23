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
        weapon_pivot.rotation_degrees = Vector3(0, 90, -92)
        var tween := create_tween()
        tween.tween_property(
            weapon_pivot,
            "rotation_degrees",
            Vector3(-8, 32, -48),
            0.14
        )
        tween.tween_property(
            weapon_pivot,
            "rotation_degrees",
            Vector3(0, 90, -92),
            0.20
        )

    if player and player.has_method("take_hit"):
        player.take_hit(16)

func take_hit(amount: int, direction: Vector3) -> void:
    health -= amount
    knockback += direction * 5.2
    _spawn_hit_vfx(direction)
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
    weapon_pivot.position = Vector3(0.0, -0.03, 0.02)
    weapon_pivot.rotation_degrees = Vector3(0, 90, -92)
    attachment.add_child(weapon_pivot)

    var sword := MeshInstance3D.new()
    sword.mesh = SWORD
    sword.scale = Vector3.ONE * 0.23
    sword.position = Vector3(0, -0.18, 0)
    weapon_pivot.add_child(sword)

func _play_loop(name: String) -> void:
    if not anim_player:
        return
    if anim_player.current_animation == name:
        return
    anim_player.play(name, 0.12)

func _spawn_hit_vfx(direction: Vector3) -> void:
    var particles := GPUParticles3D.new()
    particles.amount = 16
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
    process.initial_velocity_max = 5.2
    process.gravity = Vector3(0, -7.5, 0)
    process.color = Color("79f3ff")
    particles.process_material = process

    var quad := QuadMesh.new()
    quad.size = Vector2(0.06, 0.06)
    var material := StandardMaterial3D.new()
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.albedo_color = Color("bffcff")
    material.emission_enabled = true
    material.emission = Color("47e8ff")
    quad.material = material
    particles.draw_pass_1 = quad

    get_parent().add_child(particles)
    particles.global_position = global_position + Vector3.UP * 1.0
    particles.finished.connect(particles.queue_free)
    particles.emitting = true

    var flash := OmniLight3D.new()
    flash.light_color = Color("63efff")
    flash.light_energy = 3.2
    flash.omni_range = 3.0
    get_parent().add_child(flash)
    flash.global_position = particles.global_position
    var fade := get_tree().create_tween()
    fade.tween_property(flash, "light_energy", 0.0, 0.14)
    fade.tween_callback(flash.queue_free)
