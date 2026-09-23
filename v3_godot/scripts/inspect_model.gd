extends SceneTree

func _init() -> void:
    var scene = load("res://assets/characters/viking/Viking_Male.glb")
    var root = scene.instantiate()
    _walk(root, 0)
    root.free()
    quit()

func _walk(node: Node, depth: int) -> void:
    if node is Node3D:
        print("  ".repeat(depth), node.name, " scale=", node.scale, " pos=", node.position)
    if node is MeshInstance3D and node.mesh:
        print("  ".repeat(depth), "AABB=", node.mesh.get_aabb())
    for child in node.get_children():
        _walk(child, depth + 1)
