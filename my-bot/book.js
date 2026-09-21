// ЕДИНАЯ ТОЧКА ВХОДА В РАБОЧУЮ КНИГУ.
//
// До 01.08.2026 книг было две: «1» (недельные вкладки, истории, себестоимость) и
// книга сравнения (Цены, Evirma, Сравнение, Юнит-экономика, Цены — сценарии).
// К ним вело четыре разных /exec-адреса, и приходилось прыгать между документами.
// Книги слиты в одну — в книгу «1», листы книги сравнения перенесены в неё,
// а единый Apps Script (см. apps-script/book.gs) умеет всё, что умели оба старых.
//
// ВСЕ скрипты проекта берут адрес и id ТОЛЬКО отсюда. Если адрес когда-нибудь
// сменится (например, придётся создать новое развертывание вместо правки старого),
// правится одна строка здесь.
//
// Старые адреса, больше не используются:
//   AKfycbynMl6PeexjBp5WLGXNQ9Q4CQFKEmu8R_ko23R-K2RAYd52sPEJInoTpjQAJUfJW63UWw  — книга сравнения
//   AKfycbyuQ981qM1QSPQeN3On5oHFxfrhpLqSmZNIMSikUYgtLnJDJo5bqHr7xCfhrVfULhBsoQ  — лист «Цены»
//   AKfycbzRxvESLHz3H8QoTEyerWhpQ1EL42auATTKUjShw2JoZYf-Pzu3XhcVjDkXfaudgN1Nfw  — лист «Evirma»
// Старая книга сравнения (12Bmi7Jih3WVIhNJaQ9yBTuTd1vB_i7_1nPCtkZU-DMQ) оставлена
// нетронутой как резервная копия — но данные там уже не обновляются.

const BOOK_URL = 'https://script.google.com/macros/s/AKfycbygfctg0GocMygEuyZv6MMWyEaIZJ7Kc2bnS6Qa3-osSPuCADM1gcldKaeGg35e93Gn/exec';
const BOOK_ID = '12OLxU8EDwN6nJQGySGEczKe0wflJN1dr4-4Y1Dynyxw';
const BOOK_HTTP = `https://docs.google.com/spreadsheets/d/${BOOK_ID}/edit`;

// gviz-CSV нужной вкладки (читается из вкладки браузера, с credentials).
// Помни: gviz кэширует и занижает размер листа — размер проверяй формулами в книге.
const gvizCsv = sheet =>
  `https://docs.google.com/spreadsheets/d/${BOOK_ID}/gviz/tq?tqx=out:csv` +
  `&sheet=${encodeURIComponent(sheet)}&_=${Date.now()}`;

module.exports = { BOOK_URL, BOOK_ID, BOOK_HTTP, gvizCsv };
