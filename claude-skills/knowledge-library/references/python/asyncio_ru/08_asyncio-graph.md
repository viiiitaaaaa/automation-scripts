> Источник: https://asyncio.ru/3.15/library/asyncio-graph.html — перевод документации Python (PSF).

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

- Low level utility functions Низкоуровневые вспомогательные функции

# Call Graph Introspection Интроспекция графа вызовов ​

Исходный код: Lib/asyncio/graph.py

asyncio содержит мощные утилиты для интроспекции графа вызовов во время выполнения,
чтобы трассировать весь граф вызовов выполняемой корутины или задачи , или
приостановленного future . Эти утилиты и лежащая в их основе инфраструктура
могут использоваться из Python-программы или внешними профилировщиками
и отладчиками.

Добавлено в версии 3.14.

**asyncio. print_call_graph ( future = None , / , * , file = None , depth = 1 , limit = None )**

Выводит граф асинхронных вызовов для текущей задачи или предоставленного Task или Future .

Эта функция выводит записи, начиная с верхнего фрейма и спускаясь
вниз к точке вызова.

Функция принимает необязательный аргумент future .
Если он не передан, будет использоваться текущая выполняемая задача.

Если функция вызывается для текущей задачи , необязательный
именованный аргумент depth можно использовать для пропуска указанного
количества фреймов с вершины стека.

Если указан необязательный именованный аргумент limit , каждый стек вызовов
в результирующем графе усекается так, чтобы включать не более abs(limit) записей. Если limit положителен, остаются записи, ближайшие к
точке вызова. Если limit отрицателен, остаются верхние записи.
Если limit опущен или None , присутствуют все записи.
Если limit равен 0 , стек вызовов не выводится, выводится только
информация «awaited by».

Если file опущен или равен None , функция будет выводить
в sys.stdout .

Пример:

Следующий код Python:

```python
import
 
asyncio



async
 
def
 
test
():

    
asyncio
.
print_call_graph
()



async
 
def
 
main
():

    
async
 
with
 
asyncio
.
TaskGroup
()
 
as
 
g
:

        
g
.
create_task
(
test
(),
 
name
=
'test'
)



asyncio
.
run
(
main
())
```

выведет:

```python
*
 
Task
(
name
=
'test'
,
 
id
=
0x1039f0fe0
)


+
 
Call
 
stack
:


|
   
File
 
't2.py'
,
 
line
 
4
,
 
in
 
async
 
test
()


+
 
Awaited
 
by
:

   
*
 
Task
(
name
=
'Task-1'
,
 
id
=
0x103a5e060
)

      
+
 
Call
 
stack
:

      
|
   
File
 
'taskgroups.py'
,
 
line
 
107
,
 
in
 
async
 
TaskGroup
.
__aexit__
()

      
|
   
File
 
't2.py'
,
 
line
 
7
,
 
in
 
async
 
main
()
```

**asyncio. format_call_graph ( future = None , / , * , depth = 1 , limit = None )**

Как print_call_graph() , но возвращает строку.
Если future равен None и нет текущей задачи,
функция возвращает пустую строку.

**asyncio. capture_call_graph ( future = None , / , * , depth = 1 , limit = None )**

Захватывает граф асинхронных вызовов для текущей задачи или предоставленного Task или Future .

Функция принимает необязательный аргумент future .
Если он не передан, будет использоваться текущая выполняемая задача. Если нет
текущей задачи, функция возвращает None .

Если функция вызывается для текущей задачи , необязательный
именованный аргумент depth можно использовать для пропуска указанного
количества фреймов с вершины стека.

Возвращает объект класса данных FutureCallGraph :

- FutureCallGraph(future, call_stack, awaited_by) Где future – это ссылка на Future или Task (или их подклассы.) call_stack – это кортеж объектов FrameCallGraphEntry . awaited_by – это кортеж объектов FutureCallGraph .

FutureCallGraph(future, call_stack, awaited_by)

Где future – это ссылка на Future или Task (или их подклассы.)

call_stack – это кортеж объектов FrameCallGraphEntry .

awaited_by – это кортеж объектов FutureCallGraph .

- FrameCallGraphEntry(frame) Где frame – это объект фрейма обычной функции Python
в стеке вызовов.

FrameCallGraphEntry(frame)

Где frame – это объект фрейма обычной функции Python
в стеке вызовов.

## Low level utility functions Низкоуровневые вспомогательные функции ​

Для интроспекции графа асинхронных вызовов asyncio требует взаимодействия от
структур управления потоком, таких как shield() или TaskGroup .
Всякий раз, когда задействован промежуточный объект Future с низкоуровневыми API, такими как Future.add_done_callback() , следует использовать следующие две функции, чтобы сообщить asyncio
о том, как именно такие промежуточные объекты future связаны с
задачами, которые они оборачивают или контролируют.

**asyncio. future_add_to_awaited_by ( future , waiter , / )**

Записывает, что future ожидается waiter .

Оба future и waiter должны быть экземплярами Future или Task или их подклассов,
иначе вызов не будет иметь эффекта.

Вызов future_add_to_awaited_by() должен сопровождаться последующим
вызовом функции future_discard_from_awaited_by() с теми же аргументами.

**asyncio. future_discard_from_awaited_by ( future , waiter , / )**

Записывает, что future больше не ожидается объектом waiter .

Оба future и waiter должны быть экземплярами Future или Task или их подклассов, иначе
вызов не будет иметь эффекта.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.