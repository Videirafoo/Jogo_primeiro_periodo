extends Node

signal dialogue_line(speaker: String, text: String)
signal choice_requested(
	character: String,
	prompt: String,
	options: Array
)
signal dialogue_closed()

const BIOS := {
	"Thorvald": {
		"role": "Guardião dos Clãs Livres",
		"intro": "Valdrak não pergunta de onde você veio. Pergunta o que fará quando alguém depender de você.",
		"color": "e8c27a"
	},
	"Aurel": {
		"role": "Cronista do Círculo Rúnico",
		"intro": "Seu telefone emite o mesmo padrão das runas antigas. Isso não deveria ser possível.",
		"color": "a98cff"
	},
	"Kaion": {
		"role": "Batedor das Fronteiras",
		"intro": "Todo mundo aqui procura uma porta de saída. Eu prefiro descobrir quem decidiu trancá-la.",
		"color": "6fe6b2"
	},
	"Brenor": {
		"role": "Ferreiro de Guerra",
		"intro": "Arma boa não escolhe o dono. O dono é que prova se merece continuar segurando-a.",
		"color": "f49a61"
	},
	"Eiran": {
		"role": "Curandeira dos Despertos",
		"intro": "Você trouxe medo do seu mundo nos olhos. Não tente escondê-lo. Em Valdrak, medo também deixa rastro.",
		"color": "80d8ff"
	},
	"Noctar": {
		"role": "Exilado do Vazio",
		"intro": "Você pensa que caiu dentro de um sonho. Talvez o seu mundo seja o sonho e Valdrak seja quem acordou.",
		"color": "d66cff"
	}
}

var current_character := ""
var awaiting_choice := false

func _ready() -> void:
	add_to_group("dialogue_manager")

func start(character: String) -> void:
	if not BIOS.has(character):
		return
	if awaiting_choice:
		return
	current_character = character
	var relationships := _relationships()
	if not relationships:
		return

	if not relationships.has_talked(character):
		relationships.mark_talked(character)
		dialogue_line.emit(
			"%s // %s" % [
				character.to_upper(),
				str(BIOS[character].role)
			],
			str(BIOS[character].intro)
		)
		await get_tree().create_timer(1.0).timeout
		_open_first_choice(character)
		return

	if relationships.recruited.has(character):
		_open_companion_choice(character)
		return

	if relationships.can_recruit(character):
		_open_recruit_choice(character)
		return

	_open_followup_choice(character)

func _open_first_choice(character: String) -> void:
	var options: Array = []
	match character:
		"Thorvald":
			options = [
				{"id":"duty","text":"Se alguém depender de mim, eu fico.","delta":2},
				{"id":"home","text":"Só quero encontrar o caminho de volta.","delta":0},
				{"id":"power","text":"Primeiro preciso ficar forte.","delta":-1}
			]
		"Aurel":
			options = [
				{"id":"truth","text":"Quero entender por que o celular reage às runas.","delta":2},
				{"id":"escape","text":"Só me diga como abrir a porta de saída.","delta":0},
				{"id":"hide","text":"Talvez seja melhor ninguém saber do telefone.","delta":-1}
			]
		"Kaion":
			options = [
				{"id":"hunt","text":"Vamos descobrir quem construiu as portas.","delta":2},
				{"id":"safe","text":"Prefiro uma rota segura.","delta":0},
				{"id":"alone","text":"Trabalho melhor sozinho.","delta":-1}
			]
		"Brenor":
			options = [
				{"id":"protect","text":"Quero uma arma para proteger quem não pode lutar.","delta":2},
				{"id":"survive","text":"Quero uma arma que me mantenha vivo.","delta":1},
				{"id":"strongest","text":"Quero a arma mais destrutiva que existir.","delta":-1}
			]
		"Eiran":
			options = [
				{"id":"listen","text":"Então me ensine a escutar esse medo.","delta":2},
				{"id":"fine","text":"Estou bem. Só preciso continuar.","delta":0},
				{"id":"weakness","text":"Medo é fraqueza. Não preciso dele.","delta":-1}
			]
		"Noctar":
			options = [
				{"id":"question","text":"Então prove que meu mundo não é real.","delta":2},
				{"id":"door","text":"Não importa. Preciso da Última Porta.","delta":0},
				{"id":"threat","text":"Se estiver brincando comigo, vai se arrepender.","delta":-2}
			]
	awaiting_choice = true
	choice_requested.emit(
		character,
		"Como responder?",
		options
	)

func _open_followup_choice(character: String) -> void:
	awaiting_choice = true
	choice_requested.emit(
		character,
		"Continuar a conversa",
		[
			{"id":"learn","text":"Conte mais sobre você e Valdrak.","delta":1},
			{"id":"mission","text":"O que posso fazer para ajudar?","delta":1},
			{"id":"leave","text":"Falamos depois.","delta":0}
		]
	)

