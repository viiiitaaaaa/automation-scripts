# Переименование репозиториев и папок (без слова artmellio).
# Сначала запусти без ключа: покажет, что будет сделано, ничего не меняя.
#   powershell -ExecutionPolicy Bypass -File rename-repos.ps1
# Потом с ключом -Apply: сделает.
#   powershell -ExecutionPolicy Bypass -File rename-repos.ps1 -Apply
# Скрипт можно запускать повторно: уже сделанное он пропускает.
param([switch]$Apply)

$ErrorActionPreference = "Continue"
$H     = "C:\Users\User"
$Owner = "viiiitaaaaa"
$utf8  = New-Object System.Text.UTF8Encoding($false)

# старая папка, новая папка, старый репозиторий, новый репозиторий
$Map = @(
    @{ OldDir="artmellio-system";      NewDir="decor-store-ops";     OldRepo="artmellio-system";      NewRepo="decor-store-ops" },
    @{ OldDir="claude-skills";      NewDir="claude-skills";       OldRepo="claude-skills";      NewRepo="claude-skills" },
    @{ OldDir="shopify-decor-theme";   NewDir="shopify-decor-theme"; OldRepo="artmellio-theme";       NewRepo="shopify-decor-theme" },
    @{ OldDir="shopify-blank-theme"; NewDir="shopify-blank-theme"; OldRepo="shopify-blank-theme"; NewRepo="shopify-blank-theme" },
    @{ OldDir="case_bot";              NewDir="case-bot";            OldRepo="case-bot";              NewRepo="case-bot" }
)

# Замены в тексте файлов (регулярные выражения, порядок важен).
# Не трогаем: бренд ARTMELLIO в тексте, тему Shopify artmellio-theme/main, имя скилла artmellio-system.
$Rules = @(
    @{ P='claude-skills';                                   R='claude-skills' },
    @{ P='claude-skills';                                   R='claude-skills' },
    @{ P='shopify-blank-theme';                              R='shopify-blank-theme' },
    @{ P='viiiitaaaaa/shopify-decor-theme';                        R='viiiitaaaaa/shopify-decor-theme' },
    @{ P='(?<=Users\\User\\|viiiitaaaaa/)artmellio-system';    R='decor-store-ops' },
    @{ P='(?<![\w\-\[/\\])artmellio-system(?=[\\/])';          R='decor-store-ops' },
    @{ P='(?m)^# decor-store-ops\s*$';                        R='# decor-store-ops' },
    @{ P='(?<=Users\\User\\)case_bot';                         R='case-bot' },
    @{ P='(?<![\w\-/\\])case_bot(?=[\\/])';                    R='case-bot' }
)
$TextExt  = @(".md",".txt",".py",".ps1",".psm1",".bat",".cmd",".js",".mjs",".ts",".json",".mdc",".yml",".yaml",".toml",".ini",".cfg",".mmd",".html",".sh")
$SkipDirs = @(".git","node_modules","__pycache__",".venv","venv","data","sessions","todos","shell-snapshots","statsig","ide","file-history","plugins","cache")

function Say($t, $c="Gray") { Write-Host $t -ForegroundColor $c }
function Mode { if ($Apply) { "" } else { "[проба] " } }

function Get-TextFiles($root) {
    if (-not (Test-Path $root)) { return }
    $stack = New-Object System.Collections.Stack
    $stack.Push((Get-Item -LiteralPath $root -Force))
    while ($stack.Count) {
        $d = $stack.Pop()
        foreach ($i in (Get-ChildItem -LiteralPath $d.FullName -Force -ErrorAction SilentlyContinue)) {
            if ($i.PSIsContainer) {
                if ($SkipDirs -notcontains $i.Name -and -not ($i.Attributes -band [IO.FileAttributes]::ReparsePoint)) { $stack.Push($i) }
            } elseif ($TextExt -contains $i.Extension.ToLower() -and $i.Length -lt 5MB) { $i }
        }
    }
}

function Fix-Files($root) {
    $changed = @()
    foreach ($f in (Get-TextFiles $root)) {
        # пропускаем историю диалогов Claude (.jsonl не в списке) и огромные json
        try { $bytes = [IO.File]::ReadAllBytes($f.FullName) } catch { continue }
        $bom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
        $text = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
        $new = $text
        foreach ($r in $Rules) { $new = [regex]::Replace($new, $r.P, $r.R) }
        if ($new -ne $text) {
            $changed += $f.FullName
            if ($Apply) {
                $enc = if ($bom) { New-Object System.Text.UTF8Encoding($true) } else { $utf8 }
                [IO.File]::WriteAllText($f.FullName, $new, $enc)
            }
        }
    }
    return ,$changed
}

