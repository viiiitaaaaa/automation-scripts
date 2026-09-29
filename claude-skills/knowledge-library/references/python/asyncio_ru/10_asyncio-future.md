> Источник: https://asyncio.ru/3.15/library/asyncio-future.html — перевод документации Python (PSF).

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

- Future Functions Функции Future

- Future Object Объект Future

# Futures ​

Исходный код: Lib/asyncio/futures.py , Lib/asyncio/base_futures.py

Future -объекты используются для связи низкоуровневого кода на основе колбэков с высокоуровневым кодом async/await.

## Future Functions Функции Future ​

**asyncio. isfuture ( obj )**

Возвращает True , если obj является одним из:

- экземпляром asyncio.Future ,

экземпляром asyncio.Future ,

- экземпляром asyncio.Task ,

экземпляром asyncio.Task ,

- Future-подобным объектом с атрибутом _asyncio_future_blocking .

Future-подобным объектом с атрибутом _asyncio_future_blocking .

Добавлено в версии 3.5.

**asyncio. ensure_future ( obj , * , loop = None )**

Возвращает:

- аргумент obj как есть, если obj является Future , Task или Future-подобным объектом ( isfuture() используется для проверки.)

аргумент obj как есть, если obj является Future , Task или Future-подобным объектом ( isfuture() используется для проверки.)

- объект Task , обёртывающий obj , если obj является
корутиной ( iscoroutine() используется для проверки);
в этом случае корутина будет запланирована с помощью ensure_future() .

объект Task , обёртывающий obj , если obj является
корутиной ( iscoroutine() используется для проверки);
в этом случае корутина будет запланирована с помощью ensure_future() .

- объект Task , который будет ожидать obj , если obj является
ожидаемым объектом ( inspect.isawaitable() используется для проверки.)

объект Task , который будет ожидать obj , если obj является
ожидаемым объектом ( inspect.isawaitable() используется для проверки.)

Если obj не является ни одним из вышеперечисленных, возбуждается TypeError .

Важно

Сохраните ссылку на результат этой функции, чтобы избежать
исчезновения задачи во время выполнения.

См. также функцию create_task() , которая является предпочтительным способом создания новых задач, или используйте asyncio.TaskGroup , которая внутренне сохраняет ссылку на задачу.

Изменено в версии 3.5.1: Функция принимает любой ожидаемый объект .

Устарело с версии 3.10: Предупреждение об устаревании выдается, если obj не является Future-подобным объектом
и loop не указан, и нет запущенного цикла событий.

**asyncio. wrap_future ( future , * , loop = None )**

Оборачивает объект concurrent.futures.Future в объект asyncio.Future .

Устарело с версии 3.10: Предупреждение об устаревании выдается, если future не является Future-подобным объектом
и loop не указан, и нет запущенного цикла событий.

## Future Object Объект Future ​

**class asyncio. Future ( * , loop = None )**

Future представляет собой конечный результат асинхронной
операции. Не является потокобезопасным.

Future является ожидаемым объектом . Корутины могут ожидать объекты Future, пока те не получат результат или исключение, или пока они не будут отменены. Future можно ожидать несколько раз, и результат будет одинаковым.

Обычно Futures используются, чтобы позволить низкоуровневому
коду на основе колбэков (например, в протоколах, реализованных с использованием asyncio транспортов )
взаимодействовать с высокоуровневым кодом async/await.

Эмпирическое правило – никогда не предоставлять объекты Future в пользовательских
API, а рекомендуемый способ создания объекта Future – вызов loop.create_future() . Таким образом, альтернативные реализации
цикла событий могут внедрять свои собственные оптимизированные реализации
объекта Future.

Изменено в версии 3.7: Добавлена поддержка модуля contextvars .

Устарело с версии 3.10: Предупреждение об устаревании выдается, если loop не указан
и нет работающего цикла событий.

**result ( )**

Возвращает результат Future.

Если done и у Future есть результат, установленный методом set_result() , возвращается значение результата.

Если Future имеет статус done и установлено исключение методом set_exception() , этот метод возбуждает исключение.

Если Future был cancelled , этот метод возбуждает
исключение CancelledError .

Если результат Future еще недоступен, этот метод возбуждает
исключение InvalidStateError .

**set_result ( result )**

Помечает Future как done и устанавливает его результат.

Возбуждает ошибку InvalidStateError , если Future уже
имеет статус done .

**set_exception ( exception )**

Помечает Future как done и устанавливает исключение.

Возбуждает ошибку InvalidStateError , если Future уже
имеет статус done .

**done ( )**

Возвращает True , если Future имеет статус done .

Future имеет статус done , если он был cancelled или если у него есть результат
или исключение, установленное вызовами set_result() или set_exception() .

**cancelled ( )**

Возвращает True , если Future был cancelled .

Этот метод обычно используется для проверки, что Future не имеет статус cancelled , перед установкой результата или исключения:

