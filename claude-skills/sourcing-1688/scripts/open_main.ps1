# Открыть главную таблицу ОДИН раз в конце работы. Если уже открыта — просто показать окно, второе не открывать.
param([string]$Book = 'C:\Users\User\cj\yubka_kletka_otbor60.xlsx', [string]$Sheet = '')
try { $xl = [Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application') } catch { $xl = $null }
$wb = $null; if ($xl) { foreach ($w in @($xl.Workbooks)) { if ($w.FullName -eq $Book) { $wb = $w } } }
if (-not $wb) { Start-Process $Book; Write-Host 'открыта'; exit }
if ($Sheet) { foreach ($s in $wb.Worksheets) { if ($s.Name -like "$Sheet*") { $s.Activate() } } }
$xl.Visible = $true; $xl.WindowState = -4137
Add-Type -Name FgM -Namespace OpM -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);'
[OpM.FgM]::SetForegroundWindow([IntPtr]$xl.Hwnd) | Out-Null
Write-Host 'уже была открыта — показала окно'
