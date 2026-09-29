> Источник: https://asyncio.ru/3.15/library/asyncio-dev.html — перевод документации Python (PSF).

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

- Debug Mode Режим отладки

- Concurrency and Multithreading Конкурентность и многопоточность

- Running Blocking Code Выполнение блокирующего кода

- Logging Логирование

- Detect never-awaited coroutines Обнаружение корутин, которые никогда не ожидаются

- Detect never-retrieved exceptions Обнаружение исключений, которые никогда не извлекаются

- Asynchronous generators best practices Рекомендации по работе с асинхронными генераторами Close asynchronous generators explicitly Явное закрытие асинхронных генераторов Create asynchronous generators only when the event loop is running Создание асинхронных генераторов только при работающем цикле событий Avoid concurrent iteration and closure of the same generator Избегайте одновременной итерации и закрытия одного и того же генератора

- Close asynchronous generators explicitly Явное закрытие асинхронных генераторов

- Create asynchronous generators only when the event loop is running Создание асинхронных генераторов только при работающем цикле событий

- Avoid concurrent iteration and closure of the same generator Избегайте одновременной итерации и закрытия одного и того же генератора

# Developing with asyncio Разработка с asyncio ​

Асинхронное программирование отличается от классического «последовательного»
программирования.

На этой странице перечислены распространённые ошибки и ловушки и объясняется, как
их избежать.

## Debug Mode Режим отладки ​

По умолчанию asyncio работает в рабочем режиме.  Для упрощения
разработки asyncio имеет режим отладки .

Есть несколько способов включить режим отладки asyncio:

- Установка переменной окружения PYTHONASYNCIODEBUG в значение 1 .

Установка переменной окружения PYTHONASYNCIODEBUG в значение 1 .

- Использование режима разработки Python .

Использование режима разработки Python .

- Передача debug=True в asyncio.run() .

Передача debug=True в asyncio.run() .

- Вызов loop.set_debug() .

Вызов loop.set_debug() .

Помимо включения режима отладки, также рекомендуется:

- установка уровня журналирования регистратора asyncio в logging.DEBUG , например следующий фрагмент кода
можно запустить при запуске приложения: python logging . basicConfig ( level = logging . DEBUG )

установка уровня журналирования регистратора asyncio в logging.DEBUG , например следующий фрагмент кода
можно запустить при запуске приложения:

```python
logging
.
basicConfig
(
level
=
logging
.
DEBUG
)
```

- настройка модуля warnings для отображения
предупреждений ResourceWarning .  Один из способов сделать это –
использовать параметр командной строки -W default .

настройка модуля warnings для отображения
предупреждений ResourceWarning .  Один из способов сделать это –
использовать параметр командной строки -W default .

Когда режим отладки включен:

- Многие небезопасные в контексте потоков API asyncio (такие как методы loop.call_soon() и loop.call_at() ) вызывают исключение, если они вызваны
из неправильного потока.

Многие небезопасные в контексте потоков API asyncio (такие как методы loop.call_soon() и loop.call_at() ) вызывают исключение, если они вызваны
из неправильного потока.

- Время выполнения селектора ввода-вывода регистрируется, если выполнение операции ввода-вывода занимает слишком много времени.

Время выполнения селектора ввода-вывода регистрируется, если выполнение операции ввода-вывода занимает слишком много времени.

- Колбэки, выполняющиеся дольше 100 миллисекунд, регистрируются.  Атрибут loop.slow_callback_duration можно использовать для установки
минимальной продолжительности выполнения в секундах, которая считается «медленной».

Колбэки, выполняющиеся дольше 100 миллисекунд, регистрируются.  Атрибут loop.slow_callback_duration можно использовать для установки
минимальной продолжительности выполнения в секундах, которая считается «медленной».

## Concurrency and Multithreading Конкурентность и многопоточность ​

Цикл событий выполняется в потоке (обычно в главном потоке) и выполняет
все колбэки и задачи в своём потоке.  Пока задача выполняется в
цикле событий, никакие другие задачи не могут выполняться в том же потоке.  Когда задача
выполняет выражение await , выполняющаяся задача приостанавливается, и
цикл событий выполняет следующую задачу.

Для планирования колбэка из другого потока ОС следует использовать метод loop.call_soon_threadsafe() . Пример:

```python
loop
.
call_soon_threadsafe
(
callback
,
 
*
args
)
```

Почти все объекты asyncio не являются потокобезопасными, что обычно
не является проблемой, если только нет кода, работающего с ними извне
задачи или колбэка.  Если такому коду необходимо вызвать
низкоуровневое API asyncio, следует использовать метод loop.call_soon_threadsafe() ,
например:

```python
loop
.
call_soon_threadsafe
(
fut
.
cancel
)
```

