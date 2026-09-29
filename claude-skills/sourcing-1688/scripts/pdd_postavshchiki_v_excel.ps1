# Переносит проверенных поставщиков 1688 (pdd_postavshchiki.tsv) в столбцы N–S листов Pinduoduo
# главного документа yubka_kletka_otbor60.xlsx — ЧЕРЕЗ EXCEL (openpyxl теряет картинки).
# Строка находится по «№ на странице» (столбец C) на листе, имя которого начинается с номера поиска (list: «1.», «3.»).
# Если в открытом файле есть её несохранённые правки — не трогаем его, пишем копию _vN рядом.
# Запуск: powershell -ExecutionPolicy Bypass -File pdd_postavshchiki_v_excel.ps1
param([string]$Book = 'C:\Users\User\cj\yubka_kletka_otbor60.xlsx',
      [string]$Tsv  = 'C:\Users\User\cj\pdd_postavshchiki.tsv')

$rows = Import-Csv $Tsv -Delimiter "`t" -Encoding UTF8
try { $xl = [Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application') } catch { $xl = New-Object -ComObject Excel.Application }
$wb = $null; foreach ($w in $xl.Workbooks) { if ($w.FullName -eq $Book) { $wb = $w } }
$copy = $false
if ($wb -and -not $wb.Saved) { $copy = $true }            # её несохранённые правки — не перезаписываем
$own = $false
if (-not $wb) { $xl = New-Object -ComObject Excel.Application; $xl.DisplayAlerts = $false; $own = $true; $wb = $xl.Workbooks.Open($Book) }  # своя копия Excel, если книга нигде не открыта

$head = 'Поставщик 1688 (та же модель)','Цена 1688 ¥','Продано на 1688, шт','Повторные закупки модели (复购率)','Вывод по поставщику','Ссылка 1688'
$last = $null; $done = 0
foreach ($r in $rows) {
  $ws = $null; foreach ($s in $wb.Worksheets) { if ($s.Name -like ($r.list + '.*')) { $ws = $s } }
  if (-not $ws) { Write-Host "нет листа поиска $($r.list)"; continue }
  if (-not $ws.Range('N1').Text) { for ($i = 0; $i -lt 6; $i++) { $ws.Cells.Item(1, 14 + $i).Value2 = $head[$i] } }
  $n = $ws.UsedRange.Rows.Count; $row = $null
  for ($k = 2; $k -le $n; $k++) { if ("$($ws.Cells.Item($k, 3).Value2)" -eq $r.n) { $row = $k; break } }
  if (-not $row) { Write-Host "не нашла № $($r.n) на листе $($ws.Name)"; continue }
  $ws.Cells.Item($row, 14).Value2 = $r.seller
  $ws.Cells.Item($row, 15).Value2 = $r.price
  $ws.Cells.Item($row, 16).Value2 = $r.sold
  $ws.Cells.Item($row, 17).Value2 = $r.fg
  $ws.Cells.Item($row, 18).Value2 = $r.verdict
  $c = $ws.Cells.Item($row, 19)
  if ($r.offer) { $c.Value2 = 'открыть'; $null = $ws.Hyperlinks.Add($c, "https://detail.1688.com/offer/$($r.offer).html") } else { $c.Value2 = '' }
  $color = if ($r.ok -like 'да*') { 0xDAEFE2 } else { 0xD6E4FC }   # BGR: зелёный / розовый
  $ws.Range($ws.Cells.Item($row, 14), $ws.Cells.Item($row, 19)).Interior.Color = $color
  $ws.Range($ws.Cells.Item($row, 14), $ws.Cells.Item($row, 19)).WrapText = $true
  $last = $ws.Range($ws.Cells.Item($row, 14), $ws.Cells.Item($row, 19)); $done++
}
if ($copy) {
  $v = 2; do { $out = $Book -replace '\.xlsx$', "_v$v.xlsx"; $v++ } while (Test-Path $out)
  $wb.SaveCopyAs($out); Write-Host "В файле были ваши несохранённые правки — записала копию $out"
} else { $wb.Save() }
if ($last) { $last.Worksheet.Activate(); $xl.Goto($last, $true); $last.Select() | Out-Null }
$xl.Visible = $true; $xl.WindowState = -4137
if ($own) { $wb.Close($true); $xl.Quit(); [Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null; Write-Host 'Сохранено (без открытия — откроет open_main.ps1 в конце)'; exit }
Add-Type -Name Fg -Namespace PdS -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);'
[PdS.Fg]::SetForegroundWindow([IntPtr]$xl.Hwnd) | Out-Null
Write-Host "Внесено строк: $done"
