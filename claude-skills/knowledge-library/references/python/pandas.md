# pandas — выжимка для таблиц отбора товаров

Источник: справочник https://py-ds-ml.ru/ (раздел pandas, 60 команд; взяты ~25 нужных нам),
плюс поправки под **pandas 3.0.6**, который стоит на этом компьютере (openpyxl 3.1.5 — для xlsx).
Все примеры ниже проверены запуском.

**pandas** — библиотека «Excel внутри Python». Таблица называется **DataFrame** (`df`),
один столбец — **Series**. Всё, что делаем руками в Excel (фильтр, сортировка, сводная, ВПР),
здесь делается одной строкой и повторяется без ошибок.

```python
import pandas as pd
```

## 1. Чтение и запись

```python
df = pd.read_excel(r'C:\cj\yubka_kletka_otbor60.xlsx', sheet_name='Отбор',
                   dtype={'offerId': str})        # ID — ВСЕГДА строкой!
sheets = pd.read_excel('file.xlsx', sheet_name=None)  # все листы сразу: {имя: df}
df = pd.read_csv(r'C:\cj\postavshchiki_baza.tsv', sep='\t', dtype=str, encoding='utf-8')

df.to_excel('out.xlsx', index=False, sheet_name='Итог')   # index=False — без лишнего столбца 0,1,2…
df.to_csv('out.csv', index=False, encoding='utf-8-sig')   # -sig — чтобы Excel не показал кракозябры

# несколько листов в один файл
with pd.ExcelWriter('itog.xlsx', engine='openpyxl') as w:
    df.to_excel(w, sheet_name='Отбор', index=False)
    svod.to_excel(w, sheet_name='Свод')
```

Грабли:
- **ID как строка.** offerId 1688, ИНН, артикулы: без `dtype=str` pandas сделает число, срежет
  ведущие нули или покажет `1.08127e+12`. То же правило, что для ИНН в check_rekvizity.py.
- `to_excel` **перезаписывает файл целиком** — другие листы и форматирование пропадут.
  Дописать лист в существующий файл: `pd.ExcelWriter(path, mode='a', engine='openpyxl', if_sheet_exists='replace')`.
  Если в файле важны цвета/ширины/картинки (как в нашей главной таблице) — править через openpyxl, а не pandas.
- Файл открыт в Excel → `PermissionError`. Закрыть Excel.

## 2. Посмотреть, что внутри

```python
df.head(10)            # первые 10 строк
df.shape               # (строк, столбцов)
df.columns.tolist()    # названия столбцов
df.info()              # типы и сколько пустых
df.describe()          # мин/макс/среднее по числовым столбцам
df['поставщик'].value_counts()   # сколько товаров у каждого поставщика
```

## 3. Фильтры (как «Фильтр» в Excel)

```python
# одно условие
df[df['выкуп_%'] >= 40]

# несколько: & = И, | = ИЛИ, каждое условие в скобках
отбор = df[(df['выкуп_%'] >= 40) & (df['цена_¥'].between(25, 65)) & (df['продажи'] > 0)]

# то же самое короче — query (имена столбцов с пробелами/символами — в `обратных кавычках`)
отбор = df.query('`выкуп_%` >= 40 and 25 <= `цена_¥` <= 65 and продажи > 0')

df[df['название'].str.contains('клетк', case=False, na=False)]   # текст содержит
df[df['поставщик'].isin(['新女人花', '笑彩'])]                      # значение из списка
df[~df['offerId'].isin(уже_есть)]                                   # ~ = НЕ
df[df['цена_¥'].isna()]                                             # пустые ячейки

df.loc[df['выкуп_%'] >= 40, ['offerId', 'цена_¥']]   # строки по условию + нужные столбцы
```

## 4. Новые столбцы, сортировка, чистка

