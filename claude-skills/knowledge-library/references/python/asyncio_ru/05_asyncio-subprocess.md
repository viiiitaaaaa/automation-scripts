> Источник: https://asyncio.ru/3.15/library/asyncio-subprocess.html — перевод документации Python (PSF).

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

- Creating Subprocesses Создание подпроцессов

- Constants Константы

- Interacting with Subprocesses Взаимодействие с подпроцессами Subprocess and Threads Подпроцессы и потоки Examples Примеры

- Subprocess and Threads Подпроцессы и потоки

- Examples Примеры

# Subprocesses Подпроцессы ​

Исходный код: Lib/asyncio/subprocess.py , Lib/asyncio/base_subprocess.py

В этом разделе описываются высокоуровневые API asyncio с async/await для создания и управления подпроцессами.

Вот пример того, как asyncio может выполнить команду оболочки и получить её результат:

```python
import
 
asyncio



async
 
def
 
run
(
cmd
):

    
proc
 
=
 
await
 
asyncio
.
create_subprocess_shell
(

        
cmd
,

        
stdout
=
asyncio
.
subprocess
.
PIPE
,

        
stderr
=
asyncio
.
subprocess
.
PIPE
)


    
stdout
,
 
stderr
 
=
 
await
 
proc
.
communicate
()


    
print
(
f
'[
{
cmd
!r}
 exited with 
{
proc
.
returncode
}
]'
)

    
if
 
stdout
:

        
print
(
f
'[stdout]
\n
{
stdout
.
decode
()
}
'
)

    
if
 
stderr
:

        
print
(
f
'[stderr]
\n
{
stderr
.
decode
()
}
'
)



asyncio
.
run
(
run
(
'ls /zzz'
))
```

выведет:

```python
[
'ls /zzz'
 
exited
 
with
 
1
]


[
stderr
]


ls
:
 
/
zzz
:
 
No
 
such
 
file
 
or
 
directory
```

Поскольку все функции подпроцессов asyncio являются асинхронными и asyncio предоставляет множество инструментов для работы с такими функциями, легко выполнять и отслеживать несколько подпроцессов параллельно. Действительно, тривиально изменить приведённый выше пример для одновременного выполнения нескольких команд:

```python
async
 
def
 
main
():

    
await
 
asyncio
.
gather
(

        
run
(
'ls /zzz'
),

        
run
(
'sleep 1; echo "hello"'
))



asyncio
.
run
(
main
())
```

См. также подраздел Примеры .

## Creating Subprocesses Создание подпроцессов ​

**async asyncio. create_subprocess_exec ( program , * args , stdin = None , stdout = None , stderr = None , limit = None , ** kwds )**

Создать подпроцесс.

Аргумент limit устанавливает ограничение буфера для обёрток StreamReader для stdout и stderr (если subprocess.PIPE передаётся аргументам stdout и stderr ).

Возвращает экземпляр Process .

Смотрите документацию loop.subprocess_exec() для других
параметров.

Если объект процесса будет собран сборщиком мусора, когда процесс всё ещё выполняется, дочерний процесс будет уничтожен.

Изменено в версии 3.10: Удалён параметр loop .

**async asyncio. create_subprocess_shell ( cmd , stdin = None , stdout = None , stderr = None , limit = None , ** kwds )**

Выполняет команду оболочки cmd .

Аргумент limit устанавливает ограничение буфера для обёрток StreamReader для stdout и stderr (если subprocess.PIPE передаётся аргументам stdout и stderr ).

Возвращает экземпляр Process .

Смотрите документацию loop.subprocess_shell() для других
параметров.

Если объект процесса будет собран сборщиком мусора, когда процесс всё ещё выполняется, дочерний процесс будет уничтожен.

Важно

Ответственность приложения заключается в том, чтобы все пробельные и специальные символы были правильно экранированы для предотвращения уязвимостей внедрения команд оболочки . Функция shlex.quote() может использоваться для правильного экранирования пробельных и специальных символов оболочки в строках, которые будут использоваться для построения команд оболочки.