Для планирования объекта корутины из другого потока ОС следует использовать функцию run_coroutine_threadsafe() . Она возвращает concurrent.futures.Future для доступа к результату:

```python
async
 
def
 
coro_func
():

     
return
 
await
 
asyncio
.
sleep
(
1
,
 
42
)



# Позже в другом потоке ОС:



future
 
=
 
asyncio
.
run_coroutine_threadsafe
(
coro_func
(),
 
loop
)


# Ожидайте результат:


result
 
=
 
future
.
result
()
```

Для обработки сигналов цикл событий должен
выполняться в главном потоке.

Метод loop.run_in_executor() можно использовать с concurrent.futures.ThreadPoolExecutor или InterpreterPoolExecutor для выполнения
блокирующего кода в другом потоке ОС без блокировки потока ОС,
в котором выполняется цикл событий.

В настоящее время нет возможности напрямую планировать корутины или колбэки
из другого процесса (например, запущенного с помощью multiprocessing ). Раздел Методы цикла событий перечисляет API, которые могут читать из каналов и отслеживать файловые дескрипторы
без блокировки цикла событий. Кроме того, API asyncio Подпроцесс предоставляют способ запуска
процесса и общения с ним из цикла событий. Наконец, упомянутый ранее метод loop.run_in_executor() также можно использовать
с concurrent.futures.ProcessPoolExecutor для выполнения
кода в другом процессе.

## Running Blocking Code Выполнение блокирующего кода ​

Блокирующий (привязанный к ЦП) код не должен вызываться напрямую. Например, если функция выполняет ресурсоёмкие вычисления в течение 1 секунды, все конкурентные задачи asyncio и операции ввода-вывода будут задержаны на 1 секунду.

Исполнитель можно использовать для выполнения задачи в другом потоке, в том числе в другом интерпретаторе или даже в другом процессе, чтобы избежать блокировки потока ОС вместе с циклом событий. Подробнее см. в описании метода loop.run_in_executor() .

## Logging Логирование ​

asyncio использует модуль logging , и всё логирование выполняется через регистратор "asyncio" .

Уровень логирования по умолчанию – logging.INFO , который можно легко изменить:

```python
logging
.
getLogger
(
"asyncio"
)
.
setLevel
(
logging
.
WARNING
)
```

Сетевое логирование может блокировать цикл событий. Рекомендуется использовать отдельный поток для обработки логов или неблокирующий ввод-вывод. Например, см. Работа с блокирующими обработчиками .

## Detect never-awaited coroutines Обнаружение корутин, которые никогда не ожидаются ​

Когда корутинная функция вызывается, но не ожидается (например, coro() вместо await coro() ) или корутина не запланирована через asyncio.create_task() , asyncio выдаст RuntimeWarning :

```python
import
 
asyncio



async
 
def
 
test
():

    
print
(
"never scheduled"
)



async
 
def
 
main
():

    
test
()



asyncio
.
run
(
main
())
```

Вывод:

```python
test
.
py
:
7
:
 
RuntimeWarning
:
 
coroutine
 
'test'
 
was
 
never
 
awaited

  
test
()
```

Вывод в режиме отладки:

```python
test
.
py
:
7
:
 
RuntimeWarning
:
 
coroutine
 
'test'
 
was
 
never
 
awaited


Coroutine
 
created
 
at
 
(
most
 
recent
 
call
 
last
)

  
File
 
"../t.py"
,
 
line
 
9
,
 
in
 
<
module
>

    
asyncio
.
run
(
main
(),
 
debug
=
True
)


  
<
 
..
 
>


  
File
 
"../t.py"
,
 
line
 
7
,
 
in
 
main

    
test
()

  
test
()
```

Обычное исправление – либо ожидать корутину, либо вызвать функцию asyncio.create_task() :

```python
async
 
def
 
main
():

    
await
 
test
()
```

## Detect never-retrieved exceptions Обнаружение исключений, которые никогда не извлекаются ​

Если вызывается Future.set_exception() , но объект Future никогда не ожидается, исключение никогда не будет передано в пользовательский код. В этом случае asyncio выдаст сообщение в лог, когда объект Future будет собран сборщиком мусора.

Пример необработанного исключения:

```python
import
 
asyncio



async
 
def
 
bug
():

    
raise
 
Exception
(
"not consumed"
)



async
 
def
 
main
():

    
asyncio
.
create_task
(
bug
())



asyncio
.
run
(
main
())
```

Вывод:

```python
Task
 
exception
 
was
 
never
 
retrieved


future
:
 
<
Task
 
finished
 
coro
=<
bug
()
 
done
,
 
defined
 
at
 
test
.
py
:
3
>

  
exception
=
Exception
(
'not consumed'
)
>



Traceback
 
(
most
 
recent
 
call
 
last
):

  
File
 
"test.py"
,
 
line
 
4
,
 
in
 
bug

    
raise
 
Exception
(
"not consumed"
)


Exception
:
 
not
 
consumed
```

