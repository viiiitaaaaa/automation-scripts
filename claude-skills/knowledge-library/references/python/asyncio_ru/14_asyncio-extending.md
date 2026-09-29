> Источник: https://asyncio.ru/3.15/library/asyncio-extending.html — перевод документации Python (PSF).

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

- Writing a Custom Event Loop Написание пользовательского цикла событий

- Future and Task private constructors Приватные конструкторы Future и задача

- Task lifetime support Поддержка времени жизни задачи

# Extending Расширение ​

Основное направление для asyncio расширения – написание пользовательских классов цикла событий . Asyncio содержит вспомогательные средства, которые можно использовать для упрощения этой задачи.

Примечание

Сторонним разработчикам следует с осторожностью переиспользовать существующий код asyncio, поскольку новая версия Python может нарушить обратную совместимость в внутренней части API.

## Writing a Custom Event Loop Написание пользовательского цикла событий ​

asyncio.AbstractEventLoop объявляет очень много методов. Реализация их всех с нуля – утомительная работа.

Цикл событий может получить реализацию многих общих методов бесплатно, унаследовав от asyncio.BaseEventLoop .

В свою очередь, наследник должен реализовать ряд приватных методов, объявленных, но не реализованных в asyncio.BaseEventLoop .

Например, loop.create_connection() проверяет аргументы, разрешает DNS-адреса и вызывает loop._make_socket_transport() , который должен быть реализован унаследованным классом. Метод _make_socket_transport() не документирован и считается внутренним API.

## Future and Task private constructors Приватные конструкторы Future и задача ​

asyncio.Future и asyncio.Task никогда не должны создаваться напрямую; вместо этого используйте соответствующие loop.create_future() и loop.create_task() или фабрики asyncio.create_task() .

Однако сторонние циклы событий могут переиспользовать встроенные реализации future и задачи, чтобы бесплатно получить сложный и высокооптимизированный код.

Для этой цели перечислены следующие приватные конструкторы:

**Future. __init__ ( * , loop = None )**

Создаёт встроенный экземпляр future.

loop – необязательный экземпляр цикла событий.

**Task. __init__ ( coro , * , loop = None , name = None , context = None )**

Создаёт встроенный экземпляр задачи.

loop – необязательный экземпляр цикла событий. Остальные аргументы описаны в описании loop.create_task() .

Изменено в версии 3.11: добавлен аргумент context .

## Task lifetime support Поддержка времени жизни задачи ​

Сторонняя реализация задачи должна вызывать следующие функции, чтобы задача оставалась видимой для asyncio.all_tasks() и asyncio.current_task() :

**asyncio. _register_task ( task )**

Регистрирует новую задачу как управляемую asyncio .

Вызывайте эту функцию из конструктора задачи.

**asyncio. _unregister_task ( task )**

Удаляет регистрацию задачи из внутренних структур asyncio .

Функцию следует вызывать, когда задача завершается.

**asyncio. _enter_task ( loop , task )**

Переключает текущую задачу на аргумент задача .

Вызывайте функцию непосредственно перед выполнением части встроенной корутины ( coroutine.send() или coroutine.throw() ).

**asyncio. _leave_task ( loop , task )**

Переключает текущую задачу обратно с задачи на None .

Вызывает функцию сразу после coroutine.send() или coroutine.throw() выполнения.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.