extends CanvasLayer

var player: Node
var health_bar: ProgressBar
var health_label: Label
var stamina_bar: ProgressBar
var stamina_label: Label
var target_panel: PanelContainer
var target_bar: ProgressBar
var target_label: Label
var lock_hint: Label
var objective_label: Label

func _ready() -> void:
	player = get_tree().get_first_node_in_group("player")
	_build_status_panel()
	_build_target_panel()
	_build_crosshair()
	_build_region_tag()
	_build_objective()

func _process(_delta: float) -> void:
	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group("player")
		return

	var hp := int(player.health)
	health_bar.value = hp
	health_label.text = "VIDA  %03d / 120" % hp

	var stamina := float(player.stamina)
	stamina_bar.value = stamina
	stamina_label.text = "FÔLEGO  %03d / 100" % int(stamina)
	_update_target()
	_update_objective()
func _build_status_panel() -> void:
	var panel := PanelContainer.new()
	panel.position = Vector2(22, 22)
	panel.custom_minimum_size = Vector2(330, 160)
	panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.025, 0.045, 0.055, 0.92))
	)
	add_child(panel)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 16)
	margin.add_theme_constant_override("margin_right", 16)
	margin.add_theme_constant_override("margin_top", 12)
	margin.add_theme_constant_override("margin_bottom", 12)
	panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	margin.add_child(box)

	var title := Label.new()
	title.text = "OS ETERNOS  //  V3"
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", Color("88f7ff"))
	box.add_child(title)

	health_label = Label.new()
	health_label.text = "VIDA  120 / 120"
	health_label.add_theme_font_size_override("font_size", 12)
	box.add_child(health_label)
	health_bar = ProgressBar.new()
	health_bar.max_value = 120
	health_bar.value = 120
	health_bar.show_percentage = false
	health_bar.custom_minimum_size = Vector2(290, 9)
	_style_bar(health_bar, Color("55e6f0"))
	box.add_child(health_bar)

	stamina_label = Label.new()
	stamina_label.text = "FÔLEGO  100 / 100"
	stamina_label.add_theme_font_size_override("font_size", 12)
	box.add_child(stamina_label)

	stamina_bar = ProgressBar.new()
	stamina_bar.max_value = 100
	stamina_bar.value = 100
	stamina_bar.show_percentage = false
	stamina_bar.custom_minimum_size = Vector2(290, 8)
	_style_bar(stamina_bar, Color("e7b65c"))
	box.add_child(stamina_bar)

	var controls := Label.new()
	controls.text = "E/CLICK combo  •  F pesado  •  Q lock  •  SPACE esquiva"
	controls.add_theme_font_size_override("font_size", 10)
	controls.add_theme_color_override(
		"font_color",
		Color(0.70, 0.80, 0.83, 1.0)
	)
	box.add_child(controls)
func _build_target_panel() -> void:
	target_panel = PanelContainer.new()
	target_panel.set_anchors_preset(Control.PRESET_CENTER_TOP)
	target_panel.position = Vector2(-210, 24)
	target_panel.custom_minimum_size = Vector2(420, 68)
	target_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.035, 0.025, 0.045, 0.92))
	)
	target_panel.visible = false
	add_child(target_panel)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 14)
	margin.add_theme_constant_override("margin_right", 14)
	margin.add_theme_constant_override("margin_top", 9)
	margin.add_theme_constant_override("margin_bottom", 9)
	target_panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 5)
	margin.add_child(box)

	target_label = Label.new()
	target_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	target_label.add_theme_font_size_override("font_size", 14)
	target_label.add_theme_color_override(
		"font_color",
		Color("ffb6be")
	)
	box.add_child(target_label)
	target_bar = ProgressBar.new()
	target_bar.max_value = 100
	target_bar.value = 100
	target_bar.show_percentage = false
	target_bar.custom_minimum_size = Vector2(390, 10)
	_style_bar(target_bar, Color("ff5d67"))
	box.add_child(target_bar)

	lock_hint = Label.new()
	lock_hint.text = "ALVO TRAVADO  //  Q PARA LIBERAR"
	lock_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lock_hint.add_theme_font_size_override("font_size", 9)
	lock_hint.add_theme_color_override(
		"font_color",
		Color(0.68, 0.72, 0.78, 1.0)
	)
	box.add_child(lock_hint)