Включите режим отладки , чтобы получить трассировку, где была создана задача:

```python
asyncio
.
run
(
main
(),
 
debug
=
True
)
```

Вывод в режиме отладки:

```python
Task
 
exception
 
was
 
never
 
retrieved


future
:
 
<
Task
 
finished
 
coro
=<
bug
()
 
done
,
 
defined
 
at
 
test
.
py
:
3
>

    
exception
=
Exception
(
'not consumed'
)
 
created
 
at
 
asyncio
/
tasks
.
py
:
321
>



source_traceback
:
 
Object
 
created
 
at
 
(
most
 
recent
 
call
 
last
):

  
File
 
"../t.py"
,
 
line
 
9
,
 
in
 
<
module
>

    
asyncio
.
run
(
main
(),
 
debug
=
True
)



<
 
..
 
>



Traceback
 
(
most
 
recent
 
call
 
last
):

  
File
 
"../t.py"
,
 
line
 
4
,
 
in
 
bug

    
raise
 
Exception
(
"not consumed"
)


Exception
:
 
not
 
consumed
```

## Asynchronous generators best practices Рекомендации по работе с асинхронными генераторами ​

Написание корректного и эффективного кода asyncio требует осознания определённых подводных камней. В этом разделе описаны основные рекомендации, которые могут сэкономить вам часы отладки.

### Close asynchronous generators explicitly Явное закрытие асинхронных генераторов ​

Рекомендуется вручную закрывать асинхронный генератор . Если генератор завершается раньше времени – например, из-за исключения, возникшего в теле цикла async for , – его асинхронный код очистки может выполняться в неожиданном контексте. Это может произойти после завершения задач, от которых он зависит, или во время остановки цикла событий, когда вызывается хук сборки мусора асинхронного генератора.

Чтобы избежать этого, явно закройте генератор, вызвав его метод aclose() , или используйте контекстный менеджер contextlib.aclosing() :

```python
import
 
asyncio


import
 
contextlib



async
 
def
 
gen
():

  
yield
 
1

  
yield
 
2



async
 
def
 
func
():

  
async
 
with
 
contextlib
.
aclosing
(
gen
())
 
as
 
g
:

    
async
 
for
 
x
 
in
 
g
:

      
break
  
# Не выполняйте итерацию до конца



asyncio
.
run
(
func
())
```

Как отмечено выше, код очистки для этих асинхронных генераторов откладывается. Следующий пример демонстрирует, что финализация асинхронного генератора может происходить в неожиданном порядке:

```python
import
 
asyncio


work_done
 
=
 
False



async
 
def
 
cursor
():

    
try
:

        
yield
 
1

    
finally
:

        
assert
 
work_done



async
 
def
 
rows
():

    
global
 
work_done

    
try
:

        
yield
 
2

    
finally
:

        
await
 
asyncio
.
sleep
(
0.1
)
 
# имитировать некоторую асинхронную работу

        
work_done
 
=
 
True




async
 
def
 
main
():

    
async
 
for
 
c
 
in
 
cursor
():

        
async
 
for
 
r
 
in
 
rows
():

            
break

        
break



asyncio
.
run
(
main
())
```

Для этого примера мы получаем следующий вывод:

```python
unhandled
 
exception
 
during
 
asyncio
.
run
()
 
shutdown


task
:
 
<
Task
 
finished
 
name
=
'Task-3'
 
coro
=<<
async_generator_athrow
 
without
 
__name__
>
()
>
 
exception
=
AssertionError
()
>


Traceback
 
(
most
 
recent
 
call
 
last
):

  
File
 
"example.py"
,
 
line
 
6
,
 
in
 
cursor

    
yield
 
1


asyncio
.
exceptions
.
CancelledError



During
 
handling
 
of
 
the
 
above
 
exception
,
 
another
 
exception
 
occurred
:



Traceback
 
(
most
 
recent
 
call
 
last
):

  
File
 
"example.py"
,
 
line
 
8
,
 
in
 
cursor

    
assert
 
work_done

           
^^^^^^^^^


AssertionError
```

Асинхронный генератор cursor() был финализирован до генератора rows – неожиданное поведение.

Пример можно исправить, явно закрыв асинхронные генераторы cursor и rows :

```python
async
 
def
 
main
():

    
async
 
with
 
contextlib
.
aclosing
(
cursor
())
 
as
 
cursor_gen
:

        
async
 
for
 
c
 
in
 
cursor_gen
:

            
async
 
with
 
contextlib
.
aclosing
(
rows
())
 
as
 
rows_gen
:

                
async
 
for
 
r
 
in
 
rows_gen
:

                    
break

            
break
```

