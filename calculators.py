from datetime import datetime
import re


# =====================================
# ПРОВЕРКА И РАЗБОР ДАТЫ
# =====================================

def parse_date(date_text: str):
    date_text = date_text.strip()

    formats = [
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d%m%Y",
    ]

    for fmt in formats:
        try:
            birth_date = datetime.strptime(date_text, fmt)

            if birth_date.year < 1900:
                return None

            if birth_date.year > datetime.now().year:
                return None

            return birth_date

        except ValueError:
            pass

    digits = re.sub(r"\D", "", date_text)

    if len(digits) == 7:
        digits = "0" + digits

    if len(digits) == 8:
        try:
            birth_date = datetime.strptime(digits, "%d%m%Y")

            if birth_date.year < 1900:
                return None

            if birth_date.year > datetime.now().year:
                return None

            return birth_date

        except ValueError:
            pass

    return None


# =====================================
# ОБЩЕЕ ПРИВЕДЕНИЕ К ОДНОЙ ЦИФРЕ
# =====================================

def reduce_to_digit(number: int) -> int:
    while number > 9:
        number = sum(int(d) for d in str(number))
    return number


# =====================================
# РАСЧЁТЫ ПО ДАТЕ
# =====================================

def calculate_soul(birth_date: datetime) -> int:
    return reduce_to_digit(birth_date.day)


def calculate_expression(birth_date: datetime) -> int:
    total = sum(int(d) for d in f"{birth_date.day}{birth_date.month}")
    return reduce_to_digit(total)


def calculate_year(birth_date: datetime) -> int:
    total = sum(int(d) for d in str(birth_date.year))
    return reduce_to_digit(total)


def calculate_destiny(birth_date: datetime) -> int:
    digits = birth_date.strftime("%d%m%Y")
    total = sum(int(d) for d in digits)
    return reduce_to_digit(total)


# =====================================
# РАСЧЁТ ВАРНЫ
# =====================================

VARNA_MAP = {
    1: "kshatriya",
    2: "vaishya",
    3: "brahman",
    4: "shudra",
    5: "vaishya",
    6: "brahman",
    7: "shudra",
    8: "shudra",
    9: "kshatriya",
}


def calculate_varna(birth_date: datetime):
    soul = calculate_soul(birth_date)
    year = calculate_year(birth_date)
    destiny = calculate_destiny(birth_date)

    scores = {
        "brahman": 0,
        "kshatriya": 0,
        "vaishya": 0,
        "shudra": 0,
    }

    scores[VARNA_MAP[soul]] += 50
    scores[VARNA_MAP[year]] += 10
    scores[VARNA_MAP[destiny]] += 40

    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    main_varna = sorted_scores[0][0]
    second_varna = sorted_scores[1][0] if sorted_scores[1][1] == sorted_scores[0][1] else None

    return {
        "main_varna": main_varna,
        "second_varna": second_varna,
        "scores": scores,
    }

# =====================================
# ПРОЦЕНТ СОВМЕСТИМОСТИ
# 65% варны + 35% экспрессии
# =====================================

VARNA_SHORT = {
    "brahman": "B",
    "kshatriya": "K",
    "vaishya": "V",
    "shudra": "S",
}


VARNA_SCORE = {
    "B_B": 62,
    "B_K": 57,
    "B_V": 60,
    "B_S": 42,

    "K_K": 55,
    "K_V": 50,
    "K_S": 40,

    "V_V": 53,
    "V_S": 45,

    "S_S": 52,
}


EXPRESSION_SCORE = {
    "1_1": 12,
    "1_2": 27,
    "1_3": 31,
    "1_4": 21,
    "1_5": 25,
    "1_6": 35,
    "1_7": 31,
    "1_8": 20,
    "1_9": 35,

    "2_2": 22,
    "2_3": 32,
    "2_4": 31,
    "2_5": 20,
    "2_6": 35,
    "2_7": 25,
    "2_8": 32,
    "2_9": 19,

    "3_3": 30,
    "3_4": 32,
    "3_5": 35,
    "3_6": 35,
    "3_7": 18,
    "3_8": 14,
    "3_9": 33,

    "4_4": 26,
    "4_5": 16,
    "4_6": 35,
    "4_7": 28,
    "4_8": 22,
    "4_9": 27,

    "5_5": 31,
    "5_6": 28,
    "5_7": 32,
    "5_8": 20,
    "5_9": 26,

    "6_6": 32,
    "6_7": 27,
    "6_8": 24,
    "6_9": 34,

    "7_7": 16,
    "7_8": 10,
    "7_9": 17,

    "8_8": 25,
    "8_9": 20,

    "9_9": 23,
}


def make_pair_key(a, b) -> str:
    a = str(a)
    b = str(b)

    if int(a) > int(b):
        a, b = b, a

    return f"{a}_{b}"


def make_varna_key(varna1: str, varna2: str) -> str:
    short1 = VARNA_SHORT[varna1]
    short2 = VARNA_SHORT[varna2]

    key = f"{short1}_{short2}"

    if key not in VARNA_SCORE:
        key = f"{short2}_{short1}"

    return key


def calculate_compatibility_percent(varna1, varna2, expression1, expression2):
    varna_key = make_varna_key(varna1, varna2)
    expression_key = make_pair_key(expression1, expression2)

    varna_score = VARNA_SCORE.get(varna_key, 45)
    expression_score = EXPRESSION_SCORE.get(expression_key, 22)

    percent = varna_score + expression_score

    if percent < 45:
        percent = 45

    if percent > 95:
        percent = 95

    return percent

# =====================================
# ОСОБЫЕ СВЯЗИ
# =====================================

def has_special_4_7_connection(numbers1: list[int], numbers2: list[int]) -> bool:
    return (4 in numbers1 and 7 in numbers2) or (7 in numbers1 and 4 in numbers2)


# =====================================
# СМЕШАННАЯ ВАРНА
# =====================================
#
# Если две варны набрали одинаковый максимальный вес
# (например 40% + 40%),
# бот показывает MIXED_VARNA_RESULT_TEXT.
#
# Примеры:
# brahman + kshatriya
# brahman + vaishya
# vaishya + shudra
#