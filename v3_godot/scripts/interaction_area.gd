extends Area3D

@export var prompt_text := "Interagir"
@export var event_id := ""
@export var auto_trigger := false
@export var one_shot := false
@export var teleport_enabled := false
@export var target_position := Vector3.ZERO

var consumed := false

func _ready() -> void:
	add_to_group("interactables")
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node) -> void:
	if consumed:
		return
	if not body.is_in_group("player"):
		return

	if auto_trigger:
		_activate(body)
	elif body.has_method("set_interactable"):
		body.set_interactable(self)

func _on_body_exited(body: Node) -> void:
	if body.is_in_group("player"):
		if body.has_method("clear_interactable"):
			body.clear_interactable(self)
func interact(player: Node) -> void:
	if consumed:
		return
	_activate(player)

func _activate(player: Node) -> void:
	if teleport_enabled:
		if player.has_method("teleport_to"):
			player.teleport_to(target_position)
		elif player is Node3D:
			player.global_position = target_position

	if event_id != "":
		var director := get_tree().get_first_node_in_group(
			"game_director"
		)
		if director and director.has_method("handle_event"):
			director.handle_event(event_id)

	if one_shot:
		consumed = true
		monitoring = false
		monitorable = false
		if player.has_method("clear_interactable"):
			player.clear_interactable(self)
		visible = false

func get_prompt() -> String:
	if event_id == "blacksmith_talk":
		var director := get_tree().get_first_node_in_group(
			"game_director"
		)
		if director:
			match str(director.objective_id):
				"talk_eirik":
					return "Falar com Eirik"
				"collect_rune":
					return "Perguntar sobre a Runa Partida"
				"clear_village":
					return "Perguntar sobre os invasores"
				"reach_gate":
					return "Pedir conselho a Eirik"
				"defeat_boss":
					return "Perguntar sobre Jarl Vorun"
				"complete":
					return "Falar com Eirik"
	return prompt_text
