> Источник: https://asyncio.ru/3.15/library/asyncio-exceptions.html — перевод документации Python (PSF).

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

# Exceptions Исключения ​

Исходный код: Lib/asyncio/exceptions.py

**exception asyncio. TimeoutError**

Устаревший псевдоним TimeoutError ,
возникает, когда операция превысила заданный срок.

Изменено в версии 3.11: Этот класс стал псевдонимом TimeoutError .

**exception asyncio. CancelledError**

Операция была отменена.

Это исключение можно перехватить для выполнения пользовательских операций
при отмене задач asyncio. Почти во всех ситуациях
исключение должно быть возбуждено повторно.

Изменено в версии 3.8: CancelledError теперь является подклассом BaseException вместо Exception .

**exception asyncio. InvalidStateError**

Недопустимое внутреннее состояние Task или Future .

Может возникать в ситуациях, например, при установке значения результата для
объекта Future , у которого уже установлено значение результата.

**exception asyncio. SendfileNotAvailableError**

Системный вызов «sendfile» недоступен для данного
типа сокета или файла.

Подкласс RuntimeError .

**exception asyncio. IncompleteReadError**

Запрошенная операция чтения не была завершена полностью.

Возбуждается потоковыми API asyncio .

Это исключение является подклассом EOFError .

**expected**

Общее количество ( int ) ожидаемых байт.

**partial**

Строка из bytes , прочитанная до достижения конца потока.

**exception asyncio. LimitOverrunError**

Достигнут лимит размера буфера при поиске разделителя.

Возбуждается потоковыми API asyncio .

**consumed**

Общее количество байт, которые должны быть потреблены.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.