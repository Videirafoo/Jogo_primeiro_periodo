extends CharacterBody3D

const SPEED := 5.8
const ACCEL := 20.0
const ROTATE_SPEED := 9.0
const VIKING := preload("res://assets/characters/viking/Viking_Male.glb")
const AXE := preload("res://assets/weapons/SimpleAxe.obj")

var attack_time := 0.0
var dodge_time := 0.0
var facing := Vector3.FORWARD
var anim_player: AnimationPlayer
var model_root: Node3D
var weapon_pivot: Node3D

func _ready() -> void:
    _build_collision()
    _build_viking()
    _build_weapon()
    _play_loop("CharacterArmature|Idle")
    var leather := _mat(Color("382923"), 0.0, 0.88)
    var cloth := _mat(Color("253d46"), 0.0, 0.82)
    var skin := _mat(Color("c08c6f"), 0.0, 0.72)
    var iron := _mat(Color("70777d"), 0.72, 0.28)
    var fur := _mat(Color("766252"), 0.0, 0.96)

    var torso_mesh := CapsuleMesh.new()
    torso_mesh.radius = 0.43
    torso_mesh.height = 1.12
    _part(torso_mesh, Vector3(0, 1.35, 0), cloth, visual)

    var belt_mesh := CylinderMesh.new()
    belt_mesh.top_radius = 0.46
    belt_mesh.bottom_radius = 0.46
    belt_mesh.height = 0.16
    _part(belt_mesh, Vector3(0, 1.02, 0), leather, visual)

    var head_mesh := SphereMesh.new()
    head_mesh.radius = 0.30
    head_mesh.height = 0.58
    _part(head_mesh, Vector3(0, 2.05, 0), skin, visual)

    var helm_mesh := CylinderMesh.new()
    helm_mesh.top_radius = 0.24
    helm_mesh.bottom_radius = 0.33
    helm_mesh.height = 0.22
    _part(helm_mesh, Vector3(0, 2.28, 0), iron, visual)
    for side in [-1.0, 1.0]:
        var arm_mesh := CapsuleMesh.new()
        arm_mesh.radius = 0.13
        arm_mesh.height = 0.78
        var arm := _part(
            arm_mesh,
            Vector3(side * 0.48, 1.42, 0),
            skin,
            visual
        )
        arm.rotation_degrees.z = side * 10.0

        var leg_mesh := CapsuleMesh.new()
        leg_mesh.radius = 0.15
        leg_mesh.height = 0.92
        _part(
            leg_mesh,
            Vector3(side * 0.20, 0.52, 0),
            leather,
            visual
        )

    var shoulders := BoxMesh.new()
    shoulders.size = Vector3(1.18, 0.18, 0.52)
    _part(shoulders, Vector3(0, 1.72, 0), fur, visual)

    var weapon_pivot := Node3D.new()
    weapon_pivot.name = "WeaponPivot"
    weapon_pivot.position = Vector3(0.58, 1.42, -0.08)
    visual.add_child(weapon_pivot)
    _build_axe(weapon_pivot, leather, iron)

func _physics_process(delta: float) -> void:
    attack_time = maxf(0.0, attack_time - delta)
    dodge_time = maxf(0.0, dodge_time - delta)

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
        anim_player.play("CharacterArmature|Punch", 0.06, 1.25)
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

func _dodge() -> void:
    if dodge_time > 0.0:
        return
    dodge_time = 0.28
    if anim_player:
        anim_player.play("CharacterArmature|Walk", 0.03, 2.0)

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
        "AnimationPlayer", true, false
    ) as AnimationPlayer
func _build_axe(
    parent: Node3D,
    wood: Material,
    iron: Material
) -> void:
    var handle_mesh := CylinderMesh.new()
    handle_mesh.top_radius = 0.045
    handle_mesh.bottom_radius = 0.055
    handle_mesh.height = 1.35
    var handle := _part(
        handle_mesh,
        Vector3(0, -0.12, 0),
        wood,
        parent
    )
    handle.rotation_degrees.z = -18

    var blade_mesh := BoxMesh.new()
    blade_mesh.size = Vector3(0.52, 0.46, 0.10)
    var blade := _part(
        blade_mesh,
        Vector3(0.18, -0.72, 0),
        iron,
        parent
    )
    blade.rotation_degrees.z = -18

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
    if not anim_player:
        return
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