Изменено в версии 3.10: Удалён параметр loop .

Примечание

Подпроцессы доступны в Windows, если используется ProactorEventLoop . См. Поддержка подпроцессов в Windows для подробностей.

Смотрите также

asyncio также имеет следующие низкоуровневые API для работы с подпроцессами: loop.subprocess_exec() , loop.subprocess_shell() , loop.connect_read_pipe() , loop.connect_write_pipe() ,
а также Транспорты подпроцессов и Протоколы подпроцессов .

## Constants Константы ​

**asyncio.subprocess. PIPE**

Может быть передан параметрам stdin , stdout или stderr .

Если PIPE передаётся аргументу stdin , то атрибут Process.stdin будет указывать на экземпляр StreamWriter .

Если PIPE передаётся аргументам stdout или stderr , то атрибуты Process.stdout и Process.stderr будут указывать на экземпляры StreamReader .

**asyncio.subprocess. STDOUT**

Специальное значение, которое может использоваться как аргумент stderr и указывает, что стандартный поток ошибок должен быть перенаправлен в стандартный вывод.

**asyncio.subprocess. DEVNULL**

Специальное значение, которое может использоваться как аргумент stdin , stdout или stderr для функций создания процессов. Оно указывает, что специальный файл os.devnull будет использоваться для соответствующего потока подпроцесса.

## Interacting with Subprocesses Взаимодействие с подпроцессами ​

Функции create_subprocess_exec() и create_subprocess_shell() возвращают экземпляры класса Process . Process – это высокоуровневая обёртка, которая позволяет взаимодействовать с подпроцессами и отслеживать их завершение.

**class asyncio.subprocess. Process**

Объект, который оборачивает процессы ОС, созданные функциями create_subprocess_exec() и create_subprocess_shell() .

Этот класс предназначен для предоставления API, аналогичного классу subprocess.Popen , но имеются некоторые заметные отличия:

- в отличие от Popen, экземпляры Process не имеют эквивалента методу poll() ;

в отличие от Popen, экземпляры Process не имеют эквивалента методу poll() ;

- методы communicate() и wait() не имеют параметра timeout : используйте функцию wait_for() ;

методы communicate() и wait() не имеют параметра timeout : используйте функцию wait_for() ;

- метод Process.wait() является асинхронным, тогда как метод subprocess.Popen.wait() реализован как блокирующий занятой цикл;

метод Process.wait() является асинхронным, тогда как метод subprocess.Popen.wait() реализован как блокирующий занятой цикл;

- параметр universal_newlines не поддерживается.

параметр universal_newlines не поддерживается.

Этот класс является не потокобезопасным .

См. также раздел Подпроцессы и потоки .

**async wait ( )**

Ожидает завершения дочернего процесса.

Устанавливает и возвращает атрибут returncode .

Примечание

Этот метод может привести к взаимоблокировке при использовании stdout=PIPE или stderr=PIPE , если дочерний процесс генерирует такой большой объём вывода, что он блокируется в ожидании, пока буфер канала ОС сможет принять больше данных. Используйте метод communicate() при использовании каналов, чтобы избежать этой ситуации.

**async communicate ( input = None )**

Взаимодействие с процессом:

- отправляет данные в stdin (если input не равен None );

отправляет данные в stdin (если input не равен None );

- закрывает stdin ;

закрывает stdin ;

- читает данные из stdout и stderr , пока не будет достигнут EOF;

читает данные из stdout и stderr , пока не будет достигнут EOF;

- ожидает завершения процесса.

ожидает завершения процесса.

Необязательный аргумент input – это данные (объект bytes ), которые будут отправлены дочернему процессу.

Возвращает кортеж (stdout_data, stderr_data) .

Если при записи input в stdin возникает исключение BrokenPipeError или ConnectionResetError , оно игнорируется. Это происходит, когда процесс завершается до того, как все данные будут записаны в stdin .

Если требуется отправить данные в stdin процесса, процесс должен быть создан с stdin=PIPE . Аналогично, чтобы получить в результирующем кортеже что-либо, отличное от None , процесс должен быть создан с аргументами stdout=PIPE и/или stderr=PIPE .

