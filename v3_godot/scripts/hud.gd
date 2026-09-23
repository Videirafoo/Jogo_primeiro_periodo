extends CanvasLayer

const MINIMAP := preload("res://scripts/minimap_control.gd")

var player: Node
var director: Node

var health_bar: ProgressBar
var health_label: Label
var stamina_bar: ProgressBar
var stamina_label: Label
var weapon_label: Label
var companion_label: Label

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

var transition_layer: Control
var transition_background: ColorRect
var transition_title: Label
var transition_subtitle: Label
var region_tag: Label

var choice_panel: PanelContainer
var choice_title: Label
var choice_buttons: Array[Button] = []
var choice_options: Array = []
var dialogue_manager: Node

func _ready() -> void:
	player = get_tree().get_first_node_in_group("player")
	director = get_tree().get_first_node_in_group("game_director")
	_build_status_panel()
	_build_target_panel()
	_build_objective_panel()
	_build_interaction_panel()
	_build_story_panel()
	_build_transition_layer()
	_build_crosshair()
	_build_region_tag()
	_build_minimap()
	_build_choice_panel()
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

	var transition_cb := Callable(
		self,
		"_on_transition_requested"
	)
	if not director.transition_requested.is_connected(
		transition_cb
	):
		director.transition_requested.connect(
			transition_cb
		)

	_bind_dialogue()
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
	_update_region_tag()

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

	if weapon_label and player.has_method("get_weapon_name"):
		weapon_label.text = "ARMA  %s" % player.get_weapon_name()

	if companion_label:
		var relationships := get_tree().get_first_node_in_group(
			"relationships"
		)
		if relationships and str(relationships.active_companion) != "":
			var companion := str(relationships.active_companion)
			companion_label.text = "ALIADO  %s // %s" % [
				companion.to_upper(),
				relationships.affinity_text(companion)
			]
		else:
			companion_label.text = "ALIADO  NENHUM"

func _build_status_panel() -> void:
	var panel := PanelContainer.new()
	panel.position = Vector2(22, 22)
	panel.custom_minimum_size = Vector2(340, 206)
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

	weapon_label = Label.new()
	weapon_label.text = "ARMA  SEM ARMA"
	weapon_label.add_theme_font_size_override("font_size", 11)
	weapon_label.add_theme_color_override(
		"font_color",
		Color("a8eff5")
	)
	box.add_child(weapon_label)

	companion_label = Label.new()
	companion_label.text = "ALIADO  NENHUM"
	companion_label.add_theme_font_size_override("font_size", 11)
	companion_label.add_theme_color_override(
		"font_color",
		Color("bfcbd0")
	)
	box.add_child(companion_label)

	var controls := Label.new()
	controls.text = "WASD mover • R interagir • T celular • F aparar • 1 espada • 2 machado • 3 martelo"
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
	region_tag = Label.new()
	region_tag.text = "MUNDO REAL  //  QUARTO"
	region_tag.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	region_tag.position = Vector2(-285, 24)
	region_tag.custom_minimum_size = Vector2(260, 32)
	region_tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	region_tag.add_theme_font_size_override("font_size", 13)
	region_tag.add_theme_color_override(
		"font_color",
		Color("d9fbff")
	)
	add_child(region_tag)

func _update_region_tag() -> void:
	if not region_tag or not is_instance_valid(player):
		return
	if director and int(director.phase_index) < 0:
		region_tag.text = "MUNDO REAL  //  QUARTO"
	elif player.global_position.y > 14.0:
		region_tag.text = "VALDRAK  //  INTERIOR"
	else:
		region_tag.text = "VALDRAK  //  REGIÃO I"
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

func _build_transition_layer() -> void:
	transition_layer = Control.new()
	transition_layer.set_anchors_preset(
		Control.PRESET_FULL_RECT
	)
	transition_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	transition_layer.visible = false
	add_child(transition_layer)

	transition_background = ColorRect.new()
	transition_background.set_anchors_preset(
		Control.PRESET_FULL_RECT
	)
	transition_background.color = Color(0.01, 0.015, 0.02, 0.0)
	transition_background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	transition_layer.add_child(transition_background)

	transition_title = Label.new()
	transition_title.set_anchors_preset(Control.PRESET_CENTER)
	transition_title.position = Vector2(-260, -42)
	transition_title.custom_minimum_size = Vector2(520, 48)
	transition_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	transition_title.add_theme_font_size_override("font_size", 27)
	transition_title.add_theme_color_override(
		"font_color",
		Color("dffbff")
	)
	transition_layer.add_child(transition_title)

	transition_subtitle = Label.new()
	transition_subtitle.set_anchors_preset(Control.PRESET_CENTER)
	transition_subtitle.position = Vector2(-340, 14)
	transition_subtitle.custom_minimum_size = Vector2(680, 70)
	transition_subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	transition_subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	transition_subtitle.add_theme_font_size_override("font_size", 14)
	transition_subtitle.add_theme_color_override(
		"font_color",
		Color(0.72, 0.84, 0.86, 1.0)
	)
	transition_layer.add_child(transition_subtitle)
