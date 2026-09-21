---
name: shopify-admin
description: Правка магазина ARTMELLIO на Shopify через Admin API вместо админки — товары (названия, описания, теги, фото), категории и цвета, наличие и доставка, коллекции, главная страница, страницы и меню, футер, ленты вкладок в каталоге темы. Используй, когда просят "переименуй товары", "почисти описания", "разложи по категориям", "проставь цвета", "почему всё Sold out", "добавь зону доставки", "собери главную", "сделай страницы и футер", "настрой чекаут", "поправь фото товара". Триггеры "shopify", "артмеллио", "artmellio", "каталог магазина", "главная страница", "футер", "чекаут", "теги товаров", "sold out", "доставка", "admin api".
---

# Магазин ARTMELLIO: правки через Admin API

Админка `kmfmxn-r4` открывается через профиль Dolphin **836461485 «Декор»**, но за прокси
Cloudflare регулярно требует капчу и автоматизация на ней встаёт. Поэтому всё, что можно,
делается запросами Admin API, а браузер остаётся только для того, что API не умеет
(настройки магазина, приложение Search & Discovery).

## Доступ

Client ID и Client secret приложения — `C:\Users\User\Desktop\shopy api.txt`.
`scripts/shop_api.py` берёт по ним токен (client credentials, живёт 24 часа, кэш в
`C:\Users\User\dolphin_anty\shopify_token.json`) и шлёт GraphQL на
`/admin/api/2026-07/graphql.json`.

```python
from shop_api import gql
gql("{ shop { name currencyCode } }")
```

Права приложения выдаются в **Dev Dashboard** (dev.shopify.com/dashboard), не в админке:
Versions → Access scopes → Release → Home → Install app и подтвердить новые разрешения.
Проверить, что реально выдано:

```python
gql("{ currentAppInstallation { accessScopes { handle } } }")
```

**Запрашивать сразу весь набор прав одним списком** — пользователя раздражает
перевыпускать версию по одному scope. И **выдавать список целиком**: при релизе новый
набор заменяет старый, а не дополняет его. Сейчас выдано 57 прав (24.08.2026): товары,
инвентарь, локации, публикации, тема, контент, файлы, метаобъекты, переводы, рынки,
скидки, заказы, клиенты, доставка, правовые политики, брендинг чекаута, аккаунт
Shopify Payments.

После релиза новых прав **удалить кэш токена** `C:\Users\User\dolphin_anty\shopify_token.json`,
иначе `gql` ходит со старым токеном и правами.

## Скрипты

| Скрипт | Что делает |
|---|---|
| `shop_api.py` | токен + `gql(query, variables)`; импортируется остальными |
| `allow_oversell.py` | всем вариантам `inventoryPolicy: CONTINUE` (продажа при нуле) |
| `add_zones.py` | зоны доставки в профиль: UK, EU, бесплатный тариф |
| `fix_bathset.py` | раскладывает наборы по предметным `cat:`-тегам из значений вариантов |
| `detect_colors3.py` | вытаскивает цвет из спецификаций/вариантов/названия → `colors.json` |
| `gen_bodies.py` | собирает чистые описания вместо выгрузки поставщика → `bodies.json` |
| `upload_image.py` | `python upload_image.py <product_id> <файл.jpg> "alt"` — загрузить фото и поставить первым |
| `squarify.py` | приводит главные фото к квадрату, направление обрезки задаётся вручную по кадру |
| `upsert.py` | `python upsert.py templates/index.json …` — залить файлы темы через API (надёжнее CLI) |
| `listfiles.py` / `readfile.py` | что реально лежит в теме и содержимое конкретного файла |
| `build_home.py` | собирает главную: announcement bar, hero, ленты коллекций, о бренде, FAQ, подписка |
| `make_pages.py` | страницы About us, FAQ, Payment policy с текстами |
| `make_menus.py` | меню шапки, Information и Legal для футера |
| `upload_files.py` | `python upload_files.py <папка> hero` — картинки из папки в Files магазина |
| `find_keys.py` | `python find_keys.py "credit card"` — поиск ключей текстов чекаута |
| `checkout_texts.py` | правка текстов чекаута (упирается в ограничение, см. ниже) |
| `audit_store.py` | снимок магазина: страницы, меню, коллекции, товары, тема |
| `dump_theme.py` | выгружает файлы темы в `dump_*` рядом со скриптом (`readfile.py` рвёт длинный вывод) |
| `make_track_page.py` | страница отслеживания заказа |
| `add_track_menu.py` | пункт «Track order» в меню шапки и Information |
| `make_bundle_discounts.py` | лестница автоматических скидок на набор |
| `make_policies.py` | доставка, возврат, условия — тексты политик |
| `fix_contact.py` | страница контакта: название и текст |
| `add_faq_discount.py` | раздел про скидку на набор в FAQ |
| `remove_ships_from.py` | снимает у товаров опцию «Ships From» |
| `audit_catalog.py` | проверка каталога: названия, описания, дубли, теги, фото, статус |

