> Источник: https://asyncio.ru/3.15/library/asyncio-stream.html — перевод документации Python (PSF).

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

- StreamReader

- StreamWriter

- Examples Примеры TCP echo client using streams TCP-эхо-клиент с использованием потоков данных TCP echo server using streams TCP-эхо-сервер с использованием потоков данных Get HTTP headers Получение HTTP-заголовков Register an open socket to wait for data using streams Регистрация открытого сокета для ожидания данных с использованием потоков данных

- TCP echo client using streams TCP-эхо-клиент с использованием потоков данных

- TCP echo server using streams TCP-эхо-сервер с использованием потоков данных

- Get HTTP headers Получение HTTP-заголовков

- Register an open socket to wait for data using streams Регистрация открытого сокета для ожидания данных с использованием потоков данных

# Streams Потоки данных ​

Исходный код: Lib/asyncio/streams.py

Потоки данных – это высокоуровневые примитивы, готовые к использованию с async/await, для работы с сетевыми соединениями. Потоки данных позволяют отправлять и получать данные без использования колбэков или низкоуровневых протоколов и транспортов.

Вот пример TCP-эхо-клиента, написанного с использованием asyncio
потоков данных:

```python
import
 
asyncio



async
 
def
 
tcp_echo_client
(
message
):

    
reader
,
 
writer
 
=
 
await
 
asyncio
.
open_connection
(

        
'127.0.0.1'
,
 
8888
)


    
print
(
f
'Send: 
{
message
!r}
'
)

    
writer
.
write
(
message
.
encode
())

    
await
 
writer
.
drain
()


    
data
 
=
 
await
 
reader
.
read
(
100
)

    
print
(
f
'Received: 
{
data
.
decode
()
!r}
'
)


    
print
(
'Close the connection'
)

    
writer
.
close
()

    
await
 
writer
.
wait_closed
()



asyncio
.
run
(
tcp_echo_client
(
'Hello World!'
))
```

Смотрите также раздел Примеры ниже.

Функции потоков данных

Следующие функции верхнего уровня asyncio можно использовать для создания
и работы с потоками данных:

**async asyncio. open_connection ( host = None , port = None , * , limit = None , ssl = None , family = 0 , proto = 0 , flags = 0 , sock = None , local_addr = None , server_hostname = None , ssl_handshake_timeout = None , ssl_shutdown_timeout = None , happy_eyeballs_delay = None , interleave = None )**

Устанавливает сетевое соединение и возвращает пару
объектов (reader, writer) .

Возвращаемые объекты reader и writer являются экземплярами
классов StreamReader и StreamWriter .

limit определяет ограничение размера буфера, используемое
возвращаемым экземпляром StreamReader . По умолчанию limit установлен в 64 КиБ.

Остальные аргументы передаются непосредственно
в loop.create_connection() .

Примечание

Аргумент sock передает владение сокетом созданному StreamWriter . Чтобы закрыть сокет, вызовите его
метод close() .

Изменено в версии 3.7: Добавлен параметр ssl_handshake_timeout .

Изменено в версии 3.8: Добавлены параметры happy_eyeballs_delay и interleave .

Изменено в версии 3.10: Удалён параметр loop .

Изменено в версии 3.11: Добавлен параметр ssl_shutdown_timeout .

**async asyncio. start_server ( client_connected_cb , host = None , port = None , * , limit = None , family = socket.AF_UNSPEC , flags = socket.AI_PASSIVE , sock = None , backlog = 100 , ssl = None , reuse_address = None , reuse_port = None , keep_alive = None , ssl_handshake_timeout = None , ssl_shutdown_timeout = None , start_serving = True )**

Запускает сокет-сервер.

Колбэк client_connected_cb вызывается каждый раз, когда устанавливается новое клиентское
соединение. Он получает пару (reader, writer) в качестве двух аргументов, экземпляры классов StreamReader и StreamWriter .

client_connected_cb может быть обычным вызываемым объектом или корутинной функцией ; если это корутинная функция,
она будет автоматически запланирована как Task .

limit определяет ограничение размера буфера, используемое
возвращаемым экземпляром StreamReader . По умолчанию limit установлен в 64 КиБ.

Остальные аргументы передаются непосредственно
в loop.create_server() .

Примечание

Аргумент sock передаёт право владения сокетом созданному серверу. Чтобы закрыть сокет, вызовите метод close() сервера.

Изменено в версии 3.7: Добавлены параметры ssl_handshake_timeout и start_serving .

Изменено в версии 3.10: Удалён параметр loop .

Изменено в версии 3.11: Добавлен параметр ssl_shutdown_timeout .

Изменено в версии 3.13: Добавлен параметр keep_alive .

Unix-сокеты

