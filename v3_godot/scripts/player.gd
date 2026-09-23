extends CharacterBody3D

const SPEED := 6.2
const ACCEL := 18.0
const ROTATE_SPEED := 10.0
var attack_time := 0.0
var dodge_time := 0.0
var facing := Vector3.FORWARD

func _ready() -> void:
    _build_body()

func _physics_process(delta: float) -> void:
    attack_time = maxf(0.0, attack_time - delta)
    dodge_time = maxf(0.0, dodge_time - delta)
    var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var dir := Vector3(input.x, 0.0, input.y)
    if dir.length_squared() > 0.01:
        dir = dir.normalized()
        facing = dir
        var target := atan2(dir.x, dir.z)
        rotation.y = lerp_angle(rotation.y, target, delta * ROTATE_SPEED)
    var target_velocity := dir * SPEED
    velocity.x = move_toward(velocity.x, target_velocity.x, ACCEL * delta)
    velocity.z = move_toward(velocity.z, target_velocity.z, ACCEL * delta)
    velocity.y = -1.0
    move_and_slide()

    if Input.is_action_just_pressed("attack"):
        _attack()
    if Input.is_action_just_pressed("dodge"):
        dodge_time = 0.28
        velocity += facing * 8.0

func _attack() -> void:
    if attack_time > 0.0:
        return
    attack_time = 0.38
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_QUAD)
    tween.tween_property(self, "rotation:y", rotation.y + 0.32, 0.09)
    tween.tween_property(self, "rotation:y", rotation.y - 0.18, 0.12)

func _build_body() -> void:
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.42
    capsule.height = 1.8
    $CollisionShape3D.shape = capsule
    var body := MeshInstance3D.new()
    var mesh := CapsuleMesh.new()
    mesh.radius = 0.42
    mesh.height = 1.8
    body.mesh = mesh
    body.position.y = 0.9
    add_child(body)
