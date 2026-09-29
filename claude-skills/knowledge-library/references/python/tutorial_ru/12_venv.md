> Источник: https://docs.python.org/ru/3/tutorial/ — © Python Software Foundation, лицензия PSF / Zero-Clause BSD для документации. Перевод — проект python-docs-ru.

# 12. Виртуальные окружения и пакеты

## 12.1. Введение

Приложения Python часто используют пакеты и модули, не входящие в стандартную библиотеку. Иногда приложению необходима конкретная версия библиотеки, в которой устранена определенная ошибка, или же приложение написано с помощью устаревшей версии библиотечного интерфейса.

Это означает, что конкретная установка Python может быть непригодной одновременно для каждого приложения. Например, приложению А нужна версия 1.0 конкретного модуля, а приложению B нужна версия 2.0. Эти требования противоречат друг другу, и установка любой из версий 1.0 или 2.0 оставит одно из приложений не работоспособным.

Решением этой проблемы является создание виртуального окружения — автономного дерева каталогов, содержащего установку Python конкретной версии, а также набор дополнительных пакетов.

Разные приложения могут использовать разные виртуальные окружения. В примере с конфликтующими требованиями приложение А может использовать созданное для него виртуальное окружение с версией 1.0 нужного модуля, а приложение В исполняться в другом виртуальном окружении с версией 2.0 того же модуля. Если позднее приложению В потребуется обновить библиотеку до версии 3.0, то это никак не повлияет на виртуальное окружение приложения А.

## 12.2. Создание виртуального окружения

Модуль, используемый для создания и управления виртуальными окружениями, называется venv . venv установит ту версию Python, из которой была запущена команда (определяется опцией --version ). Например, выполнение команды с помощью python3.12 установит версию 3.12.

Чтобы создать виртуальное окружение, определитесь с каталогом, где оно должно находиться, и запустите модуль venv в виде скрипта, указав путь:

```python
python
 
-
m
 
venv
 
tutorial
-
env
```

Это создаст каталог tutorial-env , если он ещё не существует, а внутри — копию интерпретатора Python и необходимые служебные файлы.

Общепринятым расположением каталога для виртуального окружения является .venv . Это имя скрывает каталог в оболочке и не мешает работе, при этом объясняет его предназначение. Кроме того, оно не конфликтует с файлами .env , которые некоторые инструменты используют для переменных окружения.

После создания виртуального окружения его можно активировать.

В Windows запустите:

```python
tutorial
-
env
\
Scripts
\
activate
```

В Unix или MacOS выполните:

```python
source
 
tutorial
-
env
/
bin
/
activate
```

(Этот скрипт расчитан на оболочку bash. Для оболочек csh или fish есть соответственно альтернативные файлы activate.csh и activate.fish , которые можно использовать).

Активация виртуального окружения изменит приглашение оболочки, показывая, какое окружение активно, и настроит его так, что команда python будет запускать именно эту установленную версию Python. Например:

```python
$ 
source
 
~/envs/tutorial-env/bin/activate

(tutorial-env)
 
$ 
python

Python 3.5.1 (default, May  6 2016, 10:59:36)


  ...


>>> import sys


>>> sys.path


['', '/usr/local/lib/python35.zip', ...,


'~/envs/tutorial-env/lib/python3.5/site-packages']


>>>
```

Обратите внимание, что активированное виртуальное окружение никак не изменяет переменную PYTHONPATH . Это может привести к неожиданным результатам, если путь содержит ссылки на код, несовместимый с версией Python, используемой виртуальным окружением. В bash рекомендуется выполнить команду unset PYTHONPATH или её эквивалент для используемой вами оболочки.

Чтобы деактивировать виртуальное окружение, выполните:

```python
deactivate
```

в терминале.

## 12.3. Управление пакетами с помощью pip