Скрипты пишут результат в JSON рядом с собой, запись в магазин — отдельным проходом
(`tagsAdd` / `tagsRemove` / `productUpdate`), чтобы можно было сверить до записи.

## Устройство каталога: теги вместо коллекций

У товаров четыре семейства тегов: `cat:` предмет, `style:` интерьерный стиль,
`color:` цвет, `mat:` материал, плюс `room:` и `set:`.

Каталог фильтруется **встроенной tag-фильтрацией Shopify**, без приложений:
`/collections/all/cat-tray`, несколько тегов через `+`:
`/collections/all/style-neo-japandi+cat-tray`. Работает всегда, в отличие от фасетов.

Секция темы `sections/collection-category-tabs.liquid` рисует ленту вкладок по одному
семейству тегов, подключена трижды — `style-tabs`, `category-tabs`, `color-tabs`. Лежали
они только в `templates/collection.json`, который **ни одна коллекция не использует**,
поэтому вкладок не было нигде; 24.08.2026 перенесены в `collection.category.json`.
Ссылки вкладок строятся от текущей коллекции (`/collections/neo-japandi/style-…`), а не от
`/collections/all/` — искать в HTML по `cat-tabs__link`, иначе кажется, что их нет. Настройка `tag_prefix` задаёт семейство,
`tag_labels` — человеческие названия и порядок (`cat:tray = Trays`). Вкладка сохраняет
выбор в других лентах, собирая ссылку из текущих `current_tags`.

Класс `section` секции намеренно не присвоен: тема даёт `.section + .section` отступ
9.6rem (`decor-shell.css`), и три ленты подряд разносило на треть экрана.

## Диагностика «весь каталог Sold out»

Порядок проверки — от витрины к причине:

1. `curl https://artmellio.com/products.json` → `available` у вариантов.
2. Admin API: `availableForSale`, `inventoryQuantity`, `inventoryPolicy`.
   Если API говорит «доступен», а витрина «нет» — дело **не в остатках**.
3. Проверить по странам: `/products/<handle>.js?country=US` против `?country=GB`.
   Разный ответ = **нет зоны доставки** для этой страны.
4. `deliveryProfiles` → `locationGroupZones`.

Так и было: единственная зона USA, витрина открывается как UK, поэтому все 131 товара
считались недоступными. Лечится `add_zones.py`. Зона со страной, у которой есть регионы
(GB, IT, ES), не сохраняется без `includeAllProvinces: true`.

Остатки лежат на локации `dsers-fulfillment-service`, локация магазина пустая — это норма
для дропшиппинга, продажу обеспечивает `inventoryPolicy: CONTINUE`.

## Избранное (сердечки)

Своя реализация без приложений: список `handle`'ов в `localStorage` покупателя
(`artmellio:wishlist`).

- `snippets/wishlist-button.liquid` — сердечко, принимает `product` и `style` (`card` или
  `product`); `assets/wishlist.js` — хранилище и custom element (весь доступ к localStorage
  в try/catch: в приватном окне бросает); `assets/wishlist.css`.
- В сетке врезано в `snippets/card-product.liquid` внутрь `.card__inner`, на карточке
  товара — блок `wishlist` секции `main-product`.
- Страница `/pages/wishlist` («Saved pieces»): `sections/wishlist-page.liquid` +
  `templates/page.wishlist.json`, товары подтягиваются через `/products/<handle>.js`.
  Ссылка «Saved» в главном меню.

Две грабли, обе ловились на живой витрине:

1. **`z-index` сердечка обязателен.** В Dawn ссылка карточки растянута псевдоэлементом на
   всю площадь, поэтому клик уходил на страницу товара вместо сохранения.
2. **Низ карточек в ряду разъезжался**, когда одно название в строку, а другое в две:
   цена и «Remove» вставали на разной высоте. Карточка сделана flex-колонкой,
   `.wishlist-card__title` растягивается (`flex: 1 1 auto`), цена и кнопка собраны в
   `.wishlist-card__foot` и прижаты вниз. То же правило пригодится любой сетке карточек.
