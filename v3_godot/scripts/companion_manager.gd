extends Node

const ACTOR := preload("res://scripts/companion_actor.gd")

const CONFIG := {
	"Thorvald": {"model":2,"color":"e8c27a","damage":23},
	"Aurel": {"model":0,"color":"a98cff","damage":17},
	"Kaion": {"model":2,"color":"6fe6b2","damage":20},
	"Brenor": {"model":0,"color":"f49a61","damage":25},
	"Eiran": {"model":1,"color":"80d8ff","damage":15},
	"Noctar": {"model":2,"color":"d66cff","damage":22}
}

var actor: CharacterBody3D

func _ready() -> void:
	add_to_group("companion_manager")
	call_deferred("_bind_relationships")

func _bind_relationships() -> void:
	var relationships := get_tree().get_first_node_in_group(
		"relationships"
	)
	if not relationships:
		return
	var cb := Callable(self, "_on_companion_changed")
	if not relationships.companion_changed.is_connected(cb):
		relationships.companion_changed.connect(cb)
	if relationships.active_companion != "":
		_on_companion_changed(
			relationships.active_companion
		)

func _on_companion_changed(character: String) -> void:
	if is_instance_valid(actor):
		actor.queue_free()
		actor = null
	if character == "" or not CONFIG.has(character):
		return
	var player := get_tree().get_first_node_in_group(
		"player"
	) as Node3D
	if not player:
		return
	var cfg: Dictionary = CONFIG[character]
	actor = CharacterBody3D.new()
	actor.name = "Companion_%s" % character
	actor.set_script(ACTOR)
	actor.companion_name = character
	actor.model_key = int(cfg.model)
	actor.accent = Color(str(cfg.color))
	actor.attack_damage = int(cfg.damage)
	get_tree().current_scene.add_child(actor)
	actor.global_position = (
		player.global_position
		+ player.global_transform.basis.x * 1.5
		+ player.global_transform.basis.z * 1.8
	)
