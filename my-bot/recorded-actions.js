const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false
  });
  const context = await browser.newContext();
  await page.goto('https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F12Bmi7Jih3WVIhNJaQ9yBTuTd1vB_i7_1nPCtkZU-DMQ%2Fedit%3Fhl%3Dru%26gid%3D1998857782&dsh=S-586435275%3A1785374158562899&followup=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F12Bmi7Jih3WVIhNJaQ9yBTuTd1vB_i7_1nPCtkZU-DMQ%2Fedit%3Fhl%3Dru%26gid%3D1998857782&hl=ru&ltmpl=sheets&osid=1&passive=1209600&service=wise&flowName=GlifWebSignIn&flowEntry=ServiceLogin&ifkv=Ac50bxvnApi9Tbcbp9lRqPFF6awXlTa5wuYdRgbIYA_GTQBDhiIuY4dNLHU1Pyce2NtcJTATPQbn9A#gid=1998857782');
  await page.getByRole('textbox', { name: 'Телефон или адрес эл. почты' }).click();
  await page.getByRole('textbox', { name: 'Телефон или адрес эл. почты' }).fill('tehrez21@gmail.com');
  await page.getByRole('textbox', { name: 'Телефон или адрес эл. почты' }).press('Enter');
  await page.getByRole('link', { name: 'Повторить попытку' }).click();
  await page.getByRole('textbox', { name: 'Телефон или адрес эл. почты' }).click();
  await page.getByRole('textbox', { name: 'Телефон или адрес эл. почты' }).fill('tehrez21@gmail.com');
  await page.getByRole('button', { name: 'Далее' }).click();
  await page.getByRole('link', { name: 'Повторить попытку' }).click();
  const page1 = await context.newPage();
  await page1.goto('chrome://new-tab-page/');
  await page1.goto('https://docs.google.com/spreadsheets/d/12Bmi7Jih3WVIhNJaQ9yBTuTd1vB_i7_1nPCtkZU-DMQ/edit?gid=224709956#gid=224709956');
  await page1.getByRole('button', { name: 'Сравнение' }).click();

  // ---------------------
  await context.close();
  await browser.close();
})();