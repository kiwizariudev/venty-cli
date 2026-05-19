Set-Location $PSScriptRoot\..
$py = if (Test-Path ".\env\Scripts\python.exe") { ".\env\Scripts\python.exe" } else { "python" }
& $py cli.py