3. **Секция страницы стартует раньше `wishlist.js`** (тот подключён с `defer`), и список
   выходил пустым. Лечится ожиданием `window.ArtmellioWishlist` в `connectedCallback`.
   Цену форматировать с явной локалью `en-GB` — иначе локаль покупателя даёт «75,00 £».

## Состояние каталога

Проверка 24.08.2026 (131 товар): длинных названий нет, коротких описаний нет, дублей нет,
все главные фото квадратные, все ACTIVE. Единственный товар без тегов — Vintage Wood
Bluetooth Speaker, проставлены `cat:decor`, `style:neo-japandi`, `mat:wood`, `room:living`.

**Незакрытое: значения опции Color у 12 товаров.** Там не цвета, а мусор поставщика —
«Lotion bottle-A», «Cotton swab jar-B», «Jazz White-D», «6 hooks Set-of 2-A» (136 значений).
Суффиксы `-A…-E` различают подварианты, поэтому **просто срезать их нельзя** — получатся
дубли, которые Shopify не примет. Чинить по одному товару, глядя на фото вариантов.

## Тексты товаров

Данные приезжают из Dsers сырыми: названия по 100–170 символов и описание, целиком
состоящее из блока SPECIFICATIONS с полями `Brand Name`, `Origin: Mainland China`,
`High-concerned chemical`. Всё это выбрасывается.

**Названия пишутся руками, по одному.** Шаблонный генератор из тегов проверен и
отвергнут: беспроводная колонка превращалась в «Brown Decor Object», душевая система —
в «Organiser». Ориентир: 20–40 символов, различать похожие наборы по сорту камня
(Volakos, Emperador Dark, Nero Marquina, Arabescato Corchia, Tree Black, White Onyx).
`handle` не трогать — иначе умрут ссылки.

**Описания** собирает `gen_bodies.py`: абзац про предмет (два варианта на категорию,
выбор по id, чтобы соседние карточки не читались одинаково), строка про натуральный
камень, список фактов (материал, отделка, цвет, размер, число вариантов) и уход.
Из старого описания переносятся только `Material`, `Finish Type`, `Size`.

## Фото

У 121 товара из 131 главное фото квадратное; неквадратное ломает высоту карточки в сетке
(тема стоит на `image_ratio: adapt`). Перед обрезкой **посмотреть кадр**: у товаров
AliExpress предмет часто стоит в нижней части кадра, и центральная обрезка срезает его —
резать надо снизу. Загрузка: `upload_image.py`, старое фото остаётся в галерее вторым.

## Заливка файлов темы: только через API

`shopify theme push` **может отрапортовать успех и не залить файл**. Так пропал
`templates/index.json`, и главная отдавала 404 при зелёном выводе CLI. Поэтому:

1. заливать `upsert.py` (`themeFilesUpsert`), а не CLI;
2. после заливки проверять не сообщение, а страницу: `curl -o /dev/null -w "%{http_code}"`;
3. если страница легла — `listfiles.py` покажет, какого файла в теме нет.

Значения `range`-настроек в JSON шаблона обязаны попадать в шаг ползунка: `padding: 6`
при `step: 4` роняет пуш с «Setting must be a step in the range».

## Главная страница

Собрана `build_home.py`. Announcement bar из шапки убран 24.08.2026 и заменён своей секцией
`announcement-strip` **под слайдшоу** — пользователь хотела ту же плашку, но ниже фото.
Штатную `sections/announcement-bar.liquid` в шаблон главной не поставить: у неё
`enabled_on: {groups: ["header"]}`. Своя секция — тонкая полоса с волосяными линиями,
капс 1.3rem, сообщения сменяются раз в 5 с (custom element, уважает
`prefers-reduced-motion`). Проверять ротацию скриншотами бесполезно — цикл 10 с и кадры
попадают в одну фазу; смотреть `.is-active` через JS с паузами.

Порядок секций:
image-banner → две ленты `featured-collection` → `collection-list` со стилями →
`image-with-text` о бренде → `collapsible-content` FAQ → `newsletter`.

- Подписка не должна дублироваться: секция на главной плюс `newsletter_enable` в
  `footer-group.json` дают две формы подряд. Оставлять что-то одно.
- `collection-list` без обложек коллекций рисует пустые плашки. Обложку ставит
  `collectionUpdate` с `image: {src}` — берётся главное фото первого товара коллекции.
- Картинка секции задаётся как `shopify://shop_images/<имя файла>`; имена смотреть
  запросом `files(query:"filename:banner*")`.

### Слайдшоу вместо статичного баннера

