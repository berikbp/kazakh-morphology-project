"""Common Kazakh suffixes and their allomorphs."""

PLURAL_ALLOMORPHS = {
    "back_vowel": ["лар", "дар", "тар"],
    "front_vowel": ["лер", "дер", "тер"],
}

PLURAL_SELECTORS = {
    "лар": "back_vowel",
    "лер": "front_vowel",
    "дар": "back_vowel",
    "дер": "front_vowel",
    "тар": "back_vowel",
    "тер": "front_vowel",
}

CASE_SUFFIX_MAP = {
    "nominative": "",
    "genitive": {"back": "ның", "front": "нің"},
    "dative": {"back": "ға", "front": "ге", "consonant_back": "қа", "consonant_front": "ке"},
    "accusative": {"back": "ны", "front": "ні"},
    "locative": {"back": "да", "front": "де", "consonant_back": "та", "consonant_front": "те"},
    "ablative": {"back": "дан", "front": "ден", "consonant_back": "тан", "consonant_front": "тен"},
    "instrumental": {"back": "мен", "front": "мен", "consonant_back": "пен", "consonant_front": "пен"},
}

POSSESSIVE_SUFFIXES = {
    "1sg": {"vowel": "мым", "consonant": "ым"},
    "2sg": {"vowel": "сың", "consonant": "ың"},
    "3sg": {"vowel": "ы", "consonant": "ы"},
    "1pl": {"vowel": "мыз", "consonant": "ымыз"},
    "2pl": {"vowel": "сыздар", "consonant": "ыңдар"},
    "3pl": {"vowel": "лары", "consonant": "тары"},
}

SUFFIX_ORDER = [
    "plural",
    "possessive",
    "case",
]
