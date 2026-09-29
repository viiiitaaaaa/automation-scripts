# -*- coding: utf-8 -*-
"""Проверка контрольных сумм российских реквизитов: ИНН, ОГРН, ОГРНИП, СНИЛС.

Ловит опечатки (лишняя/пропущенная цифра, перестановка соседних цифр).
ВАЖНО: «верно» значит только «номер математически правильный».
Существует ли такая организация/человек — проверяется в реестре (ЕГРЮЛ/ЕГРИП, egrul.nalog.ru).

Запуск:
    python check_rekvizity.py 7707083893
    python check_rekvizity.py 7707083893 1027700132195 "112-233-445 95"
    python check_rekvizity.py ИНН 7707083893          # тип можно подсказать словом перед номером
    python check_rekvizity.py --text "ООО Ромашка, ИНН 7707083893, ОГРН 1027700132195"
    python check_rekvizity.py --file иск.txt          # найти и проверить все номера в тексте
    python check_rekvizity.py --test                  # самопроверка на эталонных номерах

Алгоритмы сверены по трём источникам:
  - habr.com/ru/articles/1046397 (Р. Васильев, «Контрольные суммы ИНН, ОГРН и СНИЛС»);
  - python-stdnum (stdnum/ru/inn.py, stdnum/ru/ogrn.py, GitHub arthurdejong/python-stdnum);
  - ru.wikipedia: «Контрольное число», «ОГРН», «ОГРНИП» (со ссылкой на приказ Минфина № 165н).
  Расхождение: для ОГРНИП python-stdnum берёт остаток от деления на 13 без «% 10», а Википедия
  («младший разряд остатка от деления на 13») и статья — с «% 10». Здесь сделано как в Википедии.
"""
import re
import sys

W_INN10 = (2, 4, 10, 3, 5, 9, 4, 6, 8)
W_INN12_1 = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
W_INN12_2 = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)

NAMES = {
    'inn10': 'ИНН организации (10 цифр)',
    'inn12': 'ИНН физлица / ИП (12 цифр)',
    'ogrn': 'ОГРН организации (13 цифр)',
    'ogrnip': 'ОГРНИП предпринимателя (15 цифр)',
    'snils': 'СНИЛС (11 цифр)',
}
# длина -> тип
BY_LEN = {10: 'inn10', 12: 'inn12', 13: 'ogrn', 15: 'ogrnip', 11: 'snils'}
# слово-подсказка -> допустимые типы
HINTS = {
    'инн': ('inn10', 'inn12'),
    'огрнип': ('ogrnip',),
    'огрн': ('ogrn', 'ogrnip'),
    'снилс': ('snils',),
}


def _ws(digits, weights):
    return sum(int(d) * w for d, w in zip(digits, weights))


def check_inn10(s):
    """Возвращает (ok, ожидаемая контрольная часть)."""
    c = _ws(s[:9], W_INN10) % 11 % 10
    return c == int(s[9]), str(c)


def check_inn12(s):
    c1 = _ws(s[:10], W_INN12_1) % 11 % 10
    c2 = _ws(s[:10] + str(c1), W_INN12_2) % 11 % 10
    return s[10:] == f'{c1}{c2}', f'{c1}{c2}'


def check_ogrn(s):
    c = int(s[:12]) % 11 % 10
    return c == int(s[12]), str(c)


def check_ogrnip(s):
    c = int(s[:14]) % 13 % 10
    return c == int(s[14]), str(c)


def check_snils(s):
    base = int(s[:9])
    if base <= 1001998:  # номера до 001-001-998 контрольной суммой не проверяются
        return True, s[9:]
    total = sum(int(d) * (9 - i) for i, d in enumerate(s[:9]))
    if total < 100:
        c = total
    elif total in (100, 101):
        c = 0
    else:
        c = total % 101
        if c == 100:
            c = 0
    return int(s[9:]) == c, f'{c:02d}'


CHECKS = {'inn10': check_inn10, 'inn12': check_inn12, 'ogrn': check_ogrn,
          'ogrnip': check_ogrnip, 'snils': check_snils}


def clean(raw):
    """Убираем пробелы, дефисы, точки. Буквы внутри номера = ошибка (не выкидываем их молча)."""
    s = raw.strip()
    if re.search(r'[^\d\s\-\.]', s):
        return None
    return re.sub(r'\D', '', s)


def detect(digits, hint=None):
    kind = BY_LEN.get(len(digits))
    if hint:
        allowed = HINTS[hint]
        if kind not in allowed:
            return None
    return kind


def fmt_snils(s):
    return f'{s[0:3]}-{s[3:6]}-{s[6:9]} {s[9:]}'