Секция `slideshow`, блоки `slide`, автопрокрутка — `auto_rotate: true` и
`change_slides_speed` (range 3–9, **шаг 2**: значение 6 пуш не примет, 5 примет).
`slide_height: adapt_image` держит родные пропорции кадра, `image_overlay_opacity: 30`
даёт тексту читаться. Каждый слайд — свой заголовок и кнопка в близкую коллекцию.

Картинки заливает `upload_files.py`. Два момента, оба ловились на практике:

- **Имена файлов переименовывать в латиницу** (`hero-1.png` …): кириллица ломает
  ссылку `shopify://shop_images/<имя>`, по которой тема ищет картинку.
- **Хранилище Shopify рвёт TLS на первой попытке** (`SSLEOFError` на
  `shopify-staged-uploads.storage.googleapis.com`). В скрипте пять повторов с паузой —
  без них загрузка падает примерно через раз.

Проверять автопрокрутку надо не по разметке, а по факту: снять кадр, подождать
двойной интервал, снять второй и сравнить `.slider-counter--current`.

## Страницы, меню, футер

Страницы создаёт `pageCreate` (`make_pages.py`), меню — `menuCreate` / `menuUpdate`
(`make_menus.py`), блоки футера — правка `sections/footer-group.json`: `brand_information`
плюс два `link_list` с `menu: information` и `menu: footer`.

Ссылки на политики (`/policies/shipping-policy` и прочие) отдают 404, пока сами политики
не заполнены.

### Политики

Заливаются `make_policies.py` через `shopPolicyUpdate(shopPolicy: {type, body})`, типы
`SHIPPING_POLICY`, `REFUND_POLICY`, `TERMS_OF_SERVICE`, `PRIVACY_POLICY`. Права
`read_legal_policies` / `write_legal_policies` выданы 24.08.2026. Проверять не мутацией,
а витриной: `/policies/<handle>` должен отдавать 200.

Тексты держать согласованными со страницей FAQ (отправка за 2 рабочих дня, доставка
7–14 рабочих дней UK/EU и 10–18 US, возврат 14 дней, повреждение по фото за 48 часов) и
с лестницей скидок. Контакт во всех политиках — `store@artmellio.com` (`shop.contactEmail`;
`shop.email` — личный `artdeco78@outlook.com`, его в тексты не ставить). Названия компании и налоговых номеров у Claude нет — **не выдумывать**, спрашивать.
**Страну и город в текстах магазина не упоминать** — прямое указание пользователя
24.08.2026; из Terms фразу «The store is operated from Poland» убрали.

## Что не поддаётся API

- **Фильтры Search & Discovery.** Приложение установлено, фильтры Price и Availability
  активны (метки переведены с польского), но витрине Shopify отдаёт только Availability.
  Фасет цены не появляется ни на одном рынке. Причина не найдена; ленты вкладок
  выше — рабочая замена.
- **Чекаут целиком.** Брендинг (логотип, цвет кнопок) — `checkoutBrandingUpsert` отвечает
  «shop must be on a Plus plan or a Development store plan» **даже с выданным**
  `write_checkout_branding_settings` (проверено 24.08.2026, профиль
  `gid://shopify/CheckoutProfile/7877427580`). Упор в тариф, а не в права: больше не
  пытаться, отправлять пользователя в Settings → Checkout → Customize. Тексты чекаута нашлись
  в переводах (`translatableResources(resourceType: ONLINE_STORE_THEME)`, ключи
  `shopify.checkout.*`, искать через `find_keys.py`), но `translationsRegister` для них
  отказывает: «Locale cannot be the same as the shop's primary locale» — основной язык
  правится только в админке. Claude находит ключи и выдаёт формулировки, вписывает
  пользователь. **Результат при этом проверяется по API**: `translatableContent` отдаёт
  актуальные значения, так что после правок видно, что применилось.

  Рабочий маршрут (проверен 24.08.2026): `admin.shopify.com/store/kmfmxn-r4/themes/
  188705603964/language` → «Больше представлений» → **Checkout & system**. В General этих
  строк нет, и поиск ищет только внутри текущего представления — отсюда «ничего не
  находится». Искать надо **полным ключом целиком** (`shopify.checkout.shipping.
  invalid_shipping_method_summary`), тогда выдача — одна строка; по английской фразе или
  по префиксу выпадают сотни полей, и пользователь бросает листать.

  Инструкции давать по одной строке в формате «Ищем: <ключ> / Вставляем: <текст>».
  Сокращённый список «→ соответственно то, сё, третье» пользователь не разбирает.
- Настройки магазина: домены, платежи, налоги — только руками в админке. Платежи на
  24.08.2026 не подключены (`shop.paymentSettings.supportedDigitalWallets` пуст, на витрине
  ноль иконок оплаты) — магазин не может принимать деньги, это блокирует запуск.
