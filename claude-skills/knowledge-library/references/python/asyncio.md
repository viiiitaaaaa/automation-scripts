# asyncio — выжимка для наших сборщиков

Источник: русская документация Python 3.15 — https://asyncio.ru/3.15/library/asyncio.html
(разделы «Корутины и задачи» asyncio-task.html и «Примитивы синхронизации» asyncio-sync.html).
Здесь — только то, что нужно для tg_monitor / news.py, радара трендов, парсинга 1688 и Telegram-бота.
Python у нас 3.14, всё ниже работает (TaskGroup и asyncio.timeout — с 3.11).

## Зачем это вообще

Обычный скрипт качает страницы по очереди: 100 страниц × 1 с = 100 с. Почти всё это время он
**ждёт ответа сервера** и ничего не делает. asyncio позволяет ждать много ответов **одновременно**:
как официант, который принял заказ у первого стола и не стоит у плиты, а идёт к второму.
Те же 100 страниц с лимитом 10 одновременно ≈ 10–15 с.

Подходит для: сетевых запросов, API, Telegram. НЕ ускоряет тяжёлые вычисления (нарезку картинок,
pandas) — там узкое место процессор, а не ожидание.

## Слова

- **корутина** — функция `async def`. Вызов `f()` её ещё не запускает, нужно `await f()`.
- **await** — «подожди результат, а пока пусть работают другие».
- **задача (Task)** — корутина, поставленная в очередь на выполнение параллельно с другими.
- **цикл событий** — «диспетчер», который переключается между задачами. Запускается `asyncio.run(main())`
  один раз в самом низу скрипта.

## 1. Запустить много дел параллельно: gather и TaskGroup

```python
import asyncio

async def fetch(n):
    await asyncio.sleep(1)          # вместо sleep — реальный запрос
    return n * 10

async def main():
    # Вариант А: gather — результаты в том же порядке, что и задания
    results = await asyncio.gather(*(fetch(i) for i in range(5)))
    print(results)                   # [0, 10, 20, 30, 40] — за ~1 с, а не 5

    # return_exceptions=True: одна упавшая страница не роняет остальные,
    # ошибка просто лежит в списке на своём месте
    results = await asyncio.gather(*(fetch(i) for i in range(5)), return_exceptions=True)
    ok = [r for r in results if not isinstance(r, Exception)]

    # Вариант Б: TaskGroup (современный). Если ОДНА задача упала — остальные отменяются,
    # и вылетает ExceptionGroup. Хорошо, когда «всё или ничего».
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(i)) for i in range(5)]
    print([t.result() for t in tasks])   # await неявный — при выходе из with

asyncio.run(main())
```

**Что выбрать:** для сборщиков (много независимых страниц, часть может упасть) —
`gather(..., return_exceptions=True)`. TaskGroup — когда без любого из шагов результат не нужен.

Результаты по мере готовности (удобно для прогресса «готово 37 из 200»):

```python
for coro in asyncio.as_completed([fetch(i) for i in range(200)]):
    res = await coro
```

## 2. Лимит одновременных запросов: Semaphore

Без лимита 500 запросов уйдут разом → сайт отдаст 429/бан (помним блокировку Taobao 27.09!).
Семафор — это «турникет на N человек»: внутрь `async with sem:` одновременно заходят не больше N.

```python
sem = asyncio.Semaphore(5)          # не больше 5 запросов одновременно

async def polite_fetch(url):
    async with sem:                  # ждём свободного места
        data = await get(url)
        await asyncio.sleep(0.5)     # доп. пауза внутри = ещё вежливее
        return data
```

Семафор создавать **внутри** `async def main()` (или в функции, вызванной из неё), а не на уровне модуля.

## 3. Таймауты

```python
# на один кусок кода (Python 3.11+)
try:
    async with asyncio.timeout(10):
        data = await get(url)
except TimeoutError:
    data = None

# на одну корутину — то же самое, старый стиль
data = await asyncio.wait_for(get(url), timeout=10)
```

Правило: у каждого сетевого запроса должен быть таймаут, иначе один зависший сайт
держит весь сбор. У aiohttp — ещё и свой: `aiohttp.ClientTimeout(total=30)`.