def check(raw, hint=None):
    """Главная функция. Возвращает словарь: ok (True/False), kind, message."""
    digits = clean(raw)
    if digits is None:
        return {'ok': False, 'kind': None, 'input': raw,
                'message': 'ОШИБКА: в номере есть буквы или посторонние символы'}
    if not digits:
        return {'ok': False, 'kind': None, 'input': raw, 'message': 'ОШИБКА: нет цифр'}
    kind = detect(digits, hint)
    if kind is None:
        n = len(digits)
        if hint:
            need = ' или '.join(str(k) for k, v in BY_LEN.items() if v in HINTS[hint])
            msg = f'ОШИБКА длины: для {hint.upper()} нужно {need} цифр, а здесь {n}'
        else:
            msg = f'ОШИБКА длины: {n} цифр — такого реквизита нет (ИНН 10/12, СНИЛС 11, ОГРН 13, ОГРНИП 15)'
        if n in (9, 11) and hint == 'инн':
            msg += '. Если номер прошёл через Excel — мог срезаться ведущий ноль'
        return {'ok': False, 'kind': None, 'input': raw, 'message': msg}
    ok, expected = CHECKS[kind](digits)
    shown = fmt_snils(digits) if kind == 'snils' else digits
    if ok:
        msg = f'ВЕРНО: {NAMES[kind]} {shown} — контрольная сумма сходится'
    else:
        tail = len(expected)
        msg = (f'ОШИБКА контрольной суммы: {NAMES[kind]} {shown} — '
               f'в конце стоит {digits[-tail:]}, а по расчёту должно быть {expected}. '
               f'Вероятна опечатка — сверьте с документом')
    return {'ok': ok, 'kind': kind, 'input': raw, 'message': msg}


NUM_RE = re.compile(r'(?:(ИНН|ОГРНИП|ОГРН|СНИЛС)\s*[:№]?\s*)?(\d[\d\- ]{8,18}\d)', re.I)


def find_in_text(text):
    """Находит номера в тексте (с подсказкой по слову ИНН/ОГРН/СНИЛС перед ними)."""
    res = []
    for m in NUM_RE.finditer(text):
        hint = m.group(1).lower() if m.group(1) else None
        raw = m.group(2).strip()
        d = re.sub(r'\D', '', raw)
        if len(d) < 9 or len(d) > 15:
            continue
        res.append(check(raw, hint))
    return res


TESTS = [
    # (номер, подсказка, ожидается ok)
    ('7707083893', None, True),        # ИНН ПАО Сбербанк
    ('1027700132195', None, True),     # ОГРН ПАО Сбербанк
    ('7736207543', None, True),        # ИНН ООО «Яндекс»
    ('1027700229193', None, True),     # ОГРН ООО «Яндекс»
    ('500100732259', None, True),      # ИНН физлица, пример из Википедии
    ('112-233-445 95', None, True),    # СНИЛС, пример из Википедии
    ('385768585948949', None, True),   # ОГРНИП, пример из python-stdnum
    ('1234567894', None, True),        # ИНН-10, пример из python-stdnum
    ('123456789047', None, True),      # ИНН-12, пример из python-stdnum
    ('1022200525819', None, True),     # ОГРН, пример из python-stdnum
    # испорченные
    ('7707083894', None, False),       # последняя цифра изменена
    ('7707038893', None, False),       # переставлены соседние цифры
    ('1027700132196', None, False),    # ОГРН, последняя цифра
    ('1027700123195', None, False),    # ОГРН, перестановка
    ('500100732258', None, False),     # ИНН-12, последняя цифра
    ('112-233-445 96', None, False),   # СНИЛС
    ('385768585948948', None, False),  # ОГРНИП
    ('1022500001328', None, False),    # ОГРН, «плохой» пример из python-stdnum
    ('77070838931', 'инн', False),     # 11 цифр с подсказкой ИНН — ошибка длины
    ('77О7083893', None, False),       # буква О вместо нуля
    ('707083893', None, False),        # 9 цифр
]


def run_tests():
    bad = 0
    for raw, hint, want in TESTS:
        r = check(raw, hint)
        status = 'ok ' if r['ok'] == want else 'СБОЙ'
        if r['ok'] != want:
            bad += 1
        print(f'[{status}] {raw!r:22} -> {r["message"]}')
    print(f'\nИтого: {len(TESTS) - bad} из {len(TESTS)} тестов прошли')
    return bad == 0


def main(argv):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    if argv[0] == '--test':
        return 0 if run_tests() else 1
    if argv[0] in ('--text', '--file'):
        text = ' '.join(argv[1:])
        if argv[0] == '--file':
            text = open(argv[1], encoding='utf-8', errors='replace').read()
        results = find_in_text(text)
        if not results:
            print('Номеров (9–15 цифр) в тексте не найдено')
        for r in results:
            print(r['message'])
        return 0 if all(r['ok'] for r in results) else 1
    all_ok = True
    hint = None
    for a in argv:
        if a.lower().strip(':') in HINTS:
            hint = a.lower().strip(':')
            continue
        r = check(a, hint)
        hint = None
        all_ok &= r['ok']
        print(r['message'])
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