- **SEO магазина**: описание в Settings → Preferences пустое, мутации для него нет. Оттуда
  же берётся og:description, который сейчас показывает просто «ARTMELLIO».
- Базовая валюта магазина PLN, витрина показывает GBP через рынок UK (primary).

## Отслеживание заказа

Страница `/pages/track-order` сделана без платного приложения: `sections/track-order.liquid`
(поле трек-номера, JS открывает `https://t.17track.net/en#nums=<номер>` в новой вкладке),
шаблон `templates/page.track-order.json`, страница с `templateSuffix: track-order`.
Пункт «Track order» добавлен в `main-menu` и `information` (`add_track_menu.py`).
`menuUpdate` требует передать **весь** список пунктов целиком, с их `id`, иначе меню
затирается; у пунктов с `resourceId` передавать его, а не `url`.

## Корзина: набор и лестница скидок

`cart_type: drawer` включается ключом в `current` файла `config/settings_data.json`
(в схеме дефолт `notification`).

В `snippets/cart-drawer.liquid` и `sections/main-cart-footer.liquid` вставлены два блока:

- `snippets/cart-savings-bar.liquid` — прогресс до следующего процента. Пороги захардкожены
  по валютам (GBP/EUR/PLN/USD), потому что `cart.total_price` приходит в валюте витрины,
  а скидки заведены в PLN. Курс на 24.08.2026: 1 USD = 3.606 PLN, 1 GBP = 1.333 USD.
- `sections/cart-upsell.liquid` + `assets/cart-upsell.js` — «Complete the set».
  Секция рендерится **только** через `/recommendations/products?section_id=cart-upsell&
  product_id=<id>&intent=related&limit=6`; custom element грузит её для первого товара
  корзины и добавляет выбранное через `cart/add.js` с `sections=cart-drawer,cart-icon-bubble`.

Скидки (`make_bundle_discounts.py`, `discountAutomaticBasicCreate`): 4 автоматические
скидки заказа, пороги 85/120/155/200 USD в PLN, проценты 5/7/8/10, все с
`combinesWith.orderDiscounts: false` — Shopify применяет одну, самую выгодную.
`customerSelection` в `DiscountAutomaticBasicInput` **не существует** (только у кодовых).

Завязать процент на цену именно дополнительного товара нативные скидки не умеют — нужен
Shopify Function (приложение с деплоем через Partner-аккаунт). Сделана замена: лестница
по сумме заказа; пользователь о подмене предупреждён, решение по Function не принято.

Правило скидки продублировано человеческим текстом в разделе «Set discount» страницы FAQ
(`add_faq_discount.py`) — пороги там в GBP. При изменении скидок править **три** места:
скидки в админке, `cart-savings-bar.liquid`, FAQ.

## Отступы

Пользователь дважды просила сократить воздух. `.section + .section` в `decor-shell.css`
уменьшен с 9.6/5.6rem до 4.8/3.2rem, а `padding_top` / `padding_bottom` секций главной
срезаны до 24. Дальше уменьшать не стоит — тема рассчитана на воздух, слипнется.

## Мелочи, которые ловились

- `template.name == 'index'` в `layout/theme.liquid` не сработал, `request.page_type == 'index'` —
  сработал. Запасной meta description главной сидит там же и уступает `page_description`,
  как только описание впишут в Settings → Preferences. og:description по-прежнему берётся
  из настроек магазина и показывает просто «ARTMELLIO».
- `pageUpdate` не принимает `handle` вместе с `title` молча — handle остаётся прежним,
  и это то, что нужно: страницу «Kontakt» переименовали в «Contact», ссылка `/pages/contact`
  выжила.
- Проверять правки витрины `grep`-ом по одной строке ненадёжно: Shopify переносит длинные
  атрибуты, и `<meta name="description"` уезжает на вторую строку. Искать regex с `re.S`
  или смотреть кусок HTML после `</title>`.
- Вывод скриптов в bash-пайпе рвётся на кириллице (cp1251). Ставить `PYTHONIOENCODING=utf-8`.

## Шаблоны коллекций: их четыре

`templates/collection.json` **не используется ни одной коллекцией**. У каждой задан
`templateSuffix`: стилевые (neo-japandi, warm-minimalism, dark-academia и остальные) —
`category`, bathroom-neo-japandi — `room-set`, aroma-ritual — `capsule`. Правки надо вносить
в `collection.category.json` / `collection.room-set.json` / `collection.capsule.json`.
Проверять перед правкой: `{ collections(first:20){ nodes { handle templateSuffix } } }`.

