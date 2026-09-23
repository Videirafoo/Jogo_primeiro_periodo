extends Control

const WORLD_HALF := 95.0

var player: Node3D
var director: Node

var pois := [
	{"name":"VALDRAK","pos":Vector2(0,-6),"color":Color("f0c46a")},
	{"name":"FORJA","pos":Vector2(12,5),"color":Color("ff9e62")},
	{"name":"TAVERNA","pos":Vector2(-13,4),"color":Color("d8b46b")},
	{"name":"CRÔNICAS","pos":Vector2(-11,-10),"color":Color("b99cff")},
	{"name":"CORVOS","pos":Vector2(-44,-8),"color":Color("76d8ae")},
	{"name":"MASMORRA","pos":Vector2(-72,-24),"color":Color("a875ff")},
	{"name":"REGIÃO II","pos":Vector2(72,42),"color":Color("69e7f5")}
]

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	player = get_tree().get_first_node_in_group(
		"player"
	) as Node3D
	director = get_tree().get_first_node_in_group(
		"game_director"
	)
	queue_redraw()

func _process(_delta: float) -> void:
	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group(
			"player"
		) as Node3D
	queue_redraw()

func _draw() -> void:
	var rect := Rect2(
		Vector2.ZERO,
		size
	)
	draw_rect(
		rect,
		Color(0.015,0.03,0.035,0.88),
		true
	)
	draw_rect(
		rect,
		Color(0.22,0.72,0.76,0.55),
		false,
		1.0
	)

	var center := size * 0.5
	draw_circle(
		center,
		min(size.x,size.y) * 0.43,
		Color(0.07,0.12,0.12,0.72)
	)

	# Estradas principais.
	draw_line(
		_map(Vector2(0,58)),
		_map(Vector2(0,-35)),
		Color(0.46,0.39,0.28,0.72),
		4.0
	)
	draw_line(
		_map(Vector2(-44,-8)),
		_map(Vector2(0,-6)),
		Color(0.31,0.34,0.27,0.72),
		3.0
	)

	for poi in pois:
		if not _poi_visible(str(poi.name)):
			continue
		var pos := _map(poi.pos)
		draw_circle(
			pos,
			4.0,
			poi.color
		)
		draw_circle(
			pos,
			7.0,
			Color(
				poi.color.r,
				poi.color.g,
				poi.color.b,
				0.18
			),
			false,
			1.0
		)

	if not is_instance_valid(player):
		return
	if player.global_position.y > 14.0:
		return

	var player_pos := _map(
		Vector2(
			player.global_position.x,
			player.global_position.z
		)
	)
	draw_circle(
		player_pos,
		5.0,
		Color("eafcff")
	)

	var forward := -player.global_transform.basis.z
	var dir := Vector2(forward.x,forward.z).normalized()
	draw_line(
		player_pos,
		player_pos + dir * 11.0,
		Color("68f1ff"),
		2.0
	)

func _map(world: Vector2) -> Vector2:
	var normalized := Vector2(
		clampf(
			(world.x + WORLD_HALF)
			/ (WORLD_HALF * 2.0),
			0.0,
			1.0
		),
		clampf(
			(world.y + WORLD_HALF)
			/ (WORLD_HALF * 2.0),
			0.0,
			1.0
		)
	)
	return Vector2(
		normalized.x * size.x,
		normalized.y * size.y
	)

func _poi_visible(name: String) -> bool:
	if name == "CORVOS" or name == "MASMORRA":
		return director and int(director.phase_index) >= 3
	if name == "REGIÃO II":
		return director and int(director.phase_index) >= 6
	return true
