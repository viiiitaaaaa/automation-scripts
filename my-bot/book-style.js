// Наводит оформление во всей книге: шрифты, фон, подсветки, диаграмма.
//
// Запускать после любых больших перестроек книги. Отдельные скрипты
// (compare.js, price-scenarios.js) возвращают оформление своего листа сами,
// а этот проходит по всем сразу.
//
// Запуск: node book-style.js

const { BOOK_URL } = require('./book');

// body: true — «зебра» PAPER/SURF. Она кладётся ТОЛЬКО поверх белых ячеек,
// поэтому включена везде: подсветка цены в колонке H «Сравнения» и цветные
// блоки недельных вкладок остаются нетронутыми.
// Недельные вкладки не перечисляем: их имена меняются при ротации, список
// берём из книги.
const FIXED = [
  { name: 'Сравнение',        body: true, freezeCols: 3 },
  { name: 'Динамика финансы', body: true, freezeCols: 2, headRows: 2 },
  { name: 'Себестоимость',    body: true, freezeCols: 1 },
  { name: 'Цены — сценарии',  body: true, freezeCols: 3 },
];
const WEEK_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;

const DYN = 'Динамика финансы';

const post = async (payload, tries = 3) => {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(BOOK_URL, {
        method: 'POST', body: JSON.stringify(payload), signal: AbortSignal.timeout(600000),
      });
      const body = await r.text();
      if (body.trim().startsWith('<')) throw new Error('Apps Script вернул страницу ошибки');
      return JSON.parse(body);
    } catch (e) {
      if (t === tries) throw e;
      await new Promise(res => setTimeout(res, 4000 * t));
    }
  }
};

(async () => {
  const list = await post({ list: true });
  const weeks = list.sheets.map(s => s.name).filter(n => WEEK_RE.test(n))
    .map(name => ({ name, body: true, freezeCols: 1 }));

  for (const s of FIXED.concat(weeks)) {
    const r = await post({ style: { sheets: [s] } });
    console.log(' ', (r.styled || [JSON.stringify(r)])[0]);
  }

  const hidden = await post({ style: { sheets: [], hideService: true } });
  console.log('\nСлужебные:', hidden.styled.length, 'скрыто');

  // ---- диаграмма: продажи и прибыль по неделям ----
  // Домен — «Даты» (B), кривые — «Продажи» (D) и «Итого Прибыль» (R).
  // Последняя строка с датой ищется, чтобы диаграмма росла вместе с книгой.
  const dyn = await post({ read: { sheet: DYN, a1: 'B1:B300' } });
  let last = 0;
  dyn.values.forEach((row, i) => { if (String(row[0] || '').trim()) last = i + 1; });

  // Настройки проверены на этой книге. Диаграмма считает только ВИДИМЫЕ строки:
  // старые недели у владельца свёрнуты, поэтому кривая идёт по актуальному
  // периоду, а не по всей истории с февраля.
  const chart = await post({
    chart: {
      sheet: DYN, headRow: 2, domain: 2, to: last, type: 'COMBO',
      series: [{ col: 4 }, { col: 18 }],       // D Продажи, R Итого Прибыль
      anchorRow: dyn.lastRow + 3, anchorCol: 2,   // под таблицей, без прокрутки вбок
      title: '📈 Продажи и прибыль по неделям',
      options: {
        width: 1320, height: 560,
        backgroundColor: '#FFFFFF',
        // Прибыль почти на порядок меньше выручки. На одной оси её кривая
        // ложится на ноль и читается как «ничего не происходит», поэтому у
        // неё своя правая ось: видно форму, а не только масштаб.
        series: {
          0: { type: 'area', targetAxisIndex: 0, color: '#6B4CA8', areaOpacity: 0.18, lineWidth: 3 },
          1: { type: 'line', targetAxisIndex: 1, color: '#17A08F', lineWidth: 4, pointSize: 7 },
        },
        vAxes: {
          0: { title: 'Продажи, ₽', format: 'short',
               textStyle: { color: '#6B4CA8', fontSize: 11 },
               titleTextStyle: { color: '#6B4CA8', fontSize: 12, italic: false },
               gridlines: { color: '#EFEAF7' }, minorGridlines: { count: 0 } },
          1: { title: 'Прибыль, ₽', format: 'short',
               textStyle: { color: '#17A08F', fontSize: 11 },
               titleTextStyle: { color: '#17A08F', fontSize: 12, italic: false },
               gridlines: { color: 'transparent' }, minorGridlines: { count: 0 } },
        },
        curveType: 'function',
        legend: { position: 'top', alignment: 'center',
                  textStyle: { color: '#241C39', fontSize: 12 } },
        titleTextStyle: { color: '#241C39', fontSize: 18, bold: true },
        hAxis: { textStyle: { color: '#5B4A78', fontSize: 10 }, slantedText: true,
                 slantedTextAngle: 45, gridlines: { color: 'transparent' } },
      },
    },
  });
  console.log('Диаграмма:', chart.chart || JSON.stringify(chart));
})();