Обратите внимание, что прочитанные данные буферизируются в памяти, поэтому не используйте этот метод, если размер данных велик или неограничен.

Изменено в версии 3.12: stdin также закрывается при input=None .

**send_signal ( signal )**

Отправляет сигнал signal дочернему процессу.

Примечание

В Windows SIGTERM является псевдонимом terminate() . Сигналы CTRL_C_EVENT и CTRL_BREAK_EVENT могут быть отправлены процессам, запущенным с параметром creationflags , который включает CREATE_NEW_PROCESS_GROUP .

**terminate ( )**

Останавливает дочерний процесс.

В системах POSIX этот метод отправляет SIGTERM дочернему процессу.

В Windows функция Win32 API TerminateProcess() вызывается для остановки дочернего процесса.

**kill ( )**

Завершить дочерний процесс.

В POSIX-системах этот метод отправляет SIGKILL дочернему процессу.

В Windows этот метод является псевдонимом для terminate() .

**stdin**

Стандартный поток ввода ( StreamWriter ) или None , если процесс был создан с stdin=None .

**stdout**

Стандартный поток вывода ( StreamReader ) или None , если процесс был создан с stdout=None .

**stderr**

Стандартный поток ошибок ( StreamReader ) или None , если процесс был создан с stderr=None .

Предупреждение

Используйте метод communicate() вместо process.stdin.write() , await process.stdout.read() или await process.stderr.read() . Это позволяет избежать взаимоблокировок из-за приостановки чтения или записи потоков и блокировки дочернего процесса.

**pid**

Идентификационный номер процесса (PID).

Обратите внимание, что для процессов, созданных функцией create_subprocess_shell() , этот атрибут является PID порождённой оболочки.

**returncode**

Код возврата процесса при его завершении.

Значение None указывает на то, что процесс ещё не завершён.

Для процессов, созданных с create_subprocess_exec() , отрицательное значение -N указывает, что дочерний процесс был завершён сигналом N (только POSIX).

Для процессов, созданных с create_subprocess_shell() , код возврата отражает статус завершения самой оболочки (например, /bin/sh ), который может отображать сигналы в коды, такие как 128+N . За подробностями обращайтесь к документации оболочки (например, раздел Exit Status руководства Bash).

### Subprocess and Threads Подпроцессы и потоки ​

Стандартный цикл событий asyncio поддерживает запуск подпроцессов из разных потоков по умолчанию.

В Windows подпроцессы поддерживаются только ProactorEventLoop (по умолчанию), SelectorEventLoop не поддерживает подпроцессы.

Обратите внимание, что альтернативные реализации цикла событий могут иметь свои ограничения; обращайтесь к их документации.

Смотрите также

Раздел Конкуренция и многопоточность в asyncio .

### Examples Примеры ​

Пример использования класса Process для управления подпроцессом и класса StreamReader для чтения из его стандартного вывода.

Подпроцесс создаётся функцией create_subprocess_exec() :

```python
import
 
asyncio


import
 
sys



async
 
def
 
get_date
():

    
code
 
=
 
'import datetime as dt; print(dt.datetime.now())'


    
# Создать подпроцесс; перенаправить стандартный вывод

    
# в канал.

    
proc
 
=
 
await
 
asyncio
.
create_subprocess_exec
(

        
sys
.
executable
,
 
'-c'
,
 
code
,

        
stdout
=
asyncio
.
subprocess
.
PIPE
)


    
# Прочитать одну строку вывода.

    
data
 
=
 
await
 
proc
.
stdout
.
readline
()

    
line
 
=
 
data
.
decode
(
'ascii'
)
.
rstrip
()


    
# Дождаться завершения подпроцесса.

    
await
 
proc
.
wait
()

    
return
 
line



date
 
=
 
asyncio
.
run
(
get_date
())


print
(
f
"Current date: 
{
date
}
"
)
```

См. также тот же пример , написанный с использованием низкоуровневых API.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.