$ghOk = $false
if (Get-Command gh -ErrorAction SilentlyContinue) { gh auth status *> $null; $ghOk = ($LASTEXITCODE -eq 0) }

Say "`n=== 1. Репозитории на GitHub ===" Cyan
$manual = @()
foreach ($m in $Map) {
    if ($m.OldRepo -eq $m.NewRepo) { continue }
    git ls-remote "https://github.com/$Owner/$($m.NewRepo).git" HEAD *> $null
    if ($LASTEXITCODE -eq 0) { Say "  $($m.NewRepo): уже переименован" Green; continue }
    if ($ghOk) {
        Say "  $(Mode)$($m.OldRepo) -> $($m.NewRepo)"
        if ($Apply) { gh repo rename $m.NewRepo -R "$Owner/$($m.OldRepo)" --yes }
    } else { $manual += $m }
}
if ($manual.Count) {
    Say "  Программа gh не найдена или не вошла в GitHub. Переименуй вручную:" Yellow
    foreach ($m in $manual) { Say "    https://github.com/$Owner/$($m.OldRepo)/settings  ->  Repository name: $($m.NewRepo)  -> Rename" Yellow }
    Say "  Потом запусти скрипт ещё раз, он допишет адреса в папки." Yellow
}

Say "`n=== 2. Программы, которые держат папки ===" Cyan
$restartBot = $false
$procs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $cl = "$($_.CommandLine) $($_.ExecutablePath)"
    foreach ($m in $Map) { if ($m.OldDir -ne $m.NewDir -and $cl -like "*$H\$($m.OldDir)*") { return $true } }
    if ($_.Name -match '^python' -and $_.CommandLine -match 'case-bot\.py|auto_razbor\.py') { return $true }
    return $false
}
foreach ($p in $procs) { Say "  $($p.Name) (PID $($p.ProcessId)): $($p.CommandLine)" Yellow }
if ($procs -and $Apply) {
    if (($procs | Where-Object { $_.CommandLine -match 'case_bot|auto_razbor' })) { $restartBot = $true }
    Say "  Останавливаю их, иначе папку не переименовать (бот «Дела» потом запущу заново)." Yellow
    $procs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}
if (-not $procs) { Say "  нет" }

Say "`n=== 3. Папки на ПК ===" Cyan
foreach ($m in $Map) {
    $old = Join-Path $H $m.OldDir; $new = Join-Path $H $m.NewDir
    if ($m.OldDir -eq $m.NewDir) { continue }
    if (Test-Path $new) { Say "  $($m.NewDir): уже есть" Green; continue }
    if (-not (Test-Path $old)) { Say "  $($m.OldDir): папки нет, пропускаю" Yellow; continue }
    Say "  $(Mode)$old -> $new"
    if ($Apply) {
        try { Rename-Item -LiteralPath $old -NewName $m.NewDir -ErrorAction Stop }
        catch { Say "  НЕ ВЫШЛО: $($_.Exception.Message). Закрой Cursor/терминал/проводник в этой папке и запусти скрипт снова." Red }
    }
}

Say "`n=== 4. Адреса репозиториев в папках (git remote) ===" Cyan
foreach ($m in $Map) {
    $dir = Join-Path $H $m.NewDir
    if (-not (Test-Path $dir)) { $dir = Join-Path $H $m.OldDir }
    if (-not (Test-Path "$dir\.git")) { continue }
    $want = "https://github.com/$Owner/$($m.NewRepo).git"
    $cur = git -C $dir remote get-url origin 2>$null
    if ($cur -eq $want) { Say "  $($m.NewDir): уже $want" Green; continue }
    git ls-remote $want HEAD *> $null
    if ($LASTEXITCODE -ne 0) { Say "  $($m.NewDir): репозиторий $($m.NewRepo) на GitHub ещё не переименован, адрес не меняю" Yellow; continue }
    Say "  $(Mode)$($m.NewDir): $cur -> $want"
    if ($Apply) { git -C $dir remote set-url origin $want }
}

Say "`n=== 5. Старые пути внутри файлов ===" Cyan
$roots = @()
foreach ($m in $Map) { $d = Join-Path $H $m.NewDir; if (-not (Test-Path $d)) { $d = Join-Path $H $m.OldDir }; $roots += $d }
$roots += @("$H\automation-scripts", "$H\lead-engine", "$H\disk-hygiene", "$H\.claude")
$byRepo = @{}
foreach ($r in ($roots | Select-Object -Unique)) {
    if (-not (Test-Path $r)) { continue }
    $c = Fix-Files $r
    if ($c.Count) {
        Say "  $(Mode)$r : файлов с заменами $($c.Count)"
        $c | Select-Object -First 8 | ForEach-Object { Say "      $_" DarkGray }
        if ($c.Count -gt 8) { Say "      ..." DarkGray }
        $byRepo[$r] = $c
    }
}

