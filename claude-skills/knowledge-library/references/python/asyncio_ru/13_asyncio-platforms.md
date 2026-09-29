> Источник: https://asyncio.ru/3.15/library/asyncio-platforms.html — перевод документации Python (PSF).

## Высокоуровневые API

Runners Исполнители

Coroutines and Tasks Корутины и задачи

Streams Потоки данных

Synchronization Primitives Примитивы синхронизации

Subprocesses Подпроцессы

Queues Очереди

Exceptions Исключения

Call Graph Introspection Интроспекция графа вызовов

## Низкоуровневые API

Event Loop Цикл событий

Futures Future

Transports and Protocols Транспорты и протоколы

Policies Политики

Platform Support Поддержка платформ

Extending Расширение

## Руководства и индексы

High-level API Index Индекс высокоуровневого API

Low-level API Index Индекс API низкого уровня

Developing with asyncio Разработка с asyncio

- All Platforms Все платформы

- Windows Subprocess Support on Windows Поддержка подпроцессов в Windows

- Subprocess Support on Windows Поддержка подпроцессов в Windows

- macOS

# Platform Support Поддержка платформ ​

Модуль asyncio спроектирован переносимым,
но некоторые платформы имеют тонкие различия и ограничения
из-за базовой архитектуры и возможностей платформ.

## All Platforms Все платформы ​

- loop.add_reader() и loop.add_writer() не могут использоваться для мониторинга файлового ввода-вывода.

loop.add_reader() и loop.add_writer() не могут использоваться для мониторинга файлового ввода-вывода.

## Windows ​

Исходный код: Lib/asyncio/proactor_events.py , Lib/asyncio/windows_events.py , Lib/asyncio/windows_utils.py

Изменено в версии 3.8: В Windows ProactorEventLoop теперь является циклом событий по умолчанию.

Все циклы событий в Windows не поддерживают следующие методы:

- loop.create_unix_connection() и loop.create_unix_server() не поддерживаются.
Семейство сокетов socket.AF_UNIX специфично для Unix.

loop.create_unix_connection() и loop.create_unix_server() не поддерживаются.
Семейство сокетов socket.AF_UNIX специфично для Unix.

- loop.add_signal_handler() и loop.remove_signal_handler() не поддерживаются.

loop.add_signal_handler() и loop.remove_signal_handler() не поддерживаются.

SelectorEventLoop имеет следующие ограничения:

- SelectSelector используется для ожидания событий сокетов:
он поддерживает сокеты и ограничен 512 сокетами.

SelectSelector используется для ожидания событий сокетов:
он поддерживает сокеты и ограничен 512 сокетами.

- loop.add_reader() и loop.add_writer() принимают только
дескрипторы сокетов (например, файловые дескрипторы каналов не поддерживаются).

loop.add_reader() и loop.add_writer() принимают только
дескрипторы сокетов (например, файловые дескрипторы каналов не поддерживаются).

- Каналы не поддерживаются, поэтому методы loop.connect_read_pipe() и loop.connect_write_pipe() не реализованы.

Каналы не поддерживаются, поэтому методы loop.connect_read_pipe() и loop.connect_write_pipe() не реализованы.

- Подпроцессы не поддерживаются, т.е.
методы loop.subprocess_exec() и loop.subprocess_shell() не реализованы.

Подпроцессы не поддерживаются, т.е.
методы loop.subprocess_exec() и loop.subprocess_shell() не реализованы.

ProactorEventLoop имеет следующие ограничения:

- Методы loop.add_reader() и loop.add_writer() не поддерживаются.

Методы loop.add_reader() и loop.add_writer() не поддерживаются.

Разрешение монотонных часов в Windows обычно составляет около 15.6
миллисекунд. Наилучшее разрешение – 0.5 миллисекунды. Разрешение зависит от
аппаратного обеспечения (наличие HPET ) и от
конфигурации Windows.

### Subprocess Support on Windows Поддержка подпроцессов в Windows ​

В Windows цикл событий по умолчанию ProactorEventLoop поддерживает
подпроцессы, тогда как SelectorEventLoop – нет.

## macOS ​

Современные версии macOS полностью поддерживаются.

macOS <= 10.8

В macOS 10.6, 10.7 и 10.8 цикл событий по умолчанию
использует selectors.KqueueSelector , который не поддерживает
символьные устройства в этих версиях. SelectorEventLoop можно вручную настроить на использование SelectSelector или PollSelector для поддержки символьных устройств на
этих старых версиях macOS. Пример:

```python
import
 
asyncio


import
 
selectors



selector
 
=
 
selectors
.
SelectSelector
()


loop
 
=
 
asyncio
.
SelectorEventLoop
(
selector
)


asyncio
.
set_event_loop
(
loop
)
```

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.