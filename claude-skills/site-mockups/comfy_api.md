# ComfyUI Cloud из браузера

Прямые `fetch('/api/...')` из страницы отбиваются: `object_info` требует bearer_jwt или x_api_key, а `/api/object_info/<NodeName>` в облаке вообще не существует. Работает только клиент самой страницы — он подписывает запросы.

```js
const api = window.comfyAPI?.api?.api || window.app.api;
```

Полезное на нём: `fetchApi`, `queuePrompt`, `getJobDetail`, `getJobAssets`, `getHistory`, `getQueue`, `interrupt`, `cancelJob`.

## Список моделей

```js
const oi = await api.fetchApi('/object_info').then(r => r.json());
oi.CheckpointLoaderSimple.input.required.ckpt_name[0];   // список чекпоинтов
```

`flux1-dev-fp8.safetensors` — всё в одном файле (unet + clip + vae), грузится обычным `CheckpointLoaderSimple`. Для Flux нужен `EmptySD3LatentImage`, обычный `EmptyLatentImage` даст 4-канальный латент и мусор на выходе.

## Сборка графа

```js
window.__mk = function(prompt, w, h, seed, prefix){
 return {
  "1": {class_type:"CheckpointLoaderSimple", inputs:{ckpt_name:"flux1-dev-fp8.safetensors"}},
  "2": {class_type:"CLIPTextEncode", inputs:{text:prompt, clip:["1",1]}},
  "3": {class_type:"FluxGuidance", inputs:{guidance:3.5, conditioning:["2",0]}},
  "4": {class_type:"CLIPTextEncode", inputs:{text:"", clip:["1",1]}},
  "5": {class_type:"EmptySD3LatentImage", inputs:{width:w, height:h, batch_size:1}},
  "6": {class_type:"KSampler", inputs:{seed, steps:25, cfg:1.0, sampler_name:"euler",
        scheduler:"simple", denoise:1.0, model:["1",0], positive:["3",0],
        negative:["4",0], latent_image:["5",0]}},
  "7": {class_type:"VAEDecode", inputs:{samples:["6",0], vae:["1",2]}},
  "8": {class_type:"SaveImage", inputs:{filename_prefix:prefix, images:["7",0]}}
 };
};
```

## Постановка в очередь

```js
const res = await api.queuePrompt(-1, {output: window.__mk(text, 1344, 768, seed, 'name'), workflow:{}});
res.prompt_id;   // по нему потом статус
```

Второй аргумент обязателен, `workflow:{}` пустой — облаку хватает `output`. Пачку ставить циклом сразу, машина обрабатывает подряд.

## Ожидание

`javascript_tool` умирает на 45 с, поэтому ждать кусками:

```js
let st;
for(let k=0;k<6;k++){
  st = [];
  for(const [p,id] of ids){ const d = await api.getJobDetail(id); st.push(d.status); }
  if(st.every(x => x==='completed')) break;
  await new Promise(r => setTimeout(r, 6000));
}
JSON.stringify(st);
```

Статусы: `pending` → `in_progress` → `completed` / `failed`. Прогресс виден и в `document.title` вида `[64%]`. Холодный старт до 3 минут, дальше ~40 с на картинку.

## Забрать результат

```js
const a = await api.getJobAssets(id);            // assets[0].hash — имя файла
const r = await api.fetchApi('/view?filename=' + a.assets[0].hash);
const url = URL.createObjectURL(await r.blob());
```

## Посмотреть глазами

Картинки существуют только как blob внутри вкладки. Рисовать в оверлей и снимать скриншот:

```js
window.__page = (keys)=>{
  const d = document.getElementById('__ov') || (()=>{ const e=document.createElement('div');
    e.id='__ov'; e.style.cssText='position:fixed;inset:0;z-index:999999;background:#111;overflow:hidden';
    document.body.appendChild(e); return e; })();
  d.innerHTML = '<div style="display:grid;grid-template-columns:repeat('+keys.length+',1fr);gap:6px;padding:6px">'
    + keys.map(k=>'<img src="'+window.__urls[k]+'" style="width:100%">').join('') + '</div>';
};
```

Сетка 4–5 в ряд — для общей проверки консистентности, 1–2 в ряд — чтобы разглядеть детали. Убрать оверлей после работы: `document.getElementById('__ov')?.remove()`.

## Скачать

```js
const a = document.createElement('a');
a.href = window.__urls[k]; a.download = k + '.png';
document.body.appendChild(a); a.click(); a.remove();
await new Promise(r => setTimeout(r, 700));   // пауза между файлами обязательна
```

Файлы падают в корень Downloads, оттуда раскладывать `Move-Item`. Скачивание требует разрешения пользователя — спросить один раз на пачку.

## Если расширение отвалилось

`tabs_context_mcp` вернёт «Browser extension is not connected». Задачи в облаке продолжают считаться. Дождаться переподключения и опросить статусы заново — состояние в `window.*` переменных вкладки сохраняется, пока страницу не перезагрузили.