Вы можете устанавливать, обновлять и удалять пакеты с помощью программы, называемой pip . По умолчанию pip будет устанавливать пакеты из Каталога пакетов Python . Вы можете просматривать его через web-браузер.

У pip есть несколько подкоманд: «install», «uninstall», «freeze» и т.д. (Подробную документацию по pip см. в руководстве Installing Python modules .)

Чтобы установить последнюю версию пакета, просто укажите его имя:

```python
(tutorial-env)
 
$ 
python
 
-m
 
pip
 
install
 
novas

Collecting novas


  Downloading novas-3.1.1.3.tar.gz (136kB)


Installing collected packages: novas


  Running setup.py install for novas


Successfully installed novas-3.1.1.3
```

Для установки конкретной версии пакета укажите его имя и == с номером версии:

```python
(tutorial-env)
 
$ 
python
 
-m
 
pip
 
install
 
requests
==
2
.6.0

Collecting requests==2.6.0


  Using cached requests-2.6.0-py2.py3-none-any.whl


Installing collected packages: requests


Successfully installed requests-2.6.0
```

Если вы повторно запустите эту команду, pip заметит, что запрошенная версия уже установлена и ничего не сделает. Вы можете указать другой номер версии, чтобы получить её, или можете запустить python -m pip install --upgrade , чтобы обновить пакет до последней версии.

```python
(tutorial-env)
 
$ 
python
 
-m
 
pip
 
install
 
--upgrade
 
requests

Collecting requests


Installing collected packages: requests


  Found existing installation: requests 2.6.0


    Uninstalling requests-2.6.0:


      Successfully uninstalled requests-2.6.0


Successfully installed requests-2.7.0
```

Команда python -m pip uninstall с одним или несколькими именами пакетов удаляет их из виртуального окружения.

Команда python -m pip show выводит информацию о конкретном пакете:

```python
(tutorial-env)
 
$ 
python
 
-m
 
pip
 
show
 
requests

---


Metadata-Version: 2.0


Name: requests


Version: 2.7.0


Summary: Python HTTP for Humans.


Home-page: http://python-requests.org


Author: Kenneth Reitz


Author-email: me@kennethreitz.com


License: Apache 2.0


Location: /Users/akuchling/envs/tutorial-env/lib/python3.4/site-packages


Requires:
```

Команда python -m pip list покажет все установленные в виртуальном окружении пакеты:

```python
(tutorial-env)
 
$ 
python
 
-m
 
pip
 
list

novas (3.1.1.3)


numpy (1.9.2)


pip (7.0.3)


requests (2.7.0)


setuptools (16.0)
```

Команда python -m pip freeze выводит аналогичный список установленных пакетов, но в формате, который ожидает python -m pip install . Обычно этот список сохраняют в файл requirements.txt :

```python
(tutorial-env)
 
$ 
python
 
-m
 
pip
 
freeze
 
>
 
requirements.txt

(tutorial-env)
 
$ 
cat
 
requirements.txt

novas==3.1.1.3


numpy==1.9.2


requests==2.7.0
```

Файл requirements.txt можно сохранить в системе контроля версий и распространять вместе с приложением. После этого пользователи смогут установить все необходимые пакеты командой install -r :

```python
(tutorial-env)
 
$ 
python
 
-m
 
pip
 
install
 
-r
 
requirements.txt

Collecting novas==3.1.1.3 (from -r requirements.txt (line 1))


  ...


Collecting numpy==1.9.2 (from -r requirements.txt (line 2))


  ...


Collecting requests==2.7.0 (from -r requirements.txt (line 3))


  ...


Installing collected packages: novas, numpy, requests


  Running setup.py install for novas


Successfully installed novas-3.1.1.3 numpy-1.9.2 requests-2.7.0
```

Инструмент pip имеет много других опций. Для полной документации по pip обратитесь к руководству Installing Python modules . Когда вы напишете собственный пакет и захотите разместить его в Каталоге пакетов Python, обратитесь к руководству пользователя по пакетированию в Python .