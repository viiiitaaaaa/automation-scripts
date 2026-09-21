const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js

fetch(SHEET_URL, {
  method: 'POST',
  body: JSON.stringify({ sheet: 'Тест', rows: [['Работает!', 123]], clear: true }),
}).then(r => console.log('Код ответа:', r.status));