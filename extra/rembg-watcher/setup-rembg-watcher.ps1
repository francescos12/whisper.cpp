param(
    [string]$BasePath = (Join-Path $env:USERPROFILE 'rembg-watcher')
)

$inputPath = Join-Path $BasePath 'input'
$outputPath = Join-Path $BasePath 'output'

Write-Host "📂 Creo le cartelle di lavoro..."
New-Item -ItemType Directory -Path $inputPath -Force | Out-Null
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null

Write-Host "📦 Installo le dipendenze Python (può metterci un po')..."
python -m pip install -U pip setuptools wheel
python -m pip install -U backgroundremover pillow pillow-heif
python -m pip install -U numpy opencv-python-headless scikit-image scipy tqdm
python -m pip install -U torch torchvision torchaudio
python -m pip install -U aiohttp asyncer gradio filetype python-dotenv moviepy imageio imageio-ffmpeg ffmpeg-python

Write-Host "🛠 Creo gli script di elaborazione..."

$softScript = @"
Get-ChildItem `"$inputPath`" -File | ForEach-Object {
    \$outPng = `"$outputPath\$(\$_.BaseName)_soft.png`"
    backgroundremover -i \$_.FullName -o \$outPng -m isnet-general-use
}
Read-Host -Prompt 'Premi INVIO per chiudere'
"@
Set-Content -Path (Join-Path $BasePath 'Processa_Soft.ps1') -Value $softScript -Encoding UTF8

$mediumScript = @"
Get-ChildItem `"$inputPath`" -File | ForEach-Object {
    \$outPng = `"$outputPath\$(\$_.BaseName)_medium.png`"
    backgroundremover -i \$_.FullName -o \$outPng -m u2net
}
Read-Host -Prompt 'Premi INVIO per chiudere'
"@
Set-Content -Path (Join-Path $BasePath 'Processa_Medium.ps1') -Value $mediumScript -Encoding UTF8

$hardScript = @"
Get-ChildItem `"$inputPath`" -File | ForEach-Object {
    \$outPng = `"$outputPath\$(\$_.BaseName)_hard.png`"
    backgroundremover -i \$_.FullName -o \$outPng -m u2netp
}
Read-Host -Prompt 'Premi INVIO per chiudere'
"@
Set-Content -Path (Join-Path $BasePath 'Processa_Hard.ps1') -Value $hardScript -Encoding UTF8

Write-Host "✅ Installazione completata!"
Write-Host "👉 Metti le foto in: $inputPath"
Write-Host "👉 Risultati in: $outputPath"
Write-Host "👉 Avvii con: Processa_Soft.ps1 / Processa_Medium.ps1 / Processa_Hard.ps1"