`room-set` и `capsule` используют свою секцию `collection-room-hero` (широкий кадр над
сеткой), а `category` — стандартный `main-collection-banner`, у которого
`show_collection_image` стоял `false`, поэтому у стилевых коллекций баннера не было вовсе.
Включено 24.08.2026, картинка встаёт справа от заголовка.

Обложку коллекции ставит `collectionUpdate` с `image: {src}`. Shopify **сохраняет старое имя
файла** (`sq_0.jpg` осталось `sq_0.jpg`), поэтому проверять подмену надо по размерам
картинки, а не по имени.

## Shop the look

Интерьерный кадр с точками на товарах: `sections/shop-the-look.liquid`,
`assets/shop-the-look.js`, `assets/shop-the-look.css`. Блок `look` = картинка сцены плюс
до четырёх товаров, у каждого координаты `_x` / `_y` в процентах кадра. Точка и карточка
подсвечивают друг друга, кнопка Add кладёт товар через `cart/add.js` с
`sections=cart-drawer,cart-icon-bubble` и открывает корзину — дальше подхватывает лестница
скидок и «Complete the set».

Идея взята из платных тем (Prestige, Impact, Focal, Symmetry — у всех есть shop-the-look
или hot-spots); код свой, чужие темы не ставились. Архив тем:
`Downloads\Платные Темы Shopify На +6000$-20260824T093249Z-1-001.zip`, распаковка
попадает в `__MACOSX`-мусор — файлы `._*` при разборе отбрасывать.

Товары в JSON шаблона задаются **handle'ом**, не gid: `"product_1": "marble-soap-…"`.
Картинка — `shopify://shop_images/hero-1.png`.

Живёт **не на главной**, а в шаблоне `collection.room-set.json` — то есть на странице
коллекции Neo-Japandi Bathroom, сразу под баннером. Так попросила пользователь: точки
уместны там, где лежат сами товары, а не на витрине. На кадре
`banner-bathroom-neo-japandi.jpg` предметы **входят в эту коллекцию**:
мох-рама 11/62, Будда 38/62, травертиновая лампа 63/34, душевая система 95/16. Правило:
точки ставить на сцену, товары которой реально есть в каталоге и собраны в коллекцию.
Координаты подбирались по кадру глазами — скачать картинку и посмотреть, а не угадывать. Проверять секцию тоже глазами: при первом
скриншоте кадр был пуст, потому что `loading: lazy` не догрузил его — прокрутить к секции
и снять заново.

Точки на мобильном отдельным медиа-запросом 1.6rem вместо 2.8rem: на десктопе они в меру,
а на узком экране кадр в разы меньше и точки того же размера закрывали предметы.

**Shopify минифицирует CSS ассетов**, поэтому проверять залитое правило по строке с
пробелами (`max-width: 749px`) бесполезно — на витрине это `max-width:749px`. Искать по
`749px` или смотреть файл в теме через API.

Разбор карточек товара платных тем (`main-product.liquid` → блоки): у Prestige и Impact
`complementary_products`, `feature_with_icon`, `accordion`, `offers`; у Shrine — целый
арсенал дропшиппинга: `estimated_shipping`, `bundle_offer`, `quantity_gifts`, `sticky_atc`,
`sizing_chart`, `shipping_checkpoints`, `icon_with_text`, `payment_badges`. Три первых
пункта уже перенесены (см. «Карточка товара»).

Что осталось взять (по убыванию пользы): липкая панель покупки (`sticky_atc` — особенно
на мобильном), вкладки-аккордеон вместо сплошного описания, `complementary` на карточке,
баннер согласия на cookies (`privacy-banner` у Maestrooo), таблица сравнения сортов камня
(`comparison-table` у Shrine, `feature-chart` у Impact), просмотренные товары,
`timeline` и `press` для страницы бренда.
Не брать: таймеры обратного отсчёта, всплывашки «кто-то только что купил», проверку
возраста, промо-попапы — они ломают позиционирование спокойного дорогого магазина.

## Карточка товара

Была голым Dawn: vendor, title, price, variant_picker, quantity, buy_buttons, description,
share. По разбору платных тем добавлены три блока сразу под кнопкой покупки (24.08.2026):

- **`delivery_estimate`** (`snippets/product-delivery-estimate.liquid`) — «Order today,
  arrives 2–9 September». Liquid не складывает даты: `'now' | date: '%s'` в unix-секунды,
  плюс `86400 × N`, обратно через `date`. Настройки — 9 и 16 дней, текст до и под датами.
