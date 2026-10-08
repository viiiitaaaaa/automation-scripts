---
name: product-scenes
description: "Пересъёмка фото товаров магазина ARTMELLIO в единой интерьерной сцене через Qwen-Image-Edit в ComfyUI Cloud. Убирает чужие фоны, логотипы, иероглифы и размерные линии, ставит товар в фирменный интерьер «дома» — светлый, белый или тёмный. Используй, когда просят \"переснять товары\", \"убрать иероглифы с фото\", \"сделать фон одинаковый\", \"поставить товары в интерьер\", \"привести картинки к одному стилю\". Триггеры: \"пересъёмка\", \"фон товаров\", \"убрать логотипы с фото\", \"единый стиль картинок\", \"qwen edit\", \"интерьерная сцена\"."
---

# Пересъёмка товаров в фирменной сцене

Товары приходят с AliExpress: чёрные глянцевые фоны, чужие ванные, логотипы продавцов,
иероглифы, размерные стрелки, инфографика. В сетке каталога это выглядит как сборка
с разных площадок. Лечится пересъёмкой: предмет сохраняется, сцена заменяется.

Магазин и тема — см. память `shopify-magazin-dekora`, коллекции — скилл `shopify-collections`.

## Рецепт — не менять между товарами

| Параметр | Значение |
|---|---|
| Модель | `qwen_image_edit_2511_fp8mixed.safetensors` (UNETLoader) |
| CLIP | `qwen_2.5_vl_7b_fp8_scaled.safetensors`, type `qwen_image` |
| VAE | `qwen_image_vae.safetensors` |
| Sampler / scheduler | `euler` / `simple` |
| Steps / CFG / denoise | 20 / 2.5 / 1.0 |
| Масштаб | `ImageScaleToTotalPixels`, 1.0 мегапиксель, `resolution_steps: 8` |

Граф: `LoadImage → ImageScaleToTotalPixels → VAEEncode → KSampler → VAEDecode → SaveImage`,
кондишены — две ноды `TextEncodeQwenImageEditPlus` (позитив с промтом, негатив с пустой
строкой), обеим подаётся `clip`, `vae` и `image1` — отмасштабированное изображение.

Время: ~40 секунд на кадр, пачка из 13 — около девяти минут.

## Комнатный сет: один проход, а не итерации

**Дорогой урок: комнату собирать за один проход.** Первая попытка шла итерациями — предмет
за предметом, правка за правкой — и обошлась в **13 генераций**. Тот же результат
повторился **за одну**, когда все товары подали сразу.

Причина проста: модель не умеет двигать уже нарисованное, но прекрасно расставляет с нуля.
Каждая итеративная правка — это ещё и риск сломать то, что уже стояло: она теряла раковину,
дублировала зеркало, разбирала вешалку.

### Рецепт

1. Собрать **коллаж из всех товаров** сеткой в один PNG (`items_sheet.png`, ячейки ~380px).
2. `image1` — фотография комнаты-референса с нужной отделкой.
3. `image2` — этот коллаж.
4. В промте: сначала перечислить, что в комнате сохраняется (отделка, мебель, растения),
   затем **по строке на каждый товар** — что это и где стоит.
5. В конце — блок фотореализма.

```
The second image is a sheet of eight products. Place every one of them in the room, each where it naturally belongs, reproducing each item exactly as shown, same shapes, same materials, same colours. The round mirror on a leather strap hangs above the basin with its centre aligned with the faucet below it. The tall black faucet with the gold lever stands on the basin. The towel rack is mounted on the left wall with folded towels on it. ... Everything arranged naturally and uncluttered, nothing floating, correct scale for each object.
```

Композиция при этом выстраивается сама: зеркало встаёт по центру над раковиной без единой
правки — то, чего итерациями добиться не удалось вообще.

### Блок фотореализма

Без него кадр выглядит как визуализация из каталога мебели. Добавлять в конец промта:

```
Render as a real photograph, not a 3D visualisation: natural window light from the left, soft realistic shadows, photographic depth of field, fine film grain, true texture in plaster, grout, wood and ceramic, believable reflections, no plastic sheen, no CGI smoothness. Shot on a full-frame camera, 35mm lens, interior magazine photography.
```

### Чего не просить никогда

