# Рабочий код: ComfyUI Cloud + QwenImageEditApi

Всё выполняется через `mcp__claude-in-chrome__javascript_tool` на вкладке `https://cloud.comfy.org/`.
Вкладку держать открытой всю сессию: токен продлевается, только пока она жива (живёт ~час).

## 0. Открыть и дождаться

```js
for (let i=0; i<20 && !window.app; i++) await new Promise(r=>setTimeout(r,1000));
if (!window.app) throw new Error('app not ready');
```

Если выскочило окно «Требуется вход для использования API Nodes» — сначала проверить токен (шаг 3),
и только если его реально нет в localStorage, просить пользователя войти самому.
Пароли не вводим никогда.

## 1. Скрытый file input

```js
let inp = document.getElementById('__mcpfile');
if (!inp) {
  inp = document.createElement('input');
  inp.type='file'; inp.id='__mcpfile'; inp.multiple=true;
  inp.style.cssText='position:fixed;top:0;left:0;z-index:99999;opacity:0.01;width:200px;height:40px;';
  document.body.appendChild(inp);
}
window.__upload = async function(file, name){
  const fd = new FormData();
  fd.append('image', file, name);
  fd.append('overwrite','true');
  const r = await window.app.api.fetchApi('/upload/image', {method:'POST', body:fd});
  return await r.json();
};
'ready'
```

Затем `find` («hidden file input at top left corner of page») → взять ref → `file_upload` с абсолютными
путями. Файлы должны лежать в scratchpad, пути с Desktop инструмент не всегда пускает — копировать заранее.

## 2. Залить на сервер

```js
const inputs = [...document.querySelectorAll('input[type=file]')];
const src = inputs.find(i => i.files && i.files.length === N);
const out = {};
for (const f of src.files) {
  const j = await window.__upload(f, f.name);
  out[f.name.replace(/\.png$/i,'')] = j.name;   // хеш-имя на сервере
}
window.__names = Object.assign(window.__names||{}, out);
JSON.stringify(out)
```

Хеш-имена сохранять — файлы переживают перезагрузку вкладки и смену сессии, второй раз заливать не надо.

## 3. Токен и постановка задачи

```js
const graph = {
 "1": {class_type:"LoadImage", inputs:{image: N.base,   upload:"image"}},
 "2": {class_type:"LoadImage", inputs:{image: N.sheetA, upload:"image"}},
 "3": {class_type:"LoadImage", inputs:{image: N.sheetB, upload:"image"}},
 "4": {class_type:"QwenImageEditApi", inputs:{
    "model": "qwen-image-3.0-pro",
    "model.images.image_1": ["1",0],
    "model.images.image_2": ["2",0],
    "model.images.image_3": ["3",0],
    "model.prompt": prompt,
    "model.negative_prompt": neg,
    "size": "match input", "n": 1, "seed": 7788,
    "prompt_extend": false, "watermark": false }},
 "5": {class_type:"SaveImage", inputs:{images:["4",0], filename_prefix:"final_room"}}
};

const k = Object.keys(localStorage).find(x => x.startsWith('firebase:authUser:'));
const tok = JSON.parse(localStorage.getItem(k)).stsTokenManager.accessToken;
window.app.api.authToken = tok;

const r = await window.app.api.fetchApi('/prompt', {
  method:'POST', headers:{'Content-Type':'application/json'},
  body: JSON.stringify({
    client_id: window.app.api.clientId,
    prompt: graph,
    extra_data: { auth_token_comfy_org: tok }
  })});
const j = await r.json();
window.__jobId = j.prompt_id;
JSON.stringify({jobId: j.prompt_id, nodeErrors: j.node_errors})
```

`node_errors: {}` — граф принят. Ошибка авторизации приходит позже, в статусе задачи.

## 4. Ждать и забрать

```js
let st='', d=null;
for (let k=0; k<12; k++) {
  await new Promise(r=>setTimeout(r,5000));
  d = await window.app.api.getJobDetail(window.__jobId);
  st = d && d.status;
  if (st==='completed' || st==='failed') break;
}
let saved = null;
if (st === 'completed') {
  const a = await window.app.api.getJobAssets(window.__jobId);
  const r = await window.app.api.fetchApi('/view?filename=' + a.assets[0].hash);
  const blob = await r.blob();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'final_room.png';
  document.body.appendChild(link); link.click(); link.remove();
  saved = blob.size;
}
JSON.stringify({st, saved, err: d && d.execution_error && d.execution_error.exception_message})
```

Файл падает в `C:\Users\User\Downloads`. Прочитать его инструментом Read, оценить самому,
затем скопировать в `C:\Users\User\Desktop\japandi_room` под финальным именем.

## Диагностика

| Симптом | Причина | Что делать |
|---|---|---|
| `Unauthorized: Please login first to use this node` | токен не ушёл в `extra_data` | шаг 3, брать токен из localStorage вручную |
| Ответ инструмента `[BLOCKED: Cookie/query string data]` | в выводе оказался токен | печатать только `typeof`/флаги |
| `Couldn't determine which page this action targets` | вкладку закрыли | `tabs_context_mcp {createIfEmpty:true}`, открыть заново |
| javascript_tool падает по таймауту | цикл ожидания длиннее 45 с | резать на куски по 10-12 итераций |
| Кадр обрезан / комната сжалась | `size` не `match input` или слабый список `same` | вернуть `match input`, удлинить перечисление |
| В кадре белые прямоугольники и швы | макет протёк в результат | усилить негатив `collage edges, pasted rectangles, white patches` |
| Модель переписала задачу по-своему | `prompt_extend: true` | поставить `false` |
