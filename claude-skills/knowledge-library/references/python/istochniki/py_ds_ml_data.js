// PY-DS-ML — База функций Python ML/DS
// Версия: 3.0 | Функций: 755 | Библиотек: 30
window.PY_DS_ML_DATA = [
  {
    "lib": "numpy",
    "name": "np.array()",
    "lvl": "beginner",
    "syntax": "np.array(object, dtype=None, copy=True)",
    "desc": "Создаёт многомерный массив из списка/кортежа. Основной тип NumPy.",
    "tags": [
      "массивы",
      "создание"
    ],
    "ex": "arr = np.array([1, 2, 3, 4, 5])"
  },
  {
    "lib": "numpy",
    "name": "np.zeros()",
    "lvl": "beginner",
    "syntax": "np.zeros(shape, dtype=float)",
    "desc": "Массив заданной формы, заполненный нулями.",
    "tags": [
      "массивы",
      "инициализация"
    ],
    "ex": "z = np.zeros((3, 4))"
  },
  {
    "lib": "numpy",
    "name": "np.ones()",
    "lvl": "beginner",
    "syntax": "np.ones(shape, dtype=float)",
    "desc": "Массив заданной формы, заполненный единицами.",
    "tags": [
      "массивы",
      "инициализация"
    ],
    "ex": "o = np.ones((2, 5))"
  },
  {
    "lib": "numpy",
    "name": "np.empty()",
    "lvl": "beginner",
    "syntax": "np.empty(shape, dtype=float)",
    "desc": "Неинициализированный массив (быстрее zeros/ones).",
    "tags": [
      "массивы",
      "инициализация"
    ],
    "ex": "e = np.empty((100, 100))"
  },
  {
    "lib": "numpy",
    "name": "np.full()",
    "lvl": "beginner",
    "syntax": "np.full(shape, fill_value)",
    "desc": "Массив, заполненный указанным значением.",
    "tags": [
      "массивы",
      "инициализация"
    ],
    "ex": "f = np.full((3, 3), 7)"
  },
  {
    "lib": "numpy",
    "name": "np.eye()",
    "lvl": "beginner",
    "syntax": "np.eye(N, M=None, k=0)",
    "desc": "Единичная матрица NxN. k — смещение диагонали.",
    "tags": [
      "массивы",
      "инициализация"
    ],
    "ex": "I = np.eye(3)\nD = np.eye(4, k=1)"
  },
  {
    "lib": "numpy",
    "name": "np.identity()",
    "lvl": "beginner",
    "syntax": "np.identity(n)",
    "desc": "Квадратная единичная матрица nxn.",
    "tags": [
      "массивы",
      "инициализация"
    ],
    "ex": "I = np.identity(4)"
  },
  {
    "lib": "numpy",
    "name": "np.arange()",
    "lvl": "beginner",
    "syntax": "np.arange(start, stop, step)",
    "desc": "Одномерный массив с равномерным шагом.",
    "tags": [
      "массивы",
      "генерация"
    ],
    "ex": "x = np.arange(0, 10, 0.5)"
  },
  {
    "lib": "numpy",
    "name": "np.linspace()",
    "lvl": "beginner",
    "syntax": "np.linspace(start, stop, num=50, endpoint=True)",
    "desc": "num равномерных значений от start до stop включительно.",
    "tags": [
      "массивы",
      "генерация"
    ],
    "ex": "x = np.linspace(0, 2*np.pi, 100)"
  },
  {
    "lib": "numpy",
    "name": "np.logspace()",
    "lvl": "beginner",
    "syntax": "np.logspace(start, stop, num=50, base=10)",
    "desc": "Логарифмическая шкала: base^start … base^stop.",
    "tags": [
      "массивы",
      "генерация"
    ],
    "ex": "x = np.logspace(0, 3, 4)  # [1, 10, 100, 1000]"
  },
  {
    "lib": "numpy",
    "name": "np.geomspace()",
    "lvl": "beginner",
    "syntax": "np.geomspace(start, stop, num=50)",
    "desc": "Геометрическая прогрессия.",
    "tags": [
      "массивы",
      "генерация"
    ],
    "ex": "x = np.geomspace(1, 1000, 4)"
  },
  {
    "lib": "numpy",
    "name": "np.meshgrid()",
    "lvl": "intermediate",
    "syntax": "np.meshgrid(x, y, indexing='xy')",
    "desc": "Сетка координат из одномерных массивов. Для 2D/3D графиков.",
    "tags": [
      "массивы"
    ],
    "ex": "X, Y = np.meshgrid(x, y)\nZ = np.sin(X) * np.cos(Y)"
  },
  {
    "lib": "numpy",
    "name": "np.ogrid / np.mgrid",
    "lvl": "intermediate",
    "syntax": "np.ogrid[0:5, 0:5]",
    "desc": "Open/密集 grid — экономит память (ogrid) или полная сетка (mgrid).",
    "tags": [
      "массивы"
    ],
    "ex": "x, y = np.ogrid[0:5, 0:5]"
  },
  {
    "lib": "numpy",
    "name": "np.diag()",
    "lvl": "beginner",
    "syntax": "np.diag(v, k=0)",
    "desc": "Извлечь диагональ или создать диагональную матрицу.",
    "tags": [
      "массивы",
      "матрицы"
    ],
    "ex": "d = np.diag([1, 2, 3])\nv = np.diag(matrix)"
  },
  {
    "lib": "numpy",
    "name": "np.triu() / np.tril()",
    "lvl": "beginner",
    "syntax": "np.triu(m, k=0)\nnp.tril(m, k=0)",
    "desc": "Верхняя / нижняя треугольная часть матрицы.",
    "tags": [
      "массивы",
      "матрицы"
    ],
    "ex": "upper = np.triu(matrix, k=1)"
  },
  {
    "lib": "numpy",
    "name": "np.tile()",
    "lvl": "beginner",
    "syntax": "np.tile(A, reps)",
    "desc": "Повторить массив reps раз в каждом измерении.",
    "tags": [
      "массивы"
    ],
    "ex": "tiled = np.tile([0,1], (3,2))  # 3x4"
  },
  {
    "lib": "numpy",
    "name": "np.repeat()",
    "lvl": "beginner",
    "syntax": "np.repeat(a, repeats, axis=None)",
    "desc": "Повторить каждый элемент repeats раз.",
    "tags": [
      "массивы"
    ],
    "ex": "r = np.repeat([1,2,3], 2)  # [1,1,2,2,3,3]"
  },
  {
    "lib": "numpy",
    "name": "np.pad()",
    "lvl": "intermediate",
    "syntax": "np.pad(array, pad_width, mode='constant')",
    "desc": "Дополнить массив значениями по краям. mode: constant, edge, reflect.",
    "tags": [
      "массивы",
      "padding"
    ],
    "ex": "padded = np.pad(img, ((1,1),(1,1)), mode='edge')"
  },
  {
    "lib": "numpy",
    "name": "np.flip()",
    "lvl": "beginner",
    "syntax": "np.flip(m, axis=None)",
    "desc": "Перевернуть массив вдоль оси. axis=0 — строки, 1 — столбцы.",
    "tags": [
      "массивы"
    ],
    "ex": "flipped = np.flip(arr, axis=0)"
  },
  {
    "lib": "numpy",
    "name": "np.rot90()",
    "lvl": "beginner",
    "syntax": "np.rot90(m, k=1)",
    "desc": "Повернуть матрицу на 90° k раз против часовой.",
    "tags": [
      "массивы"
    ],
    "ex": "rotated = np.rot90(matrix, k=1)"
  },
  {
    "lib": "numpy",
    "name": "np.transpose()",
    "lvl": "beginner",
    "syntax": "np.transpose(a, axes=None)",
    "desc": "Транспонировать массив. .T — сокращение для 2D.",
    "tags": [
      "массивы"
    ],
    "ex": "t = np.transpose(arr, (1, 0, 2))"
  },
  {
    "lib": "numpy",
    "name": "np.reshape()",
    "lvl": "beginner",
    "syntax": "np.reshape(a, newshape)",
    "desc": "Изменить форму. -1 = автоопределение.",
    "tags": [
      "форма"
    ],
    "ex": "arr.reshape(2, 3)\nb = arr.reshape(-1, 1)"
  },
  {
    "lib": "numpy",
    "name": "np.ravel()",
    "lvl": "beginner",
    "syntax": "np.ravel(a, order='C')",
    "desc": "В одномерный массив (вид, без копирования).",
    "tags": [
      "форма"
    ],
    "ex": "flat = arr.ravel()"
  },
  {
    "lib": "numpy",
    "name": "np.flatten()",
    "lvl": "beginner",
    "syntax": "np.flatten(order='C')",
    "desc": "В одномерный массив (копия).",
    "tags": [
      "форма"
    ],
    "ex": "flat = arr.flatten()"
  },
  {
    "lib": "numpy",
    "name": "np.squeeze()",
    "lvl": "beginner",
    "syntax": "np.squeeze(a, axis=None)",
    "desc": "Убрать оси размером 1.",
    "tags": [
      "форма"
    ],
    "ex": "s = np.squeeze(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.expand_dims()",
    "lvl": "beginner",
    "syntax": "np.expand_dims(a, axis)",
    "desc": "Добавить ось размером 1.",
    "tags": [
      "форма"
    ],
    "ex": "e = np.expand_dims(arr, axis=0)"
  },
  {
    "lib": "numpy",
    "name": "np.newaxis",
    "lvl": "beginner",
    "syntax": "arr[:, np.newaxis]",
    "desc": "Добавить ось через срез (None тоже работает).",
    "tags": [
      "форма"
    ],
    "ex": "col = arr[:, np.newaxis]\nrow = arr[np.newaxis, :]"
  },
  {
    "lib": "numpy",
    "name": "np.swapaxes()",
    "lvl": "intermediate",
    "syntax": "np.swapaxes(a, axis1, axis2)",
    "desc": "Поменять две оси местами.",
    "tags": [
      "форма"
    ],
    "ex": "swapped = np.swapaxes(arr, 0, 1)"
  },
  {
    "lib": "numpy",
    "name": "np.moveaxis()",
    "lvl": "intermediate",
    "syntax": "np.moveaxis(a, source, destination)",
    "desc": "Переместить ось в новую позицию.",
    "tags": [
      "форма"
    ],
    "ex": "m = np.moveaxis(arr, 0, -1)"
  },
  {
    "lib": "numpy",
    "name": "np.where()",
    "lvl": "intermediate",
    "syntax": "np.where(condition, x, y)",
    "desc": "Элементы из x/y по условию. Без x,y — индексы True.",
    "tags": [
      "индексация",
      "логика"
    ],
    "ex": "np.where(arr>0, arr, 0)\nidx = np.where(arr>5)"
  },
  {
    "lib": "numpy",
    "name": "np.argwhere()",
    "lvl": "beginner",
    "syntax": "np.argwhere(condition)",
    "desc": "Индексы всех True-элементов. Возвращает (N, ndim).",
    "tags": [
      "индексация"
    ],
    "ex": "indices = np.argwhere(arr > 0)"
  },
  {
    "lib": "numpy",
    "name": "np.nonzero()",
    "lvl": "beginner",
    "syntax": "np.nonzero(a)",
    "desc": "Индексы ненулевых элементов (кортеж по осям).",
    "tags": [
      "индексация"
    ],
    "ex": "rows, cols = np.nonzero(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.take()",
    "lvl": "beginner",
    "syntax": "np.take(a, indices, axis=None)",
    "desc": "Взять элементы по индексам вдоль оси.",
    "tags": [
      "индексация"
    ],
    "ex": "selected = np.take(arr, [0, 2, 4], axis=0)"
  },
  {
    "lib": "numpy",
    "name": "np.put()",
    "lvl": "beginner",
    "syntax": "np.put(a, indices, values)",
    "desc": "Заменить элементы по индексам (in-place).",
    "tags": [
      "индексация"
    ],
    "ex": "np.put(arr, [0, 1], [99, 88])"
  },
  {
    "lib": "numpy",
    "name": "np.clip()",
    "lvl": "beginner",
    "syntax": "np.clip(a, a_min, a_max)",
    "desc": "Обрезать значения по диапазону.",
    "tags": [
      "индексация"
    ],
    "ex": "clipped = np.clip(arr, 0, 100)"
  },
  {
    "lib": "numpy",
    "name": "np.concatenate()",
    "lvl": "beginner",
    "syntax": "np.concatenate((a,b,...), axis=0)",
    "desc": "Объединить массивы вдоль оси.",
    "tags": [
      "объединение"
    ],
    "ex": "c = np.concatenate((a, b), axis=0)"
  },
  {
    "lib": "numpy",
    "name": "np.stack()",
    "lvl": "intermediate",
    "syntax": "np.stack(arrays, axis=0)",
    "desc": "Объединить по новой оси.",
    "tags": [
      "объединение"
    ],
    "ex": "s = np.stack([a, b], axis=0)"
  },
  {
    "lib": "numpy",
    "name": "np.hstack()",
    "lvl": "beginner",
    "syntax": "np.hstack(tup)",
    "desc": "Горизонтальная склейка (вдоль второй оси).",
    "tags": [
      "объединение"
    ],
    "ex": "h = np.hstack([a, b])"
  },
  {
    "lib": "numpy",
    "name": "np.vstack()",
    "lvl": "beginner",
    "syntax": "np.vstack(tup)",
    "desc": "Вертикальная склейка (вдоль первой оси).",
    "tags": [
      "объединение"
    ],
    "ex": "v = np.vstack([a, b])"
  },
  {
    "lib": "numpy",
    "name": "np.dstack()",
    "lvl": "beginner",
    "syntax": "np.dstack(tup)",
    "desc": "Склейка по глубине (третья ось).",
    "tags": [
      "объединение"
    ],
    "ex": "d = np.dstack([r, g, b])"
  },
  {
    "lib": "numpy",
    "name": "np.column_stack()",
    "lvl": "beginner",
    "syntax": "np.column_stack(tup)",
    "desc": "Склеить 1D массивы как столбцы в 2D.",
    "tags": [
      "объединение"
    ],
    "ex": "data = np.column_stack([x, y, z])"
  },
  {
    "lib": "numpy",
    "name": "np.row_stack()",
    "lvl": "beginner",
    "syntax": "np.row_stack(tup)",
    "desc": "Синоним vstack.",
    "tags": [
      "объединение"
    ],
    "ex": "r = np.row_stack([a, b])"
  },
  {
    "lib": "numpy",
    "name": "np.split()",
    "lvl": "beginner",
    "syntax": "np.split(ary, indices_or_sections, axis=0)",
    "desc": "Разбить на части.",
    "tags": [
      "разделение"
    ],
    "ex": "parts = np.split(arr, 3)"
  },
  {
    "lib": "numpy",
    "name": "np.array_split()",
    "lvl": "beginner",
    "syntax": "np.array_split(ary, indices, axis=0)",
    "desc": "Разбить (допускает неравные части).",
    "tags": [
      "разделение"
    ],
    "ex": "parts = np.array_split(arr, 3)"
  },
  {
    "lib": "numpy",
    "name": "np.hsplit() / vsplit()",
    "lvl": "beginner",
    "syntax": "np.hsplit(ary, sections)\nnp.vsplit(ary, sections)",
    "desc": "Горизонтальное/вертикальное разбиение.",
    "tags": [
      "разделение"
    ],
    "ex": "cols = np.hsplit(arr, 3)"
  },
  {
    "lib": "numpy",
    "name": "np.random.rand()",
    "lvl": "beginner",
    "syntax": "np.random.rand(d0, d1, ...)",
    "desc": "Случайные из [0, 1).",
    "tags": [
      "случайные"
    ],
    "ex": "r = np.random.rand(3, 3)"
  },
  {
    "lib": "numpy",
    "name": "np.random.randn()",
    "lvl": "beginner",
    "syntax": "np.random.randn(d0, d1, ...)",
    "desc": "Случайные из N(0,1).",
    "tags": [
      "случайные"
    ],
    "ex": "noise = np.random.randn(100, 10)"
  },
  {
    "lib": "numpy",
    "name": "np.random.randint()",
    "lvl": "beginner",
    "syntax": "np.random.randint(low, high, size)",
    "desc": "Случайные целые из [low, high).",
    "tags": [
      "случайные"
    ],
    "ex": "ints = np.random.randint(0, 10, (2, 5))"
  },
  {
    "lib": "numpy",
    "name": "np.random.choice()",
    "lvl": "beginner",
    "syntax": "np.random.choice(a, size, replace=True, p=None)",
    "desc": "Случайная выборка из массива.",
    "tags": [
      "случайные"
    ],
    "ex": "sample = np.random.choice(arr, 10, replace=False)"
  },
  {
    "lib": "numpy",
    "name": "np.random.shuffle()",
    "lvl": "beginner",
    "syntax": "np.random.shuffle(x)",
    "desc": "Перемешать массив на месте.",
    "tags": [
      "случайные"
    ],
    "ex": "np.random.shuffle(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.random.permutation()",
    "lvl": "beginner",
    "syntax": "np.random.permutation(x)",
    "desc": "Случайная перестановка (возвращает копию).",
    "tags": [
      "случайные"
    ],
    "ex": "permuted = np.random.permutation(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.random.seed()",
    "lvl": "beginner",
    "syntax": "np.random.seed(seed)",
    "desc": "Фиксировать seed для воспроизводимости.",
    "tags": [
      "случайные"
    ],
    "ex": "np.random.seed(42)"
  },
  {
    "lib": "numpy",
    "name": "np.random.RandomState()",
    "lvl": "intermediate",
    "syntax": "rng = np.random.RandomState(42)",
    "desc": "Локальный генератор (изолированный seed).",
    "tags": [
      "случайные"
    ],
    "ex": "rng = np.random.RandomState(42)\nrng.rand(10)"
  },
  {
    "lib": "numpy",
    "name": "np.random.default_rng()",
    "lvl": "intermediate",
    "syntax": "rng = np.random.default_rng(42)",
    "desc": "Новый API генератора (NumPy 1.17+). Рекомендован.",
    "tags": [
      "случайные"
    ],
    "ex": "rng = np.random.default_rng(42)\nrng.integers(0, 10, 5)"
  },
  {
    "lib": "numpy",
    "name": "np.mean()",
    "lvl": "beginner",
    "syntax": "np.mean(a, axis=None, keepdims=False)",
    "desc": "Среднее арифметическое.",
    "tags": [
      "статистика"
    ],
    "ex": "avg = np.mean(data, axis=0)"
  },
  {
    "lib": "numpy",
    "name": "np.median()",
    "lvl": "beginner",
    "syntax": "np.median(a, axis=None)",
    "desc": "Медиана.",
    "tags": [
      "статистика"
    ],
    "ex": "med = np.median(data)"
  },
  {
    "lib": "numpy",
    "name": "np.std()",
    "lvl": "beginner",
    "syntax": "np.std(a, axis=None, ddof=0)",
    "desc": "Стандартное отклонение. ddof=1 для выборочного.",
    "tags": [
      "статистика"
    ],
    "ex": "s = np.std(data, ddof=1)"
  },
  {
    "lib": "numpy",
    "name": "np.var()",
    "lvl": "beginner",
    "syntax": "np.var(a, axis=None)",
    "desc": "Дисперсия.",
    "tags": [
      "статистика"
    ],
    "ex": "v = np.var(data)"
  },
  {
    "lib": "numpy",
    "name": "np.percentile()",
    "lvl": "intermediate",
    "syntax": "np.percentile(a, q, axis=None)",
    "desc": "q-й перцентиль. q — число или список.",
    "tags": [
      "статистика"
    ],
    "ex": "p95 = np.percentile(data, 95)\nquartiles = np.percentile(data, [25, 50, 75])"
  },
  {
    "lib": "numpy",
    "name": "np.quantile()",
    "lvl": "intermediate",
    "syntax": "np.quantile(a, q, axis=None)",
    "desc": "Квантиль (q в долях 0..1).",
    "tags": [
      "статистика"
    ],
    "ex": "q = np.quantile(data, 0.95)"
  },
  {
    "lib": "numpy",
    "name": "np.sum()",
    "lvl": "beginner",
    "syntax": "np.sum(a, axis=None, keepdims=False)",
    "desc": "Сумма элементов.",
    "tags": [
      "статистика"
    ],
    "ex": "total = np.sum(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.prod()",
    "lvl": "beginner",
    "syntax": "np.prod(a, axis=None)",
    "desc": "Произведение элементов.",
    "tags": [
      "статистика"
    ],
    "ex": "p = np.prod(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.cumsum()",
    "lvl": "beginner",
    "syntax": "np.cumsum(a, axis=None)",
    "desc": "Кумулятивная сумма.",
    "tags": [
      "статистика"
    ],
    "ex": "cum = np.cumsum(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.cumprod()",
    "lvl": "beginner",
    "syntax": "np.cumprod(a, axis=None)",
    "desc": "Кумулятивное произведение.",
    "tags": [
      "статистика"
    ],
    "ex": "cum = np.cumprod(arr)"
  },
  {
    "lib": "numpy",
    "name": "np.min() / np.max()",
    "lvl": "beginner",
    "syntax": "np.min(a, axis=None) / np.max(a, axis=None)",
    "desc": "Минимум / максимум.",
    "tags": [
      "статистика"
    ],
    "ex": "lo, hi = np.min(data), np.max(data)"
  },
  {
    "lib": "numpy",
    "name": "np.argmin() / np.argmax()",
    "lvl": "beginner",
    "syntax": "np.argmin(a, axis=None) / np.argmax(a, axis=None)",
    "desc": "Индекс минимума / максимума.",
    "tags": [
      "статистика"
    ],
    "ex": "idx_max = np.argmax(arr, axis=1)"
  },
  {
    "lib": "numpy",
    "name": "np.ptp()",
    "lvl": "beginner",
    "syntax": "np.ptp(a, axis=None)",
    "desc": "Размах: max - min.",
    "tags": [
      "статистика"
    ],
    "ex": "r = np.ptp(data)"
  },
  {
    "lib": "numpy",
    "name": "np.corrcoef()",
    "lvl": "intermediate",
    "syntax": "np.corrcoef(x, y=None)",
    "desc": "Матрица коэффициентов корреляции.",
    "tags": [
      "статистика"
    ],
    "ex": "corr = np.corrcoef(x, y)"
  },
  {
    "lib": "numpy",
    "name": "np.histogram()",
    "lvl": "intermediate",
    "syntax": "np.histogram(a, bins=10, range=None)",
    "desc": "Гистограмма: counts и границы бинов.",
    "tags": [
      "статистика"
    ],
    "ex": "counts, bins = np.histogram(data, bins=30)"
  },
  {
    "lib": "numpy",
    "name": "np.histogram2d()",
    "lvl": "intermediate",
    "syntax": "np.histogram2d(x, y, bins=10)",
    "desc": "2D-гистограмма.",
    "tags": [
      "статистика"
    ],
    "ex": "H, xedges, yedges = np.histogram2d(x, y, bins=20)"
  },
  {
    "lib": "numpy",
    "name": "np.bincount()",
    "lvl": "beginner",
    "syntax": "np.bincount(x, weights=None)",
    "desc": "Подсчёт целых неотрицательных значений.",
    "tags": [
      "статистика"
    ],
    "ex": "counts = np.bincount(labels)"
  },
  {
    "lib": "numpy",
    "name": "np.unique()",
    "lvl": "beginner",
    "syntax": "np.unique(ar, return_counts=False)",
    "desc": "Уникальные значения (+ частоты).",
    "tags": [
      "статистика"
    ],
    "ex": "vals, counts = np.unique(arr, return_counts=True)"
  },
  {
    "lib": "numpy",
    "name": "np.diff()",
    "lvl": "beginner",
    "syntax": "np.diff(a, n=1, axis=-1)",
    "desc": "Разности между соседними элементами (n раз).",
    "tags": [
      "статистика",
      "производная"
    ],
    "ex": "dx = np.diff(x)\nd2x = np.diff(x, n=2)"
  },
  {
    "lib": "numpy",
    "name": "np.gradient()",
    "lvl": "intermediate",
    "syntax": "np.gradient(f, *varargs)",
    "desc": "Градиент (центральные разности).",
    "tags": [
      "производная"
    ],
    "ex": "dy, dx = np.gradient(Z)\nmag = np.sqrt(dx**2 + dy**2)"
  },
  {
    "lib": "numpy",
    "name": "np.all() / np.any()",
    "lvl": "beginner",
    "syntax": "np.all(a, axis=None) / np.any(a, axis=None)",
    "desc": "Все элементы True? / Хотя бы один True?",
    "tags": [
      "логика"
    ],
    "ex": "all_pos = np.all(arr > 0)\nany_nan = np.any(np.isnan(arr))"
  },
  {
    "lib": "numpy",
    "name": "np.isnan() / np.isinf()",
    "lvl": "beginner",
    "syntax": "np.isnan(x) / np.isinf(x)",
    "desc": "Проверка на NaN и бесконечность.",
    "tags": [
      "логика",
      "проверка"
    ],
    "ex": "nan_mask = np.isnan(data)\nfinite = data[~np.isinf(data)]"
  },
  {
    "lib": "numpy",
    "name": "np.isfinite() / np.isinf()",
    "lvl": "beginner",
    "syntax": "np.isfinite(x)",
    "desc": "Конечные значения (не NaN и не inf).",
    "tags": [
      "логика"
    ],
    "ex": "clean = data[np.isfinite(data)]"
  },
  {
    "lib": "numpy",
    "name": "np.isclose()",
    "lvl": "beginner",
    "syntax": "np.isclose(a, b, rtol=1e-5, atol=1e-8)",
    "desc": "Поэлементное сравнение с допуском.",
    "tags": [
      "логика"
    ],
    "ex": "equal = np.isclose(a, b)"
  },
  {
    "lib": "numpy",
    "name": "np.allclose()",
    "lvl": "beginner",
    "syntax": "np.allclose(a, b, rtol=1e-5, atol=1e-8)",
    "desc": "Все элементы близки с допуском?",
    "tags": [
      "логика"
    ],
    "ex": "if np.allclose(a, b): ..."
  },
  {
    "lib": "numpy",
    "name": "np.dot() / @",
    "lvl": "intermediate",
    "syntax": "np.dot(a, b)\na @ b",
    "desc": "Скалярное/матричное умножение.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "C = A @ B\ninner = np.dot(v, w)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.inv()",
    "lvl": "intermediate",
    "syntax": "np.linalg.inv(a)",
    "desc": "Обратная матрица.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "A_inv = np.linalg.inv(A)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.det()",
    "lvl": "intermediate",
    "syntax": "np.linalg.det(a)",
    "desc": "Определитель матрицы.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "d = np.linalg.det(A)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.eig()",
    "lvl": "intermediate",
    "syntax": "np.linalg.eig(a)",
    "desc": "Собственные значения и векторы.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "vals, vecs = np.linalg.eig(A)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.svd()",
    "lvl": "intermediate",
    "syntax": "np.linalg.svd(a, full_matrices=True)",
    "desc": "SVD-разложение: U, S, Vh.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "U, S, Vh = np.linalg.svd(A)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.norm()",
    "lvl": "intermediate",
    "syntax": "np.linalg.norm(x, ord=None)",
    "desc": "Норма вектора/матрицы. ord=2 — Евклидова, ord=1 — манхэттенская.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "n = np.linalg.norm(v)\nn2 = np.linalg.norm(M, ord='fro')"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.matrix_rank()",
    "lvl": "intermediate",
    "syntax": "np.linalg.matrix_rank(M, tol=None)",
    "desc": "Ранг матрицы.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "rank = np.linalg.matrix_rank(A)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.solve()",
    "lvl": "intermediate",
    "syntax": "np.linalg.solve(A, b)",
    "desc": "Решение Ax = b.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "x = np.linalg.solve(A, b)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.lstsq()",
    "lvl": "intermediate",
    "syntax": "np.linalg.lstsq(A, b, rcond=None)",
    "desc": "МНК: решение Ax~b.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "x, residuals, rank, s = np.linalg.lstsq(A, b)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.qr()",
    "lvl": "intermediate",
    "syntax": "np.linalg.qr(a)",
    "desc": "QR-разложение.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "Q, R = np.linalg.qr(A)"
  },
  {
    "lib": "numpy",
    "name": "np.linalg.cholesky()",
    "lvl": "advanced",
    "syntax": "np.linalg.cholesky(a)",
    "desc": "Разложение Холецкого для положительно определённых матриц.",
    "tags": [
      "линейная алгебра"
    ],
    "ex": "L = np.linalg.cholesky(A)"
  },
  {
    "lib": "pandas",
    "name": "pd.read_csv()",
    "lvl": "beginner",
    "syntax": "pd.read_csv(filepath, sep=',', header=0, encoding='utf-8', nrows=None)",
    "desc": "Чтение CSV. sep — разделитель, nrows — ограничить строки.",
    "tags": [
      "чтение",
      "csv"
    ],
    "ex": "df = pd.read_csv('data.csv', nrows=1000)"
  },
  {
    "lib": "pandas",
    "name": "pd.read_excel()",
    "lvl": "beginner",
    "syntax": "pd.read_excel(filepath, sheet_name=0, header=0)",
    "desc": "Чтение Excel. sheet_name — имя или индекс листа.",
    "tags": [
      "чтение",
      "excel"
    ],
    "ex": "df = pd.read_excel('data.xlsx', sheet_name='Sheet1')"
  },
  {
    "lib": "pandas",
    "name": "pd.read_json()",
    "lvl": "beginner",
    "syntax": "pd.read_json(path_or_buf, orient='records')",
    "desc": "Чтение JSON. orient: records, columns, index, split.",
    "tags": [
      "чтение",
      "json"
    ],
    "ex": "df = pd.read_json('data.json', orient='records')"
  },
  {
    "lib": "pandas",
    "name": "pd.read_sql()",
    "lvl": "intermediate",
    "syntax": "pd.read_sql(query, connection)",
    "desc": "Выполнить SQL-запрос и получить DataFrame.",
    "tags": [
      "чтение",
      "sql"
    ],
    "ex": "df = pd.read_sql('SELECT * FROM users', conn)"
  },
  {
    "lib": "pandas",
    "name": "pd.read_parquet()",
    "lvl": "intermediate",
    "syntax": "pd.read_parquet(path, columns=None)",
    "desc": "Чтение Parquet (столбцовый формат). Быстрее CSV.",
    "tags": [
      "чтение",
      "parquet"
    ],
    "ex": "df = pd.read_parquet('data.parquet')"
  },
  {
    "lib": "pandas",
    "name": "pd.read_feather()",
    "lvl": "intermediate",
    "syntax": "pd.read_feather(path)",
    "desc": "Чтение Feather (бинарный формат Arrow).",
    "tags": [
      "чтение",
      "feather"
    ],
    "ex": "df = pd.read_feather('data.feather')"
  },
  {
    "lib": "pandas",
    "name": "pd.read_clipboard()",
    "lvl": "beginner",
    "syntax": "pd.read_clipboard()",
    "desc": "Чтение таблицы из буфера обмена.",
    "tags": [
      "чтение"
    ],
    "ex": "df = pd.read_clipboard()"
  },
  {
    "lib": "pandas",
    "name": "pd.DataFrame()",
    "lvl": "beginner",
    "syntax": "pd.DataFrame(data=None, index=None, columns=None, dtype=None)",
    "desc": "Создать DataFrame из dict, list, numpy.",
    "tags": [
      "создание"
    ],
    "ex": "df = pd.DataFrame({'a':[1,2,3], 'b':[4,5,6]})"
  },
  {
    "lib": "pandas",
    "name": "pd.Series()",
    "lvl": "beginner",
    "syntax": "pd.Series(data=None, index=None, name=None)",
    "desc": "Одномерный индексированный массив.",
    "tags": [
      "создание"
    ],
    "ex": "s = pd.Series([1,2,3], index=['a','b','c'])"
  },
  {
    "lib": "pandas",
    "name": "df.to_csv()",
    "lvl": "beginner",
    "syntax": "df.to_csv(path, index=False, encoding='utf-8')",
    "desc": "Сохранить в CSV. index=False — без номеров строк.",
    "tags": [
      "запись"
    ],
    "ex": "df.to_csv('out.csv', index=False)"
  },
  {
    "lib": "pandas",
    "name": "df.to_excel()",
    "lvl": "beginner",
    "syntax": "df.to_excel(path, index=False, sheet_name='Sheet1')",
    "desc": "Сохранить в Excel.",
    "tags": [
      "запись"
    ],
    "ex": "df.to_excel('out.xlsx', index=False)"
  },
  {
    "lib": "pandas",
    "name": "df.to_parquet()",
    "lvl": "intermediate",
    "syntax": "df.to_parquet(path, index=False)",
    "desc": "Сохранить в Parquet.",
    "tags": [
      "запись"
    ],
    "ex": "df.to_parquet('data.parquet')"
  },
  {
    "lib": "pandas",
    "name": "df.head() / df.tail()",
    "lvl": "beginner",
    "syntax": "df.head(n=5)\ndf.tail(n=5)",
    "desc": "Первые / последние n строк.",
    "tags": [
      "просмотр"
    ],
    "ex": "df.head(10)\ndf.tail(3)"
  },
  {
    "lib": "pandas",
    "name": "df.sample()",
    "lvl": "beginner",
    "syntax": "df.sample(n=5, random_state=42)",
    "desc": "Случайная выборка строк.",
    "tags": [
      "просмотр"
    ],
    "ex": "sample = df.sample(frac=0.1)"
  },
  {
    "lib": "pandas",
    "name": "df.info()",
    "lvl": "beginner",
    "syntax": "df.info(verbose=True, show_counts=True)",
    "desc": "Типы столбцов, non-null count, память.",
    "tags": [
      "просмотр"
    ],
    "ex": "df.info()"
  },
  {
    "lib": "pandas",
    "name": "df.describe()",
    "lvl": "beginner",
    "syntax": "df.describe(percentiles=[.25,.5,.75], include=None)",
    "desc": "Статистика: count, mean, std, min, квартили, max.",
    "tags": [
      "просмотр",
      "статистика"
    ],
    "ex": "df.describe()\ndf.describe(include='object')"
  },
  {
    "lib": "pandas",
    "name": "df.shape / .columns / .index / .dtypes",
    "lvl": "beginner",
    "syntax": "df.shape\ndf.columns\ndf.index\ndf.dtypes",
    "desc": "Размер, колонки, индекс, типы данных.",
    "tags": [
      "просмотр"
    ],
    "ex": "n_rows, n_cols = df.shape\nprint(df.columns.tolist())"
  },
  {
    "lib": "pandas",
    "name": "df.value_counts()",
    "lvl": "beginner",
    "syntax": "df['col'].value_counts(normalize=False)",
    "desc": "Частоты уникальных значений.",
    "tags": [
      "просмотр"
    ],
    "ex": "df['category'].value_counts(normalize=True)"
  },
  {
    "lib": "pandas",
    "name": "df.nunique()",
    "lvl": "beginner",
    "syntax": "df.nunique(axis=0)",
    "desc": "Количество уникальных значений в каждом столбце.",
    "tags": [
      "просмотр"
    ],
    "ex": "unique_counts = df.nunique()"
  },
  {
    "lib": "pandas",
    "name": "df.memory_usage()",
    "lvl": "intermediate",
    "syntax": "df.memory_usage(deep=True)",
    "desc": "Использование памяти по столбцам.",
    "tags": [
      "просмотр",
      "оптимизация"
    ],
    "ex": "mem = df.memory_usage(deep=True).sum()"
  },
  {
    "lib": "pandas",
    "name": "df.loc[]",
    "lvl": "beginner",
    "syntax": "df.loc[row_indexer, column_indexer]",
    "desc": "Доступ по меткам (индексам).",
    "tags": [
      "выборка"
    ],
    "ex": "df.loc[df['age']>18, ['name','age']]"
  },
  {
    "lib": "pandas",
    "name": "df.iloc[]",
    "lvl": "beginner",
    "syntax": "df.iloc[row_indexer, column_indexer]",
    "desc": "Доступ по позициям (целочисленный).",
    "tags": [
      "выборка"
    ],
    "ex": "df.iloc[5:10, :3]"
  },
  {
    "lib": "pandas",
    "name": "df.at[] / df.iat[]",
    "lvl": "beginner",
    "syntax": "df.at[label, column]\ndf.iat[pos, col_pos]",
    "desc": "Быстрый доступ к скаляру (по метке / позиции).",
    "tags": [
      "выборка"
    ],
    "ex": "val = df.at[3, 'price']\ndf.iat[0, 0] = 999"
  },
  {
    "lib": "pandas",
    "name": "df.query()",
    "lvl": "beginner",
    "syntax": "df.query('age > 25 and city == \"Moscow\"')",
    "desc": "Фильтрация строк SQL-подобным синтаксисом.",
    "tags": [
      "выборка"
    ],
    "ex": "df.query('price > 100 and category == \"A\"')"
  },
  {
    "lib": "pandas",
    "name": "df.filter()",
    "lvl": "beginner",
    "syntax": "df.filter(items=None, like=None, regex=None)",
    "desc": "Выбор столбцов по имени, подстроке или regex.",
    "tags": [
      "выборка"
    ],
    "ex": "df.filter(like='date')\ndf.filter(regex='^val_')"
  },
  {
    "lib": "pandas",
    "name": "df.rename()",
    "lvl": "beginner",
    "syntax": "df.rename(columns={'old':'new'}, index={...})",
    "desc": "Переименовать столбцы или индексы.",
    "tags": [
      "модификация"
    ],
    "ex": "df.rename(columns={'old_name':'new_name'}, inplace=True)"
  },
  {
    "lib": "pandas",
    "name": "df.drop()",
    "lvl": "beginner",
    "syntax": "df.drop(labels, axis=0, inplace=False)",
    "desc": "Удалить строки/столбцы.",
    "tags": [
      "модификация"
    ],
    "ex": "df.drop(['col1','col2'], axis=1)\ndf.drop([0,1], axis=0)"
  },
  {
    "lib": "pandas",
    "name": "df.assign()",
    "lvl": "beginner",
    "syntax": "df.assign(new_col=lambda x: x['a'] + x['b'])",
    "desc": "Добавить новые столбцы (возвращает копию).",
    "tags": [
      "модификация"
    ],
    "ex": "df = df.assign(total=df['price']*df['qty'])"
  },
  {
    "lib": "pandas",
    "name": "df.astype()",
    "lvl": "beginner",
    "syntax": "df.astype({'col1': 'int32', 'col2': 'category'})",
    "desc": "Привести типы столбцов.",
    "tags": [
      "модификация",
      "оптимизация"
    ],
    "ex": "df = df.astype({'id':'int32','category':'category'})"
  },
  {
    "lib": "pandas",
    "name": "df.replace()",
    "lvl": "beginner",
    "syntax": "df.replace(to_replace, value)",
    "desc": "Заменить значения.",
    "tags": [
      "модификация"
    ],
    "ex": "df.replace([np.inf, -np.inf], np.nan)\ndf.replace({'city':{'Msc':'Moscow'}})"
  },
  {
    "lib": "pandas",
    "name": "df.sort_values()",
    "lvl": "beginner",
    "syntax": "df.sort_values(by, ascending=True, na_position='last')",
    "desc": "Сортировка по столбцу(ам).",
    "tags": [
      "сортировка"
    ],
    "ex": "df.sort_values(['city','age'], ascending=[True,False])"
  },
  {
    "lib": "pandas",
    "name": "df.sort_index()",
    "lvl": "beginner",
    "syntax": "df.sort_index(axis=0, ascending=True)",
    "desc": "Сортировка по индексу.",
    "tags": [
      "сортировка"
    ],
    "ex": "df.sort_index()"
  },
  {
    "lib": "pandas",
    "name": "df.nlargest() / .nsmallest()",
    "lvl": "beginner",
    "syntax": "df.nlargest(n, columns)\ndf.nsmallest(n, columns)",
    "desc": "n строк с наибольшими / наименьшими значениями.",
    "tags": [
      "сортировка"
    ],
    "ex": "top5 = df.nlargest(5, 'revenue')"
  },
  {
    "lib": "pandas",
    "name": "df.reset_index()",
    "lvl": "beginner",
    "syntax": "df.reset_index(drop=False)",
    "desc": "Сбросить индекс (превратить в столбец).",
    "tags": [
      "индекс"
    ],
    "ex": "df.reset_index(drop=True, inplace=True)"
  },
  {
    "lib": "pandas",
    "name": "df.set_index()",
    "lvl": "beginner",
    "syntax": "df.set_index(keys, drop=True)",
    "desc": "Установить столбец как индекс.",
    "tags": [
      "индекс"
    ],
    "ex": "df.set_index('id')"
  },
  {
    "lib": "pandas",
    "name": "df.isna() / df.notna()",
    "lvl": "beginner",
    "syntax": "df.isna()\ndf.notna()",
    "desc": "Маска NaN (True) или не-NaN.",
    "tags": [
      "пропуски"
    ],
    "ex": "df.isna().sum()\ndf[df['col'].notna()]"
  },
  {
    "lib": "pandas",
    "name": "df.dropna()",
    "lvl": "beginner",
    "syntax": "df.dropna(axis=0, how='any', thresh=None)",
    "desc": "Удалить строки/столбцы с NaN.",
    "tags": [
      "пропуски"
    ],
    "ex": "df.dropna(subset=['critical_col'])\ndf.dropna(thresh=3)"
  },
  {
    "lib": "pandas",
    "name": "df.fillna()",
    "lvl": "beginner",
    "syntax": "df.fillna(value, method=None, limit=None)",
    "desc": "Заполнить NaN. method='ffill'/'bfill'.",
    "tags": [
      "пропуски"
    ],
    "ex": "df.fillna(0)\ndf.fillna(method='ffill')\ndf['col'].fillna(df['col'].median())"
  },
  {
    "lib": "pandas",
    "name": "df.interpolate()",
    "lvl": "intermediate",
    "syntax": "df.interpolate(method='linear', limit_direction='forward')",
    "desc": "Интерполяция пропусков. method: linear, polynomial, spline.",
    "tags": [
      "пропуски"
    ],
    "ex": "df.interpolate(method='linear')"
  },
  {
    "lib": "pandas",
    "name": "df.groupby()",
    "lvl": "intermediate",
    "syntax": "df.groupby(by, axis=0, level=None).agg(func)",
    "desc": "Группировка + агрегация через .agg().",
    "tags": [
      "группировка"
    ],
    "ex": "df.groupby('cat')['val'].mean()\ndf.groupby(['city','year']).agg({'sales':'sum','clicks':'mean'})"
  },
  {
    "lib": "pandas",
    "name": "df.pivot_table()",
    "lvl": "intermediate",
    "syntax": "pd.pivot_table(df, values, index, columns, aggfunc='mean', fill_value=0)",
    "desc": "Сводная таблица.",
    "tags": [
      "группировка",
      "сводка"
    ],
    "ex": "pd.pivot_table(df, values='sales', index='region', columns='year', aggfunc='sum', fill_value=0)"
  },
  {
    "lib": "pandas",
    "name": "pd.crosstab()",
    "lvl": "intermediate",
    "syntax": "pd.crosstab(index, columns, values=None, aggfunc=None, normalize=False)",
    "desc": "Таблица сопряжённости (частоты/доли).",
    "tags": [
      "группировка",
      "сводка"
    ],
    "ex": "pd.crosstab(df['gender'], df['target'], normalize='index')"
  },
  {
    "lib": "pandas",
    "name": "df.transform()",
    "lvl": "intermediate",
    "syntax": "df.groupby('cat')['val'].transform('mean')",
    "desc": "Применить функцию с группировкой, вернуть той же формы.",
    "tags": [
      "группировка"
    ],
    "ex": "df['avg'] = df.groupby('cat')['val'].transform('mean')"
  },
  {
    "lib": "pandas",
    "name": "df.rolling()",
    "lvl": "intermediate",
    "syntax": "df['col'].rolling(window, min_periods=1).mean()",
    "desc": "Скользящее окно. .mean(), .sum(), .std(), .apply().",
    "tags": [
      "окно"
    ],
    "ex": "df['ma_7'] = df['price'].rolling(7).mean()"
  },
  {
    "lib": "pandas",
    "name": "df.expanding()",
    "lvl": "intermediate",
    "syntax": "df['col'].expanding(min_periods=1).sum()",
    "desc": "Расширяющееся окно (от начала до текущей строки).",
    "tags": [
      "окно"
    ],
    "ex": "df['cum_avg'] = df['value'].expanding().mean()"
  },
  {
    "lib": "pandas",
    "name": "df.shift()",
    "lvl": "beginner",
    "syntax": "df['col'].shift(periods=1)",
    "desc": "Сдвинуть значения вниз(>0) или вверх(<0).",
    "tags": [
      "окно",
      "сдвиг"
    ],
    "ex": "df['prev'] = df['value'].shift(1)\ndf['change'] = df['value'] - df['value'].shift(1)"
  },
  {
    "lib": "pandas",
    "name": "pd.merge()",
    "lvl": "intermediate",
    "syntax": "pd.merge(left, right, on='key', how='inner', suffixes=('_x','_y'))",
    "desc": "SQL JOIN. how: inner, left, right, outer, cross.",
    "tags": [
      "объединение"
    ],
    "ex": "pd.merge(df1, df2, on='id', how='left')"
  },
  {
    "lib": "pandas",
    "name": "pd.concat()",
    "lvl": "beginner",
    "syntax": "pd.concat(objs, axis=0, ignore_index=False, join='outer')",
    "desc": "Конкатенация по строкам (0) или столбцам (1).",
    "tags": [
      "объединение"
    ],
    "ex": "pd.concat([df1, df2], axis=0, ignore_index=True)"
  },
  {
    "lib": "pandas",
    "name": "df.join()",
    "lvl": "beginner",
    "syntax": "df.join(other, on=None, how='left')",
    "desc": "JOIN по индексу.",
    "tags": [
      "объединение"
    ],
    "ex": "df.join(df2, how='inner')"
  },
  {
    "lib": "pandas",
    "name": "pd.cut() / pd.qcut()",
    "lvl": "intermediate",
    "syntax": "pd.cut(x, bins, labels=None)\npd.qcut(x, q, labels=None)",
    "desc": "Разбить на интервалы (равные / квантильные).",
    "tags": [
      "преобразование"
    ],
    "ex": "df['age_group'] = pd.cut(df['age'], bins=[0,18,35,60,100])\ndf['decile'] = pd.qcut(df['val'], q=10)"
  },
  {
    "lib": "pandas",
    "name": "pd.get_dummies()",
    "lvl": "beginner",
    "syntax": "pd.get_dummies(df, columns=['cat'], drop_first=False)",
    "desc": "One-hot кодирование категорий.",
    "tags": [
      "преобразование"
    ],
    "ex": "df_enc = pd.get_dummies(df, columns=['city'])"
  },
  {
    "lib": "pandas",
    "name": "df.apply()",
    "lvl": "intermediate",
    "syntax": "df.apply(func, axis=0, raw=False)",
    "desc": "Применить функцию: axis=0 — к столбцам, 1 — к строкам.",
    "tags": [
      "apply"
    ],
    "ex": "df['total'] = df.apply(lambda r: r['a']+r['b'], axis=1)"
  },
  {
    "lib": "pandas",
    "name": "df.map() / Series.apply()",
    "lvl": "beginner",
    "syntax": "s.map(arg)\ns.apply(func)",
    "desc": "Поэлементная замена (map) или применение (apply).",
    "tags": [
      "apply"
    ],
    "ex": "df['cat_num'] = df['cat'].map({'A':1,'B':2})"
  },
  {
    "lib": "pandas",
    "name": "pd.to_datetime()",
    "lvl": "beginner",
    "syntax": "pd.to_datetime(arg, format=None, errors='raise')",
    "desc": "Конвертировать в datetime. format ускоряет.",
    "tags": [
      "даты"
    ],
    "ex": "df['date'] = pd.to_datetime(df['date_str'], format='%Y-%m-%d')"
  },
  {
    "lib": "pandas",
    "name": "pd.date_range()",
    "lvl": "beginner",
    "syntax": "pd.date_range(start, end, periods=None, freq='D')",
    "desc": "Последовательность дат. freq: D, W, M, Q, Y, H, T.",
    "tags": [
      "даты"
    ],
    "ex": "dates = pd.date_range('2026-01-01', periods=365, freq='D')"
  },
  {
    "lib": "pandas",
    "name": "Series.dt accessor",
    "lvl": "beginner",
    "syntax": "s.dt.year / .month / .day / .dayofweek / .quarter",
    "desc": "Извлечение компонентов даты через .dt.",
    "tags": [
      "даты"
    ],
    "ex": "df['year'] = df['date'].dt.year\ndf['month'] = df['date'].dt.month_name()"
  },
  {
    "lib": "pandas",
    "name": "df.resample()",
    "lvl": "intermediate",
    "syntax": "df.resample(rule, on='date').agg(func)",
    "desc": "Ресемплинг временных рядов. rule: D, W, M, Q, Y.",
    "tags": [
      "даты"
    ],
    "ex": "df.set_index('date').resample('M')['sales'].sum()"
  },
  {
    "lib": "pandas",
    "name": "Series.str accessor",
    "lvl": "beginner",
    "syntax": "s.str.lower() / .upper() / .strip() / .replace() / .split()",
    "desc": "Строковые операции через .str.",
    "tags": [
      "строки"
    ],
    "ex": "df['clean'] = df['text'].str.lower().str.strip()\ndf['first'] = df['name'].str.split().str[0]"
  },
  {
    "lib": "pandas",
    "name": "Series.str.contains()",
    "lvl": "beginner",
    "syntax": "s.str.contains(pat, case=True, regex=True)",
    "desc": "Проверка на вхождение подстроки/паттерна.",
    "tags": [
      "строки"
    ],
    "ex": "df[df['email'].str.contains('@gmail.com')]"
  },
  {
    "lib": "pandas",
    "name": "Series.str.extract()",
    "lvl": "intermediate",
    "syntax": "s.str.extract(pat, expand=True)",
    "desc": "Извлечь совпадения regex в столбцы.",
    "tags": [
      "строки"
    ],
    "ex": "df[['first','last']] = df['name'].str.extract(r'(\\w+)\\s+(\\w+)')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.plot()",
    "lvl": "beginner",
    "syntax": "plt.plot(x, y, fmt, **kwargs)",
    "desc": "Линейный график. fmt: 'b-' (синий), 'r--o' (красный пунктир с точками).",
    "tags": [
      "график",
      "линейный"
    ],
    "ex": "plt.plot(x, y, 'b-', label='data')\nplt.legend()"
  },
  {
    "lib": "matplotlib",
    "name": "plt.scatter()",
    "lvl": "beginner",
    "syntax": "plt.scatter(x, y, s=None, c=None, marker='o', alpha=None)",
    "desc": "Диаграмма рассеяния.",
    "tags": [
      "график",
      "рассеяние"
    ],
    "ex": "plt.scatter(x, y, c=colors, s=sizes, alpha=0.5, cmap='viridis')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.hist()",
    "lvl": "beginner",
    "syntax": "plt.hist(x, bins=10, range=None, density=False, alpha=0.7)",
    "desc": "Гистограмма.",
    "tags": [
      "график",
      "гистограмма"
    ],
    "ex": "plt.hist(data, bins=30, alpha=0.7, edgecolor='black')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.hist2d()",
    "lvl": "intermediate",
    "syntax": "plt.hist2d(x, y, bins=20, cmap='Blues')",
    "desc": "2D-гистограмма.",
    "tags": [
      "график",
      "гистограмма"
    ],
    "ex": "plt.hist2d(x, y, bins=30, cmap='viridis')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.bar() / plt.barh()",
    "lvl": "beginner",
    "syntax": "plt.bar(x, height, width=0.8)\nplt.barh(y, width)",
    "desc": "Столбчатая диаграмма вертикальная / горизонтальная.",
    "tags": [
      "график",
      "столбцы"
    ],
    "ex": "plt.bar(categories, values)\nplt.barh(categories, values)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.pie()",
    "lvl": "beginner",
    "syntax": "plt.pie(x, labels=None, autopct='%1.1f%%', startangle=90)",
    "desc": "Круговая диаграмма.",
    "tags": [
      "график",
      "pie"
    ],
    "ex": "plt.pie(sizes, labels=labels, autopct='%1.1f%%')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.errorbar()",
    "lvl": "intermediate",
    "syntax": "plt.errorbar(x, y, yerr=None, xerr=None, fmt='o')",
    "desc": "График с планками погрешностей.",
    "tags": [
      "график",
      "статистика"
    ],
    "ex": "plt.errorbar(x, y, yerr=std, fmt='o', capsize=5)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.fill_between()",
    "lvl": "intermediate",
    "syntax": "plt.fill_between(x, y1, y2, alpha=0.3)",
    "desc": "Заливка между кривыми (доверительные интервалы).",
    "tags": [
      "график"
    ],
    "ex": "plt.fill_between(x, y-std, y+std, alpha=0.2)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.stem()",
    "lvl": "beginner",
    "syntax": "plt.stem(x, y)",
    "desc": "Стеблевой график (для дискретных сигналов).",
    "tags": [
      "график"
    ],
    "ex": "plt.stem(x, y)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.step()",
    "lvl": "beginner",
    "syntax": "plt.step(x, y, where='mid')",
    "desc": "Ступенчатый график.",
    "tags": [
      "график"
    ],
    "ex": "plt.step(x, y, where='post')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.boxplot()",
    "lvl": "beginner",
    "syntax": "plt.boxplot(x, labels=None, showfliers=True)",
    "desc": "Ящик с усами (box-and-whiskers).",
    "tags": [
      "график",
      "статистика"
    ],
    "ex": "plt.boxplot([data1, data2], labels=['A','B'])"
  },
  {
    "lib": "matplotlib",
    "name": "plt.contour(), contourf()",
    "lvl": "intermediate",
    "syntax": "plt.contour(X, Y, Z, levels)\nplt.contourf(X, Y, Z, levels)",
    "desc": "Изолинии / залитые изолинии.",
    "tags": [
      "график",
      "3d"
    ],
    "ex": "plt.contour(X, Y, Z, levels=20)\nplt.contourf(X, Y, Z, levels=20, cmap='viridis')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.imshow()",
    "lvl": "beginner",
    "syntax": "plt.imshow(X, cmap=None, aspect='equal')",
    "desc": "Отображение 2D-матрицы как изображения.",
    "tags": [
      "график",
      "изображение"
    ],
    "ex": "plt.imshow(matrix, cmap='hot', interpolation='nearest')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.pcolormesh()",
    "lvl": "intermediate",
    "syntax": "plt.pcolormesh(X, Y, C, cmap='viridis')",
    "desc": "Псевдоцветовой график (быстрее pcolor).",
    "tags": [
      "график"
    ],
    "ex": "plt.pcolormesh(X, Y, Z, shading='auto')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.quiver()",
    "lvl": "intermediate",
    "syntax": "plt.quiver(X, Y, U, V)",
    "desc": "Векторное поле (стрелки).",
    "tags": [
      "график"
    ],
    "ex": "plt.quiver(X, Y, U, V, angles='xy')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.streamplot()",
    "lvl": "advanced",
    "syntax": "plt.streamplot(X, Y, U, V)",
    "desc": "Линии тока векторного поля.",
    "tags": [
      "график"
    ],
    "ex": "plt.streamplot(X, Y, U, V, density=2)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.subplots()",
    "lvl": "intermediate",
    "syntax": "fig, axes = plt.subplots(nrows, ncols, figsize=(w,h), sharex=False, sharey=False)",
    "desc": "Сетка подграфиков.",
    "tags": [
      "сетка"
    ],
    "ex": "fig, (ax1, ax2) = plt.subplots(1,2,figsize=(12,4))"
  },
  {
    "lib": "matplotlib",
    "name": "plt.subplot()",
    "lvl": "beginner",
    "syntax": "plt.subplot(nrows, ncols, index)",
    "desc": "Добавить подграфик в сетку (интерфейс MATLAB).",
    "tags": [
      "сетка"
    ],
    "ex": "plt.subplot(2,1,1); plt.plot(x1,y1)\nplt.subplot(2,1,2); plt.plot(x2,y2)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.tight_layout()",
    "lvl": "beginner",
    "syntax": "plt.tight_layout(pad=1.08)",
    "desc": "Автоматически подогнать отступы.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.tight_layout()"
  },
  {
    "lib": "matplotlib",
    "name": "plt.subplots_adjust()",
    "lvl": "intermediate",
    "syntax": "plt.subplots_adjust(left, bottom, right, top, wspace, hspace)",
    "desc": "Ручная настройка отступов.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.subplots_adjust(hspace=0.4, wspace=0.3)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.figure()",
    "lvl": "beginner",
    "syntax": "plt.figure(figsize=(10,6), dpi=100, facecolor='white')",
    "desc": "Создать новую фигуру.",
    "tags": [
      "оформление"
    ],
    "ex": "fig = plt.figure(figsize=(12, 8))"
  },
  {
    "lib": "matplotlib",
    "name": "plt.xlabel() / ylabel() / title()",
    "lvl": "beginner",
    "syntax": "plt.xlabel('text', fontsize=12)\nplt.ylabel('text')\nplt.title('text')",
    "desc": "Подписи осей и заголовок.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.xlabel('X axis')\nplt.ylabel('Y axis')\nplt.title('My Plot', fontsize=14)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.legend()",
    "lvl": "beginner",
    "syntax": "plt.legend(loc='best', frameon=True)",
    "desc": "Легенда графика.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.plot(x, y, label='Data')\nplt.legend(loc='upper right')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.grid()",
    "lvl": "beginner",
    "syntax": "plt.grid(True, alpha=0.3, linestyle='--')",
    "desc": "Сетка на графике.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.grid(True, which='both', alpha=0.3)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.xlim() / ylim()",
    "lvl": "beginner",
    "syntax": "plt.xlim(left, right)\nplt.ylim(bottom, top)",
    "desc": "Границы осей.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.xlim(0, 100)\nplt.ylim(-5, 5)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.xscale() / yscale()",
    "lvl": "beginner",
    "syntax": "plt.xscale('log')\nplt.yscale('log')",
    "desc": "Логарифмический масштаб осей.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.yscale('log')\nplt.xscale('symlog')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.xticks() / yticks()",
    "lvl": "beginner",
    "syntax": "plt.xticks(ticks, labels, rotation=45)",
    "desc": "Настройка меток осей.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.xticks(rotation=45, ha='right')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.text() / annotate()",
    "lvl": "beginner",
    "syntax": "plt.text(x, y, 'text')\nplt.annotate('text', xy=(x,y), arrowprops=dict(...))",
    "desc": "Текст и аннотации на графике.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.annotate('peak', xy=(5,10), xytext=(7,12), arrowprops=dict(arrowstyle='->'))"
  },
  {
    "lib": "matplotlib",
    "name": "plt.axhline() / axvline()",
    "lvl": "beginner",
    "syntax": "plt.axhline(y, color, linestyle, linewidth)\nplt.axvline(x, color, linestyle, linewidth)",
    "desc": "Горизонтальная / вертикальная линия.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.axhspan() / axvspan()",
    "lvl": "beginner",
    "syntax": "plt.axhspan(ymin, ymax, alpha=0.3)",
    "desc": "Залитый горизонтальный/вертикальный диапазон.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.axhspan(0, 10, alpha=0.2, color='green')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.colorbar()",
    "lvl": "beginner",
    "syntax": "plt.colorbar(mappable, label='Value')",
    "desc": "Цветовая шкала.",
    "tags": [
      "оформление"
    ],
    "ex": "im = plt.imshow(data); plt.colorbar(im, label='Intensity')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.savefig()",
    "lvl": "beginner",
    "syntax": "plt.savefig(fname, dpi=100, bbox_inches='tight', facecolor='white')",
    "desc": "Сохранить фигуру в файл.",
    "tags": [
      "сохранение"
    ],
    "ex": "plt.savefig('plot.png', dpi=300, bbox_inches='tight')"
  },
  {
    "lib": "matplotlib",
    "name": "plt.show()",
    "lvl": "beginner",
    "syntax": "plt.show(block=True)",
    "desc": "Показать все фигуры.",
    "tags": [
      "отображение"
    ],
    "ex": "plt.show()"
  },
  {
    "lib": "matplotlib",
    "name": "plt.clf() / cla()",
    "lvl": "beginner",
    "syntax": "plt.clf()  # очистить фигуру\nplt.cla()  # очистить axes",
    "desc": "Очистить фигуру/axes.",
    "tags": [
      "очистка"
    ],
    "ex": "plt.clf()\nplt.cla()"
  },
  {
    "lib": "matplotlib",
    "name": "plt.rcParams / rc()",
    "lvl": "beginner",
    "syntax": "plt.rcParams['figure.figsize'] = (10,6)\nplt.rc('lines', linewidth=2)",
    "desc": "Глобальные настройки по умолчанию.",
    "tags": [
      "настройка"
    ],
    "ex": "plt.rcParams.update({'figure.dpi': 150, 'font.size': 12})"
  },
  {
    "lib": "matplotlib",
    "name": "plt.style.use()",
    "lvl": "beginner",
    "syntax": "plt.style.use('seaborn-v0_8-darkgrid')",
    "desc": "Установить стиль из предустановленных.",
    "tags": [
      "настройка"
    ],
    "ex": "plt.style.use('ggplot')\nprint(plt.style.available)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.Circle() / Rectangle() / Polygon()",
    "lvl": "intermediate",
    "syntax": "plt.Circle((x,y), radius, **kwargs)\ngca().add_patch(circle)",
    "desc": "Геометрические фигуры.",
    "tags": [
      "фигуры"
    ],
    "ex": "circle = plt.Circle((0,0), 1, fill=False)\nplt.gca().add_patch(circle)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.matshow()",
    "lvl": "beginner",
    "syntax": "plt.matshow(A, cmap='viridis')",
    "desc": "Отобразить матрицу (удобно для корреляций).",
    "tags": [
      "матрицы"
    ],
    "ex": "plt.matshow(df.corr(), cmap='coolwarm')"
  },
  {
    "lib": "matplotlib",
    "name": "3D: Axes3D",
    "lvl": "intermediate",
    "syntax": "fig = plt.figure()\nax = fig.add_subplot(projection='3d')\nax.plot_surface(X,Y,Z)",
    "desc": "3D-графики: surface, scatter, contour.",
    "tags": [
      "3d"
    ],
    "ex": "ax.plot_surface(X, Y, Z, cmap='viridis')\nax.scatter(x, y, z, c=colors)"
  },
  {
    "lib": "matplotlib",
    "name": "plt.tick_params()",
    "lvl": "beginner",
    "syntax": "plt.tick_params(axis='both', labelsize=10, direction='in')",
    "desc": "Настройка внешнего вида делений.",
    "tags": [
      "оформление"
    ],
    "ex": "plt.tick_params(axis='x', rotation=45)"
  },
  {
    "lib": "seaborn",
    "name": "sns.heatmap()",
    "lvl": "beginner",
    "syntax": "sns.heatmap(data, annot=True, fmt='.2f', cmap='coolwarm', center=0)",
    "desc": "Тепловая карта.",
    "tags": [
      "визуализация",
      "корреляция"
    ],
    "ex": "sns.heatmap(df.corr(), annot=True, cmap='viridis')"
  },
  {
    "lib": "seaborn",
    "name": "sns.pairplot()",
    "lvl": "beginner",
    "syntax": "sns.pairplot(df, hue=None, diag_kind='hist', corner=False)",
    "desc": "Матрица scatter-графиков.",
    "tags": [
      "визуализация",
      "разведка"
    ],
    "ex": "sns.pairplot(iris, hue='species', corner=True)"
  },
  {
    "lib": "seaborn",
    "name": "sns.boxplot()",
    "lvl": "beginner",
    "syntax": "sns.boxplot(x, y, data, hue=None, palette='Set2')",
    "desc": "Ящик с усами.",
    "tags": [
      "визуализация",
      "статистика"
    ],
    "ex": "sns.boxplot(x='cat', y='val', hue='group', data=df)"
  },
  {
    "lib": "seaborn",
    "name": "sns.violinplot()",
    "lvl": "beginner",
    "syntax": "sns.violinplot(x, y, data, inner='quartile', split=False)",
    "desc": "Скрипичная диаграмма.",
    "tags": [
      "визуализация"
    ],
    "ex": "sns.violinplot(x='cat', y='val', data=df, inner='quartile')"
  },
  {
    "lib": "seaborn",
    "name": "sns.boxenplot()",
    "lvl": "beginner",
    "syntax": "sns.boxenplot(x, y, data, k_depth='tukey')",
    "desc": "Letter-value plot — для больших данных (>10K точек).",
    "tags": [
      "визуализация",
      "статистика"
    ],
    "ex": "sns.boxenplot(x='cat', y='val', data=large_df)"
  },
  {
    "lib": "seaborn",
    "name": "sns.countplot()",
    "lvl": "beginner",
    "syntax": "sns.countplot(x, data, hue=None, order=None)",
    "desc": "Частоты категорий.",
    "tags": [
      "визуализация",
      "категории"
    ],
    "ex": "sns.countplot(x='category', data=df, order=df['category'].value_counts().index)"
  },
  {
    "lib": "seaborn",
    "name": "sns.barplot()",
    "lvl": "beginner",
    "syntax": "sns.barplot(x, y, data, hue=None, ci=95)",
    "desc": "Столбцы со средним и доверительным интервалом.",
    "tags": [
      "визуализация"
    ],
    "ex": "sns.barplot(x='cat', y='val', data=df, estimator=np.mean)"
  },
  {
    "lib": "seaborn",
    "name": "sns.histplot()",
    "lvl": "beginner",
    "syntax": "sns.histplot(data, x, bins='auto', kde=True, hue=None)",
    "desc": "Гистограмма + KDE.",
    "tags": [
      "визуализация",
      "распределение"
    ],
    "ex": "sns.histplot(data=df, x='age', hue='gender', kde=True, bins=30)"
  },
  {
    "lib": "seaborn",
    "name": "sns.kdeplot()",
    "lvl": "beginner",
    "syntax": "sns.kdeplot(data, x, y=None, hue=None, fill=False)",
    "desc": "Оценка плотности распределения (KDE).",
    "tags": [
      "визуализация",
      "распределение"
    ],
    "ex": "sns.kdeplot(data=df, x='age', hue='gender', fill=True, alpha=0.3)"
  },
  {
    "lib": "seaborn",
    "name": "sns.ecdfplot()",
    "lvl": "beginner",
    "syntax": "sns.ecdfplot(data, x, hue=None)",
    "desc": "Эмпирическая функция распределения (CDF).",
    "tags": [
      "визуализация",
      "распределение"
    ],
    "ex": "sns.ecdfplot(data=df, x='score', hue='group')"
  },
  {
    "lib": "seaborn",
    "name": "sns.scatterplot()",
    "lvl": "beginner",
    "syntax": "sns.scatterplot(x, y, data, hue=None, size=None, style=None)",
    "desc": "Scatter-plot с категориями.",
    "tags": [
      "визуализация"
    ],
    "ex": "sns.scatterplot(x='age', y='income', hue='city', size='population', data=df)"
  },
  {
    "lib": "seaborn",
    "name": "sns.lineplot()",
    "lvl": "beginner",
    "syntax": "sns.lineplot(x, y, data, hue=None, ci=95)",
    "desc": "Линейный график с доверительным интервалом.",
    "tags": [
      "визуализация",
      "линейный"
    ],
    "ex": "sns.lineplot(x='date', y='sales', data=df, hue='product')"
  },
  {
    "lib": "seaborn",
    "name": "sns.relplot()",
    "lvl": "beginner",
    "syntax": "sns.relplot(x, y, data, col=None, row=None, hue=None, kind='scatter')",
    "desc": "Facet-график для отношений. kind: scatter/line.",
    "tags": [
      "визуализация",
      "facet"
    ],
    "ex": "sns.relplot(x='x',y='y',col='cat',data=df,kind='scatter')"
  },
  {
    "lib": "seaborn",
    "name": "sns.displot()",
    "lvl": "beginner",
    "syntax": "sns.displot(data, x, col=None, row=None, kind='hist', kde=True)",
    "desc": "Facet-график распределений.",
    "tags": [
      "визуализация",
      "facet"
    ],
    "ex": "sns.displot(data=df, x='age', col='gender', kde=True)"
  },
  {
    "lib": "seaborn",
    "name": "sns.catplot()",
    "lvl": "beginner",
    "syntax": "sns.catplot(x, y, data, col=None, kind='strip')",
    "desc": "Facet-график категорий. kind: strip, swarm, box, violin, bar, point.",
    "tags": [
      "визуализация",
      "facet"
    ],
    "ex": "sns.catplot(x='cat',y='val',col='group',data=df,kind='box')"
  },
  {
    "lib": "seaborn",
    "name": "sns.lmplot()",
    "lvl": "intermediate",
    "syntax": "sns.lmplot(x, y, data, hue=None, col=None)",
    "desc": "Линейная регрессия на scatter-графике.",
    "tags": [
      "визуализация",
      "регрессия"
    ],
    "ex": "sns.lmplot(x='sqft', y='price', data=df, hue='city')"
  },
  {
    "lib": "seaborn",
    "name": "sns.regplot()",
    "lvl": "intermediate",
    "syntax": "sns.regplot(x, y, data, scatter=True, ci=95)",
    "desc": "Scatter + линия регрессии + доверительный интервал.",
    "tags": [
      "визуализация",
      "регрессия"
    ],
    "ex": "sns.regplot(x='x', y='y', data=df, ci=95, scatter_kws={'alpha':0.3})"
  },
  {
    "lib": "seaborn",
    "name": "sns.jointplot()",
    "lvl": "beginner",
    "syntax": "sns.jointplot(x, y, data, kind='scatter')",
    "desc": "Совместное распределение двух переменных + маргинальные распределения.",
    "tags": [
      "визуализация"
    ],
    "ex": "sns.jointplot(x='x', y='y', data=df, kind='hex')"
  },
  {
    "lib": "seaborn",
    "name": "sns.clustermap()",
    "lvl": "intermediate",
    "syntax": "sns.clustermap(data, method='average', cmap='viridis')",
    "desc": "Тепловая карта с иерархической кластеризацией.",
    "tags": [
      "визуализация",
      "кластеризация"
    ],
    "ex": "sns.clustermap(df, method='ward', cmap='coolwarm')"
  },
  {
    "lib": "seaborn",
    "name": "sns.set_theme() / set_style()",
    "lvl": "beginner",
    "syntax": "sns.set_theme(style='darkgrid', palette='muted')\nsns.set_style('whitegrid')",
    "desc": "Глобальная тема и стиль.",
    "tags": [
      "настройка"
    ],
    "ex": "sns.set_theme(context='talk', style='whitegrid')"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.ttest_ind()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.ttest_ind(a, b, alternative='two-sided')",
    "desc": "T-тест для двух независимых выборок.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = ttest_ind(group_a, group_b)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.ttest_1samp()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.ttest_1samp(a, popmean)",
    "desc": "T-тест для сравнения среднего выборки с константой.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = ttest_1samp(sample, 100)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.ttest_rel()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.ttest_rel(a, b)",
    "desc": "T-тест для связанных (парных) выборок.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = ttest_rel(before, after)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.mannwhitneyu()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.mannwhitneyu(x, y, alternative='two-sided')",
    "desc": "U-критерий Манна-Уитни (непараметрический).",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = mannwhitneyu(group_a, group_b)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.wilcoxon()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.wilcoxon(x, y=None)",
    "desc": "Критерий Вилкоксона для парных выборок.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = wilcoxon(before, after)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.kruskal()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.kruskal(*samples)",
    "desc": "Критерий Краскела-Уоллиса для k независимых выборок.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = kruskal(g1, g2, g3)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.f_oneway()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.f_oneway(*samples)",
    "desc": "Однофакторный дисперсионный анализ (one-way ANOVA).",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = f_oneway(g1, g2, g3)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.pearsonr()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.pearsonr(x, y)",
    "desc": "Коэффициент корреляции Пирсона + p-value.",
    "tags": [
      "статистика",
      "корреляция"
    ],
    "ex": "r, p = pearsonr(x, y)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.spearmanr()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.spearmanr(x, y)",
    "desc": "Ранговая корреляция Спирмена.",
    "tags": [
      "статистика",
      "корреляция"
    ],
    "ex": "rho, p = spearmanr(x, y)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.kendalltau()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.kendalltau(x, y)",
    "desc": "Ранговая корреляция Кендалла (тау).",
    "tags": [
      "статистика",
      "корреляция"
    ],
    "ex": "tau, p = kendalltau(x, y)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.chi2_contingency()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.chi2_contingency(observed)",
    "desc": "Хи-квадрат тест на независимость.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "chi2, p, dof, expected = chi2_contingency(table)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.norm",
    "lvl": "intermediate",
    "syntax": "scipy.stats.norm(loc=0, scale=1)",
    "desc": "Нормальное распределение: .pdf, .cdf, .ppf, .rvs.",
    "tags": [
      "распределение"
    ],
    "ex": "norm.pdf(0); norm.ppf(0.975); norm.rvs(size=100)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.t",
    "lvl": "intermediate",
    "syntax": "scipy.stats.t(df, loc=0, scale=1)",
    "desc": "Распределение Стьюдента.",
    "tags": [
      "распределение"
    ],
    "ex": "t.ppf(0.975, df=10)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.f",
    "lvl": "intermediate",
    "syntax": "scipy.stats.f(dfn, dfd)",
    "desc": "F-распределение Фишера.",
    "tags": [
      "распределение"
    ],
    "ex": "f.ppf(0.95, dfn=3, dfd=20)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.chi2",
    "lvl": "intermediate",
    "syntax": "scipy.stats.chi2(df)",
    "desc": "Распределение хи-квадрат.",
    "tags": [
      "распределение"
    ],
    "ex": "chi2.ppf(0.95, df=5)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.expon",
    "lvl": "intermediate",
    "syntax": "scipy.stats.expon(scale=1.0)",
    "desc": "Экспоненциальное распределение.",
    "tags": [
      "распределение"
    ],
    "ex": "samples = expon.rvs(scale=2, size=1000)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.uniform",
    "lvl": "intermediate",
    "syntax": "scipy.stats.uniform(loc=0, scale=1)",
    "desc": "Равномерное распределение на [loc, loc+scale].",
    "tags": [
      "распределение"
    ],
    "ex": "uniform.rvs(loc=5, scale=10, size=100)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.describe()",
    "lvl": "beginner",
    "syntax": "scipy.stats.describe(a)",
    "desc": "Описательная статистика: n, min, max, mean, var, skew, kurtosis.",
    "tags": [
      "статистика"
    ],
    "ex": "result = describe(data)\nprint(result.mean, result.variance)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.zscore()",
    "lvl": "beginner",
    "syntax": "scipy.stats.zscore(a, axis=0)",
    "desc": "Z-нормализация: (x - mean) / std.",
    "tags": [
      "статистика"
    ],
    "ex": "z = zscore(data)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.iqr()",
    "lvl": "beginner",
    "syntax": "scipy.stats.iqr(x)",
    "desc": "Межквартильный размах (Q3 - Q1).",
    "tags": [
      "статистика"
    ],
    "ex": "iqr_val = iqr(data)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.skew()",
    "lvl": "beginner",
    "syntax": "scipy.stats.skew(a, axis=0)",
    "desc": "Асимметрия (skewness) распределения.",
    "tags": [
      "статистика"
    ],
    "ex": "skew_val = skew(data)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.kurtosis()",
    "lvl": "beginner",
    "syntax": "scipy.stats.kurtosis(a, axis=0)",
    "desc": "Эксцесс (kurtosis). fisher=True — excess kurtosis.",
    "tags": [
      "статистика"
    ],
    "ex": "k = kurtosis(data, fisher=True)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.shapiro()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.shapiro(x)",
    "desc": "Тест Шапиро-Уилка на нормальность.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = shapiro(data)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.normaltest()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.normaltest(a)",
    "desc": "Тест Д'Агостино на нормальность (skew + kurtosis).",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = normaltest(data)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.bartlett()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.bartlett(*samples)",
    "desc": "Тест Бартлетта на равенство дисперсий.",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = bartlett(g1, g2, g3)"
  },
  {
    "lib": "scipy",
    "name": "scipy.stats.levene()",
    "lvl": "intermediate",
    "syntax": "scipy.stats.levene(*samples)",
    "desc": "Тест Ливиня на равенство дисперсий (устойчив к ненормальности).",
    "tags": [
      "статистика",
      "тест"
    ],
    "ex": "stat, p = levene(g1, g2)"
  },
  {
    "lib": "scipy",
    "name": "scipy.optimize.minimize()",
    "lvl": "intermediate",
    "syntax": "scipy.optimize.minimize(fun, x0, method='BFGS', bounds=None)",
    "desc": "Минимизация скалярной функции многих переменных.",
    "tags": [
      "оптимизация"
    ],
    "ex": "res = minimize(lambda x: (x-3)**2, x0=0)\nprint(res.x)"
  },
  {
    "lib": "scipy",
    "name": "scipy.optimize.minimize_scalar()",
    "lvl": "beginner",
    "syntax": "scipy.optimize.minimize_scalar(fun, bounds=None, method='brent')",
    "desc": "Минимизация функции одной переменной.",
    "tags": [
      "оптимизация"
    ],
    "ex": "res = minimize_scalar(lambda x: (x-2)**2, bounds=(-5,5))"
  },
  {
    "lib": "scipy",
    "name": "scipy.optimize.curve_fit()",
    "lvl": "intermediate",
    "syntax": "scipy.optimize.curve_fit(f, xdata, ydata, p0=None)",
    "desc": "Подгонка функции к данным (МНК).",
    "tags": [
      "оптимизация",
      "фиттинг"
    ],
    "ex": "popt, pcov = curve_fit(lambda x,a,b: a*x+b, x, y)"
  },
  {
    "lib": "scipy",
    "name": "scipy.optimize.root()",
    "lvl": "intermediate",
    "syntax": "scipy.optimize.root(fun, x0, method='hybr')",
    "desc": "Поиск корня системы уравнений.",
    "tags": [
      "оптимизация"
    ],
    "ex": "sol = root(lambda x: [x[0]**2-4, x[1]-1], [1,1])"
  },
  {
    "lib": "scipy",
    "name": "scipy.optimize.fsolve()",
    "lvl": "intermediate",
    "syntax": "scipy.optimize.fsolve(func, x0)",
    "desc": "Поиск корня нелинейных уравнений (враппер hybr).",
    "tags": [
      "оптимизация"
    ],
    "ex": "sol = fsolve(lambda x: x**2 - 4, 1.0)"
  },
  {
    "lib": "scipy",
    "name": "scipy.interpolate.interp1d()",
    "lvl": "intermediate",
    "syntax": "scipy.interpolate.interp1d(x, y, kind='linear', fill_value='extrapolate')",
    "desc": "Одномерная интерполяция. kind: linear, cubic, nearest.",
    "tags": [
      "интерполяция"
    ],
    "ex": "f = interp1d(x, y, kind='cubic')\ny_new = f(x_new)"
  },
  {
    "lib": "scipy",
    "name": "scipy.interpolate.griddata()",
    "lvl": "intermediate",
    "syntax": "scipy.interpolate.griddata(points, values, xi, method='linear')",
    "desc": "Интерполяция неструктурированных N-мерных данных.",
    "tags": [
      "интерполяция"
    ],
    "ex": "zi = griddata((x, y), z, (xi, yi), method='cubic')"
  },
  {
    "lib": "scipy",
    "name": "scipy.interpolate.CubicSpline()",
    "lvl": "intermediate",
    "syntax": "scipy.interpolate.CubicSpline(x, y, bc_type='not-a-knot')",
    "desc": "Кубический сплайн (интерполяция).",
    "tags": [
      "интерполяция"
    ],
    "ex": "cs = CubicSpline(x, y)\ny_new = cs(x_new); dy = cs(x_new, 1)"
  },
  {
    "lib": "scipy",
    "name": "scipy.integrate.quad()",
    "lvl": "intermediate",
    "syntax": "scipy.integrate.quad(func, a, b)",
    "desc": "Численное интегрирование. Возвращает (значение, оценка ошибки).",
    "tags": [
      "интегрирование"
    ],
    "ex": "val, err = quad(lambda x: x**2, 0, 1)"
  },
  {
    "lib": "scipy",
    "name": "scipy.integrate.simpson()",
    "lvl": "intermediate",
    "syntax": "scipy.integrate.simpson(y, x=None)",
    "desc": "Интегрирование методом Симпсона.",
    "tags": [
      "интегрирование"
    ],
    "ex": "area = simpson(y, x=x)"
  },
  {
    "lib": "scipy",
    "name": "scipy.integrate.trapezoid()",
    "lvl": "intermediate",
    "syntax": "scipy.integrate.trapezoid(y, x=None)",
    "desc": "Интегрирование методом трапеций.",
    "tags": [
      "интегрирование"
    ],
    "ex": "area = trapezoid(y, x=x)"
  },
  {
    "lib": "scipy",
    "name": "scipy.integrate.odeint()",
    "lvl": "advanced",
    "syntax": "scipy.integrate.odeint(func, y0, t)",
    "desc": "Решение системы обыкновенных дифференциальных уравнений.",
    "tags": [
      "интегрирование",
      "оду"
    ],
    "ex": "y = odeint(lambda y,t: -k*y, y0=1.0, t=np.linspace(0,10,100))"
  },
  {
    "lib": "scipy",
    "name": "scipy.signal.find_peaks()",
    "lvl": "intermediate",
    "syntax": "scipy.signal.find_peaks(x, height=None, distance=None)",
    "desc": "Поиск пиков в сигнале.",
    "tags": [
      "сигнал"
    ],
    "ex": "peaks, props = find_peaks(signal, height=0.5, distance=10)"
  },
  {
    "lib": "scipy",
    "name": "scipy.signal.butter()",
    "lvl": "intermediate",
    "syntax": "scipy.signal.butter(N, Wn, btype='low', output='ba')",
    "desc": "Фильтр Баттерворта. btype: low, high, band, stop.",
    "tags": [
      "сигнал",
      "фильтр"
    ],
    "ex": "b, a = butter(4, 0.2, 'low')"
  },
  {
    "lib": "scipy",
    "name": "scipy.signal.filtfilt()",
    "lvl": "intermediate",
    "syntax": "scipy.signal.filtfilt(b, a, x)",
    "desc": "Фильтрация с нулевой фазой (прямой + обратный проход).",
    "tags": [
      "сигнал",
      "фильтр"
    ],
    "ex": "clean = filtfilt(b, a, noisy_signal)"
  },
  {
    "lib": "scipy",
    "name": "scipy.signal.convolve()",
    "lvl": "intermediate",
    "syntax": "scipy.signal.convolve(in1, in2, mode='full')",
    "desc": "Свёртка двух сигналов.",
    "tags": [
      "сигнал"
    ],
    "ex": "conv = convolve(signal, kernel, mode='same')"
  },
  {
    "lib": "scipy",
    "name": "scipy.signal.correlate()",
    "lvl": "intermediate",
    "syntax": "scipy.signal.correlate(in1, in2, mode='full')",
    "desc": "Кросс-корреляция двух сигналов.",
    "tags": [
      "сигнал"
    ],
    "ex": "corr = correlate(a, b, mode='same')"
  },
  {
    "lib": "scipy",
    "name": "scipy.signal.spectrogram()",
    "lvl": "intermediate",
    "syntax": "scipy.signal.spectrogram(x, fs=1.0)",
    "desc": "Спектрограмма: частоты, времена, амплитуды.",
    "tags": [
      "сигнал"
    ],
    "ex": "f, t, Sxx = spectrogram(signal, fs=1000)"
  },
  {
    "lib": "scipy",
    "name": "scipy.signal.stft()",
    "lvl": "intermediate",
    "syntax": "scipy.signal.stft(x, fs=1.0)",
    "desc": "Краткосрочное преобразование Фурье (STFT).",
    "tags": [
      "сигнал"
    ],
    "ex": "f, t, Zxx = stft(signal, fs=1000)"
  },
  {
    "lib": "scipy",
    "name": "scipy.sparse.csr_matrix()",
    "lvl": "intermediate",
    "syntax": "scipy.sparse.csr_matrix(data)",
    "desc": "Разреженная матрица в CSR-формате.",
    "tags": [
      "разреженные"
    ],
    "ex": "A = csr_matrix(dense_matrix)\ncsr_matrix((data, (row, col)), shape=(M,N))"
  },
  {
    "lib": "scipy",
    "name": "scipy.sparse.csc_matrix()",
    "lvl": "intermediate",
    "syntax": "scipy.sparse.csc_matrix(data)",
    "desc": "Разреженная матрица в CSC-формате.",
    "tags": [
      "разреженные"
    ],
    "ex": "A = csc_matrix(dense_matrix)"
  },
  {
    "lib": "scipy",
    "name": "scipy.sparse.lil_matrix()",
    "lvl": "intermediate",
    "syntax": "scipy.sparse.lil_matrix((M, N))",
    "desc": "Разреженная матрица в LIL-формате (для построения).",
    "tags": [
      "разреженные"
    ],
    "ex": "A = lil_matrix((1000, 1000)); A[0,0] = 1; A = A.tocsr()"
  },
  {
    "lib": "scipy",
    "name": "scipy.sparse.coo_matrix()",
    "lvl": "intermediate",
    "syntax": "scipy.sparse.coo_matrix((data, (i, j)))",
    "desc": "Координатный формат (удобен для создания).",
    "tags": [
      "разреженные"
    ],
    "ex": "A = coo_matrix(([1,2,3], ([0,1,2], [1,2,0])), shape=(3,3))"
  },
  {
    "lib": "scipy",
    "name": "scipy.spatial.distance.euclidean()",
    "lvl": "beginner",
    "syntax": "scipy.spatial.distance.euclidean(u, v)",
    "desc": "Евклидово расстояние между двумя векторами.",
    "tags": [
      "расстояние"
    ],
    "ex": "d = euclidean(point_a, point_b)"
  },
  {
    "lib": "scipy",
    "name": "scipy.spatial.distance.cosine()",
    "lvl": "beginner",
    "syntax": "scipy.spatial.distance.cosine(u, v)",
    "desc": "Косинусное расстояние (1 - косинусное сходство).",
    "tags": [
      "расстояние"
    ],
    "ex": "d = cosine(vec_a, vec_b)"
  },
  {
    "lib": "scipy",
    "name": "scipy.spatial.distance.cdist()",
    "lvl": "intermediate",
    "syntax": "scipy.spatial.distance.cdist(XA, XB, metric='euclidean')",
    "desc": "Матрица попарных расстояний.",
    "tags": [
      "расстояние"
    ],
    "ex": "dist_matrix = cdist(X_train, X_test, metric='cosine')"
  },
  {
    "lib": "scipy",
    "name": "scipy.cluster.hierarchy.linkage()",
    "lvl": "intermediate",
    "syntax": "scipy.cluster.hierarchy.linkage(y, method='ward')",
    "desc": "Иерархическая кластеризация. method: ward, single, complete.",
    "tags": [
      "кластеризация"
    ],
    "ex": "Z = linkage(data, method='ward')"
  },
  {
    "lib": "scipy",
    "name": "scipy.cluster.hierarchy.dendrogram()",
    "lvl": "intermediate",
    "syntax": "scipy.cluster.hierarchy.dendrogram(Z, labels=None)",
    "desc": "Дендрограмма иерархической кластеризации.",
    "tags": [
      "кластеризация"
    ],
    "ex": "dendrogram(Z, labels=labels, leaf_rotation=90)"
  },
  {
    "lib": "scipy",
    "name": "scipy.cluster.hierarchy.fcluster()",
    "lvl": "intermediate",
    "syntax": "scipy.cluster.hierarchy.fcluster(Z, t, criterion='distance')",
    "desc": "Извлечь плоские кластеры из linkage-дерева.",
    "tags": [
      "кластеризация"
    ],
    "ex": "clusters = fcluster(Z, t=3, criterion='maxclust')"
  },
  {
    "lib": "sklearn",
    "name": "train_test_split()",
    "lvl": "beginner",
    "syntax": "sklearn.model_selection.train_test_split(*arrays, test_size=0.25, random_state=42)",
    "desc": "Разбиение на обучающую и тестовую выборки.",
    "tags": [
      "ml",
      "разбиение"
    ],
    "ex": "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)"
  },
  {
    "lib": "sklearn",
    "name": "StandardScaler()",
    "lvl": "beginner",
    "syntax": "sklearn.preprocessing.StandardScaler()",
    "desc": "Стандартизация: (X - mean) / std.",
    "tags": [
      "preprocessing"
    ],
    "ex": "scaler = StandardScaler()\nX_scaled = scaler.fit_transform(X_train)"
  },
  {
    "lib": "sklearn",
    "name": "MinMaxScaler()",
    "lvl": "beginner",
    "syntax": "sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))",
    "desc": "Масштабирование в заданный диапазон.",
    "tags": [
      "preprocessing"
    ],
    "ex": "scaler = MinMaxScaler()\nX_norm = scaler.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "RobustScaler()",
    "lvl": "intermediate",
    "syntax": "sklearn.preprocessing.RobustScaler()",
    "desc": "Масштабирование через медиану и IQR (устойчиво к выбросам).",
    "tags": [
      "preprocessing"
    ],
    "ex": "scaler = RobustScaler()\nX_robust = scaler.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "MaxAbsScaler()",
    "lvl": "beginner",
    "syntax": "sklearn.preprocessing.MaxAbsScaler()",
    "desc": "Масштабирование по модулю максимума к [-1, 1].",
    "tags": [
      "preprocessing"
    ],
    "ex": "scaler = MaxAbsScaler()\nX_scaled = scaler.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "Normalizer()",
    "lvl": "beginner",
    "syntax": "sklearn.preprocessing.Normalizer(norm='l2')",
    "desc": "Нормализация строк к единичной норме.",
    "tags": [
      "preprocessing"
    ],
    "ex": "X_norm = Normalizer().fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "LabelEncoder()",
    "lvl": "beginner",
    "syntax": "sklearn.preprocessing.LabelEncoder()",
    "desc": "Кодирование меток от 0 до n_classes-1.",
    "tags": [
      "preprocessing"
    ],
    "ex": "le = LabelEncoder()\ny_enc = le.fit_transform(y)"
  },
  {
    "lib": "sklearn",
    "name": "OneHotEncoder()",
    "lvl": "beginner",
    "syntax": "sklearn.preprocessing.OneHotEncoder(sparse_output=True, drop=None)",
    "desc": "One-hot кодирование категориальных признаков.",
    "tags": [
      "preprocessing"
    ],
    "ex": "ohe = OneHotEncoder(drop='first')\nX_cat = ohe.fit_transform(df[['cat']])"
  },
  {
    "lib": "sklearn",
    "name": "OrdinalEncoder()",
    "lvl": "beginner",
    "syntax": "sklearn.preprocessing.OrdinalEncoder()",
    "desc": "Порядковое кодирование категорий.",
    "tags": [
      "preprocessing"
    ],
    "ex": "enc = OrdinalEncoder()\nX[:, cat_cols] = enc.fit_transform(X[:, cat_cols])"
  },
  {
    "lib": "sklearn",
    "name": "SimpleImputer()",
    "lvl": "beginner",
    "syntax": "sklearn.impute.SimpleImputer(strategy='mean')",
    "desc": "Заполнение пропусков. strategy: mean, median, most_frequent.",
    "tags": [
      "preprocessing",
      "пропуски"
    ],
    "ex": "imp = SimpleImputer(strategy='median')\nX = imp.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "KNNImputer()",
    "lvl": "intermediate",
    "syntax": "sklearn.impute.KNNImputer(n_neighbors=5)",
    "desc": "Заполнение пропусков методом k-ближайших соседей.",
    "tags": [
      "preprocessing",
      "пропуски"
    ],
    "ex": "imp = KNNImputer(n_neighbors=5)\nX = imp.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "PolynomialFeatures()",
    "lvl": "intermediate",
    "syntax": "sklearn.preprocessing.PolynomialFeatures(degree=2, include_bias=False)",
    "desc": "Генерация полиномиальных признаков.",
    "tags": [
      "preprocessing"
    ],
    "ex": "poly = PolynomialFeatures(degree=2)\nX_poly = poly.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "FunctionTransformer()",
    "lvl": "intermediate",
    "syntax": "sklearn.preprocessing.FunctionTransformer(func, inverse_func=None)",
    "desc": "Обёртка произвольной функции как трансформера.",
    "tags": [
      "preprocessing"
    ],
    "ex": "tr = FunctionTransformer(np.log1p, inverse_func=np.expm1)\nX_log = tr.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "PowerTransformer()",
    "lvl": "intermediate",
    "syntax": "sklearn.preprocessing.PowerTransformer(method='yeo-johnson')",
    "desc": "Приведение к нормальному распределению.",
    "tags": [
      "preprocessing"
    ],
    "ex": "pt = PowerTransformer()\nX_norm = pt.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "QuantileTransformer()",
    "lvl": "intermediate",
    "syntax": "sklearn.preprocessing.QuantileTransformer(output_distribution='normal')",
    "desc": "Квантильное преобразование к нормальному распределению.",
    "tags": [
      "preprocessing"
    ],
    "ex": "qt = QuantileTransformer(output_distribution='normal')\nX_t = qt.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "Pipeline()",
    "lvl": "intermediate",
    "syntax": "sklearn.pipeline.Pipeline(steps)",
    "desc": "Последовательность трансформеров и финального оценщика.",
    "tags": [
      "ml",
      "конвейер"
    ],
    "ex": "pipe = Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression())])\npipe.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "ColumnTransformer()",
    "lvl": "intermediate",
    "syntax": "sklearn.compose.ColumnTransformer(transformers)",
    "desc": "Разные трансформеры к разным колонкам.",
    "tags": [
      "preprocessing"
    ],
    "ex": "preprocessor = ColumnTransformer([('num', scaler, num_cols), ('cat', ohe, cat_cols)])"
  },
  {
    "lib": "sklearn",
    "name": "make_pipeline()",
    "lvl": "beginner",
    "syntax": "sklearn.pipeline.make_pipeline(*steps)",
    "desc": "Создать Pipeline без явных имён шагов.",
    "tags": [
      "ml",
      "конвейер"
    ],
    "ex": "pipe = make_pipeline(StandardScaler(), PCA(n_components=2), SVC())"
  },
  {
    "lib": "sklearn",
    "name": "cross_val_score()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.cross_val_score(estimator, X, y, cv=5, scoring='accuracy')",
    "desc": "Кросс-валидация с одной метрикой.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "scores = cross_val_score(model, X, y, cv=5, scoring='f1')"
  },
  {
    "lib": "sklearn",
    "name": "cross_validate()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.cross_validate(estimator, X, y, cv=5)",
    "desc": "Кросс-валидация с несколькими метриками и временем.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "cv_results = cross_validate(model, X, y, cv=5, scoring=['accuracy','f1'])"
  },
  {
    "lib": "sklearn",
    "name": "KFold()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.KFold(n_splits=5, shuffle=True, random_state=42)",
    "desc": "K-fold разбиение.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "kf = KFold(n_splits=5, shuffle=True)\nfor train_idx, val_idx in kf.split(X): ..."
  },
  {
    "lib": "sklearn",
    "name": "StratifiedKFold()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.StratifiedKFold(n_splits=5)",
    "desc": "K-fold с сохранением пропорций классов.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "skf = StratifiedKFold(n_splits=5)\nscores = cross_val_score(clf, X, y, cv=skf)"
  },
  {
    "lib": "sklearn",
    "name": "GroupKFold()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.GroupKFold(n_splits=5)",
    "desc": "K-fold: одна группа не в train и test одновременно.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "gkf = GroupKFold(n_splits=5)\nfor ti, vi in gkf.split(X, y, groups): ..."
  },
  {
    "lib": "sklearn",
    "name": "TimeSeriesSplit()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.TimeSeriesSplit(n_splits=5)",
    "desc": "Разбиение временных рядов: train < val по времени.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "tscv = TimeSeriesSplit(n_splits=5)\nfor ti, vi in tscv.split(X): ..."
  },
  {
    "lib": "sklearn",
    "name": "GridSearchCV()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.GridSearchCV(estimator, param_grid, cv=5)",
    "desc": "Поиск по сетке гиперпараметров.",
    "tags": [
      "ml",
      "подбор"
    ],
    "ex": "gs = GridSearchCV(RandomForestClassifier(), {'n_estimators':[100,200], 'max_depth':[5,10]}, cv=5)\ngs.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "RandomizedSearchCV()",
    "lvl": "intermediate",
    "syntax": "sklearn.model_selection.RandomizedSearchCV(estimator, param_distributions, n_iter=10)",
    "desc": "Случайный поиск гиперпараметров.",
    "tags": [
      "ml",
      "подбор"
    ],
    "ex": "rs = RandomizedSearchCV(model, distributions, n_iter=20, cv=5)\nrs.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "LogisticRegression()",
    "lvl": "intermediate",
    "syntax": "sklearn.linear_model.LogisticRegression(penalty='l2', C=1.0)",
    "desc": "Логистическая регрессия для классификации.",
    "tags": [
      "ml",
      "линейная"
    ],
    "ex": "clf = LogisticRegression()\nclf.fit(X_train, y_train)\nprobs = clf.predict_proba(X_test)"
  },
  {
    "lib": "sklearn",
    "name": "LinearRegression()",
    "lvl": "beginner",
    "syntax": "sklearn.linear_model.LinearRegression()",
    "desc": "Линейная регрессия методом наименьших квадратов.",
    "tags": [
      "ml",
      "линейная"
    ],
    "ex": "reg = LinearRegression()\nreg.fit(X_train, y_train)\ny_pred = reg.predict(X_test)"
  },
  {
    "lib": "sklearn",
    "name": "Ridge()",
    "lvl": "intermediate",
    "syntax": "sklearn.linear_model.Ridge(alpha=1.0)",
    "desc": "Линейная регрессия с L2-регуляризацией.",
    "tags": [
      "ml",
      "линейная"
    ],
    "ex": "ridge = Ridge(alpha=0.5)\nridge.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "Lasso()",
    "lvl": "intermediate",
    "syntax": "sklearn.linear_model.Lasso(alpha=1.0)",
    "desc": "Линейная регрессия с L1-регуляризацией.",
    "tags": [
      "ml",
      "линейная"
    ],
    "ex": "lasso = Lasso(alpha=0.01)\nlasso.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "ElasticNet()",
    "lvl": "intermediate",
    "syntax": "sklearn.linear_model.ElasticNet(alpha=1.0, l1_ratio=0.5)",
    "desc": "Линейная регрессия с L1+L2 регуляризацией.",
    "tags": [
      "ml",
      "линейная"
    ],
    "ex": "en = ElasticNet(alpha=0.01, l1_ratio=0.5)\nen.fit(X, y)"
  },
  {
    "lib": "sklearn",
    "name": "RandomForestClassifier()",
    "lvl": "intermediate",
    "syntax": "sklearn.ensemble.RandomForestClassifier(n_estimators=100, max_depth=None)",
    "desc": "Случайный лес для классификации.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "rf = RandomForestClassifier(n_estimators=200, max_depth=10)\nrf.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "RandomForestRegressor()",
    "lvl": "intermediate",
    "syntax": "sklearn.ensemble.RandomForestRegressor(n_estimators=100)",
    "desc": "Случайный лес для регрессии.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "rf = RandomForestRegressor(n_estimators=100)\nrf.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "GradientBoostingClassifier()",
    "lvl": "intermediate",
    "syntax": "sklearn.ensemble.GradientBoostingClassifier(n_estimators=100, learning_rate=0.1)",
    "desc": "Градиентный бустинг для классификации.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "gbc = GradientBoostingClassifier(n_estimators=200, max_depth=3)\ngbc.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "GradientBoostingRegressor()",
    "lvl": "intermediate",
    "syntax": "sklearn.ensemble.GradientBoostingRegressor(n_estimators=100)",
    "desc": "Градиентный бустинг для регрессии.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "gbr = GradientBoostingRegressor(n_estimators=100)\ngbr.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "SVC()",
    "lvl": "intermediate",
    "syntax": "sklearn.svm.SVC(C=1.0, kernel='rbf', gamma='scale')",
    "desc": "Метод опорных векторов для классификации.",
    "tags": [
      "ml",
      "svm"
    ],
    "ex": "svc = SVC(kernel='rbf', C=1.0, probability=True)\nsvc.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "SVR()",
    "lvl": "intermediate",
    "syntax": "sklearn.svm.SVR(kernel='rbf', C=1.0, epsilon=0.1)",
    "desc": "Метод опорных векторов для регрессии.",
    "tags": [
      "ml",
      "svm"
    ],
    "ex": "svr = SVR(kernel='rbf', C=10)\nsvr.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "KNeighborsClassifier()",
    "lvl": "beginner",
    "syntax": "sklearn.neighbors.KNeighborsClassifier(n_neighbors=5)",
    "desc": "Классификация методом k-ближайших соседей.",
    "tags": [
      "ml",
      "knn"
    ],
    "ex": "knn = KNeighborsClassifier(n_neighbors=3)\nknn.fit(X_train, y_train)"
  },
  {
    "lib": "sklearn",
    "name": "KMeans()",
    "lvl": "intermediate",
    "syntax": "sklearn.cluster.KMeans(n_clusters=8, random_state=42, n_init='auto')",
    "desc": "Кластеризация методом k-средних.",
    "tags": [
      "ml",
      "кластеризация"
    ],
    "ex": "km = KMeans(n_clusters=5, n_init=10)\nlabels = km.fit_predict(X)\ncenters = km.cluster_centers_"
  },
  {
    "lib": "sklearn",
    "name": "DBSCAN()",
    "lvl": "intermediate",
    "syntax": "sklearn.cluster.DBSCAN(eps=0.5, min_samples=5)",
    "desc": "Плотностная кластеризация DBSCAN.",
    "tags": [
      "ml",
      "кластеризация"
    ],
    "ex": "db = DBSCAN(eps=0.5, min_samples=10)\nlabels = db.fit_predict(X)"
  },
  {
    "lib": "sklearn",
    "name": "AgglomerativeClustering()",
    "lvl": "intermediate",
    "syntax": "sklearn.cluster.AgglomerativeClustering(n_clusters=None, linkage='ward')",
    "desc": "Иерархическая агломеративная кластеризация.",
    "tags": [
      "ml",
      "кластеризация"
    ],
    "ex": "ac = AgglomerativeClustering(n_clusters=5, linkage='ward')\nlabels = ac.fit_predict(X)"
  },
  {
    "lib": "sklearn",
    "name": "PCA()",
    "lvl": "intermediate",
    "syntax": "sklearn.decomposition.PCA(n_components=None)",
    "desc": "Метод главных компонент (PCA).",
    "tags": [
      "ml",
      "снижение размерности"
    ],
    "ex": "pca = PCA(n_components=0.95)\nX_pca = pca.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "TruncatedSVD()",
    "lvl": "intermediate",
    "syntax": "sklearn.decomposition.TruncatedSVD(n_components=2)",
    "desc": "Усечённое SVD для разреженных матриц.",
    "tags": [
      "ml",
      "снижение размерности"
    ],
    "ex": "svd = TruncatedSVD(n_components=50)\nX_svd = svd.fit_transform(sparse_X)"
  },
  {
    "lib": "sklearn",
    "name": "TSNE()",
    "lvl": "intermediate",
    "syntax": "sklearn.manifold.TSNE(n_components=2, perplexity=30)",
    "desc": "t-SNE — визуализация многомерных данных.",
    "tags": [
      "ml",
      "визуализация"
    ],
    "ex": "tsne = TSNE(n_components=2, perplexity=30)\nX_tsne = tsne.fit_transform(X)"
  },
  {
    "lib": "sklearn",
    "name": "accuracy_score()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.accuracy_score(y_true, y_pred)",
    "desc": "Доля правильных предсказаний.",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "acc = accuracy_score(y_test, y_pred)"
  },
  {
    "lib": "sklearn",
    "name": "f1_score()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.f1_score(y_true, y_pred, average='weighted')",
    "desc": "F1-мера. average: micro, macro, weighted, None.",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "f1 = f1_score(y_test, y_pred, average='macro')"
  },
  {
    "lib": "sklearn",
    "name": "precision_score()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.precision_score(y_true, y_pred, average='binary')",
    "desc": "Точность (precision).",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "prec = precision_score(y_test, y_pred)"
  },
  {
    "lib": "sklearn",
    "name": "recall_score()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.recall_score(y_true, y_pred, average='binary')",
    "desc": "Полнота (recall).",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "rec = recall_score(y_test, y_pred)"
  },
  {
    "lib": "sklearn",
    "name": "classification_report()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.classification_report(y_true, y_pred, target_names=None)",
    "desc": "Сводка precision, recall, f1-score для всех классов.",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "print(classification_report(y_test, y_pred, target_names=class_names))"
  },
  {
    "lib": "sklearn",
    "name": "confusion_matrix()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.confusion_matrix(y_true, y_pred, normalize=None)",
    "desc": "Матрица ошибок.",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "cm = confusion_matrix(y_test, y_pred)\nsns.heatmap(cm, annot=True, fmt='d')"
  },
  {
    "lib": "sklearn",
    "name": "roc_auc_score()",
    "lvl": "intermediate",
    "syntax": "sklearn.metrics.roc_auc_score(y_true, y_score, multi_class='ovr')",
    "desc": "Площадь под ROC-кривой (AUC-ROC).",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')"
  },
  {
    "lib": "sklearn",
    "name": "roc_curve()",
    "lvl": "intermediate",
    "syntax": "sklearn.metrics.roc_curve(y_true, y_score)",
    "desc": "Точки ROC-кривой: fpr, tpr, thresholds.",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "fpr, tpr, thresh = roc_curve(y_test, y_score)\nplt.plot(fpr, tpr)"
  },
  {
    "lib": "sklearn",
    "name": "mean_squared_error()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.mean_squared_error(y_true, y_pred, squared=True)",
    "desc": "MSE (squared=True) или RMSE (squared=False).",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "rmse = mean_squared_error(y_test, y_pred, squared=False)"
  },
  {
    "lib": "sklearn",
    "name": "mean_absolute_error()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.mean_absolute_error(y_true, y_pred)",
    "desc": "Средняя абсолютная ошибка (MAE).",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "mae = mean_absolute_error(y_test, y_pred)"
  },
  {
    "lib": "sklearn",
    "name": "r2_score()",
    "lvl": "beginner",
    "syntax": "sklearn.metrics.r2_score(y_true, y_pred)",
    "desc": "Коэффициент детерминации R^2 (1 - идеально).",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "r2 = r2_score(y_test, y_pred)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.OLS()",
    "lvl": "intermediate",
    "syntax": "sm.OLS(endog, exog).fit()",
    "desc": "Обычный метод наименьших квадратов.",
    "tags": [
      "cтатистика",
      "регрессия"
    ],
    "ex": "model = sm.OLS(y, X).fit()\nprint(model.summary())"
  },
  {
    "lib": "statsmodels",
    "name": "sm.Logit()",
    "lvl": "intermediate",
    "syntax": "sm.Logit(endog, exog).fit()",
    "desc": "Логистическая регрессия.",
    "tags": [
      "cтатистика",
      "регрессия"
    ],
    "ex": "model = sm.Logit(y_binary, X).fit()\nprint(model.summary())"
  },
  {
    "lib": "statsmodels",
    "name": "sm.Probit()",
    "lvl": "intermediate",
    "syntax": "sm.Probit(endog, exog).fit()",
    "desc": "Пробит-регрессия.",
    "tags": [
      "cтатистика",
      "регрессия"
    ],
    "ex": "model = sm.Probit(y_binary, X).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.GLM()",
    "lvl": "advanced",
    "syntax": "sm.GLM(endog, exog, family=sm.families.Gaussian()).fit()",
    "desc": "Обобщённая линейная модель.",
    "tags": [
      "cтатистика",
      "регрессия"
    ],
    "ex": "model = sm.GLM(y, X, family=sm.families.Poisson()).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.Poisson()",
    "lvl": "intermediate",
    "syntax": "sm.Poisson(endog, exog).fit()",
    "desc": "Пуассоновская регрессия.",
    "tags": [
      "cтатистика",
      "регрессия"
    ],
    "ex": "model = sm.Poisson(count_y, X).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.WLS()",
    "lvl": "intermediate",
    "syntax": "sm.WLS(endog, exog, weights=w).fit()",
    "desc": "Взвешенный МНК.",
    "tags": [
      "cтатистика",
      "регрессия"
    ],
    "ex": "model = sm.WLS(y, X, weights=1/var).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.RLM()",
    "lvl": "advanced",
    "syntax": "sm.RLM(endog, exog, M=sm.robust.norms.HuberT()).fit()",
    "desc": "Робастная линейная модель.",
    "tags": [
      "cтатистика",
      "регрессия"
    ],
    "ex": "model = sm.RLM(y, X).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.ARIMA()",
    "lvl": "advanced",
    "syntax": "sm.tsa.ARIMA(endog, order=(p,d,q)).fit()",
    "desc": "Модель ARIMA для временных рядов.",
    "tags": [
      "cтатистика",
      "временные ряды"
    ],
    "ex": "model = sm.tsa.ARIMA(series, order=(2,1,2)).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.SARIMAX()",
    "lvl": "advanced",
    "syntax": "sm.tsa.SARIMAX(endog, order=(p,d,q), seasonal_order=(P,D,Q,s)).fit()",
    "desc": "Модель SARIMAX с сезонностью.",
    "tags": [
      "cтатистика",
      "временные ряды"
    ],
    "ex": "model = SARIMAX(series, order=(1,1,1), seasonal_order=(1,1,1,12)).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.AR()",
    "lvl": "intermediate",
    "syntax": "sm.tsa.AR(endog).fit()",
    "desc": "Авторегрессионная модель.",
    "tags": [
      "cтатистика",
      "временные ряды"
    ],
    "ex": "model = sm.tsa.AR(series).fit(maxlag=5)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.stattools.adfuller()",
    "lvl": "intermediate",
    "syntax": "sm.tsa.stattools.adfuller(x, regression='c')",
    "desc": "Тест Дики-Фуллера на стационарность.",
    "tags": [
      "cтатистика",
      "тест"
    ],
    "ex": "stat, pval, _, _, crit, _ = adfuller(series)\nprint(f'p={pval}')"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.stattools.kpss()",
    "lvl": "intermediate",
    "syntax": "sm.tsa.stattools.kpss(x, regression='c')",
    "desc": "Тест KPSS на стационарность.",
    "tags": [
      "cтатистика",
      "тест"
    ],
    "ex": "stat, pval, _, crit = kpss(series)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.stattools.acf()",
    "lvl": "intermediate",
    "syntax": "sm.tsa.stattools.acf(x, nlags=40)",
    "desc": "Автокорреляционная функция (ACF).",
    "tags": [
      "cтатистика",
      "временные ряды"
    ],
    "ex": "acf_vals = acf(series, nlags=40)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.stattools.pacf()",
    "lvl": "intermediate",
    "syntax": "sm.tsa.stattools.pacf(x, nlags=40)",
    "desc": "Частная автокорреляционная функция (PACF).",
    "tags": [
      "cтатистика",
      "временные ряды"
    ],
    "ex": "pacf_vals = pacf(series, nlags=20)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tsa.seasonal_decompose()",
    "lvl": "intermediate",
    "syntax": "sm.tsa.seasonal_decompose(x, model='additive', period=None)",
    "desc": "Декомпозиция ряда на тренд, сезонность и остатки.",
    "tags": [
      "cтатистика",
      "временные ряды"
    ],
    "ex": "decomp = seasonal_decompose(series, period=12)\nprint(decomp.trend)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.stats.proportion_confint()",
    "lvl": "intermediate",
    "syntax": "sm.stats.proportion_confint(count, nobs, alpha=0.05, method='normal')",
    "desc": "Доверительный интервал для доли.",
    "tags": [
      "cтатистика"
    ],
    "ex": "ci_low, ci_high = proportion_confint(success, total, method='wilson')"
  },
  {
    "lib": "statsmodels",
    "name": "sm.stats.DescrStatsW()",
    "lvl": "intermediate",
    "syntax": "sm.stats.DescrStatsW(data, weights=None)",
    "desc": "Взвешенная описательная статистика.",
    "tags": [
      "cтатистика"
    ],
    "ex": "d = DescrStatsW(data, weights=w)\nprint(d.mean, d.std)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.stats.multicomp.pairwise_tukeyhsd()",
    "lvl": "intermediate",
    "syntax": "sm.stats.multicomp.pairwise_tukeyhsd(endog, groups, alpha=0.05)",
    "desc": "Тест Тьюки для попарных сравнений групп.",
    "tags": [
      "cтатистика"
    ],
    "ex": "tukey = pairwise_tukeyhsd(values, groups)\nprint(tukey)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.stats.diagnostic.het_breuschpagan()",
    "lvl": "advanced",
    "syntax": "sm.stats.diagnostic.het_breuschpagan(resid, exog_het)",
    "desc": "Тест Бройша-Пагана на гетероскедастичность.",
    "tags": [
      "cтатистика",
      "диагностика"
    ],
    "ex": "stat, pval, _, _ = het_breuschpagan(residuals, X)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.graphics.plot_partregress()",
    "lvl": "intermediate",
    "syntax": "sm.graphics.plot_partregress(endog, exog_i, exog_others)",
    "desc": "График частной регрессии.",
    "tags": [
      "визуализация"
    ],
    "ex": "fig = sm.graphics.plot_partregress(y, X[:, 0], X[:, 1:])"
  },
  {
    "lib": "statsmodels",
    "name": "sm.graphics.qqplot()",
    "lvl": "beginner",
    "syntax": "sm.graphics.qqplot(data, line='45', fit=True)",
    "desc": "Q-Q plot для проверки нормальности.",
    "tags": [
      "визуализация"
    ],
    "ex": "sm.graphics.qqplot(residuals, line='45')\nplt.show()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.graphics.plot_acf()",
    "lvl": "beginner",
    "syntax": "sm.graphics.plot_acf(x, lags=40, zero=False)",
    "desc": "График автокорреляционной функции.",
    "tags": [
      "визуализация",
      "временные ряды"
    ],
    "ex": "sm.graphics.plot_acf(series, lags=30, zero=False)\nplt.show()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.graphics.plot_pacf()",
    "lvl": "beginner",
    "syntax": "sm.graphics.plot_pacf(x, lags=40, zero=False)",
    "desc": "График частной автокорреляционной функции.",
    "tags": [
      "визуализация",
      "временные ряды"
    ],
    "ex": "sm.graphics.plot_pacf(series, lags=20)\nplt.show()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.formula.ols()",
    "lvl": "intermediate",
    "syntax": "sm.formula.ols(formula, data).fit()",
    "desc": "R-style формулы: 'y ~ x1 + x2 + C(cat)'.",
    "tags": [
      "cтатистика",
      "формулы"
    ],
    "ex": "model = smf.ols('sales ~ price + C(region)', data=df).fit()"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tools.add_constant()",
    "lvl": "beginner",
    "syntax": "sm.tools.add_constant(data, prepend=True)",
    "desc": "Добавить столбец единиц (intercept).",
    "tags": [
      "cтатистика"
    ],
    "ex": "X = sm.add_constant(X)"
  },
  {
    "lib": "statsmodels",
    "name": "sm.tools.categorical()",
    "lvl": "intermediate",
    "syntax": "sm.tools.categorical(data, col, dictnames=False, drop=False)",
    "desc": "Создать dummy-переменные.",
    "tags": [
      "cтатистика"
    ],
    "ex": "dummies = categorical(df[['region']])"
  },
  {
    "lib": "statsmodels",
    "name": "OLSResults.summary()",
    "lvl": "intermediate",
    "syntax": "est.summary(yname='y', xname=['x1','x2'])",
    "desc": "Сводка OLS: R^2, p-value, доверительные интервалы.",
    "tags": [
      "результаты"
    ],
    "ex": "results = sm.OLS(y, X).fit()\nprint(results.summary())"
  },
  {
    "lib": "statsmodels",
    "name": "LogitResults.summary()",
    "lvl": "intermediate",
    "syntax": "est.summary()",
    "desc": "Сводка логит-регрессии.",
    "tags": [
      "результаты"
    ],
    "ex": "results = sm.Logit(y, X).fit()\nprint(results.summary())"
  },
  {
    "lib": "statsmodels",
    "name": "GLMResults.summary()",
    "lvl": "intermediate",
    "syntax": "est.summary()",
    "desc": "Сводка GLM: deviance, Pearson chi2, AIC.",
    "tags": [
      "результаты"
    ],
    "ex": "results = sm.GLM(y, X, family=sm.families.Gamma()).fit()\nprint(results.summary())"
  },
  {
    "lib": "statsmodels",
    "name": "ARIMAResultsWrapper.summary()",
    "lvl": "intermediate",
    "syntax": "est.summary()",
    "desc": "Сводка ARIMA: коэффициенты, AIC, BIC, HQIC.",
    "tags": [
      "результаты",
      "временные ряды"
    ],
    "ex": "results = ARIMA(series, order=(1,1,1)).fit()\nprint(results.summary())"
  },
  {
    "lib": "xgboost",
    "name": "XGBClassifier()",
    "lvl": "intermediate",
    "syntax": "xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1)",
    "desc": "Градиентный бустинг для классификации.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "clf = XGBClassifier(n_estimators=200, learning_rate=0.05)\nclf.fit(X_train, y_train)"
  },
  {
    "lib": "xgboost",
    "name": "XGBRegressor()",
    "lvl": "intermediate",
    "syntax": "xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1)",
    "desc": "Градиентный бустинг для регрессии.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "reg = XGBRegressor(n_estimators=200)\nreg.fit(X_train, y_train)"
  },
  {
    "lib": "xgboost",
    "name": "XGBRanker()",
    "lvl": "advanced",
    "syntax": "xgb.XGBRanker(n_estimators=100, max_depth=6)",
    "desc": "Ранжирование (learning to rank).",
    "tags": [
      "ml",
      "ранжирование"
    ],
    "ex": "ranker = XGBRanker()\nranker.fit(X_train, y_train, group=qid_groups)"
  },
  {
    "lib": "xgboost",
    "name": "xgb.train()",
    "lvl": "advanced",
    "syntax": "xgb.train(params, dtrain, num_boost_round=10, evals=[], early_stopping_rounds=10)",
    "desc": "Низкоуровневое обучение с DMatrix.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "booster = xgb.train({'max_depth':3}, dtrain, num_boost_round=100, evals=[(dval,'val')], early_stopping_rounds=10)"
  },
  {
    "lib": "xgboost",
    "name": "xgb.cv()",
    "lvl": "intermediate",
    "syntax": "xgb.cv(params, dtrain, num_boost_round=10, nfold=5, early_stopping_rounds=10)",
    "desc": "Кросс-валидация XGBoost.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "cv_results = xgb.cv(params, dtrain, nfold=5, early_stopping_rounds=10)"
  },
  {
    "lib": "xgboost",
    "name": "xgb.DMatrix()",
    "lvl": "intermediate",
    "syntax": "xgb.DMatrix(data, label=None, weight=None)",
    "desc": "Внутренний формат данных XGBoost.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "dtrain = xgb.DMatrix(X_train, label=y_train)\ndval = xgb.DMatrix(X_val, label=y_val)"
  },
  {
    "lib": "xgboost",
    "name": "xgb.callback.EarlyStopping()",
    "lvl": "intermediate",
    "syntax": "xgb.callback.EarlyStopping(rounds=10, metric_name='rmse')",
    "desc": "Коллбек ранней остановки.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "es = xgb.callback.EarlyStopping(rounds=10)\nbooster = xgb.train(params, dtrain, callbacks=[es])"
  },
  {
    "lib": "xgboost",
    "name": "xgb.plot_importance()",
    "lvl": "beginner",
    "syntax": "xgb.plot_importance(model, importance_type='weight')",
    "desc": "График важности признаков.",
    "tags": [
      "ml",
      "визуализация"
    ],
    "ex": "xgb.plot_importance(model, max_num_features=20)\nplt.show()"
  },
  {
    "lib": "xgboost",
    "name": "xgb.plot_tree()",
    "lvl": "beginner",
    "syntax": "xgb.plot_tree(model, num_trees=0)",
    "desc": "Визуализация одного дерева из ансамбля.",
    "tags": [
      "ml",
      "визуализация"
    ],
    "ex": "xgb.plot_tree(model, num_trees=0)\nfig = plt.gcf()"
  },
  {
    "lib": "xgboost",
    "name": "model.get_booster()",
    "lvl": "intermediate",
    "syntax": "model.get_booster()",
    "desc": "Получить Booster из scikit-learn wrapper.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "booster = model.get_booster()\nbooster.dump_model('dump.txt')"
  },
  {
    "lib": "xgboost",
    "name": "model.save_model()",
    "lvl": "beginner",
    "syntax": "model.save_model(fname)",
    "desc": "Сохранить модель в файл (JSON/UBJSON).",
    "tags": [
      "ml",
      "сохранение"
    ],
    "ex": "model.save_model('xgb_model.json')"
  },
  {
    "lib": "xgboost",
    "name": "model.load_model()",
    "lvl": "beginner",
    "syntax": "model.load_model(fname)",
    "desc": "Загрузить модель из файла.",
    "tags": [
      "ml",
      "загрузка"
    ],
    "ex": "model.load_model('xgb_model.json')"
  },
  {
    "lib": "xgboost",
    "name": "model.get_params()",
    "lvl": "beginner",
    "syntax": "model.get_params()",
    "desc": "Вернуть словарь параметров модели.",
    "tags": [
      "ml"
    ],
    "ex": "params = model.get_params()"
  },
  {
    "lib": "xgboost",
    "name": "model.set_params()",
    "lvl": "beginner",
    "syntax": "model.set_params(**params)",
    "desc": "Установить параметры модели.",
    "tags": [
      "ml"
    ],
    "ex": "model.set_params(learning_rate=0.01, n_estimators=500)"
  },
  {
    "lib": "xgboost",
    "name": "xgb.set_config()",
    "lvl": "beginner",
    "syntax": "xgb.set_config(verbosity=0)",
    "desc": "Глобальные настройки: verbosity.",
    "tags": [
      "ml",
      "настройка"
    ],
    "ex": "xgb.set_config(verbosity=0)"
  },
  {
    "lib": "lightgbm",
    "name": "LGBMClassifier()",
    "lvl": "intermediate",
    "syntax": "lgb.LGBMClassifier(n_estimators=100, num_leaves=31, learning_rate=0.1)",
    "desc": "Градиентный бустинг для классификации.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "clf = LGBMClassifier(n_estimators=200, num_leaves=50)\nclf.fit(X_train, y_train)"
  },
  {
    "lib": "lightgbm",
    "name": "LGBMRegressor()",
    "lvl": "intermediate",
    "syntax": "lgb.LGBMRegressor(n_estimators=100, num_leaves=31)",
    "desc": "Градиентный бустинг для регрессии.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "reg = LGBMRegressor(n_estimators=500)\nreg.fit(X_train, y_train)"
  },
  {
    "lib": "lightgbm",
    "name": "LGBMRanker()",
    "lvl": "advanced",
    "syntax": "lgb.LGBMRanker(n_estimators=100)",
    "desc": "Ранжирование LightGBM.",
    "tags": [
      "ml",
      "ранжирование"
    ],
    "ex": "ranker = LGBMRanker(n_estimators=100)\nranker.fit(X_train, y_train, group=q_groups)"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.train()",
    "lvl": "advanced",
    "syntax": "lgb.train(params, train_set, num_boost_round=100, valid_sets=[], callbacks=[])",
    "desc": "Низкоуровневое обучение с Dataset.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "booster = lgb.train(params, train_set, num_boost_round=100, valid_sets=[val_set])"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.cv()",
    "lvl": "intermediate",
    "syntax": "lgb.cv(params, train_set, num_boost_round=100, nfold=5)",
    "desc": "Кросс-валидация LightGBM.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "cv_res = lgb.cv(params, train_set, nfold=5)"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.Dataset()",
    "lvl": "intermediate",
    "syntax": "lgb.Dataset(data, label=None, weight=None, categorical_feature='auto')",
    "desc": "Формат данных LightGBM.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "train_set = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_cols)"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.early_stopping()",
    "lvl": "intermediate",
    "syntax": "lgb.early_stopping(stopping_rounds=10)",
    "desc": "Коллбек ранней остановки.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "booster = lgb.train(params, train_set, callbacks=[lgb.early_stopping(10)])"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.log_evaluation()",
    "lvl": "beginner",
    "syntax": "lgb.log_evaluation(period=10)",
    "desc": "Коллбек логирования метрик.",
    "tags": [
      "ml",
      "логирование"
    ],
    "ex": "booster = lgb.train(params, train_set, callbacks=[lgb.log_evaluation(50)])"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.plot_importance()",
    "lvl": "beginner",
    "syntax": "lgb.plot_importance(model, importance_type='split')",
    "desc": "График важности признаков.",
    "tags": [
      "ml",
      "визуализация"
    ],
    "ex": "lgb.plot_importance(model, max_num_features=20)\nplt.show()"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.plot_tree()",
    "lvl": "beginner",
    "syntax": "lgb.plot_tree(model, tree_index=0)",
    "desc": "Визуализация одного дерева из ансамбля.",
    "tags": [
      "ml",
      "визуализация"
    ],
    "ex": "lgb.plot_tree(model, tree_index=0, figsize=(20, 10))"
  },
  {
    "lib": "lightgbm",
    "name": "model.booster_.save_model()",
    "lvl": "beginner",
    "syntax": "model.booster_.save_model(fname)",
    "desc": "Сохранить модель в файл.",
    "tags": [
      "ml",
      "сохранение"
    ],
    "ex": "model.booster_.save_model('lgbm_model.txt')"
  },
  {
    "lib": "lightgbm",
    "name": "model.get_params()",
    "lvl": "beginner",
    "syntax": "model.get_params()",
    "desc": "Вернуть параметры модели.",
    "tags": [
      "ml"
    ],
    "ex": "params = model.get_params()"
  },
  {
    "lib": "lightgbm",
    "name": "LGBMClassifier(objective='multiclass')",
    "lvl": "intermediate",
    "syntax": "lgb.LGBMClassifier(objective='multiclass', num_class=K)",
    "desc": "Мультиклассовая классификация.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "clf = LGBMClassifier(objective='multiclass', num_class=5)\nclf.fit(X, y)"
  },
  {
    "lib": "lightgbm",
    "name": "model.predict_proba()",
    "lvl": "beginner",
    "syntax": "model.predict_proba(X)",
    "desc": "Вернуть вероятности классов.",
    "tags": [
      "ml",
      "предсказание"
    ],
    "ex": "probs = model.predict_proba(X_test)"
  },
  {
    "lib": "lightgbm",
    "name": "lgb.reset_parameter()",
    "lvl": "intermediate",
    "syntax": "lgb.reset_parameter(**params)",
    "desc": "Сбросить/обновить параметры бустера.",
    "tags": [
      "ml",
      "настройка"
    ],
    "ex": "lgb.reset_parameter(learning_rate=0.01)"
  },
  {
    "lib": "catboost",
    "name": "CatBoostClassifier()",
    "lvl": "intermediate",
    "syntax": "cb.CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)",
    "desc": "Классификация CatBoost с нативной поддержкой категорий.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "clf = CatBoostClassifier(iterations=500, verbose=False)\nclf.fit(X_train, y_train, cat_features=cat_idx)"
  },
  {
    "lib": "catboost",
    "name": "CatBoostRegressor()",
    "lvl": "intermediate",
    "syntax": "cb.CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)",
    "desc": "Регрессия CatBoost.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "reg = CatBoostRegressor(iterations=1000, verbose=100)\nreg.fit(X_train, y_train)"
  },
  {
    "lib": "catboost",
    "name": "CatBoostRanker()",
    "lvl": "advanced",
    "syntax": "cb.CatBoostRanker(iterations=500, loss_function='YetiRank')",
    "desc": "Ранжирование CatBoost.",
    "tags": [
      "ml",
      "ранжирование"
    ],
    "ex": "ranker = CatBoostRanker(loss_function='YetiRank')\nranker.fit(X, y, group_id=groups)"
  },
  {
    "lib": "catboost",
    "name": "Pool()",
    "lvl": "beginner",
    "syntax": "cb.Pool(data, label=None, cat_features=None, weight=None)",
    "desc": "Формат данных CatBoost.",
    "tags": [
      "ml",
      "ансамбль"
    ],
    "ex": "pool = Pool(X, label=y, cat_features=['city','type'])"
  },
  {
    "lib": "catboost",
    "name": "model.fit() with cat_features",
    "lvl": "beginner",
    "syntax": "model.fit(X, y, cat_features=[0,2,5], verbose=100)",
    "desc": "Обучение с указанием категориальных колонок.",
    "tags": [
      "ml"
    ],
    "ex": "model.fit(X_train, y_train, cat_features=cat_cols, eval_set=(X_val, y_val))"
  },
  {
    "lib": "catboost",
    "name": "model.get_feature_importance()",
    "lvl": "beginner",
    "syntax": "model.get_feature_importance(type='FeatureImportance')",
    "desc": "Важность признаков.",
    "tags": [
      "ml",
      "визуализация"
    ],
    "ex": "fi = model.get_feature_importance()\nfeat_imp = pd.DataFrame({'feat':features, 'imp':fi})"
  },
  {
    "lib": "catboost",
    "name": "model.get_params()",
    "lvl": "beginner",
    "syntax": "model.get_params()",
    "desc": "Вернуть параметры модели.",
    "tags": [
      "ml"
    ],
    "ex": "params = model.get_params()"
  },
  {
    "lib": "catboost",
    "name": "model.save_model()",
    "lvl": "beginner",
    "syntax": "model.save_model(fname, format='cbm')",
    "desc": "Сохранить модель.",
    "tags": [
      "ml",
      "сохранение"
    ],
    "ex": "model.save_model('catboost_model.cbm')"
  },
  {
    "lib": "catboost",
    "name": "model.load_model()",
    "lvl": "beginner",
    "syntax": "model.load_model(fname)",
    "desc": "Загрузить модель из файла.",
    "tags": [
      "ml",
      "загрузка"
    ],
    "ex": "model.load_model('catboost_model.cbm')"
  },
  {
    "lib": "catboost",
    "name": "model.predict() prediction_type",
    "lvl": "intermediate",
    "syntax": "model.predict(data, prediction_type='Probability')",
    "desc": "Предсказание: Probability, Class, RawFormulaVal.",
    "tags": [
      "ml",
      "предсказание"
    ],
    "ex": "probs = model.predict(X_test, prediction_type='Probability')\nclasses = model.predict(X_test, prediction_type='Class')"
  },
  {
    "lib": "catboost",
    "name": "model.get_best_iteration()",
    "lvl": "beginner",
    "syntax": "model.get_best_iteration()",
    "desc": "Номер итерации с лучшей метрикой.",
    "tags": [
      "ml",
      "валидация"
    ],
    "ex": "best_iter = model.get_best_iteration()"
  },
  {
    "lib": "catboost",
    "name": "model.get_all_params()",
    "lvl": "beginner",
    "syntax": "model.get_all_params()",
    "desc": "Все параметры, включая автоматические.",
    "tags": [
      "ml"
    ],
    "ex": "all_params = model.get_all_params()"
  },
  {
    "lib": "catboost",
    "name": "model.eval_metrics()",
    "lvl": "intermediate",
    "syntax": "model.eval_metrics(data, metrics)",
    "desc": "Посчитать метрики на заданном пуле.",
    "tags": [
      "ml",
      "метрики"
    ],
    "ex": "metrics = model.eval_metrics(val_pool, ['Logloss','AUC'])"
  },
  {
    "lib": "catboost",
    "name": "model.calc_feature_statistics()",
    "lvl": "intermediate",
    "syntax": "model.calc_feature_statistics(data, target=None, feature=None)",
    "desc": "Статистика признака.",
    "tags": [
      "ml",
      "анализ"
    ],
    "ex": "stats = model.calc_feature_statistics(pool, feature='age', plot=True)"
  },
  {
    "lib": "catboost",
    "name": "model.select_features()",
    "lvl": "advanced",
    "syntax": "model.select_features(X, y, eval_set)",
    "desc": "Автоматический отбор признаков.",
    "tags": [
      "ml",
      "отбор признаков"
    ],
    "ex": "selected = model.select_features(X, y, eval_set=(X_val, y_val), steps=3)"
  },
  {
    "lib": "pytorch",
    "name": "torch.tensor()",
    "lvl": "beginner",
    "syntax": "torch.tensor(data, dtype=None, device=None)",
    "desc": "Создать тензор из списка/ndarray.",
    "tags": [
      "тензоры",
      "создание"
    ],
    "ex": "t = torch.tensor([1, 2, 3], dtype=torch.float32)"
  },
  {
    "lib": "pytorch",
    "name": "torch.zeros()",
    "lvl": "beginner",
    "syntax": "torch.zeros(*size, dtype=torch.float32)",
    "desc": "Тензор, заполненный нулями.",
    "tags": [
      "тензоры",
      "инициализация"
    ],
    "ex": "z = torch.zeros(3, 4)"
  },
  {
    "lib": "pytorch",
    "name": "torch.ones()",
    "lvl": "beginner",
    "syntax": "torch.ones(*size)",
    "desc": "Тензор, заполненный единицами.",
    "tags": [
      "тензоры",
      "инициализация"
    ],
    "ex": "o = torch.ones(2, 5)"
  },
  {
    "lib": "pytorch",
    "name": "torch.rand()",
    "lvl": "beginner",
    "syntax": "torch.rand(*size)",
    "desc": "Случайный тензор из [0, 1).",
    "tags": [
      "тензоры",
      "случайные"
    ],
    "ex": "r = torch.rand(3, 3)"
  },
  {
    "lib": "pytorch",
    "name": "torch.randn()",
    "lvl": "beginner",
    "syntax": "torch.randn(*size)",
    "desc": "Случайный тензор из N(0, 1).",
    "tags": [
      "тензоры",
      "случайные"
    ],
    "ex": "x = torch.randn(100, 10)"
  },
  {
    "lib": "pytorch",
    "name": "torch.arange()",
    "lvl": "beginner",
    "syntax": "torch.arange(start, end, step)",
    "desc": "Тензор с равномерным шагом.",
    "tags": [
      "тензоры",
      "генерация"
    ],
    "ex": "x = torch.arange(0, 10, 0.5)"
  },
  {
    "lib": "pytorch",
    "name": "torch.linspace()",
    "lvl": "beginner",
    "syntax": "torch.linspace(start, end, steps)",
    "desc": "steps равномерных значений.",
    "tags": [
      "тензоры",
      "генерация"
    ],
    "ex": "x = torch.linspace(0, 2*torch.pi, 100)"
  },
  {
    "lib": "pytorch",
    "name": "torch.from_numpy()",
    "lvl": "beginner",
    "syntax": "torch.from_numpy(ndarray)",
    "desc": "Тензор из numpy (общая память).",
    "tags": [
      "тензоры",
      "конвертация"
    ],
    "ex": "t = torch.from_numpy(np_array)"
  },
  {
    "lib": "pytorch",
    "name": "tensor.to(device)",
    "lvl": "beginner",
    "syntax": "tensor.to(device, dtype)",
    "desc": "Переместить на GPU/CPU или изменить dtype.",
    "tags": [
      "тензоры",
      "устройство"
    ],
    "ex": "x = x.to('cuda')\nx = x.to(torch.float16)"
  },
  {
    "lib": "pytorch",
    "name": "tensor.cpu()",
    "lvl": "beginner",
    "syntax": "tensor.cpu()",
    "desc": "Переместить тензор на CPU.",
    "tags": [
      "тензоры"
    ],
    "ex": "x_cpu = x.cpu()"
  },
  {
    "lib": "pytorch",
    "name": "tensor.numpy()",
    "lvl": "beginner",
    "syntax": "tensor.numpy()",
    "desc": "Конвертировать тензор в numpy (только CPU).",
    "tags": [
      "тензоры",
      "конвертация"
    ],
    "ex": "np_array = x.cpu().numpy()"
  },
  {
    "lib": "pytorch",
    "name": "tensor.shape / .dtype / .item()",
    "lvl": "beginner",
    "syntax": "t.shape; t.dtype; t.item()",
    "desc": "Размер, тип данных, скалярное значение.",
    "tags": [
      "тензоры"
    ],
    "ex": "print(t.shape, t.dtype)\nscalar_val = t[0,0].item()"
  },
  {
    "lib": "pytorch",
    "name": "torch.cat()",
    "lvl": "beginner",
    "syntax": "torch.cat(tensors, dim=0)",
    "desc": "Конкатенация тензоров.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "combined = torch.cat([a, b], dim=0)"
  },
  {
    "lib": "pytorch",
    "name": "torch.stack()",
    "lvl": "intermediate",
    "syntax": "torch.stack(tensors, dim=0)",
    "desc": "Объединить тензоры по новому измерению.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "stacked = torch.stack([a, b], dim=0)"
  },
  {
    "lib": "pytorch",
    "name": "torch.split()",
    "lvl": "intermediate",
    "syntax": "torch.split(tensor, split_size, dim=0)",
    "desc": "Разделить тензор на части.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "chunks = torch.split(x, 2, dim=0)"
  },
  {
    "lib": "pytorch",
    "name": "torch.chunk()",
    "lvl": "beginner",
    "syntax": "torch.chunk(tensor, chunks, dim=0)",
    "desc": "Разделить на chunks равных частей.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "parts = torch.chunk(x, 3, dim=0)"
  },
  {
    "lib": "pytorch",
    "name": "torch.where()",
    "lvl": "beginner",
    "syntax": "torch.where(condition, x, y)",
    "desc": "Выбрать элементы из x/y по условию.",
    "tags": [
      "тензоры",
      "логика"
    ],
    "ex": "result = torch.where(mask, a, b)"
  },
  {
    "lib": "pytorch",
    "name": "torch.clamp()",
    "lvl": "beginner",
    "syntax": "torch.clamp(tensor, min=None, max=None)",
    "desc": "Обрезать значения по диапазону.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "clipped = torch.clamp(x, 0, 1)"
  },
  {
    "lib": "pytorch",
    "name": "nn.Linear()",
    "lvl": "beginner",
    "syntax": "nn.Linear(in_features, out_features, bias=True)",
    "desc": "Полносвязный (линейный) слой.",
    "tags": [
      "nn",
      "слои"
    ],
    "ex": "layer = nn.Linear(784, 256)\ny = layer(x)"
  },
  {
    "lib": "pytorch",
    "name": "nn.Conv2d()",
    "lvl": "intermediate",
    "syntax": "nn.Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0)",
    "desc": "2D свёрточный слой.",
    "tags": [
      "nn",
      "слои",
      "cnn"
    ],
    "ex": "conv = nn.Conv2d(3, 64, kernel_size=3, padding=1)"
  },
  {
    "lib": "pytorch",
    "name": "nn.Conv1d()",
    "lvl": "intermediate",
    "syntax": "nn.Conv1d(in_channels, out_channels, kernel_size)",
    "desc": "1D свёртка (для последовательностей).",
    "tags": [
      "nn",
      "слои"
    ],
    "ex": "conv = nn.Conv1d(1, 32, kernel_size=7)"
  },
  {
    "lib": "pytorch",
    "name": "nn.LSTM()",
    "lvl": "intermediate",
    "syntax": "nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)",
    "desc": "Рекуррентный LSTM слой.",
    "tags": [
      "nn",
      "слои",
      "rnn"
    ],
    "ex": "lstm = nn.LSTM(128, 64, num_layers=2, batch_first=True)\nout, (h, c) = lstm(x)"
  },
  {
    "lib": "pytorch",
    "name": "nn.GRU()",
    "lvl": "intermediate",
    "syntax": "nn.GRU(input_size, hidden_size, num_layers, batch_first=True)",
    "desc": "Рекуррентный GRU слой.",
    "tags": [
      "nn",
      "слои",
      "rnn"
    ],
    "ex": "gru = nn.GRU(128, 64, num_layers=1, batch_first=True)"
  },
  {
    "lib": "pytorch",
    "name": "nn.BatchNorm1d()",
    "lvl": "intermediate",
    "syntax": "nn.BatchNorm1d(num_features)",
    "desc": "Batch-нормализация для 1D.",
    "tags": [
      "nn",
      "нормализация"
    ],
    "ex": "bn = nn.BatchNorm1d(128)\nx_bn = bn(x)"
  },
  {
    "lib": "pytorch",
    "name": "nn.BatchNorm2d()",
    "lvl": "intermediate",
    "syntax": "nn.BatchNorm2d(num_features)",
    "desc": "Batch-нормализация для 2D.",
    "tags": [
      "nn",
      "нормализация"
    ],
    "ex": "bn = nn.BatchNorm2d(64)"
  },
  {
    "lib": "pytorch",
    "name": "nn.Dropout()",
    "lvl": "beginner",
    "syntax": "nn.Dropout(p=0.5)",
    "desc": "Дропаут (обнуление нейронов при обучении).",
    "tags": [
      "nn",
      "регуляризация"
    ],
    "ex": "dropout = nn.Dropout(p=0.3)\nx = dropout(x)"
  },
  {
    "lib": "pytorch",
    "name": "nn.ReLU()",
    "lvl": "beginner",
    "syntax": "nn.ReLU(inplace=False)",
    "desc": "ReLU: max(0, x).",
    "tags": [
      "nn",
      "активации"
    ],
    "ex": "relu = nn.ReLU()\nx = relu(x)"
  },
  {
    "lib": "pytorch",
    "name": "nn.Sigmoid()",
    "lvl": "beginner",
    "syntax": "nn.Sigmoid()",
    "desc": "Сигмоида: 1/(1+exp(-x)).",
    "tags": [
      "nn",
      "активации"
    ],
    "ex": "sigmoid = nn.Sigmoid()\nprobs = sigmoid(logits)"
  },
  {
    "lib": "pytorch",
    "name": "nn.Tanh()",
    "lvl": "beginner",
    "syntax": "nn.Tanh()",
    "desc": "Гиперболический тангенс.",
    "tags": [
      "nn",
      "активации"
    ],
    "ex": "tanh = nn.Tanh()"
  },
  {
    "lib": "pytorch",
    "name": "nn.Softmax()",
    "lvl": "beginner",
    "syntax": "nn.Softmax(dim=-1)",
    "desc": "Softmax по указанному измерению.",
    "tags": [
      "nn",
      "активации"
    ],
    "ex": "softmax = nn.Softmax(dim=1)\nprobs = softmax(logits)"
  },
  {
    "lib": "pytorch",
    "name": "nn.Sequential()",
    "lvl": "beginner",
    "syntax": "nn.Sequential(*layers)",
    "desc": "Последовательный контейнер слоёв.",
    "tags": [
      "nn",
      "архитектура"
    ],
    "ex": "model = nn.Sequential(nn.Linear(784,256), nn.ReLU(), nn.Linear(256,10))"
  },
  {
    "lib": "pytorch",
    "name": "nn.Module (class)",
    "lvl": "intermediate",
    "syntax": "class MyModel(nn.Module): ...",
    "desc": "Базовый класс для модулей. Переопределить __init__ и forward.",
    "tags": [
      "nn",
      "архитектура"
    ],
    "ex": "class Net(nn.Module):\n    def __init__(self):\n        super().__init__()\n        self.fc = nn.Linear(10,1)\n    def forward(self, x):\n        return self.fc(x)"
  },
  {
    "lib": "pytorch",
    "name": "nn.CrossEntropyLoss()",
    "lvl": "beginner",
    "syntax": "nn.CrossEntropyLoss(weight=None)",
    "desc": "Кросс-энтропия (LogSoftmax + NLLLoss).",
    "tags": [
      "nn",
      "loss"
    ],
    "ex": "criterion = nn.CrossEntropyLoss()\nloss = criterion(logits, labels)"
  },
  {
    "lib": "pytorch",
    "name": "nn.MSELoss()",
    "lvl": "beginner",
    "syntax": "nn.MSELoss(reduction='mean')",
    "desc": "Среднеквадратичная ошибка (L2).",
    "tags": [
      "nn",
      "loss"
    ],
    "ex": "criterion = nn.MSELoss()\nloss = criterion(pred, target)"
  },
  {
    "lib": "pytorch",
    "name": "nn.BCELoss()",
    "lvl": "intermediate",
    "syntax": "nn.BCELoss(weight=None)",
    "desc": "Binary Cross-Entropy (требует Sigmoid перед входом).",
    "tags": [
      "nn",
      "loss"
    ],
    "ex": "criterion = nn.BCELoss()\nloss = criterion(torch.sigmoid(logits), target)"
  },
  {
    "lib": "pytorch",
    "name": "nn.L1Loss()",
    "lvl": "beginner",
    "syntax": "nn.L1Loss(reduction='mean')",
    "desc": "L1-ошибка: mean(|pred - target|).",
    "tags": [
      "nn",
      "loss"
    ],
    "ex": "criterion = nn.L1Loss()\nloss = criterion(pred, target)"
  },
  {
    "lib": "pytorch",
    "name": "optim.SGD()",
    "lvl": "beginner",
    "syntax": "optim.SGD(params, lr=0.01, momentum=0)",
    "desc": "Стохастический градиентный спуск.",
    "tags": [
      "optim"
    ],
    "ex": "optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)"
  },
  {
    "lib": "pytorch",
    "name": "optim.Adam()",
    "lvl": "beginner",
    "syntax": "optim.Adam(params, lr=0.001)",
    "desc": "Оптимизатор Adam.",
    "tags": [
      "optim"
    ],
    "ex": "optimizer = optim.Adam(model.parameters(), lr=0.001)"
  },
  {
    "lib": "pytorch",
    "name": "optim.AdamW()",
    "lvl": "intermediate",
    "syntax": "optim.AdamW(params, lr=0.001, weight_decay=0.01)",
    "desc": "Adam с decoupled weight decay.",
    "tags": [
      "optim"
    ],
    "ex": "optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)"
  },
  {
    "lib": "pytorch",
    "name": "lr_scheduler.StepLR()",
    "lvl": "beginner",
    "syntax": "lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)",
    "desc": "Уменьшение LR в gamma раз каждые step_size эпох.",
    "tags": [
      "optim",
      "lr"
    ],
    "ex": "scheduler = StepLR(optimizer, step_size=30, gamma=0.1)"
  },
  {
    "lib": "pytorch",
    "name": "lr_scheduler.ReduceLROnPlateau()",
    "lvl": "intermediate",
    "syntax": "lr_scheduler.ReduceLROnPlateau(optimizer, patience=10)",
    "desc": "Уменьшение LR при плато метрики.",
    "tags": [
      "optim",
      "lr"
    ],
    "ex": "scheduler = ReduceLROnPlateau(optimizer, patience=5)\nscheduler.step(val_loss)"
  },
  {
    "lib": "pytorch",
    "name": "DataLoader()",
    "lvl": "beginner",
    "syntax": "DataLoader(dataset, batch_size=32, shuffle=True, num_workers=0)",
    "desc": "Итератор по батчам данных.",
    "tags": [
      "data"
    ],
    "ex": "loader = DataLoader(dataset, batch_size=64, shuffle=True, num_workers=4)"
  },
  {
    "lib": "pytorch",
    "name": "Dataset (class)",
    "lvl": "intermediate",
    "syntax": "class MyDS(Dataset): ...",
    "desc": "Пользовательский датасет. __len__ и __getitem__.",
    "tags": [
      "data"
    ],
    "ex": "class MyDS(Dataset):\n    def __len__(self): return len(self.data)\n    def __getitem__(self, i): return self.data[i], self.labels[i]"
  },
  {
    "lib": "pytorch",
    "name": "TensorDataset()",
    "lvl": "beginner",
    "syntax": "TensorDataset(*tensors)",
    "desc": "Датасет из тензоров (X, y).",
    "tags": [
      "data"
    ],
    "ex": "dataset = TensorDataset(X_tensor, y_tensor)"
  },
  {
    "lib": "pytorch",
    "name": "model.train()",
    "lvl": "beginner",
    "syntax": "model.train()",
    "desc": "Режим обучения (включает dropout/batchnorm).",
    "tags": [
      "обучение"
    ],
    "ex": "model.train()\nfor epoch in range(n_epochs): ..."
  },
  {
    "lib": "pytorch",
    "name": "model.eval()",
    "lvl": "beginner",
    "syntax": "model.eval()",
    "desc": "Режим оценки (отключает dropout).",
    "tags": [
      "обучение"
    ],
    "ex": "model.eval()\nwith torch.no_grad():\n    preds = model(X_test)"
  },
  {
    "lib": "pytorch",
    "name": "torch.no_grad()",
    "lvl": "beginner",
    "syntax": "with torch.no_grad(): ...",
    "desc": "Контекст без вычисления градиентов.",
    "tags": [
      "обучение"
    ],
    "ex": "with torch.no_grad():\n    outputs = model(inputs)"
  },
  {
    "lib": "pytorch",
    "name": "torch.save() / torch.load()",
    "lvl": "beginner",
    "syntax": "torch.save(obj, f); torch.load(f, map_location=None)",
    "desc": "Сериализация: сохранение/загрузка модели.",
    "tags": [
      "сохранение"
    ],
    "ex": "torch.save(model.state_dict(), 'model.pth')\nmodel.load_state_dict(torch.load('model.pth'))"
  },
  {
    "lib": "pytorch",
    "name": "torch.jit.script()",
    "lvl": "advanced",
    "syntax": "torch.jit.script(model)",
    "desc": "JIT-компиляция модели (TorchScript).",
    "tags": [
      "оптимизация"
    ],
    "ex": "scripted = torch.jit.script(model)\nscripted.save('model.pt')"
  },
  {
    "lib": "pytorch",
    "name": "torch.cuda.is_available()",
    "lvl": "beginner",
    "syntax": "torch.cuda.is_available()",
    "desc": "Проверить доступность CUDA (GPU).",
    "tags": [
      "устройство"
    ],
    "ex": "device = 'cuda' if torch.cuda.is_available() else 'cpu'"
  },
  {
    "lib": "tensorflow",
    "name": "tf.constant()",
    "lvl": "beginner",
    "syntax": "tf.constant(value, dtype=None)",
    "desc": "Создать неизменяемый тензор.",
    "tags": [
      "тензоры"
    ],
    "ex": "t = tf.constant([1, 2, 3], dtype=tf.float32)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.Variable()",
    "lvl": "beginner",
    "syntax": "tf.Variable(initial_value, dtype=None, trainable=True)",
    "desc": "Изменяемый тензор (параметр обучения).",
    "tags": [
      "тензоры"
    ],
    "ex": "w = tf.Variable(tf.random.normal([784, 10]))"
  },
  {
    "lib": "tensorflow",
    "name": "tf.zeros()",
    "lvl": "beginner",
    "syntax": "tf.zeros(shape, dtype=tf.float32)",
    "desc": "Тензор нулей.",
    "tags": [
      "тензоры"
    ],
    "ex": "z = tf.zeros([3, 4])"
  },
  {
    "lib": "tensorflow",
    "name": "tf.ones()",
    "lvl": "beginner",
    "syntax": "tf.ones(shape)",
    "desc": "Тензор единиц.",
    "tags": [
      "тензоры"
    ],
    "ex": "o = tf.ones([2, 5])"
  },
  {
    "lib": "tensorflow",
    "name": "tf.random.normal()",
    "lvl": "beginner",
    "syntax": "tf.random.normal(shape, mean=0.0, stddev=1.0)",
    "desc": "Случайный тензор из N(mean, std).",
    "tags": [
      "тензоры",
      "случайные"
    ],
    "ex": "x = tf.random.normal([100, 10])"
  },
  {
    "lib": "tensorflow",
    "name": "tf.range()",
    "lvl": "beginner",
    "syntax": "tf.range(start, limit, delta)",
    "desc": "Тензор с арифметической прогрессией.",
    "tags": [
      "тензоры"
    ],
    "ex": "r = tf.range(0, 10, 2)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.reshape()",
    "lvl": "beginner",
    "syntax": "tf.reshape(tensor, shape)",
    "desc": "Изменить форму тензора.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "x = tf.reshape(x, [-1, 28, 28, 1])"
  },
  {
    "lib": "tensorflow",
    "name": "tf.transpose()",
    "lvl": "beginner",
    "syntax": "tf.transpose(a, perm=None)",
    "desc": "Транспонировать тензор.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "t = tf.transpose(matrix)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.concat()",
    "lvl": "beginner",
    "syntax": "tf.concat(values, axis)",
    "desc": "Конкатенация тензоров.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "c = tf.concat([a, b], axis=0)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.stack()",
    "lvl": "intermediate",
    "syntax": "tf.stack(values, axis=0)",
    "desc": "Объединить тензоры по новой оси.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "s = tf.stack([a, b], axis=0)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.split()",
    "lvl": "intermediate",
    "syntax": "tf.split(value, num_or_size_splits, axis=0)",
    "desc": "Разделить тензор.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "chunks = tf.split(x, num_or_size_splits=3, axis=0)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.reduce_mean()",
    "lvl": "beginner",
    "syntax": "tf.reduce_mean(tensor, axis=None)",
    "desc": "Среднее по осям.",
    "tags": [
      "тензоры",
      "статистика"
    ],
    "ex": "avg = tf.reduce_mean(x, axis=0)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.reduce_sum()",
    "lvl": "beginner",
    "syntax": "tf.reduce_sum(tensor, axis=None)",
    "desc": "Сумма по осям.",
    "tags": [
      "тензоры",
      "статистика"
    ],
    "ex": "total = tf.reduce_sum(x, axis=1)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.argmax()",
    "lvl": "beginner",
    "syntax": "tf.argmax(input, axis)",
    "desc": "Индекс максимального значения по оси.",
    "tags": [
      "тензоры",
      "операции"
    ],
    "ex": "pred_classes = tf.argmax(logits, axis=1)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.cast()",
    "lvl": "beginner",
    "syntax": "tf.cast(x, dtype)",
    "desc": "Привести тип тензора.",
    "tags": [
      "тензоры"
    ],
    "ex": "x_f32 = tf.cast(x, tf.float32)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.GradientTape()",
    "lvl": "intermediate",
    "syntax": "with tf.GradientTape() as tape: ... grad = tape.gradient(loss, vars)",
    "desc": "Автоматическое дифференцирование.",
    "tags": [
      "autograd"
    ],
    "ex": "with tf.GradientTape() as tape:\n    pred = model(x)\n    loss = mse(y, pred)\ngrads = tape.gradient(loss, model.trainable_variables)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.function()",
    "lvl": "intermediate",
    "syntax": "@tf.function\ndef func(...): ...",
    "desc": "Компиляция Python-функции в граф TF.",
    "tags": [
      "оптимизация"
    ],
    "ex": "@tf.function\ndef train_step(x, y):\n    with tf.GradientTape() as tape: ..."
  },
  {
    "lib": "tensorflow",
    "name": "tf.data.Dataset.from_tensor_slices()",
    "lvl": "beginner",
    "syntax": "tf.data.Dataset.from_tensor_slices(tensors)",
    "desc": "Создать Dataset из тензоров/массивов.",
    "tags": [
      "data"
    ],
    "ex": "ds = tf.data.Dataset.from_tensor_slices((X, y))"
  },
  {
    "lib": "tensorflow",
    "name": "ds.batch()",
    "lvl": "beginner",
    "syntax": "dataset.batch(batch_size)",
    "desc": "Группировка в батчи.",
    "tags": [
      "data"
    ],
    "ex": "ds = ds.batch(64)"
  },
  {
    "lib": "tensorflow",
    "name": "ds.shuffle()",
    "lvl": "beginner",
    "syntax": "dataset.shuffle(buffer_size)",
    "desc": "Перемешивание данных.",
    "tags": [
      "data"
    ],
    "ex": "ds = ds.shuffle(buffer_size=10000)"
  },
  {
    "lib": "tensorflow",
    "name": "ds.prefetch()",
    "lvl": "beginner",
    "syntax": "dataset.prefetch(buffer_size=tf.data.AUTOTUNE)",
    "desc": "Предзагрузка данных для ускорения.",
    "tags": [
      "data"
    ],
    "ex": "ds = ds.prefetch(tf.data.AUTOTUNE)"
  },
  {
    "lib": "tensorflow",
    "name": "ds.map()",
    "lvl": "intermediate",
    "syntax": "dataset.map(map_func, num_parallel_calls=tf.data.AUTOTUNE)",
    "desc": "Применить функцию к элементам.",
    "tags": [
      "data"
    ],
    "ex": "ds = ds.map(lambda x, y: (preprocess(x), y), num_parallel_calls=tf.data.AUTOTUNE)"
  },
  {
    "lib": "tensorflow",
    "name": "ds.take()",
    "lvl": "beginner",
    "syntax": "dataset.take(count)",
    "desc": "Взять первые count элементов.",
    "tags": [
      "data"
    ],
    "ex": "sample = ds.take(5)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.Sequential()",
    "lvl": "beginner",
    "syntax": "tf.keras.Sequential(layers)",
    "desc": "Последовательная модель Keras.",
    "tags": [
      "keras"
    ],
    "ex": "model = tf.keras.Sequential([Dense(128, activation='relu'), Dense(10, activation='softmax')])"
  },
  {
    "lib": "tensorflow",
    "name": "model.compile()",
    "lvl": "beginner",
    "syntax": "model.compile(optimizer, loss, metrics)",
    "desc": "Сконфигурировать обучение.",
    "tags": [
      "keras"
    ],
    "ex": "model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])"
  },
  {
    "lib": "tensorflow",
    "name": "model.fit()",
    "lvl": "beginner",
    "syntax": "model.fit(x, y, batch_size=32, epochs=10, validation_split=0.2)",
    "desc": "Обучение модели Keras.",
    "tags": [
      "keras"
    ],
    "ex": "history = model.fit(X_train, y_train, epochs=50, validation_data=(X_val, y_val), callbacks=[EarlyStopping(patience=5)])"
  },
  {
    "lib": "tensorflow",
    "name": "model.evaluate()",
    "lvl": "beginner",
    "syntax": "model.evaluate(x, y, batch_size=32)",
    "desc": "Оценка модели на тестовых данных.",
    "tags": [
      "keras"
    ],
    "ex": "test_loss, test_acc = model.evaluate(X_test, y_test)"
  },
  {
    "lib": "tensorflow",
    "name": "model.predict()",
    "lvl": "beginner",
    "syntax": "model.predict(x, batch_size=32)",
    "desc": "Предсказание для новых данных.",
    "tags": [
      "keras"
    ],
    "ex": "preds = model.predict(X_new)"
  },
  {
    "lib": "tensorflow",
    "name": "model.summary()",
    "lvl": "beginner",
    "syntax": "model.summary()",
    "desc": "Печать архитектуры модели.",
    "tags": [
      "keras"
    ],
    "ex": "model.summary()"
  },
  {
    "lib": "tensorflow",
    "name": "model.save()",
    "lvl": "beginner",
    "syntax": "model.save(filepath, save_format='tf')",
    "desc": "Сохранить модель (SavedModel/H5).",
    "tags": [
      "keras",
      "сохранение"
    ],
    "ex": "model.save('my_model')"
  },
  {
    "lib": "tensorflow",
    "name": "model.load_weights()",
    "lvl": "beginner",
    "syntax": "model.load_weights(filepath)",
    "desc": "Загрузить веса из checkpoint.",
    "tags": [
      "keras",
      "загрузка"
    ],
    "ex": "model.load_weights('checkpoint/cp.ckpt')"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.Dense()",
    "lvl": "beginner",
    "syntax": "tf.keras.layers.Dense(units, activation=None)",
    "desc": "Полносвязный слой.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "Dense(128, activation='relu')"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.Conv2D()",
    "lvl": "intermediate",
    "syntax": "tf.keras.layers.Conv2D(filters, kernel_size, strides=(1,1), padding='valid')",
    "desc": "2D свёрточный слой.",
    "tags": [
      "keras",
      "слои",
      "cnn"
    ],
    "ex": "Conv2D(64, (3,3), activation='relu', padding='same')"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.Flatten()",
    "lvl": "beginner",
    "syntax": "tf.keras.layers.Flatten()",
    "desc": "Вытянуть многомерный тензор в 1D.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "Flatten()"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.Dropout()",
    "lvl": "beginner",
    "syntax": "tf.keras.layers.Dropout(rate)",
    "desc": "Дропаут.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "Dropout(0.5)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.BatchNormalization()",
    "lvl": "intermediate",
    "syntax": "tf.keras.layers.BatchNormalization()",
    "desc": "Batch-нормализация.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "BatchNormalization()"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.LSTM()",
    "lvl": "intermediate",
    "syntax": "tf.keras.layers.LSTM(units, return_sequences=False)",
    "desc": "LSTM слой.",
    "tags": [
      "keras",
      "слои",
      "rnn"
    ],
    "ex": "LSTM(64, return_sequences=True)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.GlobalAveragePooling2D()",
    "lvl": "intermediate",
    "syntax": "tf.keras.layers.GlobalAveragePooling2D()",
    "desc": "Глобальный average pooling.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "GlobalAveragePooling2D()"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.layers.Input()",
    "lvl": "intermediate",
    "syntax": "tf.keras.layers.Input(shape)",
    "desc": "Входной слой Functional API.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "inputs = Input(shape=(28,28,1))\nx = Conv2D(32, 3)(inputs)\nmodel = Model(inputs, outputs)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.Model()",
    "lvl": "intermediate",
    "syntax": "tf.keras.Model(inputs, outputs)",
    "desc": "Functional API модель.",
    "tags": [
      "keras"
    ],
    "ex": "model = tf.keras.Model(inputs=inputs, outputs=outputs)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.callbacks.EarlyStopping()",
    "lvl": "beginner",
    "syntax": "tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)",
    "desc": "Остановка при отсутствии улучшения.",
    "tags": [
      "keras",
      "коллбек"
    ],
    "ex": "EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.callbacks.ModelCheckpoint()",
    "lvl": "beginner",
    "syntax": "tf.keras.callbacks.ModelCheckpoint(filepath, monitor='val_loss', save_best_only=True)",
    "desc": "Сохранение модели во время обучения.",
    "tags": [
      "keras",
      "коллбек"
    ],
    "ex": "ModelCheckpoint('best_model.h5', save_best_only=True)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.callbacks.ReduceLROnPlateau()",
    "lvl": "beginner",
    "syntax": "tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5)",
    "desc": "Уменьшение LR при плато.",
    "tags": [
      "keras",
      "коллбек"
    ],
    "ex": "ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.callbacks.TensorBoard()",
    "lvl": "intermediate",
    "syntax": "tf.keras.callbacks.TensorBoard(log_dir='./logs')",
    "desc": "Логирование для TensorBoard.",
    "tags": [
      "keras",
      "коллбек"
    ],
    "ex": "TensorBoard(log_dir='./logs', histogram_freq=1)"
  },
  {
    "lib": "tensorflow",
    "name": "tf.keras.callbacks.CSVLogger()",
    "lvl": "beginner",
    "syntax": "tf.keras.callbacks.CSVLogger(filename)",
    "desc": "Запись метрик эпох в CSV.",
    "tags": [
      "keras",
      "коллбек"
    ],
    "ex": "CSVLogger('training_log.csv')"
  },
  {
    "lib": "keras",
    "name": "keras.Sequential()",
    "lvl": "beginner",
    "syntax": "keras.Sequential(layers)",
    "desc": "Последовательная модель.",
    "tags": [
      "keras"
    ],
    "ex": "model = keras.Sequential([Dense(128, activation='relu'), Dense(10, activation='softmax')])"
  },
  {
    "lib": "keras",
    "name": "keras.Model()",
    "lvl": "intermediate",
    "syntax": "keras.Model(inputs, outputs)",
    "desc": "Functional API модель.",
    "tags": [
      "keras"
    ],
    "ex": "inputs = Input(shape=(784,))\nout = Dense(10)(Dense(128)(inputs))\nmodel = keras.Model(inputs, out)"
  },
  {
    "lib": "keras",
    "name": "keras.layers.Dense()",
    "lvl": "beginner",
    "syntax": "keras.layers.Dense(units, activation=None)",
    "desc": "Полносвязный слой.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "Dense(256, activation='relu')"
  },
  {
    "lib": "keras",
    "name": "keras.layers.Conv2D()",
    "lvl": "intermediate",
    "syntax": "keras.layers.Conv2D(filters, kernel_size)",
    "desc": "2D свёртка (multi-backend).",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "Conv2D(32, (3,3), activation='relu', padding='same')"
  },
  {
    "lib": "keras",
    "name": "keras.layers.LSTM()",
    "lvl": "intermediate",
    "syntax": "keras.layers.LSTM(units, return_sequences=False)",
    "desc": "LSTM слой.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "LSTM(64, return_sequences=True)"
  },
  {
    "lib": "keras",
    "name": "keras.layers.Dropout()",
    "lvl": "beginner",
    "syntax": "keras.layers.Dropout(rate)",
    "desc": "Дропаут.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "Dropout(0.5)"
  },
  {
    "lib": "keras",
    "name": "keras.layers.BatchNormalization()",
    "lvl": "intermediate",
    "syntax": "keras.layers.BatchNormalization()",
    "desc": "Batch-нормализация.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "BatchNormalization()"
  },
  {
    "lib": "keras",
    "name": "keras.layers.Flatten()",
    "lvl": "beginner",
    "syntax": "keras.layers.Flatten()",
    "desc": "Вытянуть в 1D.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "Flatten()"
  },
  {
    "lib": "keras",
    "name": "keras.layers.Input()",
    "lvl": "intermediate",
    "syntax": "keras.layers.Input(shape)",
    "desc": "Входной слой Functional API.",
    "tags": [
      "keras",
      "слои"
    ],
    "ex": "inputs = Input(shape=(28,28,1))"
  },
  {
    "lib": "keras",
    "name": "keras.optimizers.Adam()",
    "lvl": "beginner",
    "syntax": "keras.optimizers.Adam(learning_rate=0.001)",
    "desc": "Оптимизатор Adam.",
    "tags": [
      "keras",
      "optim"
    ],
    "ex": "optimizer = Adam(learning_rate=0.001)"
  },
  {
    "lib": "keras",
    "name": "keras.optimizers.SGD()",
    "lvl": "beginner",
    "syntax": "keras.optimizers.SGD(learning_rate=0.01, momentum=0.0)",
    "desc": "Оптимизатор SGD.",
    "tags": [
      "keras",
      "optim"
    ],
    "ex": "optimizer = SGD(learning_rate=0.01, momentum=0.9)"
  },
  {
    "lib": "keras",
    "name": "keras.losses.CategoricalCrossentropy()",
    "lvl": "beginner",
    "syntax": "keras.losses.CategoricalCrossentropy()",
    "desc": "Кросс-энтропия для one-hot меток.",
    "tags": [
      "keras",
      "loss"
    ],
    "ex": "loss = CategoricalCrossentropy()"
  },
  {
    "lib": "keras",
    "name": "keras.losses.BinaryCrossentropy()",
    "lvl": "beginner",
    "syntax": "keras.losses.BinaryCrossentropy()",
    "desc": "Бинарная кросс-энтропия.",
    "tags": [
      "keras",
      "loss"
    ],
    "ex": "loss = BinaryCrossentropy()"
  },
  {
    "lib": "keras",
    "name": "keras.losses.MeanSquaredError()",
    "lvl": "beginner",
    "syntax": "keras.losses.MeanSquaredError()",
    "desc": "MSE для регрессии.",
    "tags": [
      "keras",
      "loss"
    ],
    "ex": "loss = MeanSquaredError()"
  },
  {
    "lib": "keras",
    "name": "keras.metrics.Accuracy()",
    "lvl": "beginner",
    "syntax": "keras.metrics.Accuracy()",
    "desc": "Метрика точности.",
    "tags": [
      "keras",
      "метрики"
    ],
    "ex": "model.compile(optimizer='adam', loss='cce', metrics=[Accuracy()])"
  },
  {
    "lib": "keras",
    "name": "keras.metrics.CategoricalAccuracy()",
    "lvl": "beginner",
    "syntax": "keras.metrics.CategoricalAccuracy()",
    "desc": "Категориальная точность.",
    "tags": [
      "keras",
      "метрики"
    ],
    "ex": "acc = CategoricalAccuracy()\nacc.update_state(y_true, y_pred)"
  },
  {
    "lib": "keras",
    "name": "keras.callbacks.EarlyStopping()",
    "lvl": "beginner",
    "syntax": "keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)",
    "desc": "Ранняя остановка.",
    "tags": [
      "keras",
      "коллбек"
    ],
    "ex": "EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)"
  },
  {
    "lib": "keras",
    "name": "keras.callbacks.ModelCheckpoint()",
    "lvl": "beginner",
    "syntax": "keras.callbacks.ModelCheckpoint(filepath, monitor='val_loss')",
    "desc": "Сохранение модели во время обучения.",
    "tags": [
      "keras",
      "коллбек"
    ],
    "ex": "ModelCheckpoint('best.weights.h5', save_best_only=True)"
  },
  {
    "lib": "keras",
    "name": "keras.utils.to_categorical()",
    "lvl": "beginner",
    "syntax": "keras.utils.to_categorical(y, num_classes=None)",
    "desc": "One-hot кодирование меток.",
    "tags": [
      "keras",
      "утилиты"
    ],
    "ex": "y_onehot = to_categorical([0, 1, 2], num_classes=3)"
  },
  {
    "lib": "keras",
    "name": "model.fit/evaluate/predict",
    "lvl": "beginner",
    "syntax": "model.fit(x, y, epochs, validation_data)\nmodel.evaluate(x, y)\nmodel.predict(x)",
    "desc": "Цикл обучения / оценки / предсказания.",
    "tags": [
      "keras"
    ],
    "ex": "history = model.fit(X_train, y_train, epochs=10, validation_split=0.2)\ntest_loss = model.evaluate(X_test, y_test)\npreds = model.predict(X_new)"
  },
  {
    "lib": "transformers",
    "name": "pipeline()",
    "lvl": "beginner",
    "syntax": "transformers.pipeline(task, model=None)",
    "desc": "Готовый конвейер: sentiment, ner, summarization, text-generation.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "pipe = pipeline('sentiment-analysis')\nresult = pipe('I love this!')"
  },
  {
    "lib": "transformers",
    "name": "AutoTokenizer.from_pretrained()",
    "lvl": "beginner",
    "syntax": "AutoTokenizer.from_pretrained(model_name)",
    "desc": "Загрузить токенизатор по имени модели.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')"
  },
  {
    "lib": "transformers",
    "name": "AutoModel.from_pretrained()",
    "lvl": "intermediate",
    "syntax": "AutoModel.from_pretrained(model_name)",
    "desc": "Загрузить базовую модель (без head).",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "model = AutoModel.from_pretrained('bert-base-uncased')"
  },
  {
    "lib": "transformers",
    "name": "AutoModelForSequenceClassification()",
    "lvl": "intermediate",
    "syntax": "AutoModelForSequenceClassification.from_pretrained(name, num_labels=2)",
    "desc": "Модель с head для классификации текста.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "model = AutoModelForSequenceClassification.from_pretrained('bert-base', num_labels=3)"
  },
  {
    "lib": "transformers",
    "name": "AutoModelForTokenClassification()",
    "lvl": "intermediate",
    "syntax": "AutoModelForTokenClassification.from_pretrained(name)",
    "desc": "Модель для NER/token classification.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "model = AutoModelForTokenClassification.from_pretrained('bert-base', num_labels=NLABELS)"
  },
  {
    "lib": "transformers",
    "name": "AutoModelForQuestionAnswering()",
    "lvl": "intermediate",
    "syntax": "AutoModelForQuestionAnswering.from_pretrained(name)",
    "desc": "Модель для QA: предсказание span.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "model = AutoModelForQuestionAnswering.from_pretrained('deepset/roberta-base-squad2')"
  },
  {
    "lib": "transformers",
    "name": "AutoModelForCausalLM()",
    "lvl": "intermediate",
    "syntax": "AutoModelForCausalLM.from_pretrained(name)",
    "desc": "Модель для генерации текста (GPT-style).",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "model = AutoModelForCausalLM.from_pretrained('gpt2')"
  },
  {
    "lib": "transformers",
    "name": "AutoModelForSeq2SeqLM()",
    "lvl": "intermediate",
    "syntax": "AutoModelForSeq2SeqLM.from_pretrained(name)",
    "desc": "Модель seq2seq (T5, BART).",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "model = AutoModelForSeq2SeqLM.from_pretrained('t5-small')"
  },
  {
    "lib": "transformers",
    "name": "TrainingArguments()",
    "lvl": "intermediate",
    "syntax": "TrainingArguments(output_dir, per_device_train_batch_size, num_train_epochs, ...)",
    "desc": "Конфигурация обучения Transformers.",
    "tags": [
      "nlp",
      "huggingface",
      "обучение"
    ],
    "ex": "args = TrainingArguments('output', per_device_train_batch_size=8, num_train_epochs=3, evaluation_strategy='epoch')"
  },
  {
    "lib": "transformers",
    "name": "Trainer()",
    "lvl": "intermediate",
    "syntax": "Trainer(model, args, train_dataset, eval_dataset, ...)",
    "desc": "Высокоуровневый цикл обучения.",
    "tags": [
      "nlp",
      "huggingface",
      "обучение"
    ],
    "ex": "trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=val_ds)\ntrainer.train()"
  },
  {
    "lib": "transformers",
    "name": "DataCollatorWithPadding()",
    "lvl": "intermediate",
    "syntax": "DataCollatorWithPadding(tokenizer)",
    "desc": "Динамический padding батчей.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "collator = DataCollatorWithPadding(tokenizer=tokenizer)"
  },
  {
    "lib": "transformers",
    "name": "tokenizer()",
    "lvl": "beginner",
    "syntax": "tokenizer(text, padding=True, truncation=True, return_tensors='pt')",
    "desc": "Токенизация текста: input_ids, attention_mask.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "enc = tokenizer('Hello world', padding=True, truncation=True, return_tensors='pt')"
  },
  {
    "lib": "transformers",
    "name": "tokenizer.encode()",
    "lvl": "beginner",
    "syntax": "tokenizer.encode(text, add_special_tokens=True)",
    "desc": "Закодировать текст в список ID токенов.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "ids = tokenizer.encode('Hello world')"
  },
  {
    "lib": "transformers",
    "name": "tokenizer.decode()",
    "lvl": "beginner",
    "syntax": "tokenizer.decode(token_ids, skip_special_tokens=True)",
    "desc": "Декодировать ID в текст.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "text = tokenizer.decode(ids, skip_special_tokens=True)"
  },
  {
    "lib": "transformers",
    "name": "tokenizer.batch_encode_plus()",
    "lvl": "intermediate",
    "syntax": "tokenizer.batch_encode_plus(texts, padding=True, truncation=True)",
    "desc": "Токенизация списка текстов.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "batch = tokenizer.batch_encode_plus(['text1','text2'], padding=True, return_tensors='pt')"
  },
  {
    "lib": "transformers",
    "name": "model.generate()",
    "lvl": "intermediate",
    "syntax": "model.generate(input_ids, max_new_tokens=50, do_sample=True)",
    "desc": "Генерация текста для CausalLM/Seq2SeqLM.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "outputs = model.generate(input_ids, max_new_tokens=100, temperature=0.7, do_sample=True)"
  },
  {
    "lib": "transformers",
    "name": "model(**inputs)",
    "lvl": "beginner",
    "syntax": "outputs = model(**tokenized_inputs)",
    "desc": "Прямой проход модели.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "outputs = model(**enc)\nlogits = outputs.logits"
  },
  {
    "lib": "transformers",
    "name": "load_dataset()",
    "lvl": "beginner",
    "syntax": "datasets.load_dataset(path, split='train')",
    "desc": "Загрузить датасет из HF Hub.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "dataset = load_dataset('imdb')\ntrain = dataset['train'].select(range(1000))"
  },
  {
    "lib": "transformers",
    "name": "load_metric()",
    "lvl": "beginner",
    "syntax": "evaluate.load(metric_name)",
    "desc": "Загрузить метрику (accuracy, f1, bleu).",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "metric = evaluate.load('accuracy')\nscore = metric.compute(predictions=preds, references=labels)"
  },
  {
    "lib": "transformers",
    "name": "model.save_pretrained()",
    "lvl": "beginner",
    "syntax": "model.save_pretrained(save_directory)",
    "desc": "Сохранить модель и конфигурацию.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "model.save_pretrained('./my_model')"
  },
  {
    "lib": "transformers",
    "name": "tokenizer.save_pretrained()",
    "lvl": "beginner",
    "syntax": "tokenizer.save_pretrained(save_directory)",
    "desc": "Сохранить токенизатор.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "tokenizer.save_pretrained('./my_model')"
  },
  {
    "lib": "transformers",
    "name": "BitsAndBytesConfig()",
    "lvl": "advanced",
    "syntax": "BitsAndBytesConfig(load_in_4bit=True)",
    "desc": "Конфигурация 4/8-bit квантизации.",
    "tags": [
      "nlp",
      "оптимизация"
    ],
    "ex": "config = BitsAndBytesConfig(load_in_4bit=True)\nmodel = AutoModel.from_pretrained(name, quantization_config=config)"
  },
  {
    "lib": "transformers",
    "name": "LoraConfig()",
    "lvl": "advanced",
    "syntax": "LoraConfig(r=8, lora_alpha=16, target_modules=['q_proj','v_proj'])",
    "desc": "Конфигурация LoRA для дообучения.",
    "tags": [
      "nlp",
      "оптимизация"
    ],
    "ex": "config = LoraConfig(r=8, lora_alpha=16, target_modules=['q_proj','v_proj'])\nmodel = get_peft_model(base_model, config)"
  },
  {
    "lib": "transformers",
    "name": "get_peft_model()",
    "lvl": "advanced",
    "syntax": "peft.get_peft_model(model, peft_config)",
    "desc": "Применить PEFT (LoRA) к модели.",
    "tags": [
      "nlp",
      "оптимизация"
    ],
    "ex": "model = get_peft_model(base_model, lora_config)"
  },
  {
    "lib": "transformers",
    "name": "pipeline() specific tasks",
    "lvl": "intermediate",
    "syntax": "pipeline('text-generation', model='gpt2')\npipeline('translation', model='Helsinki-NLP/opus-mt-ru-en')",
    "desc": "Специализированные пайплайны.",
    "tags": [
      "nlp",
      "huggingface"
    ],
    "ex": "gen = pipeline('text-generation', model='gpt2')\ntr = pipeline('translation_en_to_fr', model='Helsinki-NLP/opus-mt-en-fr')"
  },
  {
    "lib": "opencv",
    "name": "cv2.imread()",
    "lvl": "beginner",
    "syntax": "cv2.imread(filename, flags)",
    "desc": "Чтение изображения. flags: IMREAD_COLOR, IMREAD_GRAYSCALE.",
    "tags": [
      "cv",
      "чтение"
    ],
    "ex": "img = cv2.imread('photo.jpg')\ngray = cv2.imread('photo.jpg', cv2.IMREAD_GRAYSCALE)"
  },
  {
    "lib": "opencv",
    "name": "cv2.imwrite()",
    "lvl": "beginner",
    "syntax": "cv2.imwrite(filename, img)",
    "desc": "Сохранить изображение в файл.",
    "tags": [
      "cv",
      "запись"
    ],
    "ex": "cv2.imwrite('output.jpg', img)"
  },
  {
    "lib": "opencv",
    "name": "cv2.imshow/waitKey/destroyAllWindows",
    "lvl": "beginner",
    "syntax": "cv2.imshow(winname, img); cv2.waitKey(0); cv2.destroyAllWindows()",
    "desc": "Показать изображение в окне.",
    "tags": [
      "cv",
      "отображение"
    ],
    "ex": "cv2.imshow('Image', img)\nk = cv2.waitKey(0)\ncv2.destroyAllWindows()"
  },
  {
    "lib": "opencv",
    "name": "cv2.cvtColor()",
    "lvl": "beginner",
    "syntax": "cv2.cvtColor(src, code)",
    "desc": "Конвертация цветового пространства: BGR2GRAY, BGR2RGB, BGR2HSV.",
    "tags": [
      "cv",
      "конвертация"
    ],
    "ex": "gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nhsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)"
  },
  {
    "lib": "opencv",
    "name": "cv2.resize()",
    "lvl": "beginner",
    "syntax": "cv2.resize(src, dsize, fx, fy, interpolation)",
    "desc": "Изменить размер. interpolation: INTER_AREA, INTER_CUBIC.",
    "tags": [
      "cv",
      "геометрия"
    ],
    "ex": "small = cv2.resize(img, (100,100))\nbig = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)"
  },
  {
    "lib": "opencv",
    "name": "cv2.GaussianBlur()",
    "lvl": "beginner",
    "syntax": "cv2.GaussianBlur(src, ksize, sigmaX)",
    "desc": "Гауссово размытие.",
    "tags": [
      "cv",
      "фильтр"
    ],
    "ex": "blurred = cv2.GaussianBlur(img, (5,5), 0)"
  },
  {
    "lib": "opencv",
    "name": "cv2.medianBlur()",
    "lvl": "beginner",
    "syntax": "cv2.medianBlur(src, ksize)",
    "desc": "Медианное размытие (соль/перец).",
    "tags": [
      "cv",
      "фильтр"
    ],
    "ex": "clean = cv2.medianBlur(noisy_img, 5)"
  },
  {
    "lib": "opencv",
    "name": "cv2.bilateralFilter()",
    "lvl": "intermediate",
    "syntax": "cv2.bilateralFilter(src, d, sigmaColor, sigmaSpace)",
    "desc": "Билатеральный фильтр с сохранением краёв.",
    "tags": [
      "cv",
      "фильтр"
    ],
    "ex": "smooth = cv2.bilateralFilter(img, 9, 75, 75)"
  },
  {
    "lib": "opencv",
    "name": "cv2.Canny()",
    "lvl": "intermediate",
    "syntax": "cv2.Canny(image, threshold1, threshold2)",
    "desc": "Выделение границ (Canny).",
    "tags": [
      "cv",
      "границы"
    ],
    "ex": "edges = cv2.Canny(gray, 50, 150)"
  },
  {
    "lib": "opencv",
    "name": "cv2.threshold()",
    "lvl": "beginner",
    "syntax": "cv2.threshold(src, thresh, maxval, type)",
    "desc": "Глобальная бинаризация.",
    "tags": [
      "cv",
      "бинаризация"
    ],
    "ex": "ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)"
  },
  {
    "lib": "opencv",
    "name": "cv2.adaptiveThreshold()",
    "lvl": "intermediate",
    "syntax": "cv2.adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C)",
    "desc": "Адаптивная бинаризация.",
    "tags": [
      "cv",
      "бинаризация"
    ],
    "ex": "binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)"
  },
  {
    "lib": "opencv",
    "name": "cv2.findContours()",
    "lvl": "intermediate",
    "syntax": "cv2.findContours(image, mode, method)",
    "desc": "Поиск контуров.",
    "tags": [
      "cv",
      "контуры"
    ],
    "ex": "contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)"
  },
  {
    "lib": "opencv",
    "name": "cv2.drawContours()",
    "lvl": "beginner",
    "syntax": "cv2.drawContours(image, contours, contourIdx, color, thickness)",
    "desc": "Нарисовать контуры.",
    "tags": [
      "cv",
      "контуры"
    ],
    "ex": "cv2.drawContours(img, contours, -1, (0,255,0), 2)"
  },
  {
    "lib": "opencv",
    "name": "cv2.morphologyEx()",
    "lvl": "intermediate",
    "syntax": "cv2.morphologyEx(src, op, kernel)",
    "desc": "Морфология: OPEN, CLOSE, GRADIENT.",
    "tags": [
      "cv",
      "морфология"
    ],
    "ex": "opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)"
  },
  {
    "lib": "opencv",
    "name": "cv2.dilate()",
    "lvl": "beginner",
    "syntax": "cv2.dilate(src, kernel, iterations=1)",
    "desc": "Дилатация.",
    "tags": [
      "cv",
      "морфология"
    ],
    "ex": "dilated = cv2.dilate(binary, np.ones((3,3),np.uint8), iterations=1)"
  },
  {
    "lib": "opencv",
    "name": "cv2.erode()",
    "lvl": "beginner",
    "syntax": "cv2.erode(src, kernel, iterations=1)",
    "desc": "Эрозия.",
    "tags": [
      "cv",
      "морфология"
    ],
    "ex": "eroded = cv2.erode(binary, np.ones((3,3),np.uint8), iterations=1)"
  },
  {
    "lib": "opencv",
    "name": "cv2.getStructuringElement()",
    "lvl": "beginner",
    "syntax": "cv2.getStructuringElement(shape, ksize)",
    "desc": "Создать ядро для морфологии.",
    "tags": [
      "cv",
      "морфология"
    ],
    "ex": "kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))"
  },
  {
    "lib": "opencv",
    "name": "cv2.warpAffine()",
    "lvl": "intermediate",
    "syntax": "cv2.warpAffine(src, M, dsize)",
    "desc": "Аффинное преобразование.",
    "tags": [
      "cv",
      "геометрия"
    ],
    "ex": "M = cv2.getRotationMatrix2D((w//2,h//2), 45, 1.0)\nrotated = cv2.warpAffine(img, M, (w,h))"
  },
  {
    "lib": "opencv",
    "name": "cv2.getRotationMatrix2D()",
    "lvl": "beginner",
    "syntax": "cv2.getRotationMatrix2D(center, angle, scale)",
    "desc": "Матрица поворота.",
    "tags": [
      "cv",
      "геометрия"
    ],
    "ex": "M = cv2.getRotationMatrix2D((cx,cy), 90, 0.5)"
  },
  {
    "lib": "opencv",
    "name": "cv2.warpPerspective()",
    "lvl": "intermediate",
    "syntax": "cv2.warpPerspective(src, M, dsize)",
    "desc": "Перспективное преобразование.",
    "tags": [
      "cv",
      "геометрия"
    ],
    "ex": "M = cv2.getPerspectiveTransform(src_pts, dst_pts)\nwarped = cv2.warpPerspective(img, M, (w,h))"
  },
  {
    "lib": "opencv",
    "name": "cv2.getPerspectiveTransform()",
    "lvl": "intermediate",
    "syntax": "cv2.getPerspectiveTransform(src, dst)",
    "desc": "Матрица перспективного преобразования.",
    "tags": [
      "cv",
      "геометрия"
    ],
    "ex": "M = cv2.getPerspectiveTransform(src_pts, dst_pts)"
  },
  {
    "lib": "opencv",
    "name": "cv2.flip()",
    "lvl": "beginner",
    "syntax": "cv2.flip(src, flipCode)",
    "desc": "Отразить: 0-верт, 1-гориз, -1-оба.",
    "tags": [
      "cv",
      "геометрия"
    ],
    "ex": "flipped = cv2.flip(img, 1)"
  },
  {
    "lib": "opencv",
    "name": "cv2.rotate()",
    "lvl": "beginner",
    "syntax": "cv2.rotate(src, rotateCode)",
    "desc": "Поворот на 90/180/270.",
    "tags": [
      "cv",
      "геометрия"
    ],
    "ex": "rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)"
  },
  {
    "lib": "opencv",
    "name": "cv2.addWeighted()",
    "lvl": "beginner",
    "syntax": "cv2.addWeighted(src1, alpha, src2, beta, gamma)",
    "desc": "Смешивание двух изображений.",
    "tags": [
      "cv"
    ],
    "ex": "blend = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)"
  },
  {
    "lib": "opencv",
    "name": "cv2.split() / cv2.merge()",
    "lvl": "beginner",
    "syntax": "cv2.split(m); cv2.merge(mv)",
    "desc": "Разделить/объединить каналы B,G,R.",
    "tags": [
      "cv",
      "каналы"
    ],
    "ex": "b, g, r = cv2.split(img)\nmerged = cv2.merge([b, g, r])"
  },
  {
    "lib": "opencv",
    "name": "cv2.calcHist()",
    "lvl": "intermediate",
    "syntax": "cv2.calcHist(images, channels, mask, histSize, ranges)",
    "desc": "Вычислить гистограмму изображения.",
    "tags": [
      "cv",
      "гистограмма"
    ],
    "ex": "hist = cv2.calcHist([img], [0], None, [256], [0, 256])"
  },
  {
    "lib": "opencv",
    "name": "cv2.equalizeHist()",
    "lvl": "beginner",
    "syntax": "cv2.equalizeHist(src)",
    "desc": "Эквализация гистограммы.",
    "tags": [
      "cv",
      "гистограмма"
    ],
    "ex": "eq = cv2.equalizeHist(gray)"
  },
  {
    "lib": "opencv",
    "name": "cv2.matchTemplate()",
    "lvl": "intermediate",
    "syntax": "cv2.matchTemplate(image, templ, method)",
    "desc": "Поиск шаблона на изображении.",
    "tags": [
      "cv",
      "поиск"
    ],
    "ex": "result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)\nminv, maxv, minl, maxl = cv2.minMaxLoc(result)"
  },
  {
    "lib": "opencv",
    "name": "cv2.HoughLinesP()",
    "lvl": "intermediate",
    "syntax": "cv2.HoughLinesP(image, rho, theta, threshold)",
    "desc": "Поиск отрезков (преобразование Хафа).",
    "tags": [
      "cv",
      "поиск"
    ],
    "ex": "lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)"
  },
  {
    "lib": "opencv",
    "name": "cv2.HoughCircles()",
    "lvl": "intermediate",
    "syntax": "cv2.HoughCircles(image, method, dp, minDist)",
    "desc": "Поиск окружностей.",
    "tags": [
      "cv",
      "поиск"
    ],
    "ex": "circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10)"
  },
  {
    "lib": "opencv",
    "name": "cv2.goodFeaturesToTrack()",
    "lvl": "intermediate",
    "syntax": "cv2.goodFeaturesToTrack(image, maxCorners, qualityLevel, minDistance)",
    "desc": "Найти хорошие углы (Shi-Tomasi).",
    "tags": [
      "cv",
      "признаки"
    ],
    "ex": "corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)"
  },
  {
    "lib": "opencv",
    "name": "cv2.VideoCapture()",
    "lvl": "beginner",
    "syntax": "cv2.VideoCapture(index_or_filename)",
    "desc": "Захват видео с камеры или файла.",
    "tags": [
      "cv",
      "видео"
    ],
    "ex": "cap = cv2.VideoCapture(0)\nret, frame = cap.read()\ncap.release()"
  },
  {
    "lib": "opencv",
    "name": "cv2.VideoWriter()",
    "lvl": "intermediate",
    "syntax": "cv2.VideoWriter(filename, fourcc, fps, frameSize)",
    "desc": "Запись видео в файл.",
    "tags": [
      "cv",
      "видео"
    ],
    "ex": "out = cv2.VideoWriter('out.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (w,h))"
  },
  {
    "lib": "opencv",
    "name": "cv2.putText()",
    "lvl": "beginner",
    "syntax": "cv2.putText(img, text, org, fontFace, fontScale, color, thickness)",
    "desc": "Текст на изображении.",
    "tags": [
      "cv",
      "рисование"
    ],
    "ex": "cv2.putText(img, 'Label', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)"
  },
  {
    "lib": "opencv",
    "name": "cv2.rectangle()",
    "lvl": "beginner",
    "syntax": "cv2.rectangle(img, pt1, pt2, color, thickness)",
    "desc": "Прямоугольник.",
    "tags": [
      "cv",
      "рисование"
    ],
    "ex": "cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)"
  },
  {
    "lib": "opencv",
    "name": "cv2.circle()",
    "lvl": "beginner",
    "syntax": "cv2.circle(img, center, radius, color, thickness)",
    "desc": "Окружность.",
    "tags": [
      "cv",
      "рисование"
    ],
    "ex": "cv2.circle(img, (cx,cy), 10, (255,0,0), -1)"
  },
  {
    "lib": "opencv",
    "name": "cv2.line()",
    "lvl": "beginner",
    "syntax": "cv2.line(img, pt1, pt2, color, thickness)",
    "desc": "Линия.",
    "tags": [
      "cv",
      "рисование"
    ],
    "ex": "cv2.line(img, (0,0), (w,h), (0,0,255), 2)"
  },
  {
    "lib": "opencv",
    "name": "cv2.polylines()",
    "lvl": "beginner",
    "syntax": "cv2.polylines(img, pts, isClosed, color, thickness)",
    "desc": "Ломаная линия / полигон.",
    "tags": [
      "cv",
      "рисование"
    ],
    "ex": "cv2.polylines(img, [pts], isClosed=True, color=(0,255,0), thickness=2)"
  },
  {
    "lib": "opencv",
    "name": "cv2.fillPoly()",
    "lvl": "beginner",
    "syntax": "cv2.fillPoly(img, pts, color)",
    "desc": "Залитый многоугольник.",
    "tags": [
      "cv",
      "рисование"
    ],
    "ex": "cv2.fillPoly(img, [poly_pts], (255, 0, 0))"
  },
  {
    "lib": "nltk",
    "name": "nltk.download()",
    "lvl": "beginner",
    "syntax": "nltk.download(package)",
    "desc": "Загрузить пакет NLTK (punkt, stopwords, wordnet).",
    "tags": [
      "nlp"
    ],
    "ex": "nltk.download('punkt')\nnltk.download('wordnet')"
  },
  {
    "lib": "nltk",
    "name": "word_tokenize()",
    "lvl": "beginner",
    "syntax": "nltk.word_tokenize(text)",
    "desc": "Токенизация текста на слова.",
    "tags": [
      "nlp",
      "токенизация"
    ],
    "ex": "tokens = word_tokenize('Hello, world!')"
  },
  {
    "lib": "nltk",
    "name": "sent_tokenize()",
    "lvl": "beginner",
    "syntax": "nltk.sent_tokenize(text)",
    "desc": "Токенизация текста на предложения.",
    "tags": [
      "nlp",
      "токенизация"
    ],
    "ex": "sents = sent_tokenize('Hi there. How are you?')"
  },
  {
    "lib": "nltk",
    "name": "pos_tag()",
    "lvl": "beginner",
    "syntax": "nltk.pos_tag(tokens)",
    "desc": "Частеречная разметка (Penn Treebank).",
    "tags": [
      "nlp",
      "pos"
    ],
    "ex": "tagged = pos_tag(tokens)"
  },
  {
    "lib": "nltk",
    "name": "ne_chunk()",
    "lvl": "intermediate",
    "syntax": "nltk.ne_chunk(pos_tagged)",
    "desc": "Распознавание именованных сущностей (NER).",
    "tags": [
      "nlp",
      "ner"
    ],
    "ex": "tree = ne_chunk(pos_tag(tokens))"
  },
  {
    "lib": "nltk",
    "name": "FreqDist()",
    "lvl": "beginner",
    "syntax": "nltk.FreqDist(tokens)",
    "desc": "Частотное распределение. .most_common(n), .plot().",
    "tags": [
      "nlp",
      "частоты"
    ],
    "ex": "fd = FreqDist(tokens)\nprint(fd.most_common(10))\nfd.plot(20)"
  },
  {
    "lib": "nltk",
    "name": "ConditionalFreqDist()",
    "lvl": "intermediate",
    "syntax": "nltk.ConditionalFreqDist((category, word) pairs)",
    "desc": "Условное частотное распределение.",
    "tags": [
      "nlp",
      "частоты"
    ],
    "ex": "cfd = ConditionalFreqDist((genre, word) for genre, word in pairs)"
  },
  {
    "lib": "nltk",
    "name": "bigrams() / trigrams()",
    "lvl": "beginner",
    "syntax": "nltk.bigrams(tokens); nltk.trigrams(tokens)",
    "desc": "Генерация биграмм / триграмм.",
    "tags": [
      "nlp",
      "n-gram"
    ],
    "ex": "bigrams = list(nltk.bigrams(tokens))"
  },
  {
    "lib": "nltk",
    "name": "ngrams()",
    "lvl": "beginner",
    "syntax": "nltk.ngrams(tokens, n)",
    "desc": "Генерация n-грамм.",
    "tags": [
      "nlp",
      "n-gram"
    ],
    "ex": "ngrams = list(ngrams(tokens, 4))"
  },
  {
    "lib": "nltk",
    "name": "PorterStemmer()",
    "lvl": "beginner",
    "syntax": "PorterStemmer().stem(word)",
    "desc": "Стеммер Портера (английский).",
    "tags": [
      "nlp",
      "стемминг"
    ],
    "ex": "stemmer = PorterStemmer()\nstems = [stemmer.stem(w) for w in words]"
  },
  {
    "lib": "nltk",
    "name": "LancasterStemmer()",
    "lvl": "beginner",
    "syntax": "LancasterStemmer().stem(word)",
    "desc": "Агрессивный стеммер Ланкастера.",
    "tags": [
      "nlp",
      "стемминг"
    ],
    "ex": "ls = LancasterStemmer()\nstemmed = ls.stem('running')"
  },
  {
    "lib": "nltk",
    "name": "WordNetLemmatizer()",
    "lvl": "beginner",
    "syntax": "WordNetLemmatizer().lemmatize(word, pos='n')",
    "desc": "Лемматизация через WordNet.",
    "tags": [
      "nlp",
      "лемматизация"
    ],
    "ex": "lemmatizer = WordNetLemmatizer()\nlemma = lemmatizer.lemmatize('better', pos='a')"
  },
  {
    "lib": "nltk",
    "name": "stopwords",
    "lvl": "beginner",
    "syntax": "nltk.corpus.stopwords.words('english')",
    "desc": "Список стоп-слов.",
    "tags": [
      "nlp"
    ],
    "ex": "stop_words = set(stopwords.words('english'))\nclean = [w for w in tokens if w.lower() not in stop_words]"
  },
  {
    "lib": "nltk",
    "name": "corpus.words()",
    "lvl": "beginner",
    "syntax": "nltk.corpus.words.words()",
    "desc": "Список английских слов.",
    "tags": [
      "nlp",
      "корпус"
    ],
    "ex": "eng_words = set(corpus.words.words())"
  },
  {
    "lib": "nltk",
    "name": "corpus.gutenberg",
    "lvl": "intermediate",
    "syntax": "nltk.corpus.gutenberg.fileids(); .words(); .sents()",
    "desc": "Корпус Gutenberg (Project Gutenberg).",
    "tags": [
      "nlp",
      "корпус"
    ],
    "ex": "hamlet = gutenberg.words('shakespeare-hamlet.txt')"
  },
  {
    "lib": "nltk",
    "name": "corpus.brown",
    "lvl": "intermediate",
    "syntax": "nltk.corpus.brown.words(); .categories()",
    "desc": "Brown Corpus - размеченный корпус по жанрам.",
    "tags": [
      "nlp",
      "корпус"
    ],
    "ex": "news_text = brown.words(categories='news')"
  },
  {
    "lib": "nltk",
    "name": "corpus.reuters",
    "lvl": "intermediate",
    "syntax": "nltk.corpus.reuters.fileids(); .words()",
    "desc": "Reuters Corpus - новостные статьи.",
    "tags": [
      "nlp",
      "корпус"
    ],
    "ex": "reuters.words('training/9865')"
  },
  {
    "lib": "nltk",
    "name": "corpus.inaugural",
    "lvl": "beginner",
    "syntax": "nltk.corpus.inaugural.words(fileids)",
    "desc": "Инаугурационные речи президентов США.",
    "tags": [
      "nlp",
      "корпус"
    ],
    "ex": "obama = inaugural.words('2009-Obama.txt')"
  },
  {
    "lib": "nltk",
    "name": "sentiwordnet",
    "lvl": "intermediate",
    "syntax": "nltk.corpus.sentiwordnet.senti_synsets(word)",
    "desc": "SentiWordNet: pos_score, neg_score.",
    "tags": [
      "nlp",
      "sentiment"
    ],
    "ex": "synsets = sentiwordnet.senti_synsets('beautiful')"
  },
  {
    "lib": "nltk",
    "name": "wordnet.synsets()",
    "lvl": "intermediate",
    "syntax": "nltk.corpus.wordnet.synsets(word)",
    "desc": "Синосеты WordNet: definition, examples, hypernyms.",
    "tags": [
      "nlp",
      "wordnet"
    ],
    "ex": "syn = wordnet.synsets('bank')\nfor s in syn: print(s.definition())"
  },
  {
    "lib": "spacy",
    "name": "spacy.load()",
    "lvl": "beginner",
    "syntax": "spacy.load(model_name)",
    "desc": "Загрузить модель: en_core_web_sm, ru_core_news_sm.",
    "tags": [
      "nlp"
    ],
    "ex": "nlp = spacy.load('en_core_web_sm')"
  },
  {
    "lib": "spacy",
    "name": "nlp()",
    "lvl": "beginner",
    "syntax": "nlp(text)",
    "desc": "Обработать текст: токенизация, POS, NER, зависимости.",
    "tags": [
      "nlp"
    ],
    "ex": "doc = nlp('Apple is looking at buying U.K. startup for $1 billion')"
  },
  {
    "lib": "spacy",
    "name": "doc.ents",
    "lvl": "beginner",
    "syntax": "doc.ents",
    "desc": "Именованные сущности. .label_, .text.",
    "tags": [
      "nlp",
      "ner"
    ],
    "ex": "for ent in doc.ents:\n    print(ent.text, ent.label_)"
  },
  {
    "lib": "spacy",
    "name": "Token attributes",
    "lvl": "beginner",
    "syntax": "token.text/.lemma_/.pos_/.tag_/.dep_/.is_stop",
    "desc": "Атрибуты токена: текст, лемма, POS, зависимость.",
    "tags": [
      "nlp"
    ],
    "ex": "for token in doc:\n    print(token.text, token.pos_, token.lemma_)"
  },
  {
    "lib": "spacy",
    "name": "Matcher()",
    "lvl": "intermediate",
    "syntax": "Matcher(nlp.vocab)",
    "desc": "Поиск паттернов токенов по атрибутам.",
    "tags": [
      "nlp"
    ],
    "ex": "matcher = Matcher(nlp.vocab)\nmatcher.add('MONEY', [[{'LIKE_NUM':True},{'IS_CURRENCY':True}]])\nmatches = matcher(doc)"
  },
  {
    "lib": "spacy",
    "name": "PhraseMatcher()",
    "lvl": "intermediate",
    "syntax": "PhraseMatcher(nlp.vocab)",
    "desc": "Поиск точных фраз.",
    "tags": [
      "nlp"
    ],
    "ex": "pmatcher = PhraseMatcher(nlp.vocab)\npmatcher.add('FRUIT', [nlp('apple pie')])"
  },
  {
    "lib": "spacy",
    "name": "EntityRuler()",
    "lvl": "intermediate",
    "syntax": "EntityRuler(nlp, overwrite_ents=True)",
    "desc": "Правила для извлечения сущностей.",
    "tags": [
      "nlp",
      "ner"
    ],
    "ex": "ruler = nlp.add_pipe('entity_ruler')\nruler.add_patterns([{'label':'SKILL','pattern':'Python'}])"
  },
  {
    "lib": "spacy",
    "name": "Span",
    "lvl": "intermediate",
    "syntax": "Span(doc, start, end, label=None)",
    "desc": "Создать срез документа как Span.",
    "tags": [
      "nlp"
    ],
    "ex": "span = doc[2:5]\nspan = Span(doc, 0, 3, label='ORG')"
  },
  {
    "lib": "spacy",
    "name": "Doc",
    "lvl": "beginner",
    "syntax": "Doc(nlp.vocab, words=words)",
    "desc": "Создать Doc вручную.",
    "tags": [
      "nlp"
    ],
    "ex": "doc = Doc(nlp.vocab, words=['Hello', 'world'])"
  },
  {
    "lib": "spacy",
    "name": "displacy.render()",
    "lvl": "beginner",
    "syntax": "displacy.render(doc, style='ent'/'dep', jupyter=True)",
    "desc": "Визуализация NER или зависимостей.",
    "tags": [
      "nlp",
      "визуализация"
    ],
    "ex": "displacy.render(doc, style='ent', jupyter=True)"
  },
  {
    "lib": "spacy",
    "name": "displacy.serve()",
    "lvl": "beginner",
    "syntax": "displacy.serve(doc, style='dep', port=5000)",
    "desc": "Веб-сервер с визуализацией зависимостей.",
    "tags": [
      "nlp",
      "визуализация"
    ],
    "ex": "displacy.serve(doc, style='dep')"
  },
  {
    "lib": "spacy",
    "name": "nlp.add_pipe()",
    "lvl": "intermediate",
    "syntax": "nlp.add_pipe(component, before=None, after=None)",
    "desc": "Добавить компонент в конвейер.",
    "tags": [
      "nlp"
    ],
    "ex": "nlp.add_pipe('sentencizer', before='parser')"
  },
  {
    "lib": "spacy",
    "name": "nlp.remove_pipe()",
    "lvl": "intermediate",
    "syntax": "nlp.remove_pipe(name)",
    "desc": "Удалить компонент из конвейера.",
    "tags": [
      "nlp"
    ],
    "ex": "nlp.remove_pipe('ner')"
  },
  {
    "lib": "spacy",
    "name": "Language.component",
    "lvl": "advanced",
    "syntax": "@Language.component('name')\ndef my_component(doc): ... return doc",
    "desc": "Пользовательский компонент конвейера.",
    "tags": [
      "nlp"
    ],
    "ex": "@Language.component('custom')\ndef custom_component(doc):\n    print(len(doc))\n    return doc"
  },
  {
    "lib": "spacy",
    "name": "span.merge()",
    "lvl": "intermediate",
    "syntax": "span.merge()",
    "desc": "Объединить span в один токен.",
    "tags": [
      "nlp"
    ],
    "ex": "for ent in doc.ents:\n    ent.merge()"
  },
  {
    "lib": "dask",
    "name": "dd.read_csv()",
    "lvl": "beginner",
    "syntax": "dask.dataframe.read_csv(path, blocksize=None)",
    "desc": "Чтение CSV лениво в распределённый DataFrame.",
    "tags": [
      "dask",
      "чтение"
    ],
    "ex": "ddf = dd.read_csv('data/*.csv')"
  },
  {
    "lib": "dask",
    "name": "ddf.to_csv()",
    "lvl": "beginner",
    "syntax": "ddf.to_csv(path, single_file=False)",
    "desc": "Запись DataFrame в CSV (партиции).",
    "tags": [
      "dask",
      "запись"
    ],
    "ex": "ddf.to_csv('output/*.csv', index=False)"
  },
  {
    "lib": "dask",
    "name": "ddf.to_parquet()",
    "lvl": "beginner",
    "syntax": "ddf.to_parquet(path)",
    "desc": "Запись в Parquet.",
    "tags": [
      "dask",
      "запись"
    ],
    "ex": "ddf.to_parquet('data.parquet')"
  },
  {
    "lib": "dask",
    "name": "dask.delayed()",
    "lvl": "intermediate",
    "syntax": "@dask.delayed\ndef func(...): ...",
    "desc": "Отложенное выполнение функции.",
    "tags": [
      "dask"
    ],
    "ex": "outputs = [dask.delayed(process)(f) for f in files]\nresults = dask.compute(*outputs)"
  },
  {
    "lib": "dask",
    "name": "da.from_array()",
    "lvl": "beginner",
    "syntax": "dask.array.from_array(arr, chunks)",
    "desc": "Создать Dask Array из numpy с разбиением.",
    "tags": [
      "dask",
      "массивы"
    ],
    "ex": "darr = da.from_array(big_numpy, chunks=(1000, -1))"
  },
  {
    "lib": "dask",
    "name": "da.random.random()",
    "lvl": "beginner",
    "syntax": "da.random.random(size)",
    "desc": "Случайный Dask Array.",
    "tags": [
      "dask",
      "массивы"
    ],
    "ex": "darr = da.random.random((10000, 10000), chunks=(1000, 1000))"
  },
  {
    "lib": "dask",
    "name": "da.mean() / da.sum()",
    "lvl": "beginner",
    "syntax": "da.mean(darr, axis=None); da.sum(darr, axis=None)",
    "desc": "Среднее / сумма (лениво).",
    "tags": [
      "dask",
      "массивы"
    ],
    "ex": "mean_val = da.mean(darr).compute()"
  },
  {
    "lib": "dask",
    "name": "Client()",
    "lvl": "intermediate",
    "syntax": "Client(n_workers=4, threads_per_worker=2)",
    "desc": "Распределённый клиент Dask.",
    "tags": [
      "dask",
      "distributed"
    ],
    "ex": "client = Client(n_workers=4)\nclient.dashboard_link"
  },
  {
    "lib": "dask",
    "name": "client.compute()",
    "lvl": "beginner",
    "syntax": "future = client.compute(collection)",
    "desc": "Асинхронное вычисление на кластере.",
    "tags": [
      "dask",
      "distributed"
    ],
    "ex": "future = client.compute(ddf.sum())"
  },
  {
    "lib": "dask",
    "name": "client.gather()",
    "lvl": "beginner",
    "syntax": "results = client.gather(futures)",
    "desc": "Собрать результаты с воркеров.",
    "tags": [
      "dask",
      "distributed"
    ],
    "ex": "results = client.gather(futures)"
  },
  {
    "lib": "dask",
    "name": "client.scatter()",
    "lvl": "intermediate",
    "syntax": "future = client.scatter(data)",
    "desc": "Распределить данные по воркерам.",
    "tags": [
      "dask",
      "distributed"
    ],
    "ex": "future_x = client.scatter(large_data)"
  },
  {
    "lib": "dask",
    "name": "client.map()",
    "lvl": "intermediate",
    "syntax": "futures = client.map(func, iterable)",
    "desc": "Параллельный map функции по данным.",
    "tags": [
      "dask",
      "distributed"
    ],
    "ex": "futures = client.map(process_file, file_list)"
  },
  {
    "lib": "polars",
    "name": "pl.read_csv()",
    "lvl": "beginner",
    "syntax": "pl.read_csv(source, has_header=True)",
    "desc": "Чтение CSV в DataFrame Polars.",
    "tags": [
      "polars",
      "чтение"
    ],
    "ex": "df = pl.read_csv('data.csv')"
  },
  {
    "lib": "polars",
    "name": "pl.read_parquet()",
    "lvl": "beginner",
    "syntax": "pl.read_parquet(source)",
    "desc": "Чтение Parquet.",
    "tags": [
      "polars",
      "чтение"
    ],
    "ex": "df = pl.read_parquet('data.parquet')"
  },
  {
    "lib": "polars",
    "name": "pl.DataFrame()",
    "lvl": "beginner",
    "syntax": "pl.DataFrame(data, schema=None)",
    "desc": "Создать DataFrame из dict/списков.",
    "tags": [
      "polars"
    ],
    "ex": "df = pl.DataFrame({'a':[1,2,3], 'b':['x','y','z']})"
  },
  {
    "lib": "polars",
    "name": "pl.Series()",
    "lvl": "beginner",
    "syntax": "pl.Series(name, values)",
    "desc": "Серия Polars (аналог pd.Series).",
    "tags": [
      "polars"
    ],
    "ex": "s = pl.Series('nums', [1, 2, 3])"
  },
  {
    "lib": "polars",
    "name": "pl.scan_csv()",
    "lvl": "intermediate",
    "syntax": "pl.scan_csv(source)",
    "desc": "Ленивое чтение CSV (LazyFrame).",
    "tags": [
      "polars",
      "lazy"
    ],
    "ex": "lf = pl.scan_csv('big.csv')\nresult = lf.filter(pl.col('x')>0).collect()"
  },
  {
    "lib": "polars",
    "name": "df.with_columns()",
    "lvl": "beginner",
    "syntax": "df.with_columns([expr, ...])",
    "desc": "Добавить/заменить столбцы через выражения.",
    "tags": [
      "polars"
    ],
    "ex": "df = df.with_columns([(pl.col('price')*pl.col('qty')).alias('total')])"
  },
  {
    "lib": "polars",
    "name": "df.filter()",
    "lvl": "beginner",
    "syntax": "df.filter(predicate)",
    "desc": "Фильтр строк по условию.",
    "tags": [
      "polars"
    ],
    "ex": "filtered = df.filter(pl.col('age') > 18)"
  },
  {
    "lib": "polars",
    "name": "df.select()",
    "lvl": "beginner",
    "syntax": "df.select(exprs)",
    "desc": "Выборка столбцов с выражениями.",
    "tags": [
      "polars"
    ],
    "ex": "df.select([pl.col('name'), (pl.col('a')+pl.col('b')).alias('sum')])"
  },
  {
    "lib": "polars",
    "name": "df.group_by()",
    "lvl": "intermediate",
    "syntax": "df.group_by(keys).agg(exprs)",
    "desc": "Группировка + агрегация.",
    "tags": [
      "polars"
    ],
    "ex": "df.group_by('category').agg([pl.col('val').mean()])"
  },
  {
    "lib": "polars",
    "name": "df.join()",
    "lvl": "intermediate",
    "syntax": "df.join(other, on='key', how='inner')",
    "desc": "SQL-style JOIN.",
    "tags": [
      "polars"
    ],
    "ex": "joined = df_a.join(df_b, on='id', how='left')"
  },
  {
    "lib": "polars",
    "name": "df.sort()",
    "lvl": "beginner",
    "syntax": "df.sort(by='col', descending=False)",
    "desc": "Сортировка.",
    "tags": [
      "polars"
    ],
    "ex": "df = df.sort(by=['category', 'value'], descending=[False, True])"
  },
  {
    "lib": "polars",
    "name": "df.unique()",
    "lvl": "beginner",
    "syntax": "df.unique(subset=None)",
    "desc": "Убрать дубликаты.",
    "tags": [
      "polars"
    ],
    "ex": "uniques = df.unique(subset=['user_id'])"
  },
  {
    "lib": "polars",
    "name": "df.drop_nulls()",
    "lvl": "beginner",
    "syntax": "df.drop_nulls(subset=None)",
    "desc": "Удалить строки с null.",
    "tags": [
      "polars"
    ],
    "ex": "clean = df.drop_nulls(subset=['critical_col'])"
  },
  {
    "lib": "polars",
    "name": "df.fill_null()",
    "lvl": "beginner",
    "syntax": "df.fill_null(value)",
    "desc": "Заполнить null значения.",
    "tags": [
      "polars"
    ],
    "ex": "df = df.fill_null(0)"
  },
  {
    "lib": "polars",
    "name": "df.to_pandas()",
    "lvl": "beginner",
    "syntax": "df.to_pandas()",
    "desc": "Конвертировать в pandas.",
    "tags": [
      "polars"
    ],
    "ex": "pd_df = df.to_pandas()"
  },
  {
    "lib": "polars",
    "name": "lazy().collect()",
    "lvl": "intermediate",
    "syntax": "lf = df.lazy(); result = lf.collect()",
    "desc": "Ленивое выполнение: планирование + сбор результата.",
    "tags": [
      "polars",
      "lazy"
    ],
    "ex": "result = (df.lazy().filter(pl.col('x')>0).select('y').collect())"
  },
  {
    "lib": "polars",
    "name": "pl.col / pl.lit / pl.when-then",
    "lvl": "beginner",
    "syntax": "pl.col('name'); pl.lit(42); pl.when(cond).then(val).otherwise(other)",
    "desc": "Выражения: ссылка на столбец, литерал, условное выражение.",
    "tags": [
      "polars",
      "выражения"
    ],
    "ex": "df.select([pl.when(pl.col('x')>0).then(1).otherwise(0).alias('flag')])"
  },
  {
    "lib": "polars",
    "name": "pl.concat() / pl.date_range()",
    "lvl": "beginner",
    "syntax": "pl.concat(dfs); pl.date_range(start, end, interval)",
    "desc": "Конкатенация DataFrame; последовательность дат.",
    "tags": [
      "polars"
    ],
    "ex": "combined = pl.concat([df1, df2], how='vertical')\ndates = pl.date_range('2023-01-01', '2023-12-31', '1mo')"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.start_run()",
    "lvl": "beginner",
    "syntax": "mlflow.start_run(run_name=None)",
    "desc": "Начать новый MLflow run.",
    "tags": [
      "mlflow"
    ],
    "ex": "with mlflow.start_run():\n    mlflow.log_param('lr', 0.01)\n    mlflow.log_metric('acc', 0.95)"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.end_run()",
    "lvl": "beginner",
    "syntax": "mlflow.end_run()",
    "desc": "Завершить активный run.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.end_run()"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.log_param()",
    "lvl": "beginner",
    "syntax": "mlflow.log_param(key, value)",
    "desc": "Записать один параметр.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.log_param('learning_rate', 0.001)"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.log_params()",
    "lvl": "beginner",
    "syntax": "mlflow.log_params(params_dict)",
    "desc": "Записать несколько параметров за раз.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.log_params({'lr':0.01, 'epochs':50})"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.log_metric()",
    "lvl": "beginner",
    "syntax": "mlflow.log_metric(key, value, step=None)",
    "desc": "Записать метрику (можно step для временных рядов).",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.log_metric('accuracy', 0.95, step=epoch)"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.log_metrics()",
    "lvl": "beginner",
    "syntax": "mlflow.log_metrics(metrics_dict, step=None)",
    "desc": "Записать несколько метрик за раз.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.log_metrics({'acc':0.95, 'f1':0.93})"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.log_artifact()",
    "lvl": "beginner",
    "syntax": "mlflow.log_artifact(local_path, artifact_path=None)",
    "desc": "Записать артефакт (файл/график).",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.log_artifact('confusion_matrix.png')"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.log_artifacts()",
    "lvl": "beginner",
    "syntax": "mlflow.log_artifacts(local_dir, artifact_path=None)",
    "desc": "Записать все файлы из директории.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.log_artifacts('outputs/')"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.sklearn.log_model()",
    "lvl": "intermediate",
    "syntax": "mlflow.sklearn.log_model(model, artifact_path)",
    "desc": "Сохранить sklearn/ML-модель в MLflow.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.sklearn.log_model(model, 'model')"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.register_model()",
    "lvl": "intermediate",
    "syntax": "mlflow.register_model(model_uri, name)",
    "desc": "Зарегистрировать модель в Model Registry.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.register_model('runs:/abc123/model', 'MyModel')"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.set_tag()",
    "lvl": "beginner",
    "syntax": "mlflow.set_tag(key, value)",
    "desc": "Установить тег для run.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.set_tag('experiment_type', 'baseline')"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.get_run()",
    "lvl": "beginner",
    "syntax": "mlflow.get_run(run_id)",
    "desc": "Получить информацию о run.",
    "tags": [
      "mlflow"
    ],
    "ex": "run = mlflow.get_run(run_id)\nprint(run.data.metrics)"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.search_runs()",
    "lvl": "intermediate",
    "syntax": "mlflow.search_runs(experiment_ids, filter_string='')",
    "desc": "Поиск run'ов по критериям.",
    "tags": [
      "mlflow"
    ],
    "ex": "runs = mlflow.search_runs(experiment_ids=['1'], filter_string='metrics.acc > 0.9')"
  },
  {
    "lib": "mlflow",
    "name": "mlflow.set_tracking_uri() / create_experiment()",
    "lvl": "beginner",
    "syntax": "mlflow.set_tracking_uri(uri)\nmlflow.create_experiment(name)",
    "desc": "Настройка tracking server / создание эксперимента.",
    "tags": [
      "mlflow"
    ],
    "ex": "mlflow.set_tracking_uri('http://localhost:5000')\nmlflow.create_experiment('my_exp')"
  },
  {
    "lib": "dvc",
    "name": "dvc init",
    "lvl": "beginner",
    "syntax": "dvc init",
    "desc": "Инициализировать DVC в проекте.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc init"
  },
  {
    "lib": "dvc",
    "name": "dvc add",
    "lvl": "beginner",
    "syntax": "dvc add <path>",
    "desc": "Отслеживать файл/директорию под DVC.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc add data/raw/dataset.csv"
  },
  {
    "lib": "dvc",
    "name": "dvc push",
    "lvl": "beginner",
    "syntax": "dvc push",
    "desc": "Отправить данные в remote storage.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc push"
  },
  {
    "lib": "dvc",
    "name": "dvc pull",
    "lvl": "beginner",
    "syntax": "dvc pull",
    "desc": "Загрузить данные из remote storage.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc pull"
  },
  {
    "lib": "dvc",
    "name": "dvc repro",
    "lvl": "intermediate",
    "syntax": "dvc repro",
    "desc": "Воспроизвести пайплайн (dvc.yaml).",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc repro"
  },
  {
    "lib": "dvc",
    "name": "dvc run",
    "lvl": "intermediate",
    "syntax": "dvc run -n <stage> -d <deps> -o <outs> <command>",
    "desc": "Создать stage пайплайна.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc run -n prepare -d data/raw -o data/clean python clean.py"
  },
  {
    "lib": "dvc",
    "name": "dvc dag",
    "lvl": "beginner",
    "syntax": "dvc dag",
    "desc": "Визуализировать граф пайплайна.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc dag"
  },
  {
    "lib": "dvc",
    "name": "dvc metrics show / diff",
    "lvl": "intermediate",
    "syntax": "dvc metrics show; dvc metrics diff",
    "desc": "Показать метрики / сравнить с предыдущими.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc metrics show\n$ dvc metrics diff"
  },
  {
    "lib": "dvc",
    "name": "dvc params diff",
    "lvl": "intermediate",
    "syntax": "dvc params diff",
    "desc": "Сравнить параметры между коммитами.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc params diff HEAD~1"
  },
  {
    "lib": "dvc",
    "name": "dvc plots show / dvc.yaml",
    "lvl": "intermediate",
    "syntax": "dvc plots show; # dvc.yaml структура",
    "desc": "Графики метрик; конфигурация пайплайна в YAML.",
    "tags": [
      "dvc"
    ],
    "ex": "$ dvc plots show\n# dvc.yaml: stages, metrics, params, plots"
  },
  {
    "lib": "kubeflow",
    "name": "kfp.Client()",
    "lvl": "beginner",
    "syntax": "kfp.Client(host=None)",
    "desc": "Клиент Kubeflow Pipelines.",
    "tags": [
      "kfp"
    ],
    "ex": "client = kfp.Client()"
  },
  {
    "lib": "kubeflow",
    "name": "@dsl.component",
    "lvl": "intermediate",
    "syntax": "@dsl.component\ndef my_component(param: int) -> int:",
    "desc": "Определить компонент конвейера.",
    "tags": [
      "kfp"
    ],
    "ex": "@dsl.component\ndef add(a: int, b: int) -> int:\n    return a + b"
  },
  {
    "lib": "kubeflow",
    "name": "@dsl.pipeline",
    "lvl": "intermediate",
    "syntax": "@dsl.pipeline(name='...')\ndef my_pipeline():",
    "desc": "Определить конвейер из компонентов.",
    "tags": [
      "kfp"
    ],
    "ex": "@dsl.pipeline(name='my-pipeline')\ndef pipeline(msg: str):\n    task = component(msg=msg)"
  },
  {
    "lib": "kubeflow",
    "name": "@dsl.container_component",
    "lvl": "advanced",
    "syntax": "@dsl.container_component\ndef my_comp(): return dsl.ContainerSpec(...)",
    "desc": "Компонент из Docker-контейнера.",
    "tags": [
      "kfp"
    ],
    "ex": "@dsl.container_component\ndef train():\n    return dsl.ContainerSpec(image='python:3.11', command=['train.py'])"
  },
  {
    "lib": "kubeflow",
    "name": "client.create_run_from_pipeline_func()",
    "lvl": "beginner",
    "syntax": "client.create_run_from_pipeline_func(pipeline_func, arguments={})",
    "desc": "Запустить конвейер из функции.",
    "tags": [
      "kfp"
    ],
    "ex": "run = client.create_run_from_pipeline_func(pipeline, arguments={'msg':'hello'})"
  },
  {
    "lib": "kubeflow",
    "name": "kfp.compiler.Compiler()",
    "lvl": "intermediate",
    "syntax": "Compiler().compile(pipeline_func, package_path)",
    "desc": "Скомпилировать конвейер в YAML.",
    "tags": [
      "kfp"
    ],
    "ex": "Compiler().compile(pipeline, 'pipeline.yaml')"
  },
  {
    "lib": "kubeflow",
    "name": "OutputPath / InputPath",
    "lvl": "intermediate",
    "syntax": "OutputPath(type); InputPath(type)",
    "desc": "Типы для передачи файлов между компонентами.",
    "tags": [
      "kfp"
    ],
    "ex": "def comp(dataset: InputPath('Dataset'), model: OutputPath('Model')):"
  },
  {
    "lib": "kubeflow",
    "name": "dsl.Model / dsl.Artifact",
    "lvl": "intermediate",
    "syntax": "dsl.Model(name='...'); dsl.Artifact(name='...')",
    "desc": "Типы для передачи моделей и артефактов.",
    "tags": [
      "kfp"
    ],
    "ex": "def train(data: Input[Dataset], model: Output[Model]): ..."
  },
  {
    "lib": "airflow",
    "name": "DAG",
    "lvl": "intermediate",
    "syntax": "DAG(dag_id, start_date, schedule, catchup=False)",
    "desc": "Определение DAG - направленного ациклического графа задач.",
    "tags": [
      "airflow"
    ],
    "ex": "dag = DAG('my_dag', start_date=datetime(2024,1,1), schedule='@daily')"
  },
  {
    "lib": "airflow",
    "name": "@task",
    "lvl": "beginner",
    "syntax": "@task\ndef my_task(): ...",
    "desc": "Декоратор для определения задачи (TaskFlow API).",
    "tags": [
      "airflow"
    ],
    "ex": "@task\ndef extract():\n    return pd.read_csv('data.csv')"
  },
  {
    "lib": "airflow",
    "name": "PythonOperator",
    "lvl": "intermediate",
    "syntax": "PythonOperator(task_id, python_callable, op_args, op_kwargs)",
    "desc": "Выполнить Python-функцию как задачу Airflow.",
    "tags": [
      "airflow"
    ],
    "ex": "PythonOperator(task_id='train', python_callable=train_model, dag=dag)"
  },
  {
    "lib": "airflow",
    "name": "BashOperator",
    "lvl": "beginner",
    "syntax": "BashOperator(task_id, bash_command)",
    "desc": "Выполнить bash-команду.",
    "tags": [
      "airflow"
    ],
    "ex": "BashOperator(task_id='echo', bash_command='echo hello')"
  },
  {
    "lib": "airflow",
    "name": "BranchPythonOperator",
    "lvl": "intermediate",
    "syntax": "BranchPythonOperator(task_id, python_callable)",
    "desc": "Ветвление: вернуть task_id следующей задачи.",
    "tags": [
      "airflow"
    ],
    "ex": "BranchPythonOperator(task_id='branch', python_callable=decide_path)"
  },
  {
    "lib": "airflow",
    "name": "DummyOperator",
    "lvl": "beginner",
    "syntax": "DummyOperator(task_id)",
    "desc": "Пустая задача (заглушка).",
    "tags": [
      "airflow"
    ],
    "ex": "DummyOperator(task_id='start')"
  },
  {
    "lib": "airflow",
    "name": "EmailOperator",
    "lvl": "beginner",
    "syntax": "EmailOperator(task_id, to, subject, html_content)",
    "desc": "Отправить email.",
    "tags": [
      "airflow"
    ],
    "ex": "EmailOperator(task_id='alert', to='user@example.com', subject='Alert')"
  },
  {
    "lib": "airflow",
    "name": "PostgresOperator / MySqlOperator",
    "lvl": "intermediate",
    "syntax": "PostgresOperator(task_id, sql, postgres_conn_id)",
    "desc": "Выполнить SQL-запрос в БД.",
    "tags": [
      "airflow"
    ],
    "ex": "PostgresOperator(task_id='query', sql='SELECT COUNT(*) FROM users', postgres_conn_id='pg_default')"
  },
  {
    "lib": "airflow",
    "name": "S3Hook",
    "lvl": "intermediate",
    "syntax": "S3Hook(aws_conn_id).list_keys(bucket_name, prefix)",
    "desc": "Работа с AWS S3.",
    "tags": [
      "airflow"
    ],
    "ex": "hook = S3Hook(aws_conn_id='aws_default')\nfiles = hook.list_keys('my-bucket', prefix='data/')"
  },
  {
    "lib": "airflow",
    "name": "Variable / XCom",
    "lvl": "beginner",
    "syntax": "Variable.get(key); task_instance.xcom_push(key, value); .xcom_pull(task_ids)",
    "desc": "Переменные Airflow; обмен данными между задачами.",
    "tags": [
      "airflow"
    ],
    "ex": "val = Variable.get('api_key')\nti.xcom_push(key='result', value=result)\nprev = ti.xcom_pull(task_ids='extract')"
  },
  {
    "lib": "airflow",
    "name": "@dag / TaskGroup",
    "lvl": "intermediate",
    "syntax": "@dag(schedule=None, start_date=...); TaskGroup(group_id)",
    "desc": "Декоратор DAG; группировка задач.",
    "tags": [
      "airflow"
    ],
    "ex": "@dag(schedule='@daily', start_date=datetime(2024,1,1))\ndef my_dag():\n    task1() >> task2()"
  },
  {
    "lib": "prefect",
    "name": "@flow",
    "lvl": "intermediate",
    "syntax": "@flow(name=None, log_prints=True)\ndef my_flow(): ...",
    "desc": "Определить Flow (конвейер задач).",
    "tags": [
      "prefect"
    ],
    "ex": "@flow\ndef my_flow():\n    result = my_task.submit(data)"
  },
  {
    "lib": "prefect",
    "name": "@task",
    "lvl": "beginner",
    "syntax": "@task(retries=3, retry_delay_seconds=10)\ndef my_task(): ...",
    "desc": "Определить задачу с авто-повтором.",
    "tags": [
      "prefect"
    ],
    "ex": "@task(retries=3)\ndef fetch_data():\n    return requests.get(url).json()"
  },
  {
    "lib": "prefect",
    "name": "flow.serve()",
    "lvl": "intermediate",
    "syntax": "flow.serve(name, interval=None, cron=None)",
    "desc": "Запустить flow как сервис.",
    "tags": [
      "prefect"
    ],
    "ex": "my_flow.serve(name='daily-etl', cron='0 6 * * *')"
  },
  {
    "lib": "prefect",
    "name": "flow.deploy()",
    "lvl": "intermediate",
    "syntax": "flow.deploy(name, work_pool_name, image)",
    "desc": "Деплой flow в Prefect Cloud/Server.",
    "tags": [
      "prefect"
    ],
    "ex": "my_flow.deploy(name='prod-pipeline', work_pool_name='default', image='my-image')"
  },
  {
    "lib": "prefect",
    "name": "task.with_options()",
    "lvl": "intermediate",
    "syntax": "task.with_options(retries=5, tags=['critical'])",
    "desc": "Переопределить параметры задачи при вызове.",
    "tags": [
      "prefect"
    ],
    "ex": "my_task.with_options(retries=5)(data)"
  },
  {
    "lib": "prefect",
    "name": "prefect.task_runners",
    "lvl": "intermediate",
    "syntax": "prefect.task_runners.DaskTaskRunner()",
    "desc": "Параллельное выполнение задач через Dask.",
    "tags": [
      "prefect"
    ],
    "ex": "@flow(task_runner=DaskTaskRunner())\ndef parallel_flow(): ..."
  },
  {
    "lib": "prefect",
    "name": "get_run_logger()",
    "lvl": "beginner",
    "syntax": "get_run_logger()",
    "desc": "Логгер с контекстом текущего run.",
    "tags": [
      "prefect"
    ],
    "ex": "logger = get_run_logger()\nlogger.info('Processing...')"
  },
  {
    "lib": "prefect",
    "name": "prefect.blocks / prefect.variables",
    "lvl": "intermediate",
    "syntax": "prefect.blocks; prefect.variables",
    "desc": "Управление секретами/конфигурацией: блоки и переменные.",
    "tags": [
      "prefect"
    ],
    "ex": "from prefect import variables\ndb_url = variables.get('db_url')"
  },
  {
    "lib": "optuna",
    "name": "optuna.create_study()",
    "lvl": "intermediate",
    "syntax": "optuna.create_study(direction='minimize', sampler=None, pruner=None)",
    "desc": "Создать исследование для подбора гиперпараметров.",
    "tags": [
      "optuna"
    ],
    "ex": "study = optuna.create_study(direction='maximize')\nstudy.optimize(objective, n_trials=100)"
  },
  {
    "lib": "optuna",
    "name": "study.optimize()",
    "lvl": "beginner",
    "syntax": "study.optimize(objective, n_trials=100, timeout=None)",
    "desc": "Запустить оптимизацию.",
    "tags": [
      "optuna"
    ],
    "ex": "study.optimize(lambda trial: objective(trial), n_trials=50)"
  },
  {
    "lib": "optuna",
    "name": "trial.suggest_float / suggest_int / suggest_categorical",
    "lvl": "beginner",
    "syntax": "trial.suggest_float(name, low, high); suggest_int; suggest_categorical",
    "desc": "Предложить значение гиперпараметра.",
    "tags": [
      "optuna"
    ],
    "ex": "lr = trial.suggest_float('lr', 1e-5, 1e-1, log=True)\nn_layers = trial.suggest_int('n_layers', 1, 5)\nopt = trial.suggest_categorical('optimizer', ['adam','sgd'])"
  },
  {
    "lib": "optuna",
    "name": "plot_optimization_history()",
    "lvl": "beginner",
    "syntax": "optuna.visualization.plot_optimization_history(study)",
    "desc": "График истории оптимизации.",
    "tags": [
      "optuna",
      "визуализация"
    ],
    "ex": "optuna.visualization.plot_optimization_history(study)"
  },
  {
    "lib": "optuna",
    "name": "plot_param_importances()",
    "lvl": "intermediate",
    "syntax": "optuna.visualization.plot_param_importances(study)",
    "desc": "График важности гиперпараметров.",
    "tags": [
      "optuna",
      "визуализация"
    ],
    "ex": "optuna.visualization.plot_param_importances(study)"
  },
  {
    "lib": "optuna",
    "name": "plot_slice()",
    "lvl": "intermediate",
    "syntax": "optuna.visualization.plot_slice(study)",
    "desc": "Срезы пространства параметров.",
    "tags": [
      "optuna",
      "визуализация"
    ],
    "ex": "optuna.visualization.plot_slice(study)"
  },
  {
    "lib": "optuna",
    "name": "plot_contour()",
    "lvl": "intermediate",
    "syntax": "optuna.visualization.plot_contour(study)",
    "desc": "Контурный график двух параметров.",
    "tags": [
      "optuna",
      "визуализация"
    ],
    "ex": "optuna.visualization.plot_contour(study, params=['lr','n_layers'])"
  },
  {
    "lib": "optuna",
    "name": "study.best_params / best_value / best_trial",
    "lvl": "beginner",
    "syntax": "study.best_params; study.best_value; study.best_trial",
    "desc": "Лучшие параметры, значение и trial.",
    "tags": [
      "optuna"
    ],
    "ex": "print(study.best_params, study.best_value)"
  },
  {
    "lib": "optuna",
    "name": "TPESampler / MedianPruner",
    "lvl": "intermediate",
    "syntax": "optuna.samplers.TPESampler(); optuna.pruners.MedianPruner()",
    "desc": "Семплер TPE (Bayesian); прунер по медиане.",
    "tags": [
      "optuna"
    ],
    "ex": "sampler = TPESampler(seed=42)\nstudy = optuna.create_study(sampler=sampler, pruner=MedianPruner())"
  },
  {
    "lib": "shap",
    "name": "shap.Explainer()",
    "lvl": "intermediate",
    "syntax": "shap.Explainer(model, masker=None)",
    "desc": "Создать объяснитель SHAP для модели.",
    "tags": [
      "shap",
      "объяснение"
    ],
    "ex": "explainer = shap.Explainer(model, X_train)\nshap_values = explainer(X_test)"
  },
  {
    "lib": "shap",
    "name": "shap_values.values / base_values / data",
    "lvl": "intermediate",
    "syntax": "sv.values; sv.base_values; sv.data",
    "desc": "SHAP-значения, baseline, исходные данные.",
    "tags": [
      "shap"
    ],
    "ex": "vals = shap_values.values\nbaseline = shap_values.base_values"
  },
  {
    "lib": "shap",
    "name": "shap.summary_plot()",
    "lvl": "beginner",
    "syntax": "shap.summary_plot(shap_values, features, feature_names)",
    "desc": "Сводный график важности признаков.",
    "tags": [
      "shap",
      "визуализация"
    ],
    "ex": "shap.summary_plot(shap_values, X_test, feature_names=names)"
  },
  {
    "lib": "shap",
    "name": "shap.waterfall_plot()",
    "lvl": "intermediate",
    "syntax": "shap.waterfall_plot(shap.Explanation(values, base_values, data))",
    "desc": "Waterfall для одного предсказания.",
    "tags": [
      "shap",
      "визуализация"
    ],
    "ex": "shap.waterfall_plot(shap_values[0])"
  },
  {
    "lib": "shap",
    "name": "shap.bar_plot()",
    "lvl": "beginner",
    "syntax": "shap.bar_plot(shap_values)",
    "desc": "Столбчатая важность признаков.",
    "tags": [
      "shap",
      "визуализация"
    ],
    "ex": "shap.bar_plot(shap_values)"
  },
  {
    "lib": "shap",
    "name": "shap.dependence_plot()",
    "lvl": "intermediate",
    "syntax": "shap.dependence_plot(feature, shap_values, features)",
    "desc": "Зависимость SHAP от одного признака.",
    "tags": [
      "shap",
      "визуализация"
    ],
    "ex": "shap.dependence_plot('age', shap_values.values, X_test)"
  },
  {
    "lib": "shap",
    "name": "shap.force_plot()",
    "lvl": "intermediate",
    "syntax": "shap.force_plot(base_value, shap_values, features)",
    "desc": "Force plot для одного предсказания.",
    "tags": [
      "shap",
      "визуализация"
    ],
    "ex": "shap.force_plot(explainer.expected_value, shap_values[0], X_test[0])"
  },
  {
    "lib": "shap",
    "name": "shap.decision_plot / plots.heatmap / plots.beeswarm",
    "lvl": "intermediate",
    "syntax": "shap.decision_plot; shap.plots.heatmap; shap.plots.beeswarm",
    "desc": "Decision plot, heatmap, beeswarm для SHAP.",
    "tags": [
      "shap",
      "визуализация"
    ],
    "ex": "shap.plots.heatmap(shap_values)\nshap.plots.beeswarm(shap_values)"
  },
  {
    "lib": "fastapi",
    "name": "FastAPI()",
    "lvl": "beginner",
    "syntax": "FastAPI(title='...', version='1.0')",
    "desc": "Создание приложения FastAPI.",
    "tags": [
      "fastapi"
    ],
    "ex": "app = FastAPI(title='My API')\n@app.get('/')\ndef root(): return {'msg':'Hello'}"
  },
  {
    "lib": "fastapi",
    "name": "@app.get/post/put/delete",
    "lvl": "beginner",
    "syntax": "@app.get('/path')\n@app.post('/path')\n@app.put('/path')\n@app.delete('/path')",
    "desc": "HTTP-методы для эндпоинтов.",
    "tags": [
      "fastapi"
    ],
    "ex": "@app.get('/items/{item_id}')\ndef get_item(item_id: int): return {'id':item_id}"
  },
  {
    "lib": "fastapi",
    "name": "Query / Path / Body / Header / Cookie",
    "lvl": "beginner",
    "syntax": "Query(default, description='...'); Path(...); Body(...)",
    "desc": "Валидация параметров запроса.",
    "tags": [
      "fastapi"
    ],
    "ex": "@app.get('/items')\ndef list_items(q: str = Query(None, max_length=50), page: int = 1): ..."
  },
  {
    "lib": "fastapi",
    "name": "Depends()",
    "lvl": "intermediate",
    "syntax": "Depends(dependency)",
    "desc": "Внедрение зависимостей (аутентификация, БД).",
    "tags": [
      "fastapi"
    ],
    "ex": "def get_db(): ...\n@app.get('/data')\ndef read(db=Depends(get_db)): ..."
  },
  {
    "lib": "fastapi",
    "name": "HTTPException()",
    "lvl": "beginner",
    "syntax": "HTTPException(status_code=404, detail='Not found')",
    "desc": "Выбросить HTTP-ошибку.",
    "tags": [
      "fastapi"
    ],
    "ex": "if not item:\n    raise HTTPException(status_code=404, detail='Item not found')"
  },
  {
    "lib": "fastapi",
    "name": "BackgroundTasks",
    "lvl": "intermediate",
    "syntax": "BackgroundTasks()",
    "desc": "Фоновые задачи после ответа.",
    "tags": [
      "fastapi"
    ],
    "ex": "@app.post('/send')\ndef send(background_tasks: BackgroundTasks):\n    background_tasks.add_task(send_email, email)"
  },
  {
    "lib": "fastapi",
    "name": "File / UploadFile / Form",
    "lvl": "beginner",
    "syntax": "File(...); UploadFile(...); Form(...)",
    "desc": "Загрузка файлов и форм.",
    "tags": [
      "fastapi"
    ],
    "ex": "@app.post('/upload')\ndef upload(file: UploadFile = File(...)): ..."
  },
  {
    "lib": "fastapi",
    "name": "CORSMiddleware",
    "lvl": "beginner",
    "syntax": "CORSMiddleware(app, allow_origins=['*'])",
    "desc": "Настройка CORS для frontend.",
    "tags": [
      "fastapi"
    ],
    "ex": "app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'])"
  },
  {
    "lib": "fastapi",
    "name": "APIRouter / app.include_router",
    "lvl": "intermediate",
    "syntax": "APIRouter(prefix='/api', tags=['items'])\napp.include_router(router)",
    "desc": "Модульная организация роутов.",
    "tags": [
      "fastapi"
    ],
    "ex": "router = APIRouter(prefix='/users')\n@router.get('/{id}')\ndef get_user(id: int): ...\napp.include_router(router)"
  },
  {
    "lib": "fastapi",
    "name": "pydantic BaseModel / Field / uvicorn.run",
    "lvl": "beginner",
    "syntax": "class Item(BaseModel): name: str; price: float = Field(gt=0)\nuvicorn.run(app)",
    "desc": "Схемы данных Pydantic; запуск сервера.",
    "tags": [
      "fastapi"
    ],
    "ex": "class Item(BaseModel):\n    name: str\n    price: float = Field(gt=0)\n    tags: list[str] = []\nuvicorn.run(app, host='0.0.0.0', port=8000)"
  },
  {
    "lib": "great_expectations",
    "name": "gx.get_context()",
    "lvl": "beginner",
    "syntax": "context = gx.get_context()",
    "desc": "Получить контекст GX (FileDataContext).",
    "tags": [
      "gx"
    ],
    "ex": "context = gx.get_context()"
  },
  {
    "lib": "great_expectations",
    "name": "context.sources.add_pandas()",
    "lvl": "beginner",
    "syntax": "context.sources.add_pandas(name)",
    "desc": "Добавить pandas источник данных.",
    "tags": [
      "gx"
    ],
    "ex": "source = context.sources.add_pandas('my_source')"
  },
  {
    "lib": "great_expectations",
    "name": "expect_column_values_to_not_be_null",
    "lvl": "beginner",
    "syntax": "validator.expect_column_values_to_not_be_null('col')",
    "desc": "Проверить отсутствие NULL в колонке.",
    "tags": [
      "gx",
      "expectation"
    ],
    "ex": "validator.expect_column_values_to_not_be_null('user_id')"
  },
  {
    "lib": "great_expectations",
    "name": "expect_column_values_to_be_between",
    "lvl": "beginner",
    "syntax": "validator.expect_column_values_to_be_between('col', min_value, max_value)",
    "desc": "Проверить значения в диапазоне.",
    "tags": [
      "gx",
      "expectation"
    ],
    "ex": "validator.expect_column_values_to_be_between('age', 0, 120)"
  },
  {
    "lib": "great_expectations",
    "name": "expect_column_values_to_be_in_set",
    "lvl": "beginner",
    "syntax": "validator.expect_column_values_to_be_in_set('col', values_set)",
    "desc": "Проверить значения из заданного набора.",
    "tags": [
      "gx",
      "expectation"
    ],
    "ex": "validator.expect_column_values_to_be_in_set('country', ['US','UK','CA'])"
  },
  {
    "lib": "great_expectations",
    "name": "expect_column_values_to_be_unique",
    "lvl": "beginner",
    "syntax": "validator.expect_column_values_to_be_unique('col')",
    "desc": "Проверить уникальность значений.",
    "tags": [
      "gx",
      "expectation"
    ],
    "ex": "validator.expect_column_values_to_be_unique('id')"
  },
  {
    "lib": "great_expectations",
    "name": "expect_table_row_count_to_be_between",
    "lvl": "beginner",
    "syntax": "validator.expect_table_row_count_to_be_between(min_value, max_value)",
    "desc": "Проверить количество строк в диапазоне.",
    "tags": [
      "gx",
      "expectation"
    ],
    "ex": "validator.expect_table_row_count_to_be_between(1000, 10000)"
  },
  {
    "lib": "great_expectations",
    "name": "expect_column_mean_to_be_between",
    "lvl": "beginner",
    "syntax": "validator.expect_column_mean_to_be_between('col', min_value, max_value)",
    "desc": "Проверить среднее в диапазоне.",
    "tags": [
      "gx",
      "expectation"
    ],
    "ex": "validator.expect_column_mean_to_be_between('price', 0, 1000)"
  },
  {
    "lib": "great_expectations",
    "name": "context.build_data_docs()",
    "lvl": "beginner",
    "syntax": "context.build_data_docs()",
    "desc": "Собрать HTML-отчёты Data Docs.",
    "tags": [
      "gx"
    ],
    "ex": "context.build_data_docs()\ncontext.open_data_docs()"
  },
  {
    "lib": "bentoml",
    "name": "bentoml.Service()",
    "lvl": "intermediate",
    "syntax": "bentoml.Service(name, runners=[])",
    "desc": "Создать BentoML сервис.",
    "tags": [
      "bentoml"
    ],
    "ex": "svc = bentoml.Service('iris-classifier', runners=[runner])"
  },
  {
    "lib": "bentoml",
    "name": "@svc.api()",
    "lvl": "intermediate",
    "syntax": "@svc.api(input=JSON(), output=JSON())\ndef predict(input_data): ...",
    "desc": "Определить API эндпоинт сервиса.",
    "tags": [
      "bentoml"
    ],
    "ex": "@svc.api(input=JSON(), output=JSON())\ndef classify(input_data):\n    return runner.run(input_data)"
  },
  {
    "lib": "bentoml",
    "name": "bentoml.sklearn.save_model()",
    "lvl": "beginner",
    "syntax": "bentoml.sklearn.save_model(name, model)",
    "desc": "Сохранить sklearn модель в Model Store.",
    "tags": [
      "bentoml"
    ],
    "ex": "bentoml.sklearn.save_model('iris_clf', model)"
  },
  {
    "lib": "bentoml",
    "name": "bentoml.models.get()",
    "lvl": "beginner",
    "syntax": "bentoml.models.get(tag)",
    "desc": "Загрузить модель из Model Store.",
    "tags": [
      "bentoml"
    ],
    "ex": "model_ref = bentoml.models.get('iris_clf:latest')"
  },
  {
    "lib": "bentoml",
    "name": "bentoml.build()",
    "lvl": "intermediate",
    "syntax": "bentoml.build(service, models, ...)",
    "desc": "Собрать Bento из сервиса.",
    "tags": [
      "bentoml"
    ],
    "ex": "bento = bentoml.build(svc, models=[model_ref], name='iris-classifier')"
  },
  {
    "lib": "bentoml",
    "name": "bentoml.containerize()",
    "lvl": "intermediate",
    "syntax": "bentoml.containerize(bento_tag)",
    "desc": "Создать Docker-образ из bento.",
    "tags": [
      "bentoml"
    ],
    "ex": "bentoml.containerize('iris-classifier:latest')"
  },
  {
    "lib": "bentoml",
    "name": "svc.to_runner()",
    "lvl": "intermediate",
    "syntax": "runner = svc.to_runner()",
    "desc": "Создать Runner из сервиса.",
    "tags": [
      "bentoml"
    ],
    "ex": "runner = svc.to_runner()"
  },
  {
    "lib": "bentoml",
    "name": "bentoml.client.Client",
    "lvl": "beginner",
    "syntax": "bentoml.client.Client.from_url(url)",
    "desc": "Клиент для вызова BentoML сервиса.",
    "tags": [
      "bentoml"
    ],
    "ex": "client = bentoml.client.Client.from_url('http://localhost:3000')\nclient.classify(input_data)"
  },
  {
    "lib": "plotly",
    "name": "px.scatter()",
    "lvl": "beginner",
    "syntax": "px.scatter(df, x, y, color=None, size=None, hover_data=None, title=None)",
    "desc": "Интерактивный scatter-plot с зумом и подсказками при наведении.",
    "tags": [
      "визуализация",
      "интерактив",
      "scatter"
    ],
    "ex": "px.scatter(df, x=\"age\", y=\"income\", color=\"city\", size=\"pop\", hover_data=[\"name\"])"
  },
  {
    "lib": "plotly",
    "name": "px.line()",
    "lvl": "beginner",
    "syntax": "px.line(df, x, y, color=None, line_dash=None, markers=False)",
    "desc": "Интерактивный линейный график. Авто-форматирование дат на оси X.",
    "tags": [
      "визуализация",
      "линейный"
    ],
    "ex": "px.line(df, x=\"date\", y=\"sales\", color=\"product\")"
  },
  {
    "lib": "plotly",
    "name": "px.bar()",
    "lvl": "beginner",
    "syntax": "px.bar(df, x, y, color=None, barmode=\"group\")",
    "desc": "Интерактивная столбчатая диаграмма. barmode: group, stack, overlay.",
    "tags": [
      "визуализация",
      "столбцы"
    ],
    "ex": "px.bar(df, x=\"month\", y=\"revenue\", color=\"product\", barmode=\"stack\")"
  },
  {
    "lib": "plotly",
    "name": "px.histogram()",
    "lvl": "beginner",
    "syntax": "px.histogram(df, x, color=None, nbins=None, marginal=None)",
    "desc": "Интерактивная гистограмма. marginal: box, violin, rug по краям.",
    "tags": [
      "визуализация",
      "гистограмма"
    ],
    "ex": "px.histogram(df, x=\"age\", color=\"gender\", marginal=\"box\")"
  },
  {
    "lib": "plotly",
    "name": "px.box()",
    "lvl": "beginner",
    "syntax": "px.box(df, x, y, color=None, points=\"outliers\")",
    "desc": "Интерактивный boxplot. points=\"all\" показывает все точки.",
    "tags": [
      "визуализация",
      "статистика"
    ],
    "ex": "px.box(df, x=\"category\", y=\"value\", color=\"group\")"
  },
  {
    "lib": "plotly",
    "name": "px.violin()",
    "lvl": "beginner",
    "syntax": "px.violin(df, x, y, color=None, box=True)",
    "desc": "Скрипичная диаграмма. box=True добавляет мини-boxplot внутри.",
    "tags": [
      "визуализация",
      "распределение"
    ],
    "ex": "px.violin(df, x=\"cat\", y=\"val\", color=\"group\", box=True)"
  },
  {
    "lib": "plotly",
    "name": "px.scatter_3d()",
    "lvl": "intermediate",
    "syntax": "px.scatter_3d(df, x, y, z, color=None, size=None)",
    "desc": "3D scatter-plot. Вращение, зум — интерактивно.",
    "tags": [
      "визуализация",
      "3d"
    ],
    "ex": "px.scatter_3d(df, x=\"x\", y=\"y\", z=\"z\", color=\"label\")"
  },
  {
    "lib": "plotly",
    "name": "px.scatter_matrix()",
    "lvl": "intermediate",
    "syntax": "px.scatter_matrix(df, dimensions=None, color=None)",
    "desc": "Матрица scatter-графиков (аналог seaborn pairplot).",
    "tags": [
      "визуализация",
      "матрица"
    ],
    "ex": "px.scatter_matrix(df, dimensions=[\"a\",\"b\",\"c\"], color=\"target\")"
  },
  {
    "lib": "plotly",
    "name": "px.imshow()",
    "lvl": "beginner",
    "syntax": "px.imshow(img, text_auto=\".2f\", color_continuous_scale=\"RdBu_r\")",
    "desc": "Тепловая карта как изображение. Идеально для матриц.",
    "tags": [
      "визуализация",
      "тепловая"
    ],
    "ex": "px.imshow(df.corr(), text_auto=\".2f\")"
  },
  {
    "lib": "plotly",
    "name": "px.density_heatmap()",
    "lvl": "beginner",
    "syntax": "px.density_heatmap(df, x, y, nbinsx=None, nbinsy=None)",
    "desc": "2D тепловая карта плотности (2D-гистограмма).",
    "tags": [
      "визуализация",
      "плотность"
    ],
    "ex": "px.density_heatmap(df, x=\"age\", y=\"income\", nbinsx=20)"
  },
  {
    "lib": "plotly",
    "name": "px.pie()",
    "lvl": "beginner",
    "syntax": "px.pie(df, values, names, hole=0)",
    "desc": "Круговая/кольцевая диаграмма. hole>0 = кольцо (donut).",
    "tags": [
      "визуализация",
      "pie"
    ],
    "ex": "px.pie(df, values=\"sales\", names=\"product\", hole=0.3)"
  },
  {
    "lib": "plotly",
    "name": "px.area()",
    "lvl": "beginner",
    "syntax": "px.area(df, x, y, color=None, line_group=None)",
    "desc": "Диаграмма с областями (залитый линейный график).",
    "tags": [
      "визуализация",
      "area"
    ],
    "ex": "px.area(df, x=\"date\", y=\"value\", color=\"category\")"
  },
  {
    "lib": "plotly",
    "name": "px.strip()",
    "lvl": "beginner",
    "syntax": "px.strip(df, x, y, color=None)",
    "desc": "Точечная диаграмма по категориям (jitter plot).",
    "tags": [
      "визуализация",
      "категории"
    ],
    "ex": "px.strip(df, x=\"cat\", y=\"val\", color=\"group\")"
  },
  {
    "lib": "plotly",
    "name": "px.sunburst()",
    "lvl": "intermediate",
    "syntax": "px.sunburst(df, path, values, color=None)",
    "desc": "Иерархическая солнечная диаграмма.",
    "tags": [
      "визуализация",
      "иерархия"
    ],
    "ex": "px.sunburst(df, path=[\"region\",\"city\"], values=\"population\")"
  },
  {
    "lib": "plotly",
    "name": "px.treemap()",
    "lvl": "intermediate",
    "syntax": "px.treemap(df, path, values, color=None)",
    "desc": "Иерархическая прямоугольная диаграмма (treemap).",
    "tags": [
      "визуализация",
      "иерархия"
    ],
    "ex": "px.treemap(df, path=[\"continent\",\"country\"], values=\"pop\")"
  },
  {
    "lib": "plotly",
    "name": "px.choropleth()",
    "lvl": "intermediate",
    "syntax": "px.choropleth(df, locations, locationmode, color)",
    "desc": "Хороплет-карта (географическая тепловая карта).",
    "tags": [
      "визуализация",
      "гео"
    ],
    "ex": "px.choropleth(df, locations=\"iso_alpha\", locationmode=\"ISO-3\", color=\"gdp\")"
  },
  {
    "lib": "plotly",
    "name": "px.scatter_mapbox()",
    "lvl": "intermediate",
    "syntax": "px.scatter_mapbox(df, lat, lon, color=None, size=None, zoom=3)",
    "desc": "Scatter-plot на интерактивной карте Mapbox.",
    "tags": [
      "визуализация",
      "гео"
    ],
    "ex": "px.scatter_mapbox(df, lat=\"lat\", lon=\"lon\", color=\"type\", zoom=5)"
  },
  {
    "lib": "plotly",
    "name": "px.line_3d()",
    "lvl": "intermediate",
    "syntax": "px.line_3d(df, x, y, z, color=None)",
    "desc": "3D линейный график (траектория в пространстве).",
    "tags": [
      "визуализация",
      "3d"
    ],
    "ex": "px.line_3d(df, x=\"x\", y=\"y\", z=\"z\", color=\"path_id\")"
  },
  {
    "lib": "plotly",
    "name": "go.Figure()",
    "lvl": "advanced",
    "syntax": "go.Figure(data, layout)",
    "desc": "Низкоуровневый API Plotly для кастомных графиков.",
    "tags": [
      "визуализация",
      "кастом"
    ],
    "ex": "fig = go.Figure(data=go.Scatter(x=x,y=y), layout=go.Layout(title=\"Plot\"))"
  },
  {
    "lib": "plotly",
    "name": "fig.update_layout()",
    "lvl": "beginner",
    "syntax": "fig.update_layout(title=None, xaxis_title=None, yaxis_title=None, template=None)",
    "desc": "Обновить макет: заголовки, тема, легенда, размер.",
    "tags": [
      "оформление"
    ],
    "ex": "fig.update_layout(title=\"Chart\", template=\"plotly_dark\")"
  },
  {
    "lib": "plotly",
    "name": "fig.write_html() / fig.show()",
    "lvl": "beginner",
    "syntax": "fig.write_html(path)\nfig.show()",
    "desc": "Сохранить как HTML-файл или показать в браузере.",
    "tags": [
      "сохранение"
    ],
    "ex": "fig.write_html(\"chart.html\")\nfig.show()"
  }
];