- **двигать предмет** — `move the mirror to the left` модель понимает как «нарисуй ещё одно
  зеркало». Проверено трижды, каждый раз два зеркала в кадре;
- **двигать мебель** — просьбу сдвинуть тумбу игнорирует полностью;
- **менять размер множителем** — `1.5 times smaller` не понимает. Работает только сравнение
  с другим предметом: `no wider than one third of the basin's width`;
- **править композицию после** — если что-то встало не так, дешевле перезапустить весь кадр
  с уточнённым промтом, чем чинить правками.

### Что делать с промахами

Норма — часть товаров не попадёт в кадр или будет нарисована приблизительно. Добивать
**одним** дополнительным проходом, перечислив только недостающее и убрав из промта то, что
уже встало. Итого два прохода на комнату.

Если правка ломает соседние объекты (а это бывает часто), не чинить цепочкой — вернуться к
последней целой версии и переформулировать.

### По ТЗ фото не обязано содержать все товары

Комнатный сет по `tz_site_structure.md` — это атмосферное фото комнаты **плюс сетка карточек
товаров под ним**. Каждый товар покупатель и так видит отдельной карточкой. Поэтому для
баннера достаточно красивого кадра комнаты с несколькими узнаваемыми предметами — гнаться
за полным составом в одном кадре не нужно и дорого.

## Подавать три ракурса, а не один — обязательно

`TextEncodeQwenImageEditPlus` принимает `image1`, `image2`, `image3`. Редактируется только
`image1` (он же идёт в `VAEEncode`), остальные модель читает как **справку по конструкции**.

Без них модель достраивает невидимые части по догадке, и получаются классические провалы:
складная полка задирается вверх, круглое зеркало превращается в радиоприёмник, у держателя
пропадает кронштейн. С тремя ракурсами всё это исчезает — проверено на вешалке, которая с
одним кадром не давалась три захода подряд.

```js
g["7"].inputs.image1 = ["5",0];              // основной, отмасштабированный
g["12"] = {class_type:"LoadImage", inputs:{image: file2}};
g["7"].inputs.image2 = ["12",0];
g["13"] = {class_type:"LoadImage", inputs:{image: file3}};
g["7"].inputs.image3 = ["13",0];
```

В промт добавить строку, чтобы модель поняла назначение дополнительных кадров:

```
The additional reference views show the same product from other angles — reproduce its construction exactly: same brackets, same bars, same hooks, same proportions.
```

Скачивать с карточки товара по 3 кадра сразу — они же служат и для выбора лучшего исходника,
и как референсы. Лишней работы нет.

## Как доставить исходники в облако

Не через загрузку файлов — картинки уже лежат на CDN магазина. Прямо в консоли вкладки:

```js
const b = await fetch(imageUrl).then(x => x.blob());
const fd = new FormData();
fd.append('image', new File([b], 'name.jpg', {type:'image/jpeg'}));
fd.append('overwrite', 'true');
const up = await api.fetchApi('/upload/image', {method:'POST', body: fd}).then(r => r.json());
// up.name -> подставить в LoadImage
```

CORS Shopify это разрешает. Список товаров коллекции — `/collections/<handle>/products.json`.

## Дом ARTMELLIO: три тона ванной

Общий хвост, добавляется к любой сцене слово в слово:

```
Remove every watermark, logo, brand name, label, caption, arrow, dimension line and Chinese character. Keep the product completely identical in shape, colour, material and position. Nothing else on the countertop, no bottles, no towels, no plants, no text. Calm editorial interior photography, sharp focus on the product.
```

**Белый — основной для карточек товара.** Товар читается лучше всего, плитка даёт фактуру, но не спорит с предметом.

```
Place the product on a white stone vanity countertop in a bright minimal Japandi bathroom. Behind it a wall of small white square tiles with fine grout lines, below a pale oak wood cabinet. Clear soft daylight from the left casting a light shadow across the countertop.
```

**Тёмный — для баннеров коллекций и комнатных сетов.** Премиально, светлый оникс светится. Тёмные товары в нём теряются — для карточек не годится.

```
Place the product on a dark grey stone vanity countertop in a moody minimal Japandi bathroom. Behind it a charcoal grey stone wall, below a walnut wood cabinet with black fixtures. Soft directional light from the left casting a deep soft shadow across the countertop.
```

