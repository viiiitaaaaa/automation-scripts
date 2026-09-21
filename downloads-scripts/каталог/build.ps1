$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch { }

$here = $PSScriptRoot
if (-not $here) { $here = Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $here) { $here = (Get-Location).Path }

$csv      = Join-Path $here 'artmellio_data.csv'
$template = Join-Path $here 'artmellio_catalog_kartinki.xlsx'
$imgdir   = Join-Path $here 'images'
$out      = Join-Path $here 'ARTMELLIO katalog s kartinkami.xlsx'

Write-Host ''
Write-Host '=== ARTMELLIO ===' -ForegroundColor Cyan
Write-Host ("Papka: {0}" -f $here)
Write-Host ''

if (-not (Test-Path $csv))      { Write-Host 'NE NAYDEN artmellio_data.csv' -ForegroundColor Red; return }
if (-not (Test-Path $template)) { Write-Host 'NE NAYDEN artmellio_catalog_kartinki.xlsx' -ForegroundColor Red; return }

New-Item -ItemType Directory -Force -Path $imgdir | Out-Null
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$rows  = @(Import-Csv -Path $csv -Encoding UTF8)
$total = $rows.Count
Write-Host ("Tovarov: {0}" -f $total)

# ---------- shag 1: kartinki ----------
Write-Host 'Shag 1 iz 2 - kartinki...' -ForegroundColor Yellow

$badChars = [IO.Path]::GetInvalidFileNameChars()
$paths    = @{}
$ua       = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
$n = 0
$failed = 0

foreach ($r in $rows) {
    $n++
    $name = [string]$r.title
    foreach ($ch in $badChars) { $name = $name.Replace([string]$ch, '') }
    $name = $name.Trim().TrimEnd('.')
    if ($name.Length -gt 80) { $name = $name.Substring(0, 80) }
    if ([string]::IsNullOrWhiteSpace($name)) { $name = 'product' }
    $file = Join-Path $imgdir ('{0:d3} {1}.jpg' -f $n, $name)

    $ok = Test-Path $file
    if (-not $ok) {
        $url = [string]$r.image
        if ($url.Contains('?')) { $sep = '&' } else { $sep = '?' }
        foreach ($try in @(($url + $sep + 'width=700' + '&' + 'format=jpg'), $url)) {
            try {
                Invoke-WebRequest -Uri $try -OutFile $file -UseBasicParsing -TimeoutSec 40 -UserAgent $ua
                $fs = New-Object IO.FileStream($file, [IO.FileMode]::Open, [IO.FileAccess]::Read)
                $b0 = $fs.ReadByte(); $b1 = $fs.ReadByte(); $fs.Close()
                if (($b0 -eq 255 -and $b1 -eq 216) -or ($b0 -eq 137 -and $b1 -eq 80)) { $ok = $true; break }
                Remove-Item $file -Force -ErrorAction SilentlyContinue
            } catch { Remove-Item $file -Force -ErrorAction SilentlyContinue }
        }
        if (($n % 20) -eq 0) { Write-Host ("   ...{0} / {1}" -f $n, $total) }
    }

    if ($ok) { $paths[$n] = $file } else { $failed++ }
}
Write-Host ("Kartinok gotovo: {0}   net: {1}" -f ($total - $failed), $failed) -ForegroundColor Green

# ---------- shag 2: vstavlyaem v xlsx ----------
Write-Host ''
Write-Host 'Shag 2 iz 2 - vstavlyayu kartinki v Excel-fayl...' -ForegroundColor Yellow

if (Test-Path $out) {
    try { Remove-Item $out -Force }
    catch { Write-Host 'Zakroyte fayl v Excel i zapustite snova.' -ForegroundColor Red; return }
}
Copy-Item $template $out -Force

$SIDE = 500
$zip = [IO.Compression.ZipFile]::Open($out, [IO.Compression.ZipArchiveMode]::Update)
try {
    $done = 0
    for ($i = 1; $i -le $total; $i++) {
        if (-not $paths.ContainsKey($i)) { continue }

        $bytes = $null
        $src = $null; $bmp = $null; $g = $null; $ms = $null
        try {
            $src = [Drawing.Image]::FromFile($paths[$i])
            $bmp = New-Object Drawing.Bitmap($SIDE, $SIDE)
            $g = [Drawing.Graphics]::FromImage($bmp)
            $g.Clear([Drawing.Color]::White)
            $g.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $k = [Math]::Min($SIDE / $src.Width, $SIDE / $src.Height)
            $w = [int]($src.Width * $k)
            $h = [int]($src.Height * $k)
            $g.DrawImage($src, [int](($SIDE - $w) / 2), [int](($SIDE - $h) / 2), $w, $h)
            $ms = New-Object IO.MemoryStream
            $bmp.Save($ms, [Drawing.Imaging.ImageFormat]::Jpeg)
            $bytes = $ms.ToArray()
        }
        catch { $bytes = $null }
        finally {
            if ($g)   { $g.Dispose() }
            if ($bmp) { $bmp.Dispose() }
            if ($src) { $src.Dispose() }
            if ($ms)  { $ms.Dispose() }
        }
        if ($bytes -eq $null) { continue }

        $entryName = 'xl/media/image' + $i + '.jpeg'
        $old = $zip.GetEntry($entryName)
        if ($old) { $old.Delete() }
        $new = $zip.CreateEntry($entryName)
        $st = $new.Open()
        $st.Write($bytes, 0, $bytes.Length)
        $st.Close()

        $done++
        if (($done % 25) -eq 0) { Write-Host ("   ...{0} / {1}" -f $done, $total) }
    }
}
finally {
    $zip.Dispose()
}

Write-Host ''
Write-Host 'GOTOVO' -ForegroundColor Green
Write-Host ("Fayl: {0}" -f $out)
Write-Host ("Kartinki po otdelnosti: {0}" -f $imgdir)
try { Start-Process $out } catch { }
