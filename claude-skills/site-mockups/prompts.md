# Промты экранов

Промт = голова экрана + хвост стиля. Хвост одинаковый во всех генерациях подряд, слово в слово.

## Рабочий хвост — нейтральная оболочка

```
paper white and cool stone grey interface, strictly achromatic neutral palette, no beige, no cream, no warm tint, elegant light weight serif display headline mixed with small clean sans labels and widely letterspaced uppercase micro labels, rectangular cards with 24px rounded corners, product photos lit by a crisp directional spotlight from the upper left with a long soft shadow inside the cards, graphite black accent used only on one pill button and small circular arrow buttons, pill shaped filter chips, thin hairline dividers, near black text on white for high contrast, professional UI design mockup, sharp focus, 4k
```

Префикс к голове почти всегда нужен: `flat full width web page layout without any device frame, `

## Головы экранов

Десктоп 1344×768, мобайл 832×1216.

**Хиро**
```
Full desktop web page screenshot of a high-end home decor store homepage, wide hero card with a big spotlit product photo and an elegant serif headline beside it, a row of pill filter chips below, top navigation bar with logo, search and cart icons,
```

**Свотчи стилей**
```
Full desktop web page screenshot of a homepage section showing a row of large circular material swatches with style name labels under each in small letterspaced uppercase, circular arrow buttons at the sides, section heading in elegant serif,
```

**Каталог с фильтрами**
```
Full desktop web page screenshot of a furniture catalog page, top navigation bar, narrow left sidebar with checkbox filters for room and style, main area with two rows of three large rounded product cards, each a spotlit product photo with name and price under it,
```

**Карточка товара**
```
Full desktop web page screenshot of a home decor store product page for a ceramic vase, large spotlit vase photo in a rounded card on the left, small circular color swatches under it, on the right the vase name in elegant serif, price, short description and a graphite pill add to cart button, at the bottom a row of four related decor product cards showing vases bowls and candle holders, no clothing, no people,
```

**Категория в едином стиле (тип 2)**
```
Full desktop web page screenshot of a category page for vases in a home decor store, breadcrumb and page title at the top, under the title a row of style tabs with the first tab active, then a grid of three by two rounded cards each showing one spotlit ceramic vase with its name and price, no people, no clothing,
```

**Комнатный сет (тип 1)**
```
Full desktop web page screenshot of a room-set landing page, wide atmospheric interior photo in a rounded card at the top, grid of individual product cards below, a row of round color palette swatches,
```

**Мини-сет (тип 3)**
```
Full desktop web page screenshot of a capsule collection landing page, top navigation bar, wide rounded card with a styled flat lay photo of three decor products, serif collection title, below a row of three product cards with photo name and price, a short paragraph of story text,
```

**Страница стиля**
```
Full desktop web page screenshot of a style landing page in a home decor store, wide banner with the style name in large serif and a short description, below three room interior cards, then a row of mini collection cards showing groups of vases and ceramics, then a grid of individual decor products, no clothing, no people,
```

**Корзина**
```
Full desktop web page screenshot of a shopping cart page, three product line items each with a rounded square thumbnail, name, quantity stepper and price, order summary card on the right with subtotal, shipping, total and a graphite pill checkout button,
```

**Чекаут**
```
Full desktop web page screenshot of a checkout page, left column with labelled outlined input fields for email, address, city and postal code and radio buttons for payment method, right column with an order summary card and a graphite pill place order button,
```

**404**
```
Full desktop web page screenshot of a 404 error page of an online store, big serif 404 headline, one small spotlit object photo in a rounded card, a graphite pill button back to home, top navigation bar,
```

**Мобильная главная**
```
Mobile phone screen mockup of a home decor store homepage app screen, hero card with a spotlit product photo and elegant serif headline, pill filter chips, product cards, bottom navigation bar,
```

**Мобильная карточка**
```
Mobile phone screen mockup of a product page screen, top bar with back arrow and cart icon, large rounded card with a spotlit vase photo, serif product name and price, row of small circular color swatches, wide graphite pill add to cart button at the bottom,
```

## Демо коллекции

Одна страница коллекции в разных акцентах — доказательство, что оболочка держит любой стиль. Голова общая, между ней и хвостом вставляется описание акцента:

```
the only colored elements are the pill button, the active chip and the arrow buttons, all in <цвет акцента>, product photo backdrops in <цвет подложки>, everything else neutral white and grey,
```

Проверено на dark charcoal green grey (Neo-Japandi), antique brass gold brown (Heritage), deep emerald green (Color Drenching).

## Хвосты вариантов характера

Для этапа выбора ДНК — один и тот же хиро в разных характерах.

**Editorial / галерейный**
```
editorial art gallery aesthetic, oversized very high contrast serif display typography filling half the screen, asymmetric editorial grid with wide asymmetric margins, deep black on bone white, thin rule lines and small numbered captions, sharp square corners, underlined text links instead of buttons, dramatic scale contrast between huge headline and tiny caption text, museum catalogue feel, crisp high contrast, professional UI design mockup, sharp focus, 4k
```

**Тёплый архив**
```
warm archival heritage aesthetic, cream paper background with subtle paper grain texture, high contrast old style serif with elegant ligatures, deep ink brown text, hairline ornamental rules and catalogue numbering, letterpress printed catalogue turned into a website, generous margins, small caps labels, crisp, professional UI design mockup, sharp focus, 4k
```

**Тёмная галерея**
```
dark luxury gallery aesthetic, near black charcoal interface, product photography spotlit and glowing against the dark background, warm bronze accent color, thin widely letterspaced uppercase sans typography, delicate hairline dividers, cinematic contrast, professional UI design mockup, sharp focus, 4k
```

**Швейцарская сетка**
```
swiss neo grid design aesthetic, visible grid lines and boxed cells, oversized tightly tracked uppercase grotesk headline, very strong typographic hierarchy, one saturated rust orange accent on off white, square corners, contrast of thick bars and hairline rules, poster like structure, bold graphic energy, professional UI design mockup, sharp focus, 4k
```

Тёмная галерея выигрывает по премиальности, но чёрная подложка топит светлые стили. Рабочее решение — перенести её приёмы (направленный свет, длинная тень, сериф, разрежённый капслок) на светлую базу.

## Что стабильно ломается

| Симптом | Причина | Лечение |
|---|---|---|
| Фотография пустой освещённой стены вместо экрана | атмосферные слова в хвосте | свет описывать только внутри карточки |
| Макбук или монитор вокруг страницы | нет запрета на device frame | префикс `flat full width web page layout without any device frame` |
| Монитор/окно браузера появились после «усиления» запрета | в префикс дописали `no browser window, no address bar, no laptop, no monitor` — при CFG 1.0 Flux не читает отрицания, эти слова работают как **позитивные** и притягивают именно те объекты | префикс держать ровно таким, как выше, ни слова больше; проверено — «усиление» испортило 4 экрана из 5 |
| Страница нарисована издалека, как экран в интерьере | `zoomed out so the whole page fits` в голове | не просить отдалить кадр, вместо этого сокращать число рядов в голове |
| Каталог с одеждой и людьми | нет предметной привязки | `home decor`, `vases`, `ceramics`, `no clothing, no people` |
| Пустая бежевая простыня вместо корзины и чекаута | голова слишком абстрактная | перечислять поля и строки поимённо |
| Мелкие нечитаемые карточки | много рядов в голове | просить две строки по три карточки, не «сетку товаров» |