**Светлый — тёплый вариант.** Требует доводки: уходит в персиковый и глушит зелёный мрамор.

```
Place the product on a pale travertine vanity countertop in a minimal Japandi bathroom. Behind it a warm sand-beige microcement plaster wall with soft matte texture, below a pale oak wood cabinet. Soft warm daylight from the left casting a gentle long shadow across the countertop.
```

### Сцену выбирает не комната, а способ крепления

**Главная ошибка, стоившая двух перегенераций:** вся пачка была поставлена на столешницу,
включая коврики и настенные держатели. Ковёр на тумбе и полка для полотенец на столешнице
читаются как брак, даже если сцена красивая.

Перед прогоном разложить товары на три группы:

| Группа | Что входит | Сцена |
|---|---|---|
| Настольные | наборы, диспенсеры, подносы, шкатулки, вазы | столешница |
| Настенные | держатели бумаги, зеркала, полки, крючки, вешалки | стена, `no countertop, no cabinet in the frame` |
| Напольные | коврики, корзины, банкетки | пол, вид сверху под небольшим углом |

Дополнение к промту настенных: кронштейн должен быть **привинчен к стене**, а не висеть в
воздухе — писать `its bracket is screwed flat against the tiled wall`. Иначе модель рисует
предмет парящим, а рулон бумаги — подвешенным непонятно к чему.

Зеркало вешать явно **над раковиной**: `directly above a white ceramic washbasin standing on
a pale oak vanity, no toilet in the frame`. Без этого модель ставит его над унитазом.

### Складные и шарнирные конструкции модель разворачивает

Вешалка с откидной полкой, складной сушилке, раскладной кронштейн — Qwen любит показать их
«в движении»: полка задирается вверх под диагональю, хотя в исходнике она горизонтальна.
Выглядит как брак сборки.

Лечится описанием углов словами:

```
The upper wooden shelf is perfectly horizontal and parallel to the floor, meeting the wall plates at a right angle — it is not tilted, not angled upwards, not folded up.
```

Побочный эффект: вместе с исправлением геометрии модель нередко убирает реквизит —
полотенца с полки, мыло с подноса. Если контекст использования важен, его надо вернуть
в промт явно (`with two rolled towels resting on the shelf`), иначе получится голый товар.

### Подмена предмета — проверять каждый кадр

Qwen может заменить товар другим объектом того же силуэта: круглое зеркало на ремешке
стало **радиоприёмником**, держатель бумаги — просто рулоном. Лечится усилением в промте:

```
Keep the product completely identical in shape, colour, material, proportions and every part it consists of — do not replace it with a different object, do not add or remove any component.
```

И всё равно отсматривать всю пачку глазами: формулировка снижает частоту, но не исключает.

Оценщик-оптимизатор (курс Anthropic Academy API, kursy-konspekty): после генерации — проверка по рубрике
(нет иероглифов/логотипов/размерных линий, товар не подменён и не искажён, сцена в тоне дома) → замечания → **один**
повтор; дальше — показать ей. Картинки последней проверяет она: модель-оценщик картинок часто ошибается.

### Материалы по комнатам

Один дом, но поверхность обязана соответствовать комнате — иначе кадр читается как ошибка.

| Комната | Поверхность под товаром | Стена |
|---|---|---|
| Ванная | травертин, белый камень, тёмный камень | плитка или микроцемент |
| Кухня | светлый камень или дуб | штукатурка |
| Гостиная | дуб, низкий столик | штукатурка, реечная панель |
| Спальня | дуб, комод | штукатурка |
| Прихожая | камень, консоль | микроцемент |

Дерево в ванной допустимо **только как мебель тумбы**, не как поверхность под предметом.

## Кадр вышел не того формата — расширять в Comfy, а не в питоне

`ImageScaleToTotalPixels` держит пропорции исходника: узкий вертикальный товар (душевая
стойка 159×370) даёт вертикальный кадр, и в сетке карточек он выбивается из общего ряда.

Ни в коем случае не достраивать бока локально: зеркальное отражение краёв размножает сам
товар (получилось три душа в ряд), тайл чистой полосы тащит за собой розетки и куски
арматуры, растяжение крайних пикселей превращает плитку в полосы. Все три способа
проверены — все три брак.

