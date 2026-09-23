extends CanvasLayer

var player: Node
var health_bar: ProgressBar
var health_label: Label

func _ready() -> void:
    player = get_tree().get_first_node_in_group("player")
    _build_status_panel()
    _build_crosshair()
    _build_region_tag()

func _process(_delta: float) -> void:
    if not is_instance_valid(player):
        player = get_tree().get_first_node_in_group("player")
        return
    if "health" in player:
        var hp := int(player.health)
        health_bar.value = hp
        health_label.text = "VIDA  %03d / 120" % hp

func _build_status_panel() -> void:
    var panel := PanelContainer.new()
    panel.position = Vector2(22, 22)
    panel.custom_minimum_size = Vector2(300, 116)
    var style := StyleBoxFlat.new()
    style.bg_color = Color(0.025, 0.045, 0.055, 0.90)
    style.border_color = Color(0.20, 0.78, 0.82, 0.72)
    style.set_border_width_all(1)
    style.corner_radius_top_left = 10
    style.corner_radius_top_right = 10
    style.corner_radius_bottom_left = 10
    style.corner_radius_bottom_right = 10
    panel.add_theme_stylebox_override("panel", style)
    add_child(panel)

    var margin := MarginContainer.new()
    margin.add_theme_constant_override("margin_left", 16)
    margin.add_theme_constant_override("margin_right", 16)
    margin.add_theme_constant_override("margin_top", 12)
    margin.add_theme_constant_override("margin_bottom", 12)
    panel.add_child(margin)

    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 7)
    margin.add_child(box)

    var title := Label.new()
    title.text = "OS ETERNOS  //  V3"
    title.add_theme_font_size_override("font_size", 18)
    title.add_theme_color_override("font_color", Color("88f7ff"))
    box.add_child(title)
    health_label = Label.new()
    health_label.text = "VIDA  120 / 120"
    health_label.add_theme_font_size_override("font_size", 13)
    health_label.add_theme_color_override("font_color", Color("e8fbff"))
    box.add_child(health_label)

    health_bar = ProgressBar.new()
    health_bar.max_value = 120
    health_bar.value = 120
    health_bar.show_percentage = false
    health_bar.custom_minimum_size = Vector2(260, 10)
    box.add_child(health_bar)

    var controls := Label.new()
    controls.text = "WASD mover  •  SHIFT correr  •  E atacar  •  SPACE esquiva"
    controls.add_theme_font_size_override("font_size", 11)
    controls.add_theme_color_override("font_color", Color(0.70, 0.80, 0.83, 1.0))
    box.add_child(controls)

func _build_crosshair() -> void:
    var cross := Label.new()
    cross.text = "•"
    cross.set_anchors_preset(Control.PRESET_CENTER)
    cross.position = Vector2(-4, -15)
    cross.add_theme_font_size_override("font_size", 22)
    cross.add_theme_color_override("font_color", Color(0.76, 0.98, 1.0, 0.90))
    add_child(cross)

func _build_region_tag() -> void:
    var tag := Label.new()
    tag.text = "VALDRAK  //  VERTICAL SLICE"
    tag.set_anchors_preset(Control.PRESET_TOP_RIGHT)
    tag.position = Vector2(-260, 24)
    tag.custom_minimum_size = Vector2(235, 32)
    tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    tag.add_theme_font_size_override("font_size", 13)
    tag.add_theme_color_override("font_color", Color("d9fbff"))
    add_child(tag)
