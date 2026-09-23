extends CanvasLayer

var player: Node
var director: Node

var health_bar: ProgressBar
var health_label: Label
var stamina_bar: ProgressBar
var stamina_label: Label

var target_panel: PanelContainer
var target_bar: ProgressBar
var target_label: Label

var chapter_label: Label
var objective_title: Label
var objective_detail: Label
var objective_progress: Label

var interaction_panel: PanelContainer
var interaction_label: Label

var story_panel: PanelContainer
var story_speaker: Label
var story_text: Label
var story_timer := 0.0

func _ready() -> void:
	player = get_tree().get_first_node_in_group("player")
	director = get_tree().get_first_node_in_group("game_director")
	_build_status_panel()
	_build_target_panel()
	_build_objective_panel()
	_build_interaction_panel()
	_build_story_panel()
	_build_crosshair()
	_build_region_tag()
	call_deferred("_bind_director")
func _bind_director() -> void:
	director = get_tree().get_first_node_in_group("game_director")
	if not director:
		return

	var objective_cb := Callable(self, "_on_objective_changed")
	if not director.objective_changed.is_connected(objective_cb):
		director.objective_changed.connect(objective_cb)

	var story_cb := Callable(self, "_on_story_message")
	if not director.story_message.is_connected(story_cb):
		director.story_message.connect(story_cb)

	_on_objective_changed(
		str(director.chapter_name),
		str(director.objective_title),
		str(director.objective_detail),
		str(director.objective_progress)
	)

func _process(delta: float) -> void:
	if not is_instance_valid(player):
		player = get_tree().get_first_node_in_group("player")
		return

	_update_player_status()
	_update_target()
	_update_interaction()

	if story_timer > 0.0:
		story_timer = maxf(0.0, story_timer - delta)
		if story_timer <= 0.0:
			story_panel.visible = false
func _update_player_status() -> void:
	var hp := int(player.health)
	health_bar.value = hp
	health_label.text = "VIDA  %03d / 120" % hp

	var stamina := float(player.stamina)
	stamina_bar.value = stamina
	stamina_label.text = "FÔLEGO  %03d / 100" % int(stamina)

func _build_status_panel() -> void:
	var panel := PanelContainer.new()
	panel.position = Vector2(22, 22)
	panel.custom_minimum_size = Vector2(340, 164)
	panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.018, 0.035, 0.045, 0.94))
	)
	add_child(panel)

	var margin := _margin(16, 16, 12, 12)
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
	health_bar.custom_minimum_size = Vector2(300, 9)
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
	stamina_bar.custom_minimum_size = Vector2(300, 8)
	_style_bar(stamina_bar, Color("e7b65c"))
	box.add_child(stamina_bar)

	var controls := Label.new()
	controls.text = "WASD mover  •  SHIFT correr  •  R interagir  •  T celular  •  Q lock"
	controls.add_theme_font_size_override("font_size", 10)
	controls.add_theme_color_override(
		"font_color",
		Color(0.68, 0.78, 0.82, 1.0)
	)
	box.add_child(controls)
func _build_target_panel() -> void:
	target_panel = PanelContainer.new()
	target_panel.set_anchors_preset(Control.PRESET_CENTER_TOP)
	target_panel.position = Vector2(-220, 22)
	target_panel.custom_minimum_size = Vector2(440, 70)
	target_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.035, 0.022, 0.04, 0.93))
	)
	target_panel.visible = false
	add_child(target_panel)

	var margin := _margin(14, 14, 9, 9)
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
	target_bar.custom_minimum_size = Vector2(410, 10)
	_style_bar(target_bar, Color("ff5d67"))
	box.add_child(target_bar)
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

