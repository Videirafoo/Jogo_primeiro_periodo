extends CanvasLayer

var panel: PanelContainer
var title_label: Label
var body_label: Label
var footer_label: Label
var toast_label: Label
var toast_timer := 0.0
var mode := "pause"

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_menu()
	_build_toast()
	call_deferred("_bind_profile")

func _bind_profile() -> void:
	var profile := get_tree().get_first_node_in_group("game_profile")
	if not profile:
		return
	var cb := Callable(self, "_show_toast")
	if not profile.toast_requested.is_connected(cb):
		profile.toast_requested.connect(cb)

func _input(event: InputEvent) -> void:
	if not event is InputEventKey:
		return
	if not event.pressed or event.echo:
		return

	match event.keycode:
		KEY_ESCAPE:
			if panel.visible:
				_close()
			else:
				_open("pause")
			get_viewport().set_input_as_handled()
		KEY_J:
			_toggle_mode("journal")
			get_viewport().set_input_as_handled()
		KEY_M:
			_toggle_mode("map")
			get_viewport().set_input_as_handled()
		KEY_C:
			_toggle_mode("codex")
			get_viewport().set_input_as_handled()
		KEY_I:
			_toggle_mode("inventory")
			get_viewport().set_input_as_handled()
		KEY_F5:
			_save()
			get_viewport().set_input_as_handled()
		KEY_F9:
			_load()
			get_viewport().set_input_as_handled()

func _process(delta: float) -> void:
	if toast_timer > 0.0:
		toast_timer = maxf(0.0, toast_timer - delta)
		if toast_timer <= 0.0:
			toast_label.visible = false

func _toggle_mode(next_mode: String) -> void:
	if panel.visible and mode == next_mode:
		_close()
	else:
		_open(next_mode)

func _open(next_mode: String) -> void:
	mode = next_mode
	panel.visible = true
	get_tree().paused = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_refresh()

func _close() -> void:
	panel.visible = false
	get_tree().paused = false
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _refresh() -> void:
	var profile := get_tree().get_first_node_in_group("game_profile")
	var director := get_tree().get_first_node_in_group("game_director")

	match mode:
		"journal":
			title_label.text = "JORNAL // MISSÕES"
			var quests := get_tree().get_first_node_in_group(
				"quest_manager"
			)
			var optional: String = (
				str(quests.journal_text())
				if quests
				else "Nenhuma missão opcional registrada."
			)
			var reputation_text := ""
			if profile:
				reputation_text = (
					"

REPUTAÇÃO
"
					+ "Clãs Livres: %+d
" % int(profile.reputation["Clãs Livres"])
					+ "Círculo Rúnico: %+d
" % int(profile.reputation["Círculo Rúnico"])
					+ "Errantes do Vazio: %+d" % int(profile.reputation["Errantes do Vazio"])
				)
			if director:
				body_label.text = (
					"%s

%s
%s

Progresso: %s

"
					+ "MISSÕES OPCIONAIS
%s%s"
				) % [
					str(director.chapter_name),
					str(director.objective_title),
					str(director.objective_detail),
					str(director.objective_progress),
					optional,
					reputation_text
				]
		"map":
			title_label.text = "MAPA // AS SETE REGIÕES"
			body_label.text = profile.map_text() if profile else "Mapa indisponível."
		"codex":
			title_label.text = "CÓDICE // VALDRAK"
			body_label.text = profile.codex_text() if profile else "Códice indisponível."
		"inventory":
			title_label.text = "INVENTÁRIO // EQUIPAMENTOS"
			var header := ""
			if profile:
				header = "Nível %d   XP %d   Moedas %d

" % [
					profile.level,
					profile.xp,
					profile.coins
				]
				body_label.text = header + profile.inventory_text()
			else:
				body_label.text = "Inventário indisponível."
		_:
			title_label.text = "OS ETERNOS // PAUSA"
			body_label.text = (
				"CONTINUAR  —  Esc

"
				+ "J  Jornal de missões
"
				+ "M  Mapa das regiões
"
				+ "C  Códice
"
				+ "I  Inventário

"
				+ "F5  Salvar jogo
"
				+ "F9  Carregar jogo"
			)

	footer_label.text = "Esc fecha  •  J/M/C/I alternam telas"

func _save() -> void:
	var profile := get_tree().get_first_node_in_group("game_profile")
	if profile:
		profile.save_game()

func _load() -> void:
	var profile := get_tree().get_first_node_in_group("game_profile")
	if profile:
		profile.load_game()
func _build_menu() -> void:
	panel = PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.position = Vector2(-360, -260)
	panel.custom_minimum_size = Vector2(720, 520)

	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.012, 0.025, 0.032, 0.97)
	style.border_color = Color(0.20, 0.78, 0.82, 0.78)
	style.set_border_width_all(1)
	style.corner_radius_top_left = 14
	style.corner_radius_top_right = 14
	style.corner_radius_bottom_left = 14
	style.corner_radius_bottom_right = 14
	panel.add_theme_stylebox_override("panel", style)
	panel.visible = false
	add_child(panel)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 28)
	margin.add_theme_constant_override("margin_right", 28)
	margin.add_theme_constant_override("margin_top", 24)
	margin.add_theme_constant_override("margin_bottom", 24)
	panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 16)
	margin.add_child(box)

	title_label = Label.new()
	title_label.add_theme_font_size_override("font_size", 24)
	title_label.add_theme_color_override("font_color", Color("88f7ff"))
	box.add_child(title_label)

	var separator := HSeparator.new()
	box.add_child(separator)
	body_label = Label.new()
	body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body_label.custom_minimum_size = Vector2(650, 365)
	body_label.add_theme_font_size_override("font_size", 15)
	body_label.add_theme_color_override("font_color", Color("e9f3f5"))
	box.add_child(body_label)

	footer_label = Label.new()
	footer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	footer_label.add_theme_font_size_override("font_size", 11)
	footer_label.add_theme_color_override(
		"font_color",
		Color(0.65, 0.75, 0.78, 1.0)
	)
	box.add_child(footer_label)

func _build_toast() -> void:
	toast_label = Label.new()
	toast_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	toast_label.position = Vector2(-370, 78)
	toast_label.custom_minimum_size = Vector2(340, 42)
	toast_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	toast_label.add_theme_font_size_override("font_size", 13)
	toast_label.add_theme_color_override("font_color", Color("f4fcff"))

	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.02, 0.08, 0.095, 0.94)
	style.border_color = Color("66e9f2")
	style.set_border_width_all(1)
	style.corner_radius_top_left = 9
	style.corner_radius_top_right = 9
	style.corner_radius_bottom_left = 9
	style.corner_radius_bottom_right = 9
	toast_label.add_theme_stylebox_override("normal", style)
	toast_label.visible = false
	add_child(toast_label)

func _show_toast(text: String) -> void:
	toast_label.text = text
	toast_timer = 2.6
	toast_label.visible = true
