extends CharacterBody3D

const SPEED := 2.7
const ATTACK_RANGE := 1.65
const ATTACK_COOLDOWN := 1.15

var health := 100
var attack_cd := 0.0
var knockback := Vector3.ZERO
var player: Node3D

func _ready() -> void:
    add_to_group("enemies")
    player = get_tree().get_first_node_in_group("player")
    _build_collision()
    _build_raider()

func _physics_process(delta: float) -> void:
    attack_cd = maxf(0.0, attack_cd - delta)
    knockback = knockback.move_toward(Vector3.ZERO, 18.0 * delta)
    if not is_instance_valid(player):
        return
    var offset := player.global_position - global_position
    var planar := Vector3(offset.x, 0.0, offset.z)
    if planar.length() > 0.05:
        look_at(global_position + planar, Vector3.UP)
    var move := Vector3.ZERO
    if planar.length() > ATTACK_RANGE:
        move = planar.normalized() * SPEED
    elif attack_cd <= 0.0:
        _attack_player()
    velocity.x = move.x + knockback.x
    velocity.z = move.z + knockback.z
    velocity.y = -1.0
    move_and_slide()

func _attack_player() -> void:
    attack_cd = ATTACK_COOLDOWN
    if player.has_method("take_hit"):
        player.take_hit(16)
    var visual := get_node_or_null("Visual")
    if visual:
        var tween := create_tween()
        tween.tween_property(
            visual, "position:z", -0.34, 0.08
        )
        tween.tween_property(
            visual, "position:z", 0.0, 0.14
        )

func take_hit(amount: int, direction: Vector3) -> void:
    health -= amount
    knockback += direction * 5.2
    if health <= 0:
        queue_free()
func _mat(color: Color, metallic := 0.0) -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.metallic = metallic
    mat.roughness = 0.78 if metallic < 0.5 else 0.32
    return mat

func _part(
    mesh: Mesh,
    pos: Vector3,
    mat: Material,
    parent: Node3D
) -> MeshInstance3D:
    var item := MeshInstance3D.new()
    item.mesh = mesh
    item.position = pos
    item.material_override = mat
    parent.add_child(item)
    return item

func _build_collision() -> void:
    var shape := CapsuleShape3D.new()
    shape.radius = 0.42
    shape.height = 1.8
    $CollisionShape3D.shape = shape

func _build_raider() -> void:
    var visual := Node3D.new()
    visual.name = "Visual"
    add_child(visual)
    var cloth := _mat(Color("522a2d"))
    var leather := _mat(Color("2d211f"))
    var skin := _mat(Color("9c6959"))
    var iron := _mat(Color("555d64"), 0.72)

    var torso := CapsuleMesh.new()
    torso.radius = 0.42
    torso.height = 1.08
    _part(torso, Vector3(0, 1.34, 0), cloth, visual)

    var head := SphereMesh.new()
    head.radius = 0.29
    head.height = 0.56
    _part(head, Vector3(0, 2.03, 0), skin, visual)

    var helm := CylinderMesh.new()
    helm.top_radius = 0.22
    helm.bottom_radius = 0.32
    helm.height = 0.25
    _part(helm, Vector3(0, 2.27, 0), iron, visual)

    for side in [-1.0, 1.0]:
        var leg := CapsuleMesh.new()
        leg.radius = 0.15
        leg.height = 0.9
        _part(
            leg,
            Vector3(side * 0.19, 0.51, 0),
            leather,
            visual
        )
