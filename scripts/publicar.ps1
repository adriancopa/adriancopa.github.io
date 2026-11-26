# Publica en GitHub Pages los archivos del portafolio que cambiaron, usando la API de GitHub (gh CLI).
# No necesita git instalado. Uso: powershell -File scripts\publicar.ps1 "mensaje del commit"
param([string]$Mensaje = "Actualizacion automatica del portafolio")
$ErrorActionPreference = "Stop"
$env:Path = "C:\Program Files\GitHub CLI;$env:Path"
$repo = "adriancopa/adriancopa.github.io"
$root = Split-Path -Parent $PSScriptRoot
$excluir = '^(\.git|\.vite|node_modules|__pycache__)(/|$)|^data/(linkedin_raw|linkedin_nuevos)\.json$|\.pyc$'

# Arbol remoto: ruta -> sha del blob
$arbol = gh api "repos/$repo/git/trees/main?recursive=1" | ConvertFrom-Json
$remoto = @{}
foreach ($e in $arbol.tree) { if ($e.type -eq "blob") { $remoto[$e.path] = $e.sha } }

function Get-BlobSha([byte[]]$bytes) {
    $cab = [Text.Encoding]::ASCII.GetBytes("blob $($bytes.Length)`0")
    $sha = [Security.Cryptography.SHA1]::Create()
    ($sha.ComputeHash($cab + $bytes) | ForEach-Object { $_.ToString("x2") }) -join ""
}

$subidos = @()
Get-ChildItem $root -Recurse -File -Force | ForEach-Object {
    $rel = $_.FullName.Substring($root.Length + 1).Replace("\", "/")
    if ($rel -match $excluir) { return }
    $bytes = [IO.File]::ReadAllBytes($_.FullName)
    $sha = Get-BlobSha $bytes
    if ($remoto[$rel] -eq $sha) { return }
    $cuerpo = @{ message = $Mensaje; content = [Convert]::ToBase64String($bytes); branch = "main" }
    if ($remoto.ContainsKey($rel)) { $cuerpo.sha = $remoto[$rel] }
    $tmp = [IO.Path]::GetTempFileName()
    [IO.File]::WriteAllText($tmp, ($cuerpo | ConvertTo-Json -Compress), [Text.UTF8Encoding]::new($false))
    gh api -X PUT "repos/$repo/contents/$rel" --input $tmp | Out-Null
    Remove-Item $tmp
    $subidos += $rel
}
if ($subidos.Count) { "Publicados: " + ($subidos -join ", ") } else { "Sin cambios que publicar." }