### Create asynchronous generators only when the event loop is running Создание асинхронных генераторов только при работающем цикле событий ​

Рекомендуется создавать асинхронные генераторы только после создания цикла событий.

Чтобы обеспечить надёжное закрытие асинхронных генераторов, цикл событий использует функцию sys.set_asyncgen_hooks() для регистрации функций колбэков. Эти колбэки обновляют список работающих асинхронных генераторов, чтобы поддерживать его в согласованном состоянии.

Когда вызывается функция loop.shutdown_asyncgens() , работающие генераторы останавливаются корректно, и список очищается.

Асинхронный генератор вызывает соответствующий системный хук во время своей первой итерации. В то же время генератор записывает, что хук был вызван, и больше не вызывает его.

Следовательно, если итерация начинается до создания цикла событий, цикл событий не сможет добавить генератор в свой список активных генераторов, потому что хуки устанавливаются после того, как генератор пытается их вызвать. В результате цикл событий не сможет завершить генератор при необходимости.

Рассмотрим следующий пример:

```python
import
 
asyncio



async
 
def
 
agenfn
():

    
try
:

        
yield
 
10

    
finally
:

        
await
 
asyncio
.
sleep
(
0
)




with
 
asyncio
.
Runner
()
 
as
 
runner
:

    
agen
 
=
 
agenfn
()

    
print
(
runner
.
run
(
anext
(
agen
)))

    
del
 
agen
```

Вывод:

```python
10


Exception
 
ignored
 
while
 
closing
 
generator
 
<
async_generator
 
object
 
agenfn
 
at
 
0x000002F71CD10D70
>
:


Traceback
 
(
most
 
recent
 
call
 
last
):

  
File
 
"example.py"
,
 
line
 
13
,
 
in
 
<
module
>

    
del
 
agen

        
^^^^


RuntimeError
:
 
async
 
generator
 
ignored
 
GeneratorExit
```

Этот пример можно исправить следующим образом:

```python
import
 
asyncio



async
 
def
 
agenfn
():

    
try
:

        
yield
 
10

    
finally
:

        
await
 
asyncio
.
sleep
(
0
)



async
 
def
 
main
():

    
agen
 
=
 
agenfn
()

    
print
(
await
 
anext
(
agen
))

    
del
 
agen



asyncio
.
run
(
main
())
```

### Avoid concurrent iteration and closure of the same generator Избегайте одновременной итерации и закрытия одного и того же генератора ​

Асинхронные генераторы могут быть повторно вызваны во время выполнения другого __anext__() / athrow() / aclose() вызова. Это может привести к несогласованному состоянию асинхронного генератора и вызвать ошибки.

Рассмотрим следующий пример:

```python
import
 
asyncio



async
 
def
 
consumer
():

    
for
 
idx
 
in
 
range
(
100
):

        
await
 
asyncio
.
sleep
(
0
)

        
message
 
=
 
yield
 
idx

        
print
(
'received'
,
 
message
)



async
 
def
 
amain
():

    
agenerator
 
=
 
consumer
()

    
await
 
agenerator
.
asend
(
None
)


    
fa
 
=
 
asyncio
.
create_task
(
agenerator
.
asend
(
'A'
))

    
fb
 
=
 
asyncio
.
create_task
(
agenerator
.
asend
(
'B'
))

    
await
 
fa

    
await
 
fb



asyncio
.
run
(
amain
())
```

Вывод:

```python
received
 
A


Traceback
 
(
most
 
recent
 
call
 
last
):

  
File
 
"test.py"
,
 
line
 
38
,
 
in
 
<
module
>

    
asyncio
.
run
(
amain
())

    
~~~~~~~~~~~^^^^^^^^^

  
File
 
"Lib/asyncio/runners.py"
,
 
line
 
204
,
 
in
 
run

    
return
 
runner
.
run
(
main
)

           
~~~~~~~~~~^^^^^^

  
File
 
"Lib/asyncio/runners.py"
,
 
line
 
127
,
 
in
 
run

    
return
 
self
.
_loop
.
run_until_complete
(
task
)

           
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^

  
File
 
"Lib/asyncio/base_events.py"
,
 
line
 
719
,
 
in
 
run_until_complete

    
return
 
future
.
result
()

           
~~~~~~~~~~~~~^^

  
File
 
"test.py"
,
 
line
 
36
,
 
in
 
amain

    
await
 
fb


RuntimeError
:
 
anext
():
 
asynchronous
 
generator
 
is
 
already
 
running
```

Поэтому рекомендуется избегать использования асинхронных генераторов в параллельных задачах или в разных циклах событий.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.