func _build_objective_panel() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	panel.position = Vector2(22, -152)
	panel.custom_minimum_size = Vector2(500, 126)
	panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.018, 0.035, 0.045, 0.93))
	)
	add_child(panel)
	var margin := _margin(16, 16, 12, 12)
	panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 4)
	margin.add_child(box)

	chapter_label = Label.new()
	chapter_label.text = "CAPÍTULO I // A CHEGADA"
	chapter_label.add_theme_font_size_override("font_size", 10)
	chapter_label.add_theme_color_override(
		"font_color",
		Color("77dce6")
	)
	box.add_child(chapter_label)

	objective_title = Label.new()
	objective_title.text = "Siga a fumaça"
	objective_title.add_theme_font_size_override("font_size", 16)
	objective_title.add_theme_color_override(
		"font_color",
		Color("eafcff")
	)
	box.add_child(objective_title)

	objective_detail = Label.new()
	objective_detail.text = "Alcance a fogueira no centro de Valdrak."
	objective_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	objective_detail.custom_minimum_size = Vector2(440, 34)
	objective_detail.add_theme_font_size_override("font_size", 11)
	objective_detail.add_theme_color_override(
		"font_color",
		Color(0.76, 0.84, 0.86, 1.0)
	)
	box.add_child(objective_detail)

	objective_progress = Label.new()
	objective_progress.text = "0 / 1"
	objective_progress.add_theme_font_size_override("font_size", 10)
	objective_progress.add_theme_color_override(
		"font_color",
		Color("e7b65c")
	)
	box.add_child(objective_progress)
func _on_objective_changed(
	chapter: String,
	title: String,
	detail: String,
	progress: String
) -> void:
	chapter_label.text = chapter
	objective_title.text = title
	objective_detail.text = detail
	objective_progress.text = progress

func _build_interaction_panel() -> void:
	interaction_panel = PanelContainer.new()
	interaction_panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	interaction_panel.position = Vector2(-225, -72)
	interaction_panel.custom_minimum_size = Vector2(450, 48)
	interaction_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.025, 0.055, 0.065, 0.94))
	)
	interaction_panel.visible = false
	add_child(interaction_panel)

	var margin := _margin(14, 14, 8, 8)
	interaction_panel.add_child(margin)

	interaction_label = Label.new()
	interaction_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	interaction_label.add_theme_font_size_override("font_size", 13)
	interaction_label.add_theme_color_override(
		"font_color",
		Color("aaf8ff")
	)
	margin.add_child(interaction_label)

func _update_interaction() -> void:
	var prompt := ""
	if player.has_method("get_interaction_prompt"):
		prompt = player.get_interaction_prompt()

	interaction_panel.visible = prompt != ""
	if prompt != "":
		interaction_label.text = "[ R ]  %s" % prompt
func _build_story_panel() -> void:
	story_panel = PanelContainer.new()
	story_panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	story_panel.position = Vector2(-360, -205)
	story_panel.custom_minimum_size = Vector2(720, 96)
	story_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.015, 0.02, 0.025, 0.95))
	)
	story_panel.visible = false
	add_child(story_panel)

	var margin := _margin(18, 18, 12, 12)
	story_panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 5)
	margin.add_child(box)

	story_speaker = Label.new()
	story_speaker.add_theme_font_size_override("font_size", 11)
	story_speaker.add_theme_color_override(
		"font_color",
		Color("7fefff")
	)
	box.add_child(story_speaker)

	story_text = Label.new()
	story_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	story_text.custom_minimum_size = Vector2(675, 42)
	story_text.add_theme_font_size_override("font_size", 15)
	story_text.add_theme_color_override(
		"font_color",
		Color("f0f4f5")
	)
	box.add_child(story_text)
func _on_story_message(
	speaker: String,
	text: String,
	duration: float
) -> void:
	story_speaker.text = speaker
	story_text.text = text
	story_timer = duration
	story_panel.visible = true

func _build_crosshair() -> void:
	var cross := Label.new()
	cross.text = "•"
	cross.set_anchors_preset(Control.PRESET_CENTER)
	cross.position = Vector2(-4, -15)
	cross.add_theme_font_size_override("font_size", 22)
	cross.add_theme_color_override(
		"font_color",
		Color(0.76, 0.98, 1.0, 0.88)
	)
	add_child(cross)

func _build_region_tag() -> void:
	var tag := Label.new()
	tag.text = "VALDRAK  //  REGIÃO I"
	tag.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	tag.position = Vector2(-250, 24)
	tag.custom_minimum_size = Vector2(225, 32)
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
	style.border_color = Color(0.20, 0.78, 0.82, 0.62)
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

func _margin(
	left: int,
	right: int,
	top: int,
	bottom: int
) -> MarginContainer:
	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", left)
	margin.add_theme_constant_override("margin_right", right)
	margin.add_theme_constant_override("margin_top", top)
	margin.add_theme_constant_override("margin_bottom", bottom)
	return margin
