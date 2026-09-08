"""Vowel harmony checker for Kazakh morphology."""

from enum import Enum


class HarmonyClass(Enum):
    BACK = "back"
    FRONT = "front"
    MIXED = "mixed"
    UNKNOWN = "unknown"


BACK_VOWELS = set("аоұыэ")
FRONT_VOWELS = set("еиіөү")


def classify_vowel(vowel: str) -> HarmonyClass:
    v = vowel.lower()
    if v in BACK_VOWELS:
        return HarmonyClass.BACK
    elif v in FRONT_VOWELS:
        return HarmonyClass.FRONT
    return HarmonyClass.UNKNOWN


def get_vowel_harmony_class(word: str) -> HarmonyClass:
    vowels = [c for c in word if classify_vowel(c) != HarmonyClass.UNKNOWN]
    if not vowels:
        return HarmonyClass.UNKNOWN

    classes = {classify_vowel(v) for v in vowels}
    classes.discard(HarmonyClass.UNKNOWN)

    if len(classes) == 1:
        return classes.pop()
    elif len(classes) > 1:
        return HarmonyClass.MIXED
    return HarmonyClass.UNKNOWN


def get_last_vowel(word: str) -> str | None:
    for c in reversed(word):
        if classify_vowel(c) != HarmonyClass.UNKNOWN:
            return c
    return None


SONORANTS = set("йлмнң")


def _ends_with_vowel(word: str) -> bool:
    return classify_vowel(word[-1]) != HarmonyClass.UNKNOWN


def select_plural_suffix(word: str) -> str:
    last_vowel = get_last_vowel(word)
    if last_vowel is None:
        return "тар"

    vc = classify_vowel(last_vowel)
    last_char = word[-1].lower()

    if _ends_with_vowel(word) or last_char in SONORANTS:
        if vc == HarmonyClass.BACK:
            return "лар"
        return "лер"

    if last_char in "қғ":
        if vc == HarmonyClass.BACK:
            return "тар"
        return "тер"
    else:
        if vc == HarmonyClass.BACK:
            return "дар"
        return "дер"


def select_dative_suffix(word: str) -> str:
    last_vowel = get_last_vowel(word)
    if last_vowel is None:
        return "қа"

    vc = classify_vowel(last_vowel)
    last_char = word[-1].lower()

    if _ends_with_vowel(word) or last_char in SONORANTS:
        if vc == HarmonyClass.BACK:
            return "ға"
        return "ге"
    else:
        if vc == HarmonyClass.BACK:
            return "қа"
        return "ке"


def select_genitive_suffix(word: str) -> str:
    last_vowel = get_last_vowel(word)
    if last_vowel is None:
        return "тың"

    vc = classify_vowel(last_vowel)
    last_char = word[-1].lower()

    if _ends_with_vowel(word) or last_char in SONORANTS:
        if vc == HarmonyClass.BACK:
            return "ның"
        return "нің"
    else:
        if vc == HarmonyClass.BACK:
            return "тың"
        return "тің"


def select_accusative_suffix(word: str) -> str:
    last_vowel = get_last_vowel(word)
    if last_vowel is None:
        return "ты"

    vc = classify_vowel(last_vowel)
    last_char = word[-1].lower()

    if _ends_with_vowel(word) or last_char in SONORANTS:
        if vc == HarmonyClass.BACK:
            return "ны"
        return "ні"
    else:
        if vc == HarmonyClass.BACK:
            return "ты"
        return "ті"


def select_locative_suffix(word: str) -> str:
    last_vowel = get_last_vowel(word)
    if last_vowel is None:
        return "та"

    vc = classify_vowel(last_vowel)
    last_char = word[-1].lower()

    if _ends_with_vowel(word) or last_char in SONORANTS:
        if vc == HarmonyClass.BACK:
            return "да"
        return "де"
    else:
        if vc == HarmonyClass.BACK:
            return "та"
        return "те"


def select_ablative_suffix(word: str) -> str:
    last_vowel = get_last_vowel(word)
    if last_vowel is None:
        return "тан"

    vc = classify_vowel(last_vowel)
    last_char = word[-1].lower()

    if _ends_with_vowel(word) or last_char in SONORANTS:
        if vc == HarmonyClass.BACK:
            return "дан"
        return "ден"
    else:
        if vc == HarmonyClass.BACK:
            return "тан"
        return "тен"


def select_instrumental_suffix(word: str) -> str:
    last_vowel = get_last_vowel(word)
    if last_vowel is None:
        return "пен"

    vc = classify_vowel(last_vowel)
    last_char = word[-1].lower()

    if _ends_with_vowel(word) or last_char in SONORANTS:
        if vc == HarmonyClass.BACK:
            return "мен"
        return "мен"
    else:
        if vc == HarmonyClass.BACK:
            return "пен"
        return "пен"
