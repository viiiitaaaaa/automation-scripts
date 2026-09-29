> Источник: https://asyncio.ru/3.15/library/asyncio-protocol.html — перевод документации Python (PSF).

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

- Transports Транспорты Transports Hierarchy Иерархия транспортов Base Transport Базовый транспорт Read-only Transports Транспорты только для чтения Write-only Transports Транспорты только для записи Datagram Transports Дейтаграммные транспорты Subprocess Transports Транспорты подпроцессов

- Transports Hierarchy Иерархия транспортов

- Base Transport Базовый транспорт

- Read-only Transports Транспорты только для чтения

- Write-only Transports Транспорты только для записи

- Datagram Transports Дейтаграммные транспорты

- Subprocess Transports Транспорты подпроцессов

- Protocols Протоколы Base Protocols Базовые протоколы Base Protocol Базовый протокол Streaming Protocols Потоковые протоколы Buffered Streaming Protocols Буферизованные потоковые протоколы Datagram Protocols Протоколы дейтаграмм Subprocess Protocols Протоколы подпроцессов

- Base Protocols Базовые протоколы

- Base Protocol Базовый протокол

- Streaming Protocols Потоковые протоколы

- Buffered Streaming Protocols Буферизованные потоковые протоколы

- Datagram Protocols Протоколы дейтаграмм

- Subprocess Protocols Протоколы подпроцессов

