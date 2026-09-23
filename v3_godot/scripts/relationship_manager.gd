extends Node

signal affinity_changed(character: String, value: int)
signal companion_changed(character: String)
signal choice_recorded(character: String, choice_id: String)

const CHARACTERS := [
	"Thorvald",
	"Aurel",
	"Kaion",
	"Brenor",
	"Eiran",
	"Noctar"
]

var affinity := {
	"Thorvald": 0,
	"Aurel": 0,
	"Kaion": 0,
	"Brenor": 0,
	"Eiran": 0,
	"Noctar": 0
}
var talked: Array[String] = []
var recruited: Array[String] = []
var choice_history: Array[Dictionary] = []
var active_companion := ""

func _ready() -> void:
	add_to_group("relationships")

func add_affinity(character: String, amount: int) -> int:
	if not affinity.has(character):
		return 0
	affinity[character] = clampi(
		int(affinity[character]) + amount,
		-10,
		10
	)
	affinity_changed.emit(character, int(affinity[character]))
	return int(affinity[character])

func mark_talked(character: String) -> void:
	if not talked.has(character):
		talked.append(character)

func has_talked(character: String) -> bool:
	return talked.has(character)

func record_choice(
	character: String,
	choice_id: String,
	affinity_delta: int
) -> void:
	add_affinity(character, affinity_delta)
	choice_history.append({
		"character": character,
		"choice": choice_id,
		"affinity_delta": affinity_delta
	})
	choice_recorded.emit(character, choice_id)

func can_recruit(character: String) -> bool:
	return (
		affinity.has(character)
		and int(affinity[character]) >= 2
	)

func recruit(character: String) -> bool:
	if not can_recruit(character):
		return false
	if not recruited.has(character):
		recruited.append(character)
	active_companion = character
	companion_changed.emit(character)
	return true

func set_active_companion(character: String) -> bool:
	if character == "":
		active_companion = ""
		companion_changed.emit("")
		return true
	if not recruited.has(character):
		return false
	active_companion = character
	companion_changed.emit(character)
	return true

func affinity_text(character: String) -> String:
	if not affinity.has(character):
		return "DESCONHECIDO"
	var value := int(affinity[character])
	if value >= 7:
		return "LEAL"
	if value >= 4:
		return "ALIADO"
	if value >= 2:
		return "CONFIANÇA"
	if value <= -4:
		return "HOSTIL"
	if value <= -2:
		return "DESCONFIADO"
	return "NEUTRO"

func export_state() -> Dictionary:
	return {
		"affinity": affinity.duplicate(true),
		"talked": talked.duplicate(),
		"recruited": recruited.duplicate(),
		"choice_history": choice_history.duplicate(true),
		"active_companion": active_companion
	}

func import_state(value) -> void:
	if not value is Dictionary:
		return
	var loaded_affinity = value.get("affinity", {})
	if loaded_affinity is Dictionary:
		for character in CHARACTERS:
			if loaded_affinity.has(character):
				affinity[character] = int(
					loaded_affinity[character]
				)
	talked = _string_array(value.get("talked", []))
	recruited = _string_array(value.get("recruited", []))
	var loaded_history = value.get("choice_history", [])
	choice_history.clear()
	if loaded_history is Array:
		for entry in loaded_history:
			if entry is Dictionary:
				choice_history.append(entry.duplicate(true))
	active_companion = str(
		value.get("active_companion", "")
	)
	if active_companion != "":
		call_deferred(
			"_emit_loaded_companion"
		)

func _emit_loaded_companion() -> void:
	companion_changed.emit(active_companion)

func _string_array(value) -> Array[String]:
	var result: Array[String] = []
	if value is Array:
		for entry in value:
			result.append(str(entry))
	return result
