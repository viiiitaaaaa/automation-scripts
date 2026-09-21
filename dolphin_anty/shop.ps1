# Обёртка над Shopify CLI для магазина ARTMELLIO.
# Подставляет свежий Admin API токен, чтобы CLI НИКОГДА не открывал браузер.
# Использование:  .\shop.ps1 theme list
#                 .\shop.ps1 theme pull --theme 188705603964
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

# Запрет на OAuth-команды: только они дёргают системный Chrome.
$line = ($CliArgs -join " ")
if ($line -match '^(auth|login|logout|app)\b' -or $line -match '^store\s+auth\b') {
    Write-Host "'shopify $line' открывает системный Chrome - запрещено." -ForegroundColor Red
    Write-Host "Работаем только по токену: theme / version / config." -ForegroundColor Yellow
    exit 1
}

$env:SHOPIFY_CLI_THEME_TOKEN  = python "$PSScriptRoot\shop_api.py"
$env:SHOPIFY_FLAG_STORE       = "kmfmxn-r4.myshopify.com"
$env:SHOPIFY_CLI_NO_ANALYTICS = "1"

& shopify @CliArgs
