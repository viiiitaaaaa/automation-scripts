> Источник: https://asyncio.ru/3.15/library/asyncio-llapi-index.html — перевод документации Python (PSF).

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

- Obtaining the Event Loop Получение цикла событий

- Event Loop Methods Методы цикла событий

- Transports Транспорты

- Protocols Протоколы

- Event Loop Policies Политики цикла событий

# Low-level API Index Индекс низкоуровневого API ​

На этой странице перечислены все низкоуровневые API asyncio.

## Obtaining the Event Loop Получение цикла событий ​

asyncio.get_running_loop()

Предпочтительная функция для получения работающего цикла событий.

asyncio.get_event_loop()

Получить экземпляр цикла событий (работающий или текущий через текущую политику).

asyncio.set_event_loop()

Установить цикл событий как текущий через текущую политику.

asyncio.new_event_loop()

Создать новый цикл событий.

Примеры

- Использование asyncio.get_running_loop() .

Использование asyncio.get_running_loop() .

## Event Loop Methods Методы цикла событий ​

См. также основной раздел документации о методах цикла событий .

Жизненный цикл

loop.run_until_complete()

Запустить Future/задачу/ожидаемый объект до завершения.

loop.run_forever()

Запустить цикл событий бесконечно.

loop.stop()

Останавливает цикл событий.

loop.close()

Закрывает цикл событий.

loop.is_running()

Возвращает True , если цикл событий выполняется.

loop.is_closed()

Возвращает True , если цикл событий закрыт.

await loop.shutdown_asyncgens()

Закрыть асинхронные генераторы.

Отладка

loop.set_debug()

Включить или выключить режим отладки.

loop.get_debug()

Получить текущий режим отладки.

Планирование колбэков

loop.call_soon()

Вызвать колбэк в ближайшее время.

loop.call_soon_threadsafe()

Потокобезопасный вариант loop.call_soon() .

loop.call_later()

Вызвать колбэк после заданного времени.

loop.call_at()

Вызвать колбэк в заданное время.

Пул потоков/интерпретаторов/процессов

await loop.run_in_executor()

Выполнить функцию, связанную с ЦП, или другую блокирующую функцию в concurrent.futures исполнителе.

loop.set_default_executor()

Установить исполнитель по умолчанию для loop.run_in_executor() .

Задачи и Future

loop.create_future()

Создать объект Future .

loop.create_task()

Запланировать корутину как Task .

loop.set_task_factory()

Устанавливает фабрику, используемую loop.create_task() для
создания Tasks .

loop.get_task_factory()

Возвращает фабрику, которую loop.create_task() использует
для создания Tasks .

DNS

await loop.getaddrinfo()

Асинхронная версия socket.getaddrinfo() .

await loop.getnameinfo()

Асинхронная версия socket.getnameinfo() .

Сеть и IPC

await loop.create_connection()

Открывает TCP-соединение.

await loop.create_server()

Создаёт TCP-сервер.

await loop.create_unix_connection()

Открывает Unix-сокетное соединение.

await loop.create_unix_server()

Создаёт Unix-сокетный сервер.

await loop.connect_accepted_socket()

Оборачивает socket в пару (transport, protocol) .

await loop.create_datagram_endpoint()

Открывает датаграммное (UDP) соединение.

await loop.sendfile()

Отправляет файл через транспорт.

await loop.start_tls()

Обновляет существующее соединение до TLS.

await loop.connect_read_pipe()

Оборачивает читающий конец канала в пару (transport, protocol) .

await loop.connect_write_pipe()

Оборачивает записывающий конец канала в пару (transport, protocol) .

Сокеты

await loop.sock_recv()

Получает данные из socket .

await loop.sock_recv_into()

Получает данные из socket в буфер.

await loop.sock_recvfrom()

Получает датаграмму из socket .

await loop.sock_recvfrom_into()

Получает датаграмму из socket в буфер.

await loop.sock_sendall()

Отправляет данные в socket .

await loop.sock_sendto()

Отправляет датаграмму через socket по указанному адресу.

await loop.sock_connect()

Подключает socket .

await loop.sock_accept()

Принимает соединение socket .

await loop.sock_sendfile()

Отправляет файл через socket .

loop.add_reader()

Начинает отслеживать файловый дескриптор на готовность к чтению.

loop.remove_reader()

Прекращает отслеживать файловый дескриптор на готовность к чтению.

loop.add_writer()

Начинает отслеживать файловый дескриптор на готовность к записи.

loop.remove_writer()

Прекращает отслеживать файловый дескриптор на готовность к записи.

Сигналы Unix

loop.add_signal_handler()

Добавляет обработчик для signal .

loop.remove_signal_handler()

Удаляет обработчик для signal .

Подпроцессы

loop.subprocess_exec()

Создать подпроцесс.

loop.subprocess_shell()

Создать подпроцесс из команды оболочки.

Обработка ошибок

loop.call_exception_handler()

Вызвать обработчик исключений.

loop.set_exception_handler()

Установить новый обработчик исключений.

loop.get_exception_handler()

Получить текущий обработчик исключений.

loop.default_exception_handler()

Реализация обработчика исключений по умолчанию.