- **`bundle_ladder`** (`snippets/product-bundle-ladder.liquid`) — те же четыре порога, что
  у автоматических скидок и полосы в корзине. **Третье место, где прописаны пороги.**
- **иконки-выгоды** — штатный блок Dawn `icon-with-text`, кода не потребовалось: truck /
  return / leaf. Список доступных иконок — в схеме `main-product.liquid`, настройка `icon_1`.

Свои блоки вписываются в `sections/main-product.liquid` двумя правками: ветка `when` рядом
с `{%- when 'icon-with-text' -%}` и запись в `blocks` схемы. Файл 100 КБ — править
скриптом по якорю, а не целиком.

В Dawn 16 уже есть готовые `collapsible_tab`, `complementary`, `custom_liquid`, `popup`,
`rating` — прежде чем писать блок, посмотреть схему секции.

### Опция «Ships From»

У 32 товаров Dsers приносил опцию **Ships From** со значением China Mainland (у двух —
United States), и она показывалась покупателю на карточке. Снята `remove_ships_from.py`
(`productOptionsDelete`, `strategy: POSITION`): у всех было по одному значению, поэтому
варианты не пострадали. Проверять после импорта новых товаров — опция приезжает снова.
Причина та же, что и с политиками: страну и город в текстах магазина не упоминать.

Названия вариантов остаются мусорными («Jazz White-D», «Advanced black-A») — отдельная
незакрытая задача.

## Цветовые схемы