func _open_recruit_choice(character: String) -> void:
	awaiting_choice = true
	choice_requested.emit(
		character,
		"%s parece disposto a acompanhar você." % character,
		[
			{"id":"recruit","text":"Venha comigo.","delta":1},
			{"id":"later","text":"Ainda não. Preciso pensar.","delta":0}
		]
	)

func _open_companion_choice(character: String) -> void:
	var relationships := _relationships()
	var active: bool = (
		str(relationships.active_companion) == character
	)
	awaiting_choice = true
	choice_requested.emit(
		character,
		"Companheiro recrutado",
		[
			{
				"id":"stay" if active else "follow",
				"text":"Fique aqui por enquanto." if active else "Venha comigo.",
				"delta":0
			},
			{"id":"talk","text":"Quero conversar.","delta":1}
		]
	)

func choose(index: int) -> void:
	if not awaiting_choice:
		return
	var relationships := _relationships()
	if not relationships:
		return
	var options := _current_options()
	if index < 0 or index >= options.size():
		return
	var option: Dictionary = options[index]
	var choice_id := str(option.get("id", ""))
	var delta := int(option.get("delta", 0))
	relationships.record_choice(
		current_character,
		choice_id,
		delta
	)

	awaiting_choice = false

	match choice_id:
		"recruit":
			if relationships.recruit(current_character):
				dialogue_line.emit(
					current_character.to_upper(),
					"Então seguimos juntos. Não espere que eu concorde com tudo."
				)
		"follow":
			relationships.set_active_companion(current_character)
			dialogue_line.emit(
				current_character.to_upper(),
				"Estou com você."
			)
		"stay":
			relationships.set_active_companion("")
			dialogue_line.emit(
				current_character.to_upper(),
				"Estarei aqui quando precisar."
			)
		"mission":
			_issue_character_quest(current_character)
		"talk":
			dialogue_line.emit(
				current_character.to_upper(),
				_affinity_line(current_character)
			)
		_:
			dialogue_line.emit(
				current_character.to_upper(),
				_reaction_line(
					current_character,
					choice_id,
					delta
				)
			)

	dialogue_closed.emit()

func _current_options() -> Array:
	# The HUD sends the original option back through choose_with_option.
	return []

func choose_with_option(option: Dictionary) -> void:
	if not awaiting_choice:
		return
	var relationships := _relationships()
	if not relationships:
		return
	var choice_id := str(option.get("id", ""))
	var delta := int(option.get("delta", 0))
	relationships.record_choice(
		current_character,
		choice_id,
		delta
	)
	awaiting_choice = false

	match choice_id:
		"recruit":
			if relationships.recruit(current_character):
				dialogue_line.emit(
					current_character.to_upper(),
					"Então seguimos juntos. Não espere que eu concorde com tudo."
				)
		"follow":
			relationships.set_active_companion(current_character)
			dialogue_line.emit(
				current_character.to_upper(),
				"Estou com você."
			)
		"stay":
			relationships.set_active_companion("")
			dialogue_line.emit(
				current_character.to_upper(),
				"Estarei aqui quando precisar."
			)
		"mission":
			_issue_character_quest(current_character)
		"talk":
			dialogue_line.emit(
				current_character.to_upper(),
				_affinity_line(current_character)
			)
		_:
			dialogue_line.emit(
				current_character.to_upper(),
				_reaction_line(
					current_character,
					choice_id,
					delta
				)
			)
	dialogue_closed.emit()

func _reaction_line(
	character: String,
	choice_id: String,
	delta: int
) -> String:
	if delta >= 2:
		return "Não é a resposta que eu esperava de alguém recém-chegado. Talvez eu tenha julgado você cedo demais."
	if delta == 1:
		return "Isso já é mais do que muitos em Valdrak estariam dispostos a fazer."
	if delta < 0:
		return "Cuidado. Em Valdrak, escolhas ruins costumam sobreviver a quem as fez."
	return "Entendo. Continue vivo o bastante e talvez mude de ideia."

func _affinity_line(character: String) -> String:
	var relationships := _relationships()
	var state: String = str(
		relationships.affinity_text(character)
	)
	return "Nossa relação agora é: %s. Ainda há muito que você não sabe sobre mim." % state

func _issue_character_quest(character: String) -> void:
	var quests := get_tree().get_first_node_in_group(
		"quest_manager"
	)
	if quests and quests.has_method("accept_character_quest"):
		quests.accept_character_quest(character)
	dialogue_line.emit(
		character.to_upper(),
		"Tenho algo que só alguém de fora talvez consiga resolver. Marquei no seu mapa."
	)

func _relationships() -> Node:
	return get_tree().get_first_node_in_group(
		"relationships"
	)
