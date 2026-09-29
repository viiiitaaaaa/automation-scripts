# Две практики: закрывать ресурсы и кешировать без утечек памяти

## 1. Файлы, соединения, браузеры — только через `with`, не через `__del__`

Источник: https://thecode.media/vsyo-chto-nuzhno-znat-o-destruktorah-v-python/

**Правило.** Всё, что надо «закрыть» (файл, xlsx, сессия requests/aiohttp, Telethon-клиент,
соединение с БД, браузер Playwright/Dolphin), открываем через `with` / `async with`. Деструктор
`__del__` для этого не годится: Python вызывает его когда захочет (иногда только в конце программы),
при ошибке внутри него исключение молча проглатывается, а при зависших ссылках не вызывается вовсе.
`with` закрывает ресурс сразу по выходу из блока — даже если внутри случилась ошибка.
Бытовой пример: `with` — дверь с доводчиком, `__del__` — надежда, что уборщица когда-нибудь закроет.
Для своих классов вместо `__del__` пишем `__enter__`/`__exit__` или `@contextlib.contextmanager`;
несколько ресурсов разом — `contextlib.ExitStack`.

```python
with open('log.txt', 'a', encoding='utf-8') as f, requests.Session() as s:
    f.write(s.get(url, timeout=20).text[:100])
# здесь файл и сессия уже закрыты

from contextlib import contextmanager
@contextmanager
def browser(profile_id):
    b = start_profile(profile_id)      # свой запуск
    try:
        yield b
    finally:
        stop_profile(profile_id)       # выполнится всегда, даже при ошибке
```

## 2. Кеш объектов без утечки памяти — `weakref`

Источник: https://habr.com/ru/companies/piter/articles/893088 (перевод Martin Heinz)

**Правило.** Если долгоживущий скрипт (бот, радар) хранит в словаре-кеше «тяжёлые» объекты
(картинки PIL, распарсенные страницы, клиенты), обычный `dict` держит их вечно — память растёт,
пока процесс не упадёт. `weakref.WeakValueDictionary` хранит объект только пока он нужен кому-то ещё:
как только остальные ссылки пропали, запись из кеша исчезает сама. Слабая ссылка — «закладка», которая
не мешает выбросить книгу. Ограничения: на `str`, `int`, `dict`, `list`, `tuple` слабую ссылку сделать
нельзя (TypeError) — для кеша результатов функций берём `functools.lru_cache(maxsize=...)`
с ограничением размера. `weakref` — для экземпляров своих классов и объектов библиотек
(PIL.Image, сессии, узлы дерева, где ссылка на «родителя» должна быть слабой).

```python
import weakref, functools

_images = weakref.WeakValueDictionary()          # кеш открытых картинок
def get_image(path):
    img = _images.get(path)
    if img is None:
        img = Image.open(path); _images[path] = img
    return img

@functools.lru_cache(maxsize=2000)               # кеш ответов: не больше 2000 записей
def rate_cny_usd(date: str) -> float: ...
```