В `settings_data.json` не было ключа `color_schemes`, и редактор темы ругался «Не удалось
отобразить цветовые схемы. Схемы должны быть определены в файлах settings_data и
settings_schema» — цвета в редакторе не правились. В `settings_schema.json` у группы
`color_schemes` **нет** `default`, схемы обязаны лежать в `current`. Прописаны пять схем
(`scheme-1`…`scheme-5`) полями `background`, `background_gradient`, `text`, `button`,
`button_label`, `secondary_button_label`, `shadow` — теми же цветами, что навязывал
пользовательский CSS (фон #232323, текст и кнопки белые), поэтому витрина не изменилась.

После этого хак в `platform_customizations.custom_css`, который перекрывал все схемы одним
набором, стал избыточен — при следующей правке цветов его лучше убрать, иначе схемы в
редакторе будут выглядеть рабочими, а на витрине их перекроет CSS.

## Логотип

Исходник — `C:\Users\User\Desktop\лого главнеое.PNG` (1059×511): белая надпись ARTMELLIO
между двух тонких линий на **непрозрачном** тёплом тёмном фоне (38,34,27), который не
совпадает с фоном сайта (35,35,35) и даёт видимый прямоугольник. Поэтому фон вырезается:
alpha из яркости пикселя (`(lum-45) * 255/185`), цвет заливается чистым белым, поля
обрезаются по `getbbox`.

Готовые файлы лежат в `scripts/`: `logo-artmellio.png` (921×191, прозрачный) и
`favicon-artmellio.png` (512×512). Фавикон — буква A из логотипа на квадрате #232323:
широкий логотип в 32 пикселя не читается. Букву вырезать по профилю пикселей, а не долей
ширины: линии тянутся шире текста, простой кроп берёт их куски. Верхняя линия в исходнике
тусклее нижней (alpha < 40) — при подборе порогов не принимать её за пустую строку.

Заливка — `upload_files.upload(Path(...), имя, alt)`, подключение — ключи `logo`,
`favicon`, `logo_width` (range 50–300, шаг 10; стоит 190 → высота в шапке ~39px) в `current`
файла `config/settings_data.json`. После заливки в шапке пропадает текстовый
`<span class="h2">ARTMELLIO</span>` — по нему и проверять.

Логотип чекаута через API недоступен (тариф), грузится руками в Settings → Checkout.

## Что и где сделано 24.08.2026

Сессия шла по разбору обучающих видео (`Downloads\Record 23.08.2026-*.txt`) плюс разбор
платных тем. Ниже — какое действие какого места магазина касается.

### Витрина, главная страница
| Что сделано | Где лежит |
|---|---|
| Убрана бегущая строка из шапки | `sections/header-group.json`, секция `announcement-bar` удалена |
| Та же плашка возвращена **под фото** | своя секция `announcement-strip`, в `templates/index.json` сразу после `slideshow` |
| Сокращён воздух между секциями (9.6/5.6 → 4.8/3.2rem) и внутренние отступы до 24 | `assets/decor-shell.css`, `templates/index.json` |
| Запасное meta description главной | `layout/theme.liquid`, условие `request.page_type == 'index'` |
| Секция «Shop the look» сначала стояла здесь, потом снята | `templates/index.json` |

### Страницы коллекций
| Что сделано | Где лежит |
|---|---|
| Включён показ обложки коллекции — раньше баннера не было ни у одной стилевой коллекции | `templates/collection.category.json`, `show_collection_image: true` |
| Обложка Neo-Japandi заменена на интерьерный кадр | `collectionUpdate`, файл `banner-bathroom-neo-japandi-v2.jpg` |
| Ленты вкладок (стили, категории, цвета) перенесены в рабочий шаблон — раньше не выводились нигде | `templates/collection.category.json` |
| «Shop this room» — кадр с точками по товарам | `templates/collection.room-set.json`, только Neo-Japandi Bathroom |

### Карточка товара
| Что сделано | Где лежит |
|---|---|
| Срок доставки «Order today, arrives …» | блок `delivery_estimate`, `snippets/product-delivery-estimate.liquid` |
| Лестница скидок на набор | блок `bundle_ladder`, `snippets/product-bundle-ladder.liquid` |
| Три иконки-выгоды | штатный блок Dawn `icon-with-text` |
| Кнопка «Save for later» | блок `wishlist` |
| Убрана опция «Ships From: China Mainland» у 32 товаров | `remove_ships_from.py` |

### Корзина и скидки
| Что сделано | Где лежит |
|---|---|
| Переключена на выдвижную | `config/settings_data.json`, `cart_type: drawer` |
| Полоса прогресса до следующей скидки | `snippets/cart-savings-bar.liquid` |
| «Complete the set» — рекомендации с кнопкой Add | `sections/cart-upsell.liquid`, `assets/cart-upsell.js` |
| Четыре автоматические скидки 5/7/8/10% | `make_bundle_discounts.py` |
| Правило скидки человеческим текстом | страница FAQ, `add_faq_discount.py` |

### Служебные страницы
| Что сделано | Где лежит |
|---|---|
| Отслеживание заказа по трек-номеру | `sections/track-order.liquid`, `/pages/track-order` |
| Избранное (сердечки) | `wishlist-*`, `/pages/wishlist`, пункт «Saved» в меню |
| Политики: доставка, возврат, условия | `make_policies.py` |
| Страница контакта переименована и заполнена | `fix_contact.py` |

### Оформление
| Что сделано | Где лежит |
|---|---|
| Логотип в шапке и фавикон | `logo-artmellio.png`, `favicon-artmellio.png`, ключи `logo` / `favicon` / `logo_width` |
| Определены пять цветовых схем — редактор темы ругался на их отсутствие | `config/settings_data.json` |

### Чекаут
Тексты вписаны пользователем вручную (API их менять не даёт): разделитель
«OR continue with your credit card», «Debit or Credit Card», чекбокс подписки, четыре
строки про доставку. Логотип чекаута загружен через Settings → Checkout.

### Осталось
1. **Платежи не подключены** — магазин не может принять заказ. За пользователем.
2. **Значения опции Color у 12 товаров** — мусор поставщика, чинить по одному, глядя на фото.
3. Описание магазина в Settings → Preferences (SEO и превью ссылок).
4. Из платных тем не взято: липкая кнопка покупки, вкладки-аккордеон в описании,
   баннер cookies, таблица сравнения сортов камня, просмотренные товары.

## Состояние на 24.08.2026

Сделано: каталог, коллекции, главная, страницы, меню, футер, зоны доставки, страница
отслеживания, выдвижная корзина с апселлом и лестницей скидок, четыре политики,
запасной meta description.

Осталось (по разбору обучающих видео в `Downloads\Record 23.08.2026-*.txt`):

1. **Платежи** — не подключены, делает пользователь.
2. **Логотип** — в шапке и фавиконе стоит; в чекауте остаётся загрузить руками.
3. ~~Тексты чекаута~~ — сделано 24.08.2026: разделитель «OR continue with your credit card»,
   «Debit or Credit Card», чекбокс «Email me my order updates, news and offers», четыре
   строки про доставку «Free delivery with tracking — …». У трёх shipping-строк остался
   ведущий пробел в значении.

   Чекбокс маркетинга намеренно **не** переименован в «I want to track my order by email»,
   как советует видео: это согласие на рекламную рассылку, магазин под GDPR, подписывать
   человека на маркетинг под видом трекинга — повод для жалоб. Пользователь согласился с
   честной формулировкой.
4. **Описание магазина** в Settings → Preferences (SEO и og:description).
5. Опционально: секция multicolumn с гарантиями и сроками на главной.