func _update_target() -> void:
	var target: Node = player.lock_target
	if not is_instance_valid(target):
		target_panel.visible = false
		return

	target_panel.visible = true
	target_bar.max_value = int(target.max_health)
	target_bar.value = int(target.health)
	target_label.text = "%s  //  %d / %d" % [
		str(target.display_name),
		int(target.health),
		int(target.max_health)
	]
	if bool(target.boss):
		target_label.add_theme_color_override(
			"font_color",
			Color("e5a7ff")
		)
		_style_bar(target_bar, Color("c56cff"))
	else:
		target_label.add_theme_color_override(
			"font_color",
			Color("ffb6be")
		)
		_style_bar(target_bar, Color("ff5d67"))

func _build_crosshair() -> void:
	var cross := Label.new()
	cross.text = "•"
	cross.set_anchors_preset(Control.PRESET_CENTER)
	cross.position = Vector2(-4, -15)
	cross.add_theme_font_size_override("font_size", 22)
	cross.add_theme_color_override(
		"font_color",
		Color(0.76, 0.98, 1.0, 0.90)
	)
	add_child(cross)

func _build_region_tag() -> void:
	var tag := Label.new()
	tag.text = "VALDRAK  //  VERTICAL SLICE"
	tag.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	tag.position = Vector2(-260, 24)
	tag.custom_minimum_size = Vector2(235, 32)
	tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	tag.add_theme_font_size_override("font_size", 13)
	tag.add_theme_color_override(
		"font_color",
		Color("d9fbff")
	)
	add_child(tag)

func _panel_style(background: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = Color(0.20, 0.78, 0.82, 0.68)
	style.set_border_width_all(1)
	style.corner_radius_top_left = 10
	style.corner_radius_top_right = 10
	style.corner_radius_bottom_left = 10
	style.corner_radius_bottom_right = 10
	return style

func _style_bar(bar: ProgressBar, fill_color: Color) -> void:
	var background := StyleBoxFlat.new()
	background.bg_color = Color(0.10, 0.13, 0.14, 0.95)
	background.corner_radius_top_left = 4
	background.corner_radius_top_right = 4
	background.corner_radius_bottom_left = 4
	background.corner_radius_bottom_right = 4
	bar.add_theme_stylebox_override("background", background)

	var fill := StyleBoxFlat.new()
	fill.bg_color = fill_color
	fill.corner_radius_top_left = 4
	fill.corner_radius_top_right = 4
	fill.corner_radius_bottom_left = 4
	fill.corner_radius_bottom_right = 4
	bar.add_theme_stylebox_override("fill", fill)

func _build_objective() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	panel.position = Vector2(22, -92)
	panel.custom_minimum_size = Vector2(410, 64)
	panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.025, 0.045, 0.055, 0.88))
	)
	add_child(panel)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 14)
	margin.add_theme_constant_override("margin_right", 14)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	panel.add_child(margin)

	objective_label = Label.new()
	objective_label.text = "OBJETIVO // atravesse Valdrak e encontre o Jarl"
	objective_label.add_theme_font_size_override("font_size", 12)
	objective_label.add_theme_color_override(
		"font_color",
		Color("d8f9ff")
	)
	margin.add_child(objective_label)

func _update_objective() -> void:
	if not objective_label:
		return
	var enemies := get_tree().get_nodes_in_group("enemies")
	var bosses := get_tree().get_nodes_in_group("bosses")
	if bosses.is_empty():
		objective_label.text = "OBJETIVO CONCLUÍDO // Valdrak está livre"
		return
	var regular := maxi(0, enemies.size() - bosses.size())
	objective_label.text = "OBJETIVO // %d inimigos restantes  •  derrote JARL VORUN" % regular