Рабочий путь — аутпейнт тем же Qwen-edit: вписать **готовый кадр** в квадратный холст,
поля залить ровным серым (`(238,238,238)`), залить в облако и прогнать обычным графом.

```
Outpainting task. The photograph in the centre of this square canvas shows <что на нём>.
Keep that central photograph completely unchanged — same object, same tiles, same light,
same perspective, do not move it, do not resize it, do not redraw it, do not add a second
<товар>. Only fill the two flat grey empty margins on the left and on the right: continue
the very same <поверхность> into them, matching the tile size, the grout lines, the
perspective and the light exactly, so the finished square looks like one single wider
photograph with no seam, no border, no frame, no colour break. Nothing else in the new areas.
```

Два обязательных условия: подавать **уже отрендеренный кадр**, а не исходник с AliExpress
(иначе модель перерисует сцену целиком и плитка уедет в мозаику), и явно запрещать второй
экземпляр товара — без запрета он дублирует его в полях.

## Ровная подложка вместо интерьера

Если интерьер не нужен — вариант с чистым фоном под токен коллекции:

```
Replace the background with a seamless uniform cool light grey studio backdrop, the colour of pale stone, slightly green-grey, strictly neutral, no beige, no cream, no warm tint, no room, no furniture, no tiles. <общий хвост>
```

Работает надёжнее интерьера, но каталог выглядит суше.

## Выбор исходника

У товара обычно 3–8 кадров, и первый часто худший — инфографика с размерами или коллаж.
Скачать по 3 кадра на товар, собрать контактный лист и выбрать глазами: предмет крупно,
без людей, без наложенного текста, ракурс три четверти. Модель уберёт надписи, но чем
чище исходник, тем меньше она домысливает.

**Исходник мелкий или мыльный (у 1688 часто 750 px и сжатие):** сначала поднять качество, потом в сцену.
- Локально, без отправки наружу (🟡/🟢 — файлы остаются на ПК): Upscayl (уже стоит; при ошибке видеокарты
  «vkQueueSubmit failed -4» — `upscayl-bin -t 64`).
- В браузере: **Tapir** — 2K/4K, без регистрации, лимитов и водяных знаков (PushEnter/13609, пост 331, 26.08.2026).
  Проверено 07.10: ссылка tapirconvert.com/video-upscaler теперь ведёт на **squishyfile.com/video-upscaler** — это
  апскейл ВИДЕО ×2/×4 (MP4/MOV/MKV/WebM → MP4), считается на видеокарте в самом браузере (WebGPU), файл никуда не
  уходит, без входа и знаков. Апскейлера ФОТО на сайте нет → для фото 1688 остаётся Upscayl; squishyfile — для
  мутных роликов поставщика перед рекламой (ещё там: MOV→MP4, кадры из видео, сжатие GIF).
  Фото товара поставщика — 🟢 можно в облако; свои фото/лица/документы — нет.
- После апскейла сверить мелкие детали (пуговицы, клетку ткани, швы): апскейлер иногда «дорисовывает» узор —
  для одежды это меняет товар, такой кадр не брать.

## Грабли

| Симптом | Причина | Лечение |
|---|---|---|
| `required_input_missing: resolution_steps` | у `ImageScaleToTotalPixels` этот вход обязателен | передавать `resolution_steps: 8` |
| Фон уходит в тёплый бежевый | модель тяготеет к теплу | явно писать `cool`, `no beige, no cream, no warm tint` |
| С предмета пропадают мелкие детали (кусок мыла, крышка) | сцена перетягивает внимание модели | отсматривать каждый кадр, провальные перегенерировать с другим seed |
| Товар перерисован, изменилась форма | слишком свободный промт | всегда включать `Keep the product completely identical in shape, colour, material and position` |
| В кадре появились чужие бутылки и полотенца | сцена описана без запретов | держать в хвосте `nothing else on the countertop` |

## Что дальше с файлами

Картинки живут только как blob во вкладке, пока не скачаны — закрытие вкладки means
перегенерацию. Скачивать сразу: `<a download>` по одному с паузой 900 мс.

Загрузка в Shopify — руками в админке: `Products → товар → Media`, добавить новое фото
и **удалить старое**, иначе главным на витрине останется прежнее. Массовый путь через
CSV требует, чтобы файлы лежали в интернете по прямым ссылкам.