**async asyncio. open_unix_connection ( path = None , * , limit = None , ssl = None , sock = None , server_hostname = None , ssl_handshake_timeout = None , ssl_shutdown_timeout = None )**

Устанавливает соединение через Unix-сокет и возвращает пару (reader, writer) .

Аналогично open_connection() , но работает с Unix-сокетами.

См. также документацию loop.create_unix_connection() .

Примечание

Аргумент sock передает владение сокетом созданному StreamWriter . Чтобы закрыть сокет, вызовите его
метод close() .

Доступность : Unix.

Изменено в версии 3.7: Добавлен параметр ssl_handshake_timeout .
Параметр path теперь может быть объектом, подобным пути

Изменено в версии 3.10: Удалён параметр loop .

Изменено в версии 3.11: Добавлен параметр ssl_shutdown_timeout .

**async asyncio. start_unix_server ( client_connected_cb , path = None , * , limit = None , sock = None , backlog = 100 , ssl = None , ssl_handshake_timeout = None , ssl_shutdown_timeout = None , start_serving = True , cleanup_socket = True )**

Запустить сервер Unix-сокетов.

Похож на start_server() , но работает с сокетами Unix.

Если cleanup_socket равен true, то сокет Unix будет автоматически удалён из файловой системы при закрытии сервера, если только сокет не был заменён после создания сервера.

См. также документацию loop.create_unix_server() .

Примечание

Аргумент sock передаёт право владения сокетом созданному серверу. Чтобы закрыть сокет, вызовите метод close() сервера.

Доступность : Unix.

Изменено в версии 3.7: Добавлены параметры ssl_handshake_timeout и start_serving .
Параметр path теперь может быть объектом, подобным пути .

Изменено в версии 3.10: Удалён параметр loop .

Изменено в версии 3.11: Добавлен параметр ssl_shutdown_timeout .

Изменено в версии 3.13: Добавлен параметр cleanup_socket .

## StreamReader ​

**class asyncio. StreamReader**

Представляет объект чтения, предоставляющий API для чтения данных
из потока ввода-вывода. Будучи асинхронным итератором , этот
объект поддерживает инструкцию async for .

Не рекомендуется создавать объекты StreamReader напрямую; вместо этого используйте open_connection() и start_server() .

**feed_eof ( )**

Подтверждает EOF.

**async read ( n = -1 )**

Читает до n байт из потока.

Если n не указан или равен -1 ,
читает до EOF, затем возвращает все прочитанные bytes .
Если получен EOF и внутренний буфер пуст,
возвращает пустой объект bytes .

Если n равен 0 , немедленно возвращает пустой объект bytes .

Если n положителен, возвращает не более n доступных bytes ,
как только во внутреннем буфере появляется хотя бы 1 байт.
Если EOF получен до чтения какого-либо байта, возвращает пустой
объект bytes .

**async readline ( )**

Читает одну строку, где «строка» – это последовательность байт,
заканчивающаяся \n .

Если получен EOF и \n не найден, метод
возвращает частично прочитанные данные.

Если получен EOF и внутренний буфер пуст,
возвращает пустой объект bytes .

**async readexactly ( n )**

Читает ровно n байт.

Возбуждает IncompleteReadError , если EOF достигнут до того, как
удалось прочитать n . Используйте атрибут IncompleteReadError.partial ,
чтобы получить частично прочитанные данные.

**async readuntil ( separator = b'\n' )**

Читает данные из потока, пока не будет найден separator .

В случае успеха данные и разделитель удаляются из
внутреннего буфера (потребляются). Возвращаемые данные будут включать
разделитель в конце.

Если объем прочитанных данных превышает настроенное ограничение потока,
возбуждается исключение LimitOverrunError , и данные
остаются во внутреннем буфере и могут быть прочитаны снова.

Если EOF достигнут до того, как найден полный разделитель,
возбуждается исключение IncompleteReadError , и внутренний
буфер сбрасывается. Атрибут IncompleteReadError.partial может содержать часть разделителя.

separator также может быть кортежем разделителей. В этом
случае возвращаемое значение будет кратчайшим возможным, имеющим любой
разделитель в качестве суффикса. Для целей LimitOverrunError кратчайшим возможным разделителем считается тот, который совпал.

Добавлено в версии 3.5.2.

Изменено в версии 3.13: Параметр separator теперь может быть tuple разделителей.

**at_eof ( )**

Возвращает True , если буфер пуст и был вызван feed_eof() .

## StreamWriter ​

**class asyncio. StreamWriter**

Представляет объект writer, который предоставляет API для записи данных в поток ввода-вывода.

Не рекомендуется создавать объекты StreamWriter напрямую; вместо этого используйте open_connection() и start_server() .

**write ( data )**