## 4. Синхронный код внутри async (requests, openpyxl, Telethon-синхронные вызовы)

Наши `tg_monitor.py`, `news.py` написаны на обычном `requests`. Переписывать не обязательно:
`asyncio.to_thread` запускает обычную функцию в отдельном потоке и не блокирует остальные задачи.

```python
import asyncio, requests

def get_sync(url):
    return requests.get(url, timeout=20).text

async def main(urls):
    sem = asyncio.Semaphore(8)
    async def one(u):
        async with sem:
            return await asyncio.to_thread(get_sync, u)
    return await asyncio.gather(*(one(u) for u in urls), return_exceptions=True)
```

Внимание: **нельзя** вызывать `requests.get` или `time.sleep` прямо в `async def` без `to_thread` —
это остановит весь цикл событий, и «параллельность» исчезнет. В async-коде спать — только `await asyncio.sleep()`.

Ещё проще, если async вообще не нужен (скрипт маленький) — пул потоков из стандартной библиотеки:

```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=8) as pool:      # 8 = лимит одновременных запросов
    pages = list(pool.map(get_sync, urls))           # порядок сохраняется
```

## 5. Готовый шаблон: скачать N страниц параллельно с лимитом, таймаутом и повторами

aiohttp 3.14 установлен. Шаблон проверен запуском.

```python
import asyncio
import aiohttp

LIMIT = 8            # одновременно запросов
RETRIES = 3          # попыток на страницу
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0 Safari/537.36'}

async def fetch(session, sem, url):
    for attempt in range(1, RETRIES + 1):
        try:
            async with sem:
                async with session.get(url) as r:
                    if r.status == 429:                  # «слишком часто» — подождать и повторить
                        raise aiohttp.ClientResponseError(r.request_info, (), status=429)
                    r.raise_for_status()
                    return url, await r.text()
        except (aiohttp.ClientError, TimeoutError) as e:
            if attempt == RETRIES:
                return url, e                             # ошибку возвращаем, а не роняем сбор
            await asyncio.sleep(2 ** attempt)             # 2, 4, 8 с — «экспоненциальная пауза»

async def fetch_all(urls):
    sem = asyncio.Semaphore(LIMIT)
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
        return await asyncio.gather(*(fetch(session, sem, u) for u in urls))

if __name__ == '__main__':
    urls = [f'https://example.com/?p={i}' for i in range(20)]
    results = asyncio.run(fetch_all(urls))
    good = {u: t for u, t in results if isinstance(t, str)}
    bad = {u: t for u, t in results if not isinstance(t, str)}
    print(f'скачано {len(good)}, ошибок {len(bad)}')
```

Одна `ClientSession` на весь сбор (не на каждый запрос) — она держит соединения открытыми и
работает быстрее. `async with` сам закроет её в конце.

## 6. Частые ошибки

| Симптом | Причина | Что делать |
|---|---|---|
| `RuntimeWarning: coroutine ... was never awaited` | вызвали `f()` без `await` | `await f()` или `create_task(f())` |
| `asyncio.run() cannot be called from a running event loop` | запуск внутри Jupyter / уже работающего цикла (Telethon, aiogram) | там просто `await main()` |
| Всё идёт по одному, быстрее не стало | внутри `async def` стоит `requests.get` / `time.sleep` | `asyncio.to_thread(...)` / `await asyncio.sleep` |
| Сайт начал отвечать 429 / капча | лимит слишком большой | `Semaphore(3–5)` + пауза + повторы |
| Задача «пропала», ошибки не видно | `create_task` без сохранения ссылки | держать задачи в списке и `await` их |
| Ctrl+C не останавливает сразу | задачи ждут ответа | нормально; таймауты делают это быстрее |

## Связь с нашими проектами

- **tg_monitor / news.py** — сбор каналов через `requests`: обернуть в `to_thread` + `Semaphore(5)`.
- **Радар трендов** — запросы к treg.to / Trends MCP: шаблон из п.5, `LIMIT` = лимиту API.
- **1688 через treg API** — то же; платные запросы — обязательно `return_exceptions`, чтобы не терять оплаченные ответы.
- **Бот «Дела»** — Telegram-библиотеки уже асинхронные: внутри обработчиков только `await`, тяжёлое — в `to_thread`.
