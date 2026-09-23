extends SceneTree

func _init() -> void:
    var scene = load("res://assets/characters/viking/Viking_Male.glb")
    if scene == null:
        print("LOAD_FAILED")
        quit(1)
        return
    var root = scene.instantiate()
    print("ROOT:", root.name)
    _walk(root, 0)
    quit()

func _walk(node: Node, depth: int) -> void:
    print("  ".repeat(depth), node.name, " [", node.get_class(), "]")
    if node is AnimationPlayer:
        print("ANIMS:", node.get_animation_list())
    for child in node.get_children():
        _walk(child, depth + 1)