Метод пытается немедленно записать data в нижележащий сокет. Если это не удаётся, данные помещаются во внутренний буфер записи, пока их не удастся отправить.

Буфер data должен быть объектом bytes, bytearray или C-contiguous одномерным memoryview.

Метод следует использовать вместе с методом drain() :

```python
stream
.
write
(
data
)


await
 
stream
.
drain
()
```

**writelines ( data )**

Метод немедленно записывает список (или любой итерируемый объект) байтов в нижележащий сокет. Если это не удаётся, данные помещаются во внутренний буфер записи, пока их не удастся отправить.

Метод следует использовать вместе с методом drain() :

```python
stream
.
writelines
(
lines
)


await
 
stream
.
drain
()
```

**close ( )**

Метод закрывает поток и нижележащий сокет.

Метод следует использовать, хотя это не обязательно, вместе с методом wait_closed() :

```python
stream
.
close
()


await
 
stream
.
wait_closed
()
```

**can_write_eof ( )**

Возвращает True , если нижележащий транспорт поддерживает метод write_eof() , иначе False .

**write_eof ( )**

Закрывает записывающий конец потока после сброса данных буфера записи.

**transport**

Возвращает нижележащий транспорт asyncio.

**get_extra_info ( name , default = None )**

Предоставляет доступ к дополнительной информации о транспорте; подробнее см. BaseTransport.get_extra_info() .

**async drain ( )**

Ожидает, пока не станет уместно возобновить запись в поток. Пример:

```python
writer
.
write
(
data
)


await
 
writer
.
drain
()
```

Это метод управления потоком, который взаимодействует с нижележащим буфером записи ввода-вывода. Когда размер буфера достигает верхней отметки (high watermark), drain() блокируется, пока размер буфера не уменьшится до нижней отметки (low watermark) и запись не сможет быть возобновлена. Когда ждать нечего, drain() возвращает управление немедленно.

**async start_tls ( sslcontext , * , server_hostname = None , ssl_handshake_timeout = None , ssl_shutdown_timeout = None )**

Обновляет существующее потоковое соединение до TLS.

Параметры:

- sslcontext : настроенный экземпляр SSLContext .

sslcontext : настроенный экземпляр SSLContext .

- server_hostname : устанавливает или переопределяет имя хоста, с которым будет сопоставляться сертификат целевого сервера.

server_hostname : устанавливает или переопределяет имя хоста, с которым будет сопоставляться сертификат целевого сервера.

- ssl_handshake_timeout – время в секундах ожидания завершения TLS-рукопожатия, прежде чем прервать соединение. 60.0 секунд, если None (по умолчанию).

ssl_handshake_timeout – время в секундах ожидания завершения TLS-рукопожатия, прежде чем прервать соединение. 60.0 секунд, если None (по умолчанию).

- ssl_shutdown_timeout – это время в секундах ожидания завершения SSL-завершения перед разрывом соединения. 30.0 секунд, если None (по умолчанию).

ssl_shutdown_timeout – это время в секундах ожидания завершения SSL-завершения перед разрывом соединения. 30.0 секунд, если None (по умолчанию).

Добавлено в версии 3.11.

Изменено в версии 3.12: Добавлен параметр ssl_shutdown_timeout .

**is_closing ( )**

Возвращает True , если поток закрыт или находится в процессе закрытия.

Добавлено в версии 3.7.

**async wait_closed ( )**

Ожидает закрытия потока данных.

Должен вызываться после close() , чтобы дождаться закрытия базового соединения, гарантируя, что все данные были сброшены перед, например, выходом из программы.

Добавлено в версии 3.7.

## Examples Примеры ​

### TCP echo client using streams TCP-эхо-клиент с использованием потоков данных ​

TCP-эхо-клиент с использованием функции asyncio.open_connection() :

```python
import
 
asyncio



async
 
def
 
tcp_echo_client
(
message
):

    
reader
,
 
writer
 
=
 
await
 
asyncio
.
open_connection
(

        
'127.0.0.1'
,
 
8888
)


    
print
(
f
'Send: 
{
message
!r}
'
)

    
writer
.
write
(
message
.
encode
())

    
await
 
writer
.
drain
()


    
data
 
=
 
await
 
reader
.
read
(
100
)

    
print
(
f
'Received: 
{
data
.
decode
()
!r}
'
)


    
print
(
'Close the connection'
)

    
writer
.
close
()

    
await
 
writer
.
wait_closed
()



asyncio
.
run
(
tcp_echo_client
(
'Hello World!'
))
```

Смотрите также

Пример протокола TCP-эхо-клиента использует низкоуровневый метод loop.create_connection() .

### TCP echo server using streams TCP-эхо-сервер с использованием потоков данных ​

TCP-эхо-сервер с использованием функции asyncio.start_server() :

