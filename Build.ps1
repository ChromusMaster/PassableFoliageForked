[CmdletBinding()]
param(
    [ValidateSet('All', 'Fabric', 'NeoForge')][string]$Loader = 'All',
    [ValidateSet('All', '26.2', '26.3')][string]$Minecraft = 'All',
    [ValidateSet('full', 'partial')][string]$Mode = 'full',
    [switch]$IncludeBeta,
    [switch]$Clean
)
$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw 'Python 3.10+ is required. Install it and ensure python is in PATH.' }
$arguments = @((Join-Path $PSScriptRoot 'scripts/build.py'), '--loader', $Loader, '--minecraft', $Minecraft, '--mode', $Mode)
if ($IncludeBeta) { $arguments += '--include-beta' }
if ($Clean) { $arguments += '--clean' }
& $python.Source @arguments
if ($LASTEXITCODE -ne 0) { throw "Build failed (exit code $LASTEXITCODE). Read build/<Loader>/<Minecraft>/<Mod>/logs." }
