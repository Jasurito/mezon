"""First names used to tell a character's gender from ``char.<id>.name`` (Uzbek and Russian, both scripts).

Lowercase, the first word of the name only ("Малика Р." -> "малика"). A name that looks like a person's
("<Name> <Initial>.") but is missing here stops ``python -m app.tts build``: add it here or set ``voice`` on the
character in scenario.json.
"""

MALE_NAMES = frozenset({
    # Uzbek, Latin
    "abbos", "abdulaziz", "abdulla", "akmal", "alisher", "anvar", "aziz", "bahodir", "bekzod", "bobur", "davron",
    "dilshod", "doniyor", "eldor", "elyor", "farhod", "farrux", "hasan", "husan", "ibrohim", "ilhom", "islom",
    "jahongir", "jamshid", "jasur", "javlon", "kamol", "laziz", "mansur", "mirzo", "muhammad", "nodir", "oybek",
    "otabek", "rustam", "sanjar", "sardor", "sherzod", "shohruh", "sobir", "temur", "timur", "ulugʻbek", "ulug'bek",
    "umid", "xurshid", "yusuf", "zafar",
    # Uzbek / Russian, Cyrillic
    "аббос", "абдулазиз", "абдулла", "акмал", "алишер", "анвар", "азиз", "баходир", "бекзод", "бобур", "даврон",
    "дилшод", "дониёр", "элдор", "элёр", "фарход", "фаррух", "хасан", "хусан", "иброхим", "илхом", "ислом",
    "жахонгир", "джахонгир", "жамшид", "джамшид", "жасур", "жавлон", "камол", "лазиз", "мансур", "мирзо", "мухаммад",
    "нодир", "ойбек", "отабек", "рустам", "санжар", "сардор", "шерзод", "шохрух", "собир", "темур", "тимур",
    "улугбек", "умид", "хуршид", "юсуф", "зафар",
    # Russian
    "александр", "алексей", "андрей", "дмитрий", "иван", "игорь", "михаил", "николай", "павел", "сергей",
    "aleksandr", "aleksey", "andrey", "dmitriy", "ivan", "igor", "mixail", "nikolay", "pavel", "sergey",
})

FEMALE_NAMES = frozenset({
    # Uzbek, Latin
    "aziza", "barno", "dilfuza", "dildora", "dilnoza", "durdona", "feruza", "gulnora", "gulchehra", "kamola",
    "laylo", "lola", "madina", "malika", "mohinur", "munisa", "nargiza", "nasiba", "nigora", "nilufar", "nodira",
    "ozoda", "robiya", "rayhona", "sabina", "sevara", "shahnoza", "shoira", "umida", "yulduz", "zarina", "zebo",
    "zilola", "zuhra",
    # Uzbek / Russian, Cyrillic
    "азиза", "барно", "дилфуза", "дилдора", "дилноза", "дурдона", "феруза", "гулнора", "гулчехра", "камола",
    "лайло", "лола", "мадина", "малика", "мохинур", "муниса", "наргиза", "насиба", "нигора", "нилуфар", "нодира",
    "озода", "робия", "райхона", "сабина", "севара", "шахноза", "шоира", "умида", "юлдуз", "зарина", "зебо",
    "зилола", "зухра",
    # Russian
    "анна", "елена", "ирина", "мария", "наталья", "ольга", "светлана", "татьяна", "юлия",
    "anna", "yelena", "irina", "mariya", "natalya", "olga", "svetlana", "tatyana", "yuliya",
})

# Russian role nouns that are grammatically feminine. Only the FIRST word of the role text is checked:
# "Представитель ответчицы ..." is about someone else and must not make the character female.
FEMALE_ROLE_WORDS = frozenset({
    "истица", "ответчица", "покупательница", "заказчица", "продавщица", "свидетельница", "студентка",
    "представительница", "заявительница", "потребительница", "нанимательница", "арендаторша",
    "невеста", "мать", "дочь", "жена", "сестра", "бабушка",
})
MALE_ROLE_WORDS = frozenset({"жених", "отец", "сын", "муж", "брат", "дедушка"})
# kinship in parentheses describes the character itself: "Представитель ответчицы Зарины Х. (сын)"
FEMALE_KIN = frozenset({"дочь", "мать", "жена", "сестра", "бабушка", "qizi", "onasi", "xotini", "opasi", "singlisi"})
MALE_KIN = frozenset({"сын", "отец", "муж", "брат", "дедушка", "o'g'li", "oʻgʻli", "otasi", "eri", "akasi", "ukasi"})
