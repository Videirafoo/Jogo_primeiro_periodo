extends SceneTree

func _init() -> void:
    for path in [
        "res://assets/weapons/SimpleAxe.obj",
        "res://assets/environment/village/House_1.obj",
        "res://assets/environment/village/Blacksmith.obj",
        "res://assets/environment/village/Bonfire_Lit.obj"
    ]:
        var mesh = load(path) as Mesh
        print(path, " AABB=", mesh.get_aabb() if mesh else "null")
    quit()
