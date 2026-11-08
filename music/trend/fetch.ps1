# Downloads the ElevenLabs trend-style music beds listed in urls.tsv into this folder (PowerShell 5+).
$ErrorActionPreference='Stop'
Get-Content "$PSScriptRoot\urls.tsv" | ForEach-Object {
  $p=$_ -split "`t"; if($p.Length -lt 2){return}
  $f=Join-Path $PSScriptRoot $p[0]
  Invoke-WebRequest -Uri $p[1] -OutFile $f -UseBasicParsing
  Write-Host ("{0} {1} bytes" -f $p[0], (Get-Item $f).Length)
}