func _on_transition_requested(
	title: String,
	subtitle: String,
	duration: float
) -> void:
	transition_title.text = title
	transition_subtitle.text = subtitle
	transition_layer.visible = true
	transition_layer.modulate = Color(1, 1, 1, 1)

	var tween := create_tween()
	tween.tween_property(
		transition_background,
		"color",
		Color(0.01, 0.015, 0.02, 0.97),
		0.55
	)
	tween.tween_interval(maxf(0.4, duration - 1.2))
	tween.tween_property(
		transition_layer,
		"modulate",
		Color(1, 1, 1, 0),
		0.65
	)
	tween.tween_callback(
		func():
			transition_layer.visible = false
			transition_background.color = Color(
				0.01,
				0.015,
				0.02,
				0.0
			)
			transition_layer.modulate = Color.WHITE
	)


func _build_minimap() -> void:
	var minimap := Control.new()
	minimap.name = "Minimap"
	minimap.set_script(MINIMAP)
	minimap.set_anchors_preset(
		Control.PRESET_TOP_RIGHT
	)
	minimap.position = Vector2(-216, 58)
	minimap.custom_minimum_size = Vector2(180, 180)
	add_child(minimap)

func _build_choice_panel() -> void:
	choice_panel = PanelContainer.new()
	choice_panel.set_anchors_preset(
		Control.PRESET_CENTER
	)
	choice_panel.position = Vector2(-360, -110)
	choice_panel.custom_minimum_size = Vector2(720, 220)
	choice_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(
			Color(0.012, 0.024, 0.030, 0.98)
		)
	)
	choice_panel.visible = false
	add_child(choice_panel)

	var margin := _margin(20, 20, 18, 18)
	choice_panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override(
		"separation",
		10
	)
	margin.add_child(box)

	choice_title = Label.new()
	choice_title.text = "ESCOLHA"
	choice_title.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)
	choice_title.add_theme_font_size_override(
		"font_size",
		18
	)
	choice_title.add_theme_color_override(
		"font_color",
		Color("89f2ff")
	)
	box.add_child(choice_title)

	for i in range(3):
		var button := Button.new()
		button.text = "%d. ..." % (i + 1)
		button.custom_minimum_size = Vector2(
			660,
			42
		)
		button.add_theme_font_size_override(
			"font_size",
			14
		)
		button.pressed.connect(
			func(index := i):
				_select_dialogue_choice(index)
		)
		choice_buttons.append(button)
		box.add_child(button)

func _bind_dialogue() -> void:
	dialogue_manager = get_tree().get_first_node_in_group(
		"dialogue_manager"
	)
	if not dialogue_manager:
		return

	var line_cb := Callable(
		self,
		"_on_dialogue_line"
	)
	if not dialogue_manager.dialogue_line.is_connected(
		line_cb
	):
		dialogue_manager.dialogue_line.connect(
			line_cb
		)

	var choice_cb := Callable(
		self,
		"_on_choice_requested"
	)
	if not dialogue_manager.choice_requested.is_connected(
		choice_cb
	):
		dialogue_manager.choice_requested.connect(
			choice_cb
		)

	var close_cb := Callable(
		self,
		"_on_dialogue_closed"
	)
	if not dialogue_manager.dialogue_closed.is_connected(
		close_cb
	):
		dialogue_manager.dialogue_closed.connect(
			close_cb
		)

func _on_dialogue_line(
	speaker: String,
	text: String
) -> void:
	_on_story_message(
		speaker,
		text,
		6.0
	)

func _on_choice_requested(
	character: String,
	prompt: String,
	options: Array
) -> void:
	choice_options = options.duplicate(true)
	choice_title.text = "%s // %s" % [
		character.to_upper(),
		prompt
	]
	for i in range(choice_buttons.size()):
		var button := choice_buttons[i]
		if i < choice_options.size():
			button.visible = true
			button.disabled = false
			button.text = "%d. %s" % [
				i + 1,
				str(choice_options[i].get(
					"text",
					"..."
				))
			]
		else:
			button.visible = false
			button.disabled = true
	choice_panel.visible = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _select_dialogue_choice(index: int) -> void:
	if not choice_panel.visible:
		return
	if index < 0 or index >= choice_options.size():
		return
	if not dialogue_manager:
		return
	var option: Dictionary = choice_options[index]
	choice_panel.visible = false
	dialogue_manager.choose_with_option(option)
	choice_options.clear()
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _on_dialogue_closed() -> void:
	if choice_panel.visible:
		return
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
	if not choice_panel or not choice_panel.visible:
		return
	if not event is InputEventKey:
		return
	if not event.pressed or event.echo:
		return
	match event.physical_keycode:
		KEY_1:
			_select_dialogue_choice(0)
		KEY_2:
			_select_dialogue_choice(1)
		KEY_3:
			_select_dialogue_choice(2)