Примеры

- Использование asyncio.new_event_loop() и loop.run_forever() .

Использование asyncio.new_event_loop() и loop.run_forever() .

- Использование loop.call_later() .

Использование loop.call_later() .

- Использование loop.create_connection() для реализации эхо-клиента .

Использование loop.create_connection() для реализации эхо-клиента .

- Использование loop.create_connection() для подключения сокета .

Использование loop.create_connection() для подключения сокета .

- Использование add_reader() для наблюдения за FD на события чтения .

Использование add_reader() для наблюдения за FD на события чтения .

- Использование loop.add_signal_handler() .

Использование loop.add_signal_handler() .

- Использование loop.subprocess_exec() .

Использование loop.subprocess_exec() .

## Transports Транспорты ​

Все транспорты реализуют следующие методы:

transport.close()

Закрыть транспорт.

transport.is_closing()

Возвращает True , если транспорт закрывается или закрыт.

transport.get_extra_info()

Запросить информацию о транспорте.

transport.set_protocol()

Установить новый протокол.

transport.get_protocol()

Возвращает текущий протокол.

Транспорты, которые могут принимать данные (TCP- и Unix-соединения,
каналы и т.д.). Возвращаются из методов, таких как loop.create_connection() , loop.create_unix_connection() , loop.connect_read_pipe() и т.д.:

Транспорты чтения

transport.is_reading()

Возвращает True , если транспорт принимает.

transport.pause_reading()

Приостановить приём.

transport.resume_reading()

Возобновить приём.

Транспорты, которые могут отправлять данные (TCP- и Unix-соединения,
каналы и т.д.). Возвращаются из методов, таких как loop.create_connection() , loop.create_unix_connection() , loop.connect_write_pipe() и т.д.:

Транспорты записи

transport.write()

Записать данные в транспорт.

transport.writelines()

Записать буферы в транспорт.

transport.can_write_eof()

Возвращает True , если транспорт поддерживает отправку EOF.

transport.write_eof()

Закрыть и отправить EOF после сброса буферизованных данных.

transport.abort()

Немедленно закрывает транспорт.

transport.get_write_buffer_size()

Возвращает текущий размер выходного буфера.

transport.get_write_buffer_limits()

Возвращает верхний и нижний пороги для управления потоком записи.

transport.set_write_buffer_limits()

Устанавливает новые верхний и нижний пороги для управления потоком записи.

Транспорты, возвращаемые loop.create_datagram_endpoint() :

Транспорты дейтаграмм

transport.sendto()

Отправляет данные удалённому узлу.

transport.abort()

Немедленно закрывает транспорт.

Низкоуровневая абстракция транспорта над подпроцессами.
Возвращается loop.subprocess_exec() и loop.subprocess_shell() :

Транспорты подпроцессов

transport.get_pid()

Возвращает идентификатор процесса подпроцесса.

transport.get_pipe_transport()

Возвращает транспорт для запрошенного канала связи
( stdin , stdout или stderr ).

transport.get_returncode()

Возвращает код возврата подпроцесса.

transport.kill()

Завершает подпроцесс.

transport.send_signal()

Отправляет сигнал подпроцессу.

transport.terminate()

Останавливает подпроцесс.

transport.close()

Завершает подпроцесс и закрывает все каналы.

## Protocols Протоколы ​

Классы протоколов могут реализовывать следующие методы-колбэки :

callback connection_made()

Вызывается при установлении соединения.

callback connection_lost()

Вызывается при потере или закрытии соединения.

callback pause_writing()

Вызывается, когда буфер транспорта превышает верхний порог.

callback resume_writing()

Вызывается, когда буфер транспорта опускается ниже нижнего порога.

Потоковые протоколы (TCP, UNIX-сокеты, каналы)

callback data_received()

Вызывается при получении некоторых данных.

callback eof_received()

Вызывается при получении EOF.

Буферизированные потоковые протоколы

callback get_buffer()

Вызывается для выделения нового буфера приёма.

callback buffer_updated()

Вызывается при обновлении буфера полученными данными.

callback eof_received()

Вызывается при получении EOF.

Протоколы дейтаграмм

callback datagram_received()

Вызывается при получении дейтаграммы.

callback error_received()

Вызывается, когда предыдущая операция отправки или получения вызывает OSError .

Протоколы подпроцессов

callback pipe_data_received()

Вызывается, когда дочерний процесс записывает данные в свой канал stdout или stderr .

callback pipe_connection_lost()

Вызывается, когда один из каналов связи с дочерним процессом закрыт.

callback process_exited()

Вызывается, когда дочерний процесс завершился. Может быть вызван до методов pipe_data_received() и pipe_connection_lost() .

## Event Loop Policies Политики цикла событий ​

Политики – это низкоуровневый механизм для изменения поведения таких функций, как asyncio.get_event_loop() . См. также основной раздел о политиках для получения дополнительных сведений.

Доступ к политикам

asyncio.get_event_loop_policy()

Возвращает текущую общепроцессную политику.

asyncio.set_event_loop_policy()

Устанавливает новую общепроцессную политику.

AbstractEventLoopPolicy

Базовый класс для объектов политик.

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.