```python
if
 
not
 
fut
.
cancelled
():

    
fut
.
set_result
(
42
)
```

**add_done_callback ( callback , * , context = None )**

Добавляет колбэк, который будет выполнен, когда Future имеет статус done .

колбэк вызывается с объектом Future в качестве единственного
аргумента.

Если Future уже имеет статус done , когда этот метод вызывается,
колбэк планируется с помощью loop.call_soon() .

Необязательный именованный аргумент context позволяет указать
пользовательский contextvars.Context для выполнения колбэк .
Если context не указан, используется текущий контекст.

functools.partial() можно использовать для передачи параметров
колбэку, например:

```python
# Вызвать 'print("Future:", fut)', когда 'fut' выполнен.


fut
.
add_done_callback
(

    
functools
.
partial
(
print
,
 
"Future:"
))
```

Изменено в версии 3.7: Добавлен параметр context , передаваемый только по ключу.
См. PEP 567 для подробностей.

**remove_done_callback ( callback )**

Удаляет колбэк из списка колбэков.

Возвращает количество удаленных колбэков, обычно 1,
если колбэк не был добавлен более одного раза.

**cancel ( msg = None )**

Отменяет Future и планирует колбэки.

Если Future уже имеет статус done или cancelled , возвращает False .
В противном случае меняет состояние Future на cancelled ,
планирует колбэки и возвращает True .

Необязательный строковый аргумент msg передаётся в качестве аргумента исключению CancelledError , которое возбуждается при ожидании отменённого Future.

Изменено в версии 3.9: Добавлен параметр msg .

**exception ( )**

Возвращает исключение, которое было установлено для этого Future.

Исключение (или None , если исключение не было установлено) возвращается только в том случае, если Future находится в состоянии done .

Если Future был отменён , то этот метод возбуждает исключение CancelledError .

Если Future ещё не находится в состоянии done , то этот метод возбуждает исключение InvalidStateError .

**get_loop ( )**

Возвращает цикл событий, к которому привязан объект Future.

Добавлено в версии 3.7.

В этом примере создаётся объект Future, создаётся и планируется асинхронная задача для установки результата для Future, и выполняется ожидание, пока Future не получит результат:

```python
async
 
def
 
set_after
(
fut
,
 
delay
,
 
value
):

    
# Приостановиться на *delay* секунд.

    
await
 
asyncio
.
sleep
(
delay
)


    
# Установить *value* в качестве результата *fut* Future.

    
fut
.
set_result
(
value
)



async
 
def
 
main
():

    
# Получить текущий цикл событий.

    
loop
 
=
 
asyncio
.
get_running_loop
()


    
# Создать новый объект Future.

    
fut
 
=
 
loop
.
create_future
()


    
# Запустить корутину "set_after()" в параллельной задаче.

    
# Мы используем низкоуровневый API "loop.create_task()", потому что

    
# у нас уже есть ссылка на цикл событий под рукой.

    
# В противном случае мы могли бы просто использовать "asyncio.create_task()".

    
loop
.
create_task
(

        
set_after
(
fut
,
 
1
,
 
'... world'
))


    
print
(
'hello ...'
)


    
# Ждать, пока *fut* не получит результат (1 секунда), и вывести его.

    
print
(
await
 
fut
)



asyncio
.
run
(
main
())
```

Важно

Объект Future был разработан для подражания concurrent.futures.Future . Основные отличия включают:

- в отличие от asyncio Futures, экземпляры concurrent.futures.Future не могут быть ожидаемыми.

в отличие от asyncio Futures, экземпляры concurrent.futures.Future не могут быть ожидаемыми.

- asyncio.Future.result() и asyncio.Future.exception() не принимают аргумент timeout .

asyncio.Future.result() и asyncio.Future.exception() не принимают аргумент timeout .

- asyncio.Future.result() и asyncio.Future.exception() возбуждают исключение InvalidStateError , когда Future не находится в состоянии done .

asyncio.Future.result() и asyncio.Future.exception() возбуждают исключение InvalidStateError , когда Future не находится в состоянии done .

- Колбэки, зарегистрированные с помощью asyncio.Future.add_done_callback() , не вызываются немедленно. Вместо этого они планируются с помощью loop.call_soon() .

Колбэки, зарегистрированные с помощью asyncio.Future.add_done_callback() , не вызываются немедленно. Вместо этого они планируются с помощью loop.call_soon() .

- asyncio Future несовместим с функциями concurrent.futures.wait() и concurrent.futures.as_completed() .

asyncio Future несовместим с функциями concurrent.futures.wait() и concurrent.futures.as_completed() .

- asyncio.Future.cancel() принимает необязательный аргумент msg , а concurrent.futures.Future.cancel() – нет.

asyncio.Future.cancel() принимает необязательный аргумент msg , а concurrent.futures.Future.cancel() – нет.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.