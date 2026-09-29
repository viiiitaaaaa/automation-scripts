> Источник: https://habr.com/ru/companies/piter/articles/893088 — копия для личной справки, права у автора.

### Основы

```python
import sys

class SomeObject:
    def __del__(self):
        print(f"(Deleting {self=})")

obj = SomeObject()

print(sys.getrefcount(obj))  # 2

obj2 = obj
print(sys.getrefcount(obj))  # 3

obj = None
obj2 = None

# (Deleting self=<__main__.SomeObject object at 0x7d303fee7e80>)
```

```python
import weakref

obj = SomeObject()

reference = weakref.ref(obj)

print(reference)  # <weakref at 0x734b0a514590; to 'SomeObject' at 0x734b0a4e7700>
print(reference())  # <__main__.SomeObject object at 0x707038c0b700>
print(obj.__weakref__)  # <weakref at 0x734b0a514590; to 'SomeObject' at 0x734b0a4e7700>

print(sys.getrefcount(obj))  # 2

obj = None

# (Deleting self=<__main__.SomeObject object at 0x70744d42b700>)

print(reference)  # <weakref at 0x7988e2d70590; dead>
print(reference())  # None
```

```python
obj = SomeObject()

reference = weakref.proxy(obj)

print(reference)  # <__main__.SomeObject object at 0x78a420e6b700>

obj.attr = 1
print(reference.attr)  # 1
```

### Когда этим можно пользоваться

```python
class Node:
    def __init__(self, value):
        self.value = value
        self._parent = None
        self.children = []

    def __repr__(self):
        return "Node({!r:})".format(self.value)

    @property
    def parent(self):
        return self._parent if self._parent is None else self._parent()

    @parent.setter
    def parent(self, node):
        self._parent = weakref.ref(node)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

root = Node("parent")
n = Node("child")
root.add_child(n)
print(n.parent)  # Node('parent')

del root
print(n.parent)  # None
```

```python
class Node:
    def __init__(self, value):
        self.value = value
        self._children = weakref.WeakValueDictionary()

    @property
    def children(self):
        return list(self._children.items())

    def add_child(self, key, child):
        self._children[key] = child

root = Node("parent")
n1 = Node("child one")
n2 = Node("child two")
root.add_child("n1", n1)
root.add_child("n2", n2)
print(root.children)  # [('n1', Node('child one')), ('n2', Node('child two'))]

del n1
print(root.children)  # [('n2', Node('child two'))]
```

```python
class Observable:
    def __init__(self):
        self._observers = weakref.WeakSet()

    def register_observer(self, obs):
        self._observers.add(obs)

    def notify_observers(self, *args, **kwargs):
        for obs in self._observers:
            obs.notify(self, *args, **kwargs)


class Observer:
    def __init__(self, observable):
        observable.register_observer(self)

    def notify(self, observable, *args, **kwargs):
        print("Got", args, kwargs, "From", observable)


subject = Observable()
observer = Observer(subject)
subject.notify_observers("test", kw="python")
# Got ('test',) {'kw': 'python'} From <__main__.Observable object at 0x757957b892d0>
```

```python
import tempfile, shutil
from pathlib import Path

class TempDir:
    def __init__(self):
        self.name = tempfile.mkdtemp()
        self._finalizer = weakref.finalize(self, shutil.rmtree, self.name)

    def __repr__(self):
        return "TempDir({!r:})".format(self.name)

    def remove(self):
        self._finalizer()

    @property
    def removed(self):
        return not self._finalizer.alive

tmp = TempDir()
print(tmp)  # TempDir('/tmp/tmp8o0aecl3')
print(tmp.removed)  # False
print(Path(tmp.name).is_dir()) # True
```

### Примеры из реальной практики

```python
import logging
a = logging.getLogger("first")
b = logging.getLogger("second")
print(a is b)  # False

c = logging.getLogger("first")
print(a is c)  # True
```

```python
class Logger:
    def __init__(self, name):
        self.name = name

_logger_cache = weakref.WeakValueDictionary()

def get_logger(name):
    if name not in _logger_cache:
        l = Logger(name)
        _logger_cache[name] = l
    else:
        l = _logger_cache[name]
    return l

a = get_logger("first")
b = get_logger("second")
print(a is b)  # False

c = get_logger("first")
print(a is c)  # True
```

```python
from _weakref import proxy as _proxy

class OrderedDict(dict):

    def __new__(cls, /, *args, **kwds):
        self = dict.__new__(cls)
        self.__hardroot = _Link()
        self.__root = root = _proxy(self.__hardroot)
        root.prev = root.next = root
        self.__map = {}
        return self
```

### Заключение