```python
import
 
asyncio



async
 
def
 
handle_echo
(
reader
,
 
writer
):

    
data
 
=
 
await
 
reader
.
read
(
100
)

    
message
 
=
 
data
.
decode
()

    
addr
 
=
 
writer
.
get_extra_info
(
'peername'
)


    
print
(
f
"Received 
{
message
!r}
 from 
{
addr
!r}
"
)


    
print
(
f
"Send: 
{
message
!r}
"
)

    
writer
.
write
(
data
)

    
await
 
writer
.
drain
()


    
print
(
"Close the connection"
)

    
writer
.
close
()

    
await
 
writer
.
wait_closed
()



async
 
def
 
main
():

    
server
 
=
 
await
 
asyncio
.
start_server
(

        
handle_echo
,
 
'127.0.0.1'
,
 
8888
)


    
addrs
 
=
 
', '
.
join
(
str
(
sock
.
getsockname
())
 
for
 
sock
 
in
 
server
.
sockets
)

    
print
(
f
'Serving on 
{
addrs
}
'
)


    
async
 
with
 
server
:

        
await
 
server
.
serve_forever
()



asyncio
.
run
(
main
())
```

Смотрите также

Пример протокола TCP-эхо-сервера использует метод loop.create_server() .

### Get HTTP headers Получение HTTP-заголовков ​

Простой пример запроса HTTP-заголовков URL, переданного в командной строке:

```python
import
 
asyncio


import
 
urllib.parse


import
 
sys



async
 
def
 
print_http_headers
(
url
):

    
url
 
=
 
urllib
.
parse
.
urlsplit
(
url
)

    
if
 
url
.
scheme
 
==
 
'https'
:

        
reader
,
 
writer
 
=
 
await
 
asyncio
.
open_connection
(

            
url
.
hostname
,
 
443
,
 
ssl
=
True
)

    
else
:

        
reader
,
 
writer
 
=
 
await
 
asyncio
.
open_connection
(

            
url
.
hostname
,
 
80
)


    
query
 
=
 
(

        
f
"HEAD 
{
url
.
path
 
or
 
'/'
}
 HTTP/1.0
\r\n
"

        
f
"Host: 
{
url
.
hostname
}
\r\n
"

        
f
"
\r\n
"

    
)


    
writer
.
write
(
query
.
encode
(
'latin-1'
))

    
while
 
True
:

        
line
 
=
 
await
 
reader
.
readline
()

        
if
 
not
 
line
:

            
break


        
line
 
=
 
line
.
decode
(
'latin1'
)
.
rstrip
()

        
if
 
line
:

            
print
(
f
'HTTP header> 
{
line
}
'
)


    
# Игнорировать тело, закрыть сокет

    
writer
.
close
()

    
await
 
writer
.
wait_closed
()



url
 
=
 
sys
.
argv
[
1
]


asyncio
.
run
(
print_http_headers
(
url
))
```

Использование:

```python
python
 
example
.
py
 
http
:
//
example
.
com
/
path
/
page
.
html
```

или с HTTPS:

```python
python
 
example
.
py
 
https
:
//
example
.
com
/
path
/
page
.
html
```

### Register an open socket to wait for data using streams Регистрация открытого сокета для ожидания данных с использованием потоков данных ​

Корутина, ожидающая получения данных сокетом с помощью функции open_connection() :

```python
import
 
asyncio


import
 
socket



async
 
def
 
wait_for_data
():

    
# Получить ссылку на текущий цикл событий, потому что

    
# мы хотим получить доступ к низкоуровневым API.

    
loop
 
=
 
asyncio
.
get_running_loop
()


    
# Создать пару соединённых сокетов.

    
rsock
,
 
wsock
 
=
 
socket
.
socketpair
()


    
# Зарегистрировать открытый сокет для ожидания данных.

    
reader
,
 
writer
 
=
 
await
 
asyncio
.
open_connection
(
sock
=
rsock
)


    
# Симулировать приём данных из сети

    
loop
.
call_soon
(
wsock
.
send
,
 
'abc'
.
encode
())


    
# Ожидать данные

    
data
 
=
 
await
 
reader
.
read
(
100
)


    
# Получены данные, готово: закрыть сокет

    
print
(
"Received:"
,
 
data
.
decode
())

    
writer
.
close
()

    
await
 
writer
.
wait_closed
()


    
# Закрыть второй сокет

    
wsock
.
close
()



asyncio
.
run
(
wait_for_data
())
```

Смотрите также

Пример регистрации открытого сокета для ожидания данных с помощью протокола использует низкоуровневый протокол и метод loop.create_connection() .

Пример отслеживания файлового дескриптора на наличие событий чтения использует низкоуровневый метод loop.add_reader() для наблюдения за файловым дескриптором.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.