Say "`n=== 6. Память Claude Code (папки в .claude\projects) ===" Cyan
$proj = "$H\.claude\projects"
if (Test-Path $proj) {
    foreach ($m in $Map) {
        if ($m.OldDir -eq $m.NewDir) { continue }
        $oldKey = "C--Users-User-" + ($m.OldDir -replace '[^A-Za-z0-9]', '-')
        $newKey = "C--Users-User-" + ($m.NewDir -replace '[^A-Za-z0-9]', '-')
        if ($oldKey -eq $newKey) { continue }
        foreach ($d in (Get-ChildItem $proj -Directory | Where-Object { $_.Name -eq $oldKey -or $_.Name.StartsWith("$oldKey-") })) {
            $target = $newKey + $d.Name.Substring($oldKey.Length)
            if (Test-Path (Join-Path $proj $target)) { Say "  $target уже есть, $($d.Name) не трогаю" Yellow; continue }
            Say "  $(Mode)$($d.Name) -> $target"
            if ($Apply) { Rename-Item -LiteralPath $d.FullName -NewName $target }
        }
    }
}

Say "`n=== 7. Планировщик задач и автозагрузка ===" Cyan
$pat = '(?i)\\(artmellio-system|claude-skills|shopify-blank-theme|case_bot)(\\|"|$)'
foreach ($t in (Get-ScheduledTask -ErrorAction SilentlyContinue)) {
    $dirty = $false
    foreach ($a in $t.Actions) { if ("$($a.Execute) $($a.Arguments) $($a.WorkingDirectory)" -match $pat) { $dirty = $true } }
    if (-not $dirty) { continue }
    Say "  $(Mode)задача «$($t.TaskName)»"
    if ($Apply) {
        foreach ($a in $t.Actions) { foreach ($r in $Rules) {
            if ($a.Execute) { $a.Execute = [regex]::Replace($a.Execute, $r.P, $r.R) }
            if ($a.Arguments) { $a.Arguments = [regex]::Replace($a.Arguments, $r.P, $r.R) }
            if ($a.WorkingDirectory) { $a.WorkingDirectory = [regex]::Replace($a.WorkingDirectory, $r.P, $r.R) }
        } }
        try { Set-ScheduledTask -TaskName $t.TaskName -TaskPath $t.TaskPath -Action $t.Actions -ErrorAction Stop | Out-Null }
        catch { Say "    не вышло (нужны права администратора?): $($_.Exception.Message)" Red }
    }
}
$sh = New-Object -ComObject WScript.Shell
$lnkDirs = @([Environment]::GetFolderPath("Startup"), [Environment]::GetFolderPath("Desktop"), "$H\Desktop")
foreach ($l in (Get-ChildItem $lnkDirs -Filter *.lnk -ErrorAction SilentlyContinue | Select-Object -Unique)) {
    $s = $sh.CreateShortcut($l.FullName)
    if ("$($s.TargetPath) $($s.Arguments) $($s.WorkingDirectory)" -notmatch $pat) { continue }
    Say "  $(Mode)ярлык $($l.FullName)"
    if ($Apply) {
        foreach ($r in $Rules) {
            $s.TargetPath = [regex]::Replace($s.TargetPath, $r.P, $r.R)
            $s.Arguments = [regex]::Replace($s.Arguments, $r.P, $r.R)
            $s.WorkingDirectory = [regex]::Replace($s.WorkingDirectory, $r.P, $r.R)
        }
        $s.Save()
    }
}

Say "`n=== 8. Сохранить правки путей на GitHub ===" Cyan
foreach ($r in $byRepo.Keys) {
    if (-not (Test-Path "$r\.git")) { continue }
    $files = $byRepo[$r] | ForEach-Object { $_.Substring($r.Length + 1) }
    Say "  $(Mode)коммит в $r ($($files.Count) файлов)"
    if ($Apply) {
        git -C $r add -- $files
        git -C $r -c user.name="viiiitaaaaa" -c user.email="tehrez21@gmail.com" commit -q -m "Переименование: новые пути и имена репозиториев" -- $files
        git -C $r push -q
        if ($LASTEXITCODE -ne 0) { Say "    push не прошёл, коммит остался на ПК" Yellow }
    }
}

if ($restartBot -and (Test-Path "$H\case-bot\start_bot.bat")) {
    Say "`nЗапускаю бота «Дела» из новой папки" Cyan
    Start-Process "$H\case-bot\start_bot.bat" -WorkingDirectory "$H\case-bot" -WindowStyle Minimized
}

if ($Apply) { Say "`nГотово." Green } else { Say "`nЭто была проба, ничего не изменено. Чтобы сделать: добавь -Apply" Green }