- Examples Примеры TCP Echo Server TCP-эхо-сервер TCP Echo Client TCP-эхо-клиент UDP Echo Server UDP-эхо-сервер UDP Echo Client UDP-эхо-клиент Connecting Existing Sockets Подключение существующих сокетов loop.subprocess_exec ) and SubprocessProtocol (loop.subprocess_exec() и SubprocessProtocol

- TCP Echo Server TCP-эхо-сервер

- TCP Echo Client TCP-эхо-клиент

- UDP Echo Server UDP-эхо-сервер

- UDP Echo Client UDP-эхо-клиент

- Connecting Existing Sockets Подключение существующих сокетов

- loop.subprocess_exec ) and SubprocessProtocol (loop.subprocess_exec() и SubprocessProtocol

# Transports and Protocols Транспорты и протоколы ​

Предисловие

Транспорты и протоколы используются низкоуровневыми API цикла событий, такими как loop.create_connection() . Они используют стиль программирования на основе колбэков и обеспечивают высокопроизводительные реализации сетевых протоколов или протоколов межпроцессного взаимодействия (например, HTTP).

По сути, транспорты и протоколы следует использовать только в библиотеках и фреймворках, но никогда в высокоуровневых приложениях asyncio.

Эта страница документации охватывает как Транспорты , так и Протоколы .

Введение

На самом высоком уровне транспорт отвечает за то, как передаются байты, в то время как протокол определяет какие байты передавать (и в некоторой степени когда).

Другой способ сказать то же самое: транспорт – это абстракция сокета (или аналогичной конечной точки ввода-вывода), в то время как протокол – это абстракция приложения с точки зрения транспорта.

Ещё одна точка зрения: интерфейсы транспорта и протокола вместе определяют абстрактный интерфейс для использования сетевого ввода-вывода и межпроцессного ввода-вывода.

Между объектами транспорта и протокола всегда существует отношение 1:1: протокол вызывает методы транспорта для отправки данных, а транспорт вызывает методы протокола, чтобы передать ему полученные данные.

Большинство методов цикла событий, ориентированных на соединения (такие как loop.create_connection() ), обычно принимают аргумент protocol_factory , используемый для создания объекта Protocol для принятого соединения, представленного объектом Transport . Такие методы обычно возвращают кортеж из (transport, protocol) .

Содержание

Эта страница документации содержит следующие разделы:

- В разделе Транспорты документируются классы asyncio BaseTransport , ReadTransport , WriteTransport , Transport , DatagramTransport и SubprocessTransport .

В разделе Транспорты документируются классы asyncio BaseTransport , ReadTransport , WriteTransport , Transport , DatagramTransport и SubprocessTransport .

- В разделе Протоколы документируются классы asyncio BaseProtocol , Protocol , BufferedProtocol , DatagramProtocol и SubprocessProtocol .

В разделе Протоколы документируются классы asyncio BaseProtocol , Protocol , BufferedProtocol , DatagramProtocol и SubprocessProtocol .

- Раздел Примеры демонстрирует, как работать с транспортами,
протоколами и низкоуровневыми API цикла событий.

Раздел Примеры демонстрирует, как работать с транспортами,
протоколами и низкоуровневыми API цикла событий.

## Transports Транспорты ​

Исходный код: Lib/asyncio/transports.py

Транспорты – это классы, предоставляемые asyncio для абстрагирования
различных видов коммуникационных каналов.

Объекты транспорта всегда создаются циклом событий asyncio .

Модуль asyncio реализует транспорты для TCP, UDP, SSL и каналов подпроцессов.
Доступные методы зависят от типа транспорта.

Классы транспортов не являются потокобезопасными .

### Transports Hierarchy Иерархия транспортов ​

**class asyncio. BaseTransport**

Базовый класс для всех транспортов. Содержит методы, общие для всех
транспортов asyncio.

**class asyncio. WriteTransport ( BaseTransport )**

Базовый транспорт для соединений только на запись.

Экземпляры класса WriteTransport возвращаются
методом цикла событий loop.connect_write_pipe() , а также используются
методами, связанными с подпроцессами, например loop.subprocess_exec() .

**class asyncio. ReadTransport ( BaseTransport )**

Базовый транспорт для соединений только на чтение.

Экземпляры класса ReadTransport возвращаются
методом цикла событий loop.connect_read_pipe() , а также используются
методами, связанными с подпроцессами, например loop.subprocess_exec() .

**class asyncio. Transport ( WriteTransport , ReadTransport )**

Интерфейс, представляющий двунаправленный транспорт, например
TCP-соединение.

Пользователь не создаёт транспорт напрямую; он вызывает
вспомогательную функцию, передавая ей фабрику протоколов и другую
информацию, необходимую для создания транспорта и протокола.

Экземпляры класса Transport возвращаются или используются
методами цикла событий, такими как loop.create_connection() , loop.create_unix_connection() , loop.create_server() , loop.sendfile() и т.д.

**class asyncio. DatagramTransport ( BaseTransport )**

Транспорт для дейтаграммных (UDP) соединений.

Экземпляры класса DatagramTransport возвращаются
методом цикла событий loop.create_datagram_endpoint() .

**class asyncio. SubprocessTransport ( BaseTransport )**

Абстракция, представляющая соединение между родительским и дочерним
процессом операционной системы.

Экземпляры класса SubprocessTransport возвращаются
методами цикла событий loop.subprocess_shell() и loop.subprocess_exec() .

### Base Transport Базовый транспорт ​

**BaseTransport. close ( )**

Закрыть транспорт.

Если транспорт имеет буфер для исходящих данных, буферизованные данные
будут асинхронно сброшены. Дальнейший приём данных прекратится.
После того, как все буферизованные данные будут сброшены, будет вызван
метод protocol.connection_lost() протокола с аргументом None .
Транспорт нельзя использовать после его закрытия.

**BaseTransport. is_closing ( )**

Возвращает True , если транспорт закрывается или закрыт.

**BaseTransport. get_extra_info ( name , default = None )**

Возвращает информацию о транспорте или базовых ресурсах,
которые он использует.

name – это строка, представляющая фрагмент информации,
специфичной для транспорта, которую необходимо получить.

По умолчанию – это значение, возвращаемое, если информация недоступна, или если транспорт не поддерживает её запрос с данной реализацией цикла событий стороннего производителя или на текущей платформе.

Например, следующий код пытается получить базовый объект сокета транспорта:

```python
sock
 
=
 
transport
.
get_extra_info
(
'socket'
)


if
 
sock
 
is
 
not
 
None
:

    
print
(
sock
.
getsockopt
(
...
))
```

Категории информации, которые можно запросить для некоторых транспортов:

- сокет: 'peername' : удаленный адрес, к которому подключен сокет, результат socket.socket.getpeername() ( None в случае ошибки) 'socket' : экземпляр socket.socket 'sockname' : собственный адрес сокета,
результат socket.socket.getsockname()

сокет:

- 'peername' : удаленный адрес, к которому подключен сокет, результат socket.socket.getpeername() ( None в случае ошибки)

'peername' : удаленный адрес, к которому подключен сокет, результат socket.socket.getpeername() ( None в случае ошибки)

- 'socket' : экземпляр socket.socket

'socket' : экземпляр socket.socket

- 'sockname' : собственный адрес сокета,
результат socket.socket.getsockname()

'sockname' : собственный адрес сокета,
результат socket.socket.getsockname()

- SSL-сокет: 'compression' : используемый алгоритм сжатия в виде строки, или None , если соединение не сжато; результат ssl.SSLSocket.compression() 'cipher' : кортеж из трех значений, содержащий имя используемого шифра, версию протокола SSL, определяющую его использование, и количество используемых секретных битов; результат ssl.SSLSocket.cipher() 'peercert' : сертификат пира; результат ssl.SSLSocket.getpeercert() 'sslcontext' : экземпляр ssl.SSLContext 'ssl_object' : экземпляр ssl.SSLObject или ssl.SSLSocket

SSL-сокет:

- 'compression' : используемый алгоритм сжатия в виде строки, или None , если соединение не сжато; результат ssl.SSLSocket.compression()

'compression' : используемый алгоритм сжатия в виде строки, или None , если соединение не сжато; результат ssl.SSLSocket.compression()

- 'cipher' : кортеж из трех значений, содержащий имя используемого шифра, версию протокола SSL, определяющую его использование, и количество используемых секретных битов; результат ssl.SSLSocket.cipher()

'cipher' : кортеж из трех значений, содержащий имя используемого шифра, версию протокола SSL, определяющую его использование, и количество используемых секретных битов; результат ssl.SSLSocket.cipher()

- 'peercert' : сертификат пира; результат ssl.SSLSocket.getpeercert()

'peercert' : сертификат пира; результат ssl.SSLSocket.getpeercert()

- 'sslcontext' : экземпляр ssl.SSLContext

'sslcontext' : экземпляр ssl.SSLContext

- 'ssl_object' : экземпляр ssl.SSLObject или ssl.SSLSocket

'ssl_object' : экземпляр ssl.SSLObject или ssl.SSLSocket

- канал: 'pipe' : объект канала

канал:

- 'pipe' : объект канала

'pipe' : объект канала

- подпроцесс: 'subprocess' : экземпляр subprocess.Popen

подпроцесс:

- 'subprocess' : экземпляр subprocess.Popen

'subprocess' : экземпляр subprocess.Popen

**BaseTransport. set_protocol ( protocol )**

Установить новый протокол.

Смена протокола должна производиться только в случае, когда оба протокола задокументированно поддерживают переключение.

**BaseTransport. get_protocol ( )**

Возвращает текущий протокол.

### Read-only Transports Транспорты только для чтения ​

**ReadTransport. is_reading ( )**

Возвращает True , если транспорт получает новые данные.

Добавлено в версии 3.7.

**ReadTransport. pause_reading ( )**

Приостанавливает прием данных транспортом. Данные не будут передаваться методу protocol.data_received() протокола, пока не будет вызван resume_reading() .

Изменено в версии 3.7: Метод идемпотентен, то есть его можно вызывать, когда транспорт уже приостановлен или закрыт.

**ReadTransport. resume_reading ( )**

Возобновляет прием данных. Метод protocol.data_received() протокола будет вызван снова, если есть данные для чтения.

Изменено в версии 3.7: Метод идемпотентен, то есть его можно вызывать, когда транспорт уже читает.

### Write-only Transports Транспорты только для записи ​

**WriteTransport. abort ( )**

Немедленно закрывает транспорт, не дожидаясь завершения ожидающих операций. Буферизованные данные будут потеряны. Новые данные приниматься не будут. Метод protocol.connection_lost() протокола в конечном итоге будет вызван с None в качестве аргумента.

**WriteTransport. can_write_eof ( )**

Возвращает True , если транспорт поддерживает write_eof() , и False в противном случае.

**WriteTransport. get_write_buffer_size ( )**

Возвращает текущий размер выходного буфера, используемого транспортом.

**WriteTransport. get_write_buffer_limits ( )**

Возвращает верхний и нижний пороги для управления потоком записи. Возвращает кортеж (low, high) , где нижний и верхний – положительное количество
байтов.

Для установки порогов используется set_write_buffer_limits() .

Добавлено в версии 3.4.2.

**WriteTransport. set_write_buffer_limits ( high = None , low = None )**

Устанавливает верхний и нижний пороги для управления потоком записи.

Эти два значения (измеряются в количестве
байтов) управляют тем, когда вызываются методы protocol.pause_writing() и protocol.resume_writing() протокола. Если указаны, нижний порог должен быть меньше
или равен верхнему порогу. Ни верхний , ни нижний не могут быть отрицательными.

pause_writing() вызывается, когда размер буфера
становится больше или равен верхнему значению. Если запись была
приостановлена, resume_writing() вызывается, когда
размер буфера становится меньше или равен нижнему значению.

Значения по умолчанию зависят от реализации. Если указан только
верхний порог, нижний порог по умолчанию принимает
значение, зависящее от реализации, которое меньше или равно
верхнему порогу. Установка верхнего порога в ноль принуждает нижний порог также стать нулевым
и приводит к вызову pause_writing() всякий раз, когда буфер становится непустым. Установка нижнего порога в ноль приводит к вызову resume_writing() только после того, как
буфер опустеет. Использование нуля для любого из порогов в целом
неоптимально, так как сокращает возможности для одновременного выполнения ввода-вывода и
вычислений.

Для получения порогов используется get_write_buffer_limits() .

**WriteTransport. write ( data )**

Записывает в транспорт некоторые данные (байты).

Этот метод не блокирует выполнение; он буферизует данные и обеспечивает их
асинхронную отправку.

**WriteTransport. writelines ( list_of_data )**

Записывает список (или любой итерируемый объект) байтов данных в транспорт.
Функционально это эквивалентно вызову write() для каждого
элемента, полученного из итерируемого объекта, но может быть реализовано более
эффективно.

**WriteTransport. write_eof ( )**

Закрывает конец записи транспорта после сброса всех буферизованных данных.
Данные всё ещё могут приниматься.

Этот метод может вызывать NotImplementedError , если транспорт
(например, SSL) не поддерживает полузакрытые соединения.

### Datagram Transports Дейтаграммные транспорты ​

**DatagramTransport. sendto ( data , addr = None )**

Отправляет байты данных удалённому узлу, заданному addr (зависимый от транспорта целевой адрес).  Если addr равно None ,
данные отправляются на целевой адрес, указанный при создании
транспорта.

Этот метод не блокирует выполнение; он буферизует данные и обеспечивает их
асинхронную отправку.

Изменено в версии 3.13: Этот метод можно вызывать с пустым байтовым объектом для отправки
дейтаграммы нулевой длины. Расчёт размера буфера, используемый для управления
потоком, также обновлён для учёта заголовка дейтаграммы.

**DatagramTransport. abort ( )**

Закрывает транспорт немедленно, не дожидаясь завершения ожидающих
операций. Буферизованные данные будут потеряны.
Дальнейший приём данных прекратится. Метод protocol.connection_lost() протокола в конечном счёте будет вызван с None в качестве аргумента.

### Subprocess Transports Транспорты подпроцессов ​

**SubprocessTransport. get_pid ( )**

Возвращает идентификатор процесса подпроцесса в виде целого числа.

**SubprocessTransport. get_pipe_transport ( fd )**

Возвращает транспорт для канала связи, соответствующего целочисленному файловому дескриптору fd :

- 0 : потоковый транспорт для записи стандартного ввода ( stdin ), или None , если подпроцесс не был создан с stdin=PIPE

0 : потоковый транспорт для записи стандартного ввода ( stdin ), или None , если подпроцесс не был создан с stdin=PIPE

- 1 : потоковый транспорт для чтения стандартного вывода ( stdout ), или None , если подпроцесс не был создан с stdout=PIPE

1 : потоковый транспорт для чтения стандартного вывода ( stdout ), или None , если подпроцесс не был создан с stdout=PIPE

- 2 : потоковый транспорт для чтения стандартного вывода ошибок ( stderr ), или None , если подпроцесс не был создан с stderr=PIPE

2 : потоковый транспорт для чтения стандартного вывода ошибок ( stderr ), или None , если подпроцесс не был создан с stderr=PIPE

- другой fd : None

другой fd : None

**SubprocessTransport. get_returncode ( )**

Возвращает код возврата подпроцесса в виде целого числа или None ,
если он ещё не завершился, что аналогично атрибуту subprocess.Popen.returncode .

**SubprocessTransport. kill ( )**

Завершает подпроцесс.

В системах POSIX функция отправляет SIGKILL подпроцессу.
В Windows этот метод является псевдонимом для terminate() .

См. также subprocess.Popen.kill() .

**SubprocessTransport. send_signal ( signal )**

Отправляет номер сигнала signal подпроцессу, как в subprocess.Popen.send_signal() .

**SubprocessTransport. terminate ( )**

Останавливает подпроцесс.

В системах POSIX этот метод отправляет SIGTERM подпроцессу.
В Windows вызывается функция Windows API TerminateProcess() для
остановки подпроцесса.

См. также subprocess.Popen.terminate() .

**SubprocessTransport. close ( )**

Завершает подпроцесс вызовом метода kill() .

Если подпроцесс ещё не завершился, и закрывает транспорты каналов stdin , stdout и stderr .

## Protocols Протоколы ​

Исходный код: Lib/asyncio/protocols.py

asyncio предоставляет набор абстрактных базовых классов, которые следует использовать
для реализации сетевых протоколов. Эти классы предназначены для использования
совместно с транспортами .

Подклассы абстрактных базовых классов протоколов могут реализовывать некоторые или
все методы. Все эти методы являются колбэками: они вызываются
транспортами при определённых событиях, например, когда получены некоторые данные.
Метод базового протокола должен вызываться соответствующим транспортом.

### Base Protocols Базовые протоколы ​

**class asyncio. BaseProtocol**

Базовый протокол с методами, общими для всех протоколов.

**class asyncio. Protocol ( BaseProtocol )**

Базовый класс для реализации потоковых протоколов
(TCP, сокеты Unix и т.д.).

**class asyncio. BufferedProtocol ( BaseProtocol )**

Базовый класс для реализации потоковых протоколов с ручным
управлением буфером приёма.

**class asyncio. DatagramProtocol ( BaseProtocol )**

Базовый класс для реализации дейтаграммных (UDP) протоколов.

**class asyncio. SubprocessProtocol ( BaseProtocol )**

Базовый класс для реализации протоколов, взаимодействующих с дочерними процессами (однонаправленные каналы).

### Base Protocol Базовый протокол ​

Все протоколы asyncio могут реализовывать колбэки базового протокола.

Колбэки подключения

Колбэки подключения вызываются для всех протоколов, ровно один раз за успешное подключение. Все остальные колбэки протокола могут вызываться только между этими двумя методами.

**BaseProtocol. connection_made ( transport )**

Вызывается при установлении соединения.

Аргумент transport представляет транспорт подключения. Протокол отвечает за хранение ссылки на свой транспорт.

**BaseProtocol. connection_lost ( exc )**

Вызывается при потере или закрытии соединения.

Аргумент является либо объектом исключения, либо None . Последнее означает, что получен обычный EOF, или соединение было прервано или закрыто этой стороной соединения.

Колбэки управления потоком

Колбэки управления потоком могут вызываться транспортами для приостановки или возобновления записи, выполняемой протоколом.

Смотрите документацию метода set_write_buffer_limits() для получения более подробной информации.

**BaseProtocol. pause_writing ( )**

Вызывается, когда буфер транспорта превышает верхнюю отметку.

**BaseProtocol. resume_writing ( )**

Вызывается, когда буфер транспорта опускается ниже нижней отметки.

Если размер буфера равен верхней отметке, pause_writing() не вызывается: размер буфера должен строго превышать её.

И наоборот, resume_writing() вызывается, когда размер буфера равен нижней отметке или меньше её. Эти граничные условия важны для обеспечения ожидаемого поведения, когда любая из отметок равна нулю.

### Streaming Protocols Потоковые протоколы ​

Методы событий, такие как loop.create_server() , loop.create_unix_server() , loop.create_connection() , loop.create_unix_connection() , loop.connect_accepted_socket() , loop.connect_read_pipe() и loop.connect_write_pipe() , принимают фабрики, возвращающие потоковые протоколы.

**Protocol. data_received ( data )**

Вызывается при получении некоторых данных. data – это непустой объект bytes, содержащий входящие данные.

Буферизуются ли данные, передаются ли они частями или собираются заново, зависит от транспорта. В общем случае не следует полагаться на конкретную семантику, а делать свой анализ обобщённым и гибким. Однако данные всегда принимаются в правильном порядке.

Метод может вызываться произвольное количество раз, пока соединение открыто.

Однако protocol.eof_received() вызывается не более одного раза. После вызова eof_received() , data_received() больше не вызывается.

**Protocol. eof_received ( )**

Вызывается, когда другой конец сигнализирует, что больше не будет отправлять данные (например, вызовом transport.write_eof() , если другой конец также использует asyncio).

Этот метод может возвращать ложное значение (включая None ), в этом случае транспорт закроется сам. И наоборот, если этот метод возвращает истинное значение, используемый протокол определяет, закрывать ли транспорт. Поскольку реализация по умолчанию возвращает None , она неявно закрывает соединение.

Некоторые транспорты, включая SSL, не поддерживают полузакрытые соединения; в этом случае возврат true из этого метода приведёт к закрытию соединения.

Машина состояний:

```python
start -> connection_made
    [-> data_received]*
    [-> eof_received]?
-> connection_lost -> end
```

### Buffered Streaming Protocols Буферизованные потоковые протоколы ​

Добавлено в версии 3.7.

Буферизованные протоколы могут использоваться с любым методом цикла событий, который поддерживает потоковые протоколы .

Реализации BufferedProtocol позволяют явно распределять и управлять буфером приема вручную. Циклы событий затем могут использовать буфер, предоставленный протоколом, чтобы избежать ненужного копирования данных. Это может привести к заметному улучшению производительности для протоколов, которые получают большие объемы данных. Сложные реализации протоколов могут значительно сократить количество выделений буфера.

Следующие колбэки вызываются на экземплярах BufferedProtocol :

**BufferedProtocol. get_buffer ( sizehint )**

Вызывается для выделения нового буфера приёма.

sizehint – это рекомендуемый минимальный размер для возвращаемого буфера. Допускается возвращать буферы меньше или больше, чем предполагает sizehint . При установке в -1 размер буфера может быть произвольным. Возвращать буфер нулевого размера – ошибка.

get_buffer() должен возвращать объект, реализующий буферный протокол .

**BufferedProtocol. buffer_updated ( nbytes )**

Вызывается при обновлении буфера полученными данными.

nbytes – это общее количество байтов, записанных в буфер.

**BufferedProtocol. eof_received ( )**

См. документацию метода protocol.eof_received() .

get_buffer() может вызываться произвольное количество раз в течение соединения. Однако protocol.eof_received() вызывается не более одного раза, и если он вызывается, то get_buffer() и buffer_updated() не будут вызываться после него.

Машина состояний:

```python
start -> connection_made
    [-> get_buffer
        [-> buffer_updated]?
    ]*
    [-> eof_received]?
-> connection_lost -> end
```

### Datagram Protocols Протоколы дейтаграмм ​

Экземпляры протокола дейтаграмм должны создаваться фабриками протоколов, передаваемыми методу loop.create_datagram_endpoint() .

**DatagramProtocol. datagram_received ( data , addr )**

Вызывается при получении дейтаграммы. data – это объект bytes, содержащий входящие данные. addr – это адрес узла, отправляющего данные; точный формат зависит от транспорта.

**DatagramProtocol. error_received ( exc )**

Вызывается, когда предыдущая операция отправки или получения вызывает OSError . exc – это экземпляр OSError .

Этот метод вызывается в редких случаях, когда транспорт (например, UDP) обнаруживает, что дейтаграмма не может быть доставлена получателю. Однако во многих случаях недоставленные дейтаграммы молча отбрасываются.

Примечание

В системах BSD (macOS, FreeBSD и т.д.) управление потоком не поддерживается для протоколов дейтаграмм, поскольку нет надежного способа обнаружить ошибки отправки, вызванные записью слишком большого количества пакетов.

Сокет всегда выглядит «готовым», и избыточные пакеты отбрасываются. Исключение OSError с errno , установленным в errno.ENOBUFS , может быть возбуждено или нет; если оно возбуждено, оно будет сообщено DatagramProtocol.error_received() , но в остальном игнорируется.

### Subprocess Protocols Протоколы подпроцессов ​

Экземпляры протокола подпроцесса должны создаваться фабриками протоколов, передаваемыми методам loop.subprocess_exec() и loop.subprocess_shell() .

**SubprocessProtocol. pipe_data_received ( fd , data )**

Вызывается, когда дочерний процесс записывает данные в свой канал stdout или stderr.

fd – это целочисленный файловый дескриптор канала.

data – это непустой объект bytes, содержащий полученные данные.

**SubprocessProtocol. pipe_connection_lost ( fd , exc )**

Вызывается, когда один из каналов, связывающих с дочерним процессом, закрыт.

fd – это целочисленный файловый дескриптор, который был закрыт.

**SubprocessProtocol. process_exited ( )**

Вызывается, когда дочерний процесс завершился.

Он может быть вызван до методов pipe_data_received() и pipe_connection_lost() .

## Examples Примеры ​

### TCP Echo Server TCP-эхо-сервер ​

Создаёт TCP-эхо-сервер с помощью метода loop.create_server() , отправляет обратно полученные данные и закрывает соединение:

```python
import
 
asyncio




class
 
EchoServerProtocol
(
asyncio
.
Protocol
):

    
def
 
connection_made
(
self
,
 
transport
):

        
peername
 
=
 
transport
.
get_extra_info
(
'peername'
)

        
print
(
'Connection from 
{}
'
.
format
(
peername
))

        
self
.
transport
 
=
 
transport


    
def
 
data_received
(
self
,
 
data
):

        
message
 
=
 
data
.
decode
()

        
print
(
'Data received: 
{!r}
'
.
format
(
message
))


        
print
(
'Send: 
{!r}
'
.
format
(
message
))

        
self
.
transport
.
write
(
data
)


        
print
(
'Close the client socket'
)

        
self
.
transport
.
close
()




async
 
def
 
main
():

    
# Получить ссылку на цикл событий, так как мы планируем использовать

    
# низкоуровневые API.

    
loop
 
=
 
asyncio
.
get_running_loop
()


    
server
 
=
 
await
 
loop
.
create_server
(

        
EchoServerProtocol
,

        
'127.0.0.1'
,
 
8888
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

Пример TCP-эхо-сервера с использованием потоков использует высокоуровневую функцию asyncio.start_server() .

### TCP Echo Client TCP-эхо-клиент ​

TCP-эхо-клиент с помощью метода loop.create_connection() отправляет данные и ожидает закрытия соединения:

```python
import
 
asyncio




class
 
EchoClientProtocol
(
asyncio
.
Protocol
):

    
def
 
__init__
(
self
,
 
message
,
 
on_con_lost
):

        
self
.
message
 
=
 
message

        
self
.
on_con_lost
 
=
 
on_con_lost


    
def
 
connection_made
(
self
,
 
transport
):

        
transport
.
write
(
self
.
message
.
encode
())

        
print
(
'Data sent: 
{!r}
'
.
format
(
self
.
message
))


    
def
 
data_received
(
self
,
 
data
):

        
print
(
'Data received: 
{!r}
'
.
format
(
data
.
decode
()))


    
def
 
connection_lost
(
self
,
 
exc
):

        
print
(
'The server closed the connection'
)

        
self
.
on_con_lost
.
set_result
(
True
)




async
 
def
 
main
():

    
# Получить ссылку на цикл событий, так как мы планируем использовать

    
# низкоуровневые API.

    
loop
 
=
 
asyncio
.
get_running_loop
()


    
on_con_lost
 
=
 
loop
.
create_future
()

    
message
 
=
 
'Hello World!'


    
transport
,
 
protocol
 
=
 
await
 
loop
.
create_connection
(

        
lambda
:
 
EchoClientProtocol
(
message
,
 
on_con_lost
),

        
'127.0.0.1'
,
 
8888
)


    
# Ждать, пока протокол не сообщит, что соединение

    
# потеряно, и закрыть транспорт.

    
try
:

        
await
 
on_con_lost

    
finally
:

        
transport
.
close
()




asyncio
.
run
(
main
())
```

Смотрите также

Пример TCP-эхо-клиента с использованием потоков использует высокоуровневую функцию asyncio.open_connection() .

### UDP Echo Server UDP-эхо-сервер ​

UDP-эхо-сервер, использующий метод loop.create_datagram_endpoint() ,
отправляет обратно полученные данные:

```python
import
 
asyncio




class
 
EchoServerProtocol
:

    
def
 
connection_made
(
self
,
 
transport
):

        
self
.
transport
 
=
 
transport


    
def
 
datagram_received
(
self
,
 
data
,
 
addr
):

        
message
 
=
 
data
.
decode
()

        
print
(
'Received 
%r
 from 
%s
'
 
%
 
(
message
,
 
addr
))

        
print
(
'Send 
%r
 to 
%s
'
 
%
 
(
message
,
 
addr
))

        
self
.
transport
.
sendto
(
data
,
 
addr
)




async
 
def
 
main
():

    
print
(
"Starting UDP server"
)


    
# Получить ссылку на цикл событий, так как мы планируем использовать

    
# низкоуровневые API.

    
loop
 
=
 
asyncio
.
get_running_loop
()


    
# Один экземпляр протокола будет создан для обслуживания всех

    
# запросов клиентов.

    
transport
,
 
protocol
 
=
 
await
 
loop
.
create_datagram_endpoint
(

        
EchoServerProtocol
,

        
local_addr
=
(
'127.0.0.1'
,
 
9999
))


    
try
:

        
await
 
asyncio
.
sleep
(
3600
)
  
# Обслуживать в течение 1 часа.

    
finally
:

        
transport
.
close
()




asyncio
.
run
(
main
())
```

### UDP Echo Client UDP-эхо-клиент ​

UDP-эхо-клиент, использующий метод loop.create_datagram_endpoint() ,
отправляет данные и закрывает транспорт при получении ответа:

```python
import
 
asyncio




class
 
EchoClientProtocol
:

    
def
 
__init__
(
self
,
 
message
,
 
on_con_lost
):

        
self
.
message
 
=
 
message

        
self
.
on_con_lost
 
=
 
on_con_lost

        
self
.
transport
 
=
 
None


    
def
 
connection_made
(
self
,
 
transport
):

        
self
.
transport
 
=
 
transport

        
print
(
'Send:'
,
 
self
.
message
)

        
self
.
transport
.
sendto
(
self
.
message
.
encode
())


    
def
 
datagram_received
(
self
,
 
data
,
 
addr
):

        
print
(
"Received:"
,
 
data
.
decode
())


        
print
(
"Close the socket"
)

        
self
.
transport
.
close
()


    
def
 
error_received
(
self
,
 
exc
):

        
print
(
'Error received:'
,
 
exc
)


    
def
 
connection_lost
(
self
,
 
exc
):

        
print
(
"Connection closed"
)

        
self
.
on_con_lost
.
set_result
(
True
)




async
 
def
 
main
():

    
# Получить ссылку на цикл событий, так как мы планируем использовать

    
# низкоуровневые API.

    
loop
 
=
 
asyncio
.
get_running_loop
()


    
on_con_lost
 
=
 
loop
.
create_future
()

    
message
 
=
 
"Hello World!"


    
transport
,
 
protocol
 
=
 
await
 
loop
.
create_datagram_endpoint
(

        
lambda
:
 
EchoClientProtocol
(
message
,
 
on_con_lost
),

        
remote_addr
=
(
'127.0.0.1'
,
 
9999
))


    
try
:

        
await
 
on_con_lost

    
finally
:

        
transport
.
close
()




asyncio
.
run
(
main
())
```

### Connecting Existing Sockets Подключение существующих сокетов ​

Ожидание получения данных сокетом с помощью
метода loop.create_connection() с протоколом:

```python
import
 
asyncio


import
 
socket




class
 
MyProtocol
(
asyncio
.
Protocol
):


    
def
 
__init__
(
self
,
 
on_con_lost
):

        
self
.
transport
 
=
 
None

        
self
.
on_con_lost
 
=
 
on_con_lost


    
def
 
connection_made
(
self
,
 
transport
):

        
self
.
transport
 
=
 
transport


    
def
 
data_received
(
self
,
 
data
):

        
print
(
"Received:"
,
 
data
.
decode
())


        
# Мы закончили: закрыть транспорт;

        
# connection_lost() будет вызван автоматически.

        
self
.
transport
.
close
()


    
def
 
connection_lost
(
self
,
 
exc
):

        
# Сокет был закрыт.

        
self
.
on_con_lost
.
set_result
(
True
)




async
 
def
 
main
():

    
# Получить ссылку на цикл событий, так как мы планируем использовать

    
# низкоуровневые API.

    
loop
 
=
 
asyncio
.
get_running_loop
()

    
on_con_lost
 
=
 
loop
.
create_future
()


    
# Создать пару соединённых сокетов

    
rsock
,
 
wsock
 
=
 
socket
.
socketpair
()


    
# Зарегистрировать сокет для ожидания данных.

    
transport
,
 
protocol
 
=
 
await
 
loop
.
create_connection
(

        
lambda
:
 
MyProtocol
(
on_con_lost
),
 
sock
=
rsock
)


    
# Смоделировать приём данных из сети.

    
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


    
try
:

        
await
 
protocol
.
on_con_lost

    
finally
:

        
transport
.
close
()

        
wsock
.
close
()



asyncio
.
run
(
main
())
```

Смотрите также

Пример отслеживания событий чтения у файлового дескриптора использует низкоуровневый
метод loop.add_reader() для регистрации файлового дескриптора.

Пример регистрации открытого сокета для ожидания данных с использованием потоков использует высокоуровневые потоки,
созданные функцией open_connection() в корутине.

### loop.subprocess_exec ) and SubprocessProtocol (loop.subprocess_exec() и SubprocessProtocol ​

Пример протокола подпроцесса, используемого для получения вывода подпроцесса и ожидания его завершения.

Подпроцесс создаётся методом loop.subprocess_exec() :

```python
import
 
asyncio


import
 
sys



class
 
DateProtocol
(
asyncio
.
SubprocessProtocol
):

    
def
 
__init__
(
self
,
 
exit_future
):

        
self
.
exit_future
 
=
 
exit_future

        
self
.
output
 
=
 
bytearray
()

        
self
.
pipe_closed
 
=
 
False

        
self
.
exited
 
=
 
False


    
def
 
pipe_connection_lost
(
self
,
 
fd
,
 
exc
):

        
self
.
pipe_closed
 
=
 
True

        
self
.
check_for_exit
()


    
def
 
pipe_data_received
(
self
,
 
fd
,
 
data
):

        
self
.
output
.
extend
(
data
)


    
def
 
process_exited
(
self
):

        
self
.
exited
 
=
 
True

        
# Метод process_exited() может быть вызван до

        
# метод pipe_connection_lost(): ожидать, пока оба метода не будут

        
# вызваны.

        
self
.
check_for_exit
()


    
def
 
check_for_exit
(
self
):

        
if
 
self
.
pipe_closed
 
and
 
self
.
exited
:

            
self
.
exit_future
.
set_result
(
True
)



async
 
def
 
get_date
():

    
# Получить ссылку на цикл событий, так как мы планируем использовать

    
# низкоуровневые API.

    
loop
 
=
 
asyncio
.
get_running_loop
()


    
code
 
=
 
'import datetime as dt; print(dt.datetime.now())'

    
exit_future
 
=
 
asyncio
.
Future
(
loop
=
loop
)


    
# Создать подпроцесс, управляемый DateProtocol;

    
# перенаправить стандартный вывод в канал.

    
transport
,
 
protocol
 
=
 
await
 
loop
.
subprocess_exec
(

        
lambda
:
 
DateProtocol
(
exit_future
),

        
sys
.
executable
,
 
'-c'
,
 
code
,

        
stdin
=
None
,
 
stderr
=
None
)


    
# Ожидать завершения подпроцесса, используя process_exited()

    
# метод протокола.

    
await
 
exit_future


    
# Закрыть канал stdout.

    
transport
.
close
()


    
# Прочитать вывод, который был собран

    
# методом pipe_data_received() протокола.

    
data
 
=
 
bytes
(
protocol
.
output
)

    
return
 
data
.
decode
(
'ascii'
)
.
rstrip
()



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

См. также тот же пример ,
написанный с использованием высокоуровневых API.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.