```python
df['цена_$'] = (df['цена_¥'] / 7.1).round(2)
df['маржа_%'] = ((df['цена_продажи_$'] - df['себест_$']) / df['цена_продажи_$'] * 100).round(1)
df['статус'] = df['выкуп_%'].map(lambda x: '✅' if x >= 40 else '❌')

df = df.sort_values(['выкуп_%', 'продажи'], ascending=[False, False])
df.nlargest(10, 'продажи')                     # топ-10
df = df.rename(columns={'price': 'цена_¥'})
df = df.drop(columns=['лишний'])
df = df.drop_duplicates(subset='offerId')      # убрать дубли по ID
df['цена_¥'] = pd.to_numeric(df['цена_¥'], errors='coerce')   # «25 ¥», «—» → число или пусто
df['цена_¥'] = df['цена_¥'].fillna(0)
df['название'] = df['название'].str.strip()

df = df[['offerId', 'название', 'цена_¥', 'выкуп_%']]   # задать ПОРЯДОК столбцов (её порядок из itog!)
```

## 5. groupby — итоги по группам

```python
df.groupby('поставщик')['продажи'].sum()

svod = df.groupby('поставщик').agg(
    товаров=('offerId', 'count'),
    средняя_цена=('цена_¥', 'mean'),
    лучший_выкуп=('выкуп_%', 'max'),
).round(1).sort_values('товаров', ascending=False)

# доля/среднее группы рядом с каждой строкой (без схлопывания)
df['средняя_цена_поставщика'] = df.groupby('поставщик')['цена_¥'].transform('mean')
```

## 6. merge — «ВПР» / сверка двух таблиц

```python
# добавить к отбору данные поставщиков по названию магазина
итог = pd.merge(отбор, база_поставщиков, on='поставщик', how='left')

# разные имена ключей
итог = pd.merge(pdd, отбор, left_on='offer_id', right_on='offerId', how='inner')

# сверка «что есть в одной, но нет в другой» (сверка PDD↔1688 по ID)
m = pd.merge(pdd, отбор, on='offerId', how='outer', indicator=True)
только_pdd   = m[m['_merge'] == 'left_only']
в_обеих      = m[m['_merge'] == 'both']

pd.concat([df1, df2], ignore_index=True)   # склеить таблицы одна под другой
```

`how`: `inner` — только совпавшие; `left` — все строки левой + что нашлось; `outer` — все из обеих.
Ключи должны быть одного типа (оба `str`), иначе ничего не совпадёт — снова `dtype=str`.

## 7. Сводные таблицы

```python
pd.pivot_table(df, values='продажи', index='поставщик', columns='стиль',
               aggfunc='sum', fill_value=0, margins=True, margins_name='Итого')

pd.crosstab(df['стиль'], df['статус'])     # сколько товаров каждого стиля ✅/❌
```

## 8. Даты и ряды (радар трендов)

```python
df['дата'] = pd.to_datetime(df['дата'], format='%Y-%m-%d')
df['месяц'] = df['дата'].dt.to_period('M')
по_месяцам = df.set_index('дата').resample('ME')['интерес'].mean()   # 'ME' (не 'M') в pandas 3
df['сглаж_4нед'] = df['интерес'].rolling(4, min_periods=1).mean()
df['рост_к_году_%'] = (df['интерес'] / df['интерес'].shift(52) - 1) * 100   # недельные данные
```

## pandas 3.0: чего больше нет (встречается в старых примерах, в т.ч. на py-ds-ml.ru)

| Старое | Теперь |
|---|---|
| `df.fillna(method='ffill')` | `df.ffill()` |
| `resample('M')`, `'Q'`, `'Y'` | `'ME'`, `'QE'`, `'YE'` |
| `df['a'][df['b'] > 0] = 1` (цепочкой) | `df.loc[df['b'] > 0, 'a'] = 1` |
| `inplace=True` | `df = df.method(...)` — надёжнее |
| `df.append(other)` | `pd.concat([df, other])` |
| текст хранится как `object` | теперь тип `str` — на код обычно не влияет |
