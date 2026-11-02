# Build the local demo (test version) folder: as_center code + demo files + portable PHP.
# Usage: powershell -ExecutionPolicy Bypass -File make_demo.ps1 -Out "<demo folder>" -Php "<portable php folder>"
# Re-running refreshes app code and keeps app\data (demo data) unless the seed is run again.
param([Parameter(Mandatory = $true)][string]$Out, [string]$Php = '', [string]$Zip = '')
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = Join-Path (Split-Path -Parent $here) 'as_center'
$app = Join-Path $Out 'app'
New-Item -ItemType Directory -Force $app | Out-Null

# app code (no install.php: the demo seed installs; no README/.gitignore)
Get-ChildItem $src -Force | Where-Object { $_.Name -notin 'README.md', '.gitignore', 'install.php', 'data', 'config.php' } |
  ForEach-Object { Copy-Item $_.FullName -Destination $app -Recurse -Force }
Copy-Item (Join-Path $here 'config.demo.php') (Join-Path $app 'config.php') -Force
foreach ($f in 'router.php', 'seed_demo.php', 'demo.php') { Copy-Item (Join-Path $here $f) $app -Force }

# .bat files need CRLF for labels/goto
Get-ChildItem $here -Filter *.bat | ForEach-Object {
  $t = [IO.File]::ReadAllText($_.FullName, [Text.Encoding]::UTF8) -replace "`r?`n", "`r`n"
  [IO.File]::WriteAllText((Join-Path $Out $_.Name), $t, (New-Object Text.UTF8Encoding $false))
}
Get-ChildItem $here -Filter *.txt | ForEach-Object { Copy-Item $_.FullName $Out -Force }

# portable PHP (only what the app needs)
if ($Php -and -not (Test-Path (Join-Path $Out 'php\php.exe'))) {
  $dst = Join-Path $Out 'php'
  New-Item -ItemType Directory -Force (Join-Path $dst 'ext') | Out-Null
  Get-ChildItem $Php -File | Where-Object { $_.Name -notmatch '^(icu|deplister|phpdbg|php-cgi|php8embed|php8phpdbg|news|readme-redist|php\.ini-|pharcommand|phar\.phar)' } |
    ForEach-Object { Copy-Item $_.FullName $dst -Force }
  foreach ($e in 'curl', 'fileinfo', 'gd', 'mbstring', 'openssl', 'pdo_sqlite', 'sqlite3') { Copy-Item (Join-Path $Php "ext\php_$e.dll") (Join-Path $dst 'ext') -Force }
  # demo php.ini: only the extensions above (pdo_mysql not needed for the demo)
  $ini = "extension_dir = ""ext""`r`nextension=curl`r`nextension=fileinfo`r`nextension=gd`r`nextension=mbstring`r`nextension=openssl`r`nextension=pdo_sqlite`r`nextension=sqlite3`r`n" +
    "date.timezone = Asia/Seoul`r`nupload_max_filesize = 20M`r`npost_max_size = 60M`r`nmemory_limit = 256M`r`nmax_file_uploads = 10`r`ndisplay_errors = Off`r`nlog_errors = On`r`n"
  [IO.File]::WriteAllText((Join-Path $dst 'php.ini'), $ini, (New-Object Text.UTF8Encoding $false))
}
# app-local VC++ runtime so the folder runs on a PC without the VC++ 2019 redistributable
foreach ($d in 'vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll') {
  $s = Join-Path $env:WINDIR "System32\$d"; $t = Join-Path $Out "php\$d"
  if ((Test-Path $s) -and (Test-Path (Join-Path $Out 'php')) -and -not (Test-Path $t)) { Copy-Item $s $t }
}

# portable ZIP next to the folder (UTF-8 names so Korean file names survive; demo data left out — the .bat makes it)
if ($Zip) {
  Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
  if (Test-Path $Zip) { Remove-Item $Zip }
  $root = Split-Path -Leaf $Out
  $z = [IO.Compression.ZipFile]::Open($Zip, 'Create', [Text.Encoding]::UTF8)
  try {
    Get-ChildItem $Out -Recurse -File | Where-Object { $_.FullName -notlike (Join-Path $app 'data\*') } | ForEach-Object {
      $rel = $root + '/' + $_.FullName.Substring($Out.TrimEnd('\').Length + 1).Replace('\', '/')
      [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($z, $_.FullName, $rel, 'Optimal')
    }
  } finally { $z.Dispose() }
  Write-Output "zip: $Zip"
}
Write-Output "done: $Out"
