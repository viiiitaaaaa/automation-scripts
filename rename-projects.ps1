# Rename GitHub repos + local folders + fix path references.
# Default = dry run (shows what would change). Run with -Apply to do it.
param([switch]$Apply)

$ErrorActionPreference = 'Stop'
$owner = 'viiiitaaaaa'
$home_ = 'C:\Users\User'

$map = @(
  @{ Old = 'shopify-decor-theme'; New = 'decor-store-theme';        Parent = $home_ },
  @{ Old = 'shopify-blank-theme'; New = 'blank-store-theme';        Parent = $home_ },
  @{ Old = 'frivent-preview';     New = 'ventilation-site-preview'; Parent = "$home_\AppData\Local" },
  @{ Old = 'claude-skills';       New = 'skills-archive';           Parent = $home_ }
)

# Where to look for path references
$scanRoots = @("$home_\.claude\skills") + (Get-ChildItem "$home_\.claude\projects" -Directory | ForEach-Object { Join-Path $_.FullName 'memory' } | Where-Object { Test-Path $_ })
$skipTop = 'AppData','Application Data','Local Settings','node_modules','tools','Documents','OneDrive','Music','Videos','Pictures','Saved Games','Favorites','Contacts','Links','Searches','3D Objects','Muse Hub','Cookies','NetHood','PrintHood','Recent','SendTo','aliens_eye'
$scanRoots += Get-ChildItem $home_ -Directory -Force | Where-Object { $_.Name -notlike '.*' -and $skipTop -notcontains $_.Name -and $_.Name -notmatch '^[^\x00-\x7F]' } | ForEach-Object FullName
$scanFiles = @("$home_\.claude\settings.json", "$home_\.claude\settings.local.json") | Where-Object { Test-Path $_ }
$exts = '.md','.txt','.json','.ps1','.psm1','.py','.js','.mjs','.cjs','.ts','.yml','.yaml','.toml','.ini','.cfg','.bat','.cmd','.sh','.html','.liquid','.csv'
$skipDir = '\\(\.git|node_modules|\.venv|venv|__pycache__|file-history)\\'

function Get-Pattern($old) { "(?<pre>$owner/|User[\\/]+|USERPROFILE[\\/]+|Local[\\/]+|~/)" + [regex]::Escape($old) + '(?![\w-])' }

Write-Host ("=== MODE: " + $(if ($Apply) { 'APPLY' } else { 'DRY RUN (nothing is changed)' }) + " ===")

# 1. Repos, remotes, folders
foreach ($m in $map) {
  $oldDir = Join-Path $m.Parent $m.Old; $newDir = Join-Path $m.Parent $m.New
  Write-Host "`n[$($m.Old) -> $($m.New)]"
  Write-Host "  GitHub:  $owner/$($m.Old) -> $owner/$($m.New)"
  Write-Host "  remote:  https://github.com/$owner/$($m.New).git"
  Write-Host "  folder:  $oldDir -> $newDir"
  if (-not (Test-Path $oldDir)) { Write-Host "  !! folder not found, skipping"; continue }
  if (Test-Path $newDir) { Write-Host "  !! target folder already exists, skipping"; continue }
  if ($Apply) {
    gh repo rename $m.New -R "$owner/$($m.Old)" --yes
    if ($LASTEXITCODE -ne 0) { Write-Host "  !! gh rename failed, folder left as is"; continue }
    git -C $oldDir remote set-url origin "https://github.com/$owner/$($m.New).git"
    try { Rename-Item -LiteralPath $oldDir -NewName $m.New } catch { Write-Host "  !! folder rename failed (close programs using it, then rename by hand): $_" }
    Write-Host "  done"
  }
}

# 2. Path references in files
Write-Host "`n=== Path references ==="
$ErrorActionPreference = 'Continue'
$files = @($scanFiles) + ($scanRoots | ForEach-Object { Get-ChildItem $_ -Recurse -File -Force -ErrorAction SilentlyContinue }) |
  ForEach-Object { if ($_ -is [string]) { Get-Item $_ } else { $_ } } |
  Where-Object { $exts -contains $_.Extension.ToLower() -and $_.Length -lt 5MB -and $_.FullName -notmatch $skipDir -and $_.Name -ne 'rename-repos.ps1' } |
  Sort-Object FullName -Unique
$utf8 = New-Object System.Text.UTF8Encoding($false)
$total = 0
foreach ($f in $files) {
  $bytes = [IO.File]::ReadAllBytes($f.FullName)
  $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
  $text = $utf8.GetString($bytes, $(if ($bom) {3} else {0}), $bytes.Length - $(if ($bom) {3} else {0}))
  $new = $text; $n = 0
  foreach ($m in $map) {
    $p = Get-Pattern $m.Old
    $n += ([regex]::Matches($new, $p)).Count
    $new = [regex]::Replace($new, $p, { param($x) $x.Groups['pre'].Value + $m.New })
  }
  if ($n -gt 0) {
    $total += $n
    Write-Host "  $n x  $($f.FullName)"
    if ($Apply) {
      $out = $utf8.GetBytes($new)
      if ($bom) { $out = [byte[]](0xEF,0xBB,0xBF) + $out }
      [IO.File]::WriteAllBytes($f.FullName, $out)
    }
  }
}
Write-Host "  total: $total replacements in files above"

# 3. Report only (not changed): scheduled tasks and shortcuts with old paths
Write-Host "`n=== Check by hand (not changed by script) ==="
$olds = ($map | ForEach-Object { [regex]::Escape($_.Old) }) -join '|'
Get-ScheduledTask -ErrorAction SilentlyContinue | ForEach-Object { $t = $_; $t.Actions | Where-Object { "$($_.Execute) $($_.Arguments) $($_.WorkingDirectory)" -match $olds } | ForEach-Object { Write-Host "  task: $($t.TaskPath)$($t.TaskName)" } }
$sh = New-Object -ComObject WScript.Shell
Get-ChildItem "$home_\Desktop","$env:APPDATA\Microsoft\Windows\Start Menu" -Recurse -Filter *.lnk -ErrorAction SilentlyContinue | ForEach-Object { $l = $sh.CreateShortcut($_.FullName); if ("$($l.TargetPath) $($l.Arguments) $($l.WorkingDirectory)" -match $olds) { Write-Host "  shortcut: $($_.FullName)" } }
Write-Host "=== end ==="
