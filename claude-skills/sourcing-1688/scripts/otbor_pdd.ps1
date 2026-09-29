# Результаты сверки PDD ↔ 1688 пишутся в лист «Отбор» главного документа (её решение 27.09.2026):
# столбцы L «Есть на Pinduoduo (лист, №)», M «Как проверено», N «Дата проверки». Строка ищется по «O№» = порядковый номер
# товара в «Отборе» (O1 = строка 2). Данные — cj\otbor_pdd.tsv. Пишет через Excel — картинки не теряются.
param([string]$Book = 'C:\Users\User\cj\yubka_kletka_otbor60.xlsx', [string]$Tsv = 'C:\Users\User\cj\otbor_pdd.tsv')
$rows = Import-Csv $Tsv -Delimiter "`t" -Encoding UTF8
try { $xl = [Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application') } catch { $xl = New-Object -ComObject Excel.Application }
$wb = $null; foreach ($w in $xl.Workbooks) { if ($w.FullName -eq $Book) { $wb = $w } }
$copy = $false; if ($wb -and -not $wb.Saved) { $copy = $true }
$own = $false
if (-not $wb) { $xl = New-Object -ComObject Excel.Application; $xl.DisplayAlerts = $false; $own = $true; $wb = $xl.Workbooks.Open($Book) }  # своя копия Excel, если книга нигде не открыта
$xl.DisplayAlerts = $false
foreach ($s in @($wb.Worksheets)) { if ($s.Name -eq 'Сверка') { $s.Delete() } }   # временный лист 27.09 — не нужен
$xl.DisplayAlerts = $true
$ws = $wb.Worksheets.Item('Отбор')
$head = 'Есть на Pinduoduo (лист, №)', 'Как проверено', 'Дата проверки'
for ($i = 0; $i -lt 3; $i++) { $c = $ws.Cells.Item(1, 12 + $i); $c.Value2 = $head[$i]; $c.Font.Bold = $true; $c.WrapText = $true }
$ws.Columns.Item(12).ColumnWidth = 55; $ws.Columns.Item(13).ColumnWidth = 30; $ws.Columns.Item(14).ColumnWidth = 12
$last = $null
foreach ($x in $rows) {
  $row = [int]($x.O.TrimStart('O')) + 1
  $ws.Cells.Item($row, 12).Value2 = $x.pdd; $ws.Cells.Item($row, 13).Value2 = $x.how; $ws.Cells.Item($row, 14).Value2 = $x.date
  $rg = $ws.Range($ws.Cells.Item($row, 12), $ws.Cells.Item($row, 14)); $rg.WrapText = $true
  $rg.Interior.Color = if ($x.pdd -like 'ЕСТЬ*') { 0xDAEFE2 } elseif ($x.pdd -like 'ВЕРОЯТНО*') { 0xCCF2FF } else { 0xF2F2F2 }
  # фото сопоставленных юбок PDD: столбцы O, P, Q… (pics = «лист:№,лист:№»), старые картинки этой строки в O+ убрать
  foreach ($sh in @($ws.Shapes)) { if ($sh.TopLeftCell.Row -eq $row -and $sh.TopLeftCell.Column -ge 15) { $sh.Delete() } }
  $j = 0
  foreach ($p in ("$($x.pics)" -split ',' | Where-Object { $_ })) {
    $lst, $num = $p.Split(':'); $f = "C:\Users\User\cj\sverka\pdd_pics\$($lst)_$($num).jpg"
    if (-not (Test-Path $f)) { continue }
    $cell = $ws.Cells.Item($row, 15 + $j); $ws.Columns.Item(15 + $j).ColumnWidth = 17
    $cell.Value2 = "лист $lst, №$num"; $cell.VerticalAlignment = -4160; $cell.Font.Size = 8; $cell.Font.Bold = $true
    $sz = [Math]::Max(40, $ws.Rows.Item($row).Height - 14)
    $pic = $ws.Shapes.AddPicture($f, $false, $true, $cell.Left + 2, $cell.Top + 12, $sz, $sz)
    $pic.LockAspectRatio = -1; $pic.Placement = 1
    $j++
  }
  if ($j -gt 0) { $h = $ws.Cells.Item(1, 15); $h.Value2 = 'Фото с Pinduoduo (с чем сопоставлено)'; $h.Font.Bold = $true; $h.WrapText = $true }
  $last = $rg
}
if ($copy) { $v = 2; do { $out = $Book -replace '\.xlsx$', "_v$v.xlsx"; $v++ } while (Test-Path $out); $wb.SaveCopyAs($out); Write-Host "копия $out" } else { $wb.Save() }
$ws.Activate(); if ($last) { $xl.Goto($last, $true); $last.Select() | Out-Null }
$xl.Visible = $true; $xl.WindowState = -4137
if ($own) { $wb.Close($true); $xl.Quit(); [Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null; Write-Host 'Сохранено (без открытия — откроет open_main.ps1 в конце)'; exit }
Add-Type -Name Fg3 -Namespace OtP -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);'
[OtP.Fg3]::SetForegroundWindow([IntPtr]$xl.Hwnd) | Out-Null
Write-Host "Отбор: внесено $($rows.Count)"
