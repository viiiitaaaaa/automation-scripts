> Источник: https://asyncio.ru/3.15/library/asyncio-policy.html — перевод документации Python (PSF).

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

- Getting and Setting the Policy Получение и установка политики

- Policy Objects Объекты политики

- Custom Policies Пользовательские политики

# Policies Политики ​

Предупреждение

Политики устарели и будут удалены в Python 3.16.
Пользователям рекомендуется использовать функцию asyncio.run() или asyncio.Runner с loop_factory для использования
нужной реализации цикла событий.

Политика цикла событий – это глобальный объект,
используемый для получения и установки текущего цикла событий ,
а также для создания новых циклов событий.
Политику по умолчанию можно заменить на встроенные альтернативы для использования различных реализаций цикла событий,
или заменить на пользовательскую политику которая может переопределять эти поведения.

Объект политики получает и устанавливает отдельный цикл событий для каждого контекста .
По умолчанию это для каждого потока,
хотя пользовательские политики могут определять контекст иначе.

Пользовательские политики цикла событий могут управлять поведением get_event_loop() , set_event_loop() и new_event_loop() .

Объекты политики должны реализовывать API, определённые
в абстрактном базовом классе AbstractEventLoopPolicy .

## Getting and Setting the Policy Получение и установка политики ​

Следующие функции можно использовать для получения и установки политики
для текущего процесса:

**asyncio. get_event_loop_policy ( )**

Возвращает текущую общепроцессную политику.

Устарело с версии 3.14: Функция get_event_loop_policy() устарела и будет удалена в Python 3.16.

**asyncio. set_event_loop_policy ( policy )**

Устанавливает политику текущего процесса на policy .

Если policy установлено в None , восстанавливается политика по умолчанию.

Устарело с версии 3.14: Функция set_event_loop_policy() устарела и будет удалена в Python 3.16.

## Policy Objects Объекты политики ​

Абстрактный базовый класс политики цикла событий определён следующим образом:

**class asyncio. AbstractEventLoopPolicy**

Абстрактный базовый класс для политик asyncio.

**get_event_loop ( )**

Получает цикл событий для текущего контекста.

Возвращает объект цикла событий, реализующий интерфейс AbstractEventLoop .

Этот метод никогда не должен возвращать None .

Изменено в версии 3.6.

**set_event_loop ( loop )**

Устанавливает цикл событий для текущего контекста в loop .

**new_event_loop ( )**

Создает и возвращает новый объект цикла событий.

Этот метод никогда не должен возвращать None .

Устарело с версии 3.14: Класс AbstractEventLoopPolicy устарел и
будет удалён в Python 3.16.

asyncio поставляется со следующими встроенными политиками:

**class asyncio. DefaultEventLoopPolicy**

Политика asyncio по умолчанию. Использует SelectorEventLoop в Unix и ProactorEventLoop в Windows.

Не требуется устанавливать политику по умолчанию вручную. asyncio
настроена на автоматическое использование политики по умолчанию.

Изменено в версии 3.8: В Windows, ProactorEventLoop теперь используется по умолчанию.

Изменено в версии 3.14: Метод get_event_loop() политики asyncio по умолчанию теперь
вызывает RuntimeError , если не установлен цикл событий.

Устарело с версии 3.14: Класс DefaultEventLoopPolicy устарел и
будет удалён в Python 3.16.

**class asyncio. WindowsSelectorEventLoopPolicy**

Альтернативная политика цикла событий, использующая
реализацию SelectorEventLoop цикла событий.

Доступность : Windows.

Устарело с версии 3.14: Класс WindowsSelectorEventLoopPolicy устарел и
будет удалён в Python 3.16.

**class asyncio. WindowsProactorEventLoopPolicy**

Альтернативная политика цикла событий, использующая
реализацию ProactorEventLoop цикла событий.

Доступность : Windows.

Устарело с версии 3.14: Класс WindowsProactorEventLoopPolicy устарел и
будет удалён в Python 3.16.

## Custom Policies Пользовательские политики ​

Чтобы реализовать новую политику цикла событий, рекомендуется создать подкласс DefaultEventLoopPolicy и переопределить методы, для которых
требуется настраиваемое поведение, например:

```python
class
 
MyEventLoopPolicy
(
asyncio
.
DefaultEventLoopPolicy
):


    
def
 
get_event_loop
(
self
):


        
"""Get the event loop.



        This may be None or an instance of EventLoop.


        """

        
loop
 
=
 
super
()
.
get_event_loop
()

        
# Сделать что-то с loop ...

        
return
 
loop



asyncio
.
set_event_loop_policy
(
MyEventLoopPolicy
())
```

Офлайн-копия документации Python asyncio · оформление в стиле openai-doc.ru

© 2001–2026 Python Software Foundation · Sphinx 8.2.3.