# Inbox test for YardSwaps outreach email 1. Sends ONE copy per address you pass, through Resend, from hello@mail.yardswaps.com.
# Usage:  $env:RESEND_API_KEY="<value from Railway web service > Variables>"
#         powershell -File send-test.ps1 first@example.com second@example.com
# The key is read from the environment only and never written anywhere.
param([Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)][string[]]$To)
$key = $env:RESEND_API_KEY
if (-not $key) { $key = Read-Host "RESEND_API_KEY" }
$template = (Get-Content -Raw -Encoding UTF8 "$PSScriptRoot\email1.json" | ConvertFrom-Json)[0]
$batch = @()
foreach ($addr in $To) {
  $m = $template.PSObject.Copy()
  $m.to = @($addr)
  $batch += $m
}
$json = ConvertTo-Json -InputObject $batch -Depth 6 -Compress
Invoke-RestMethod -Method Post -Uri "https://api.resend.com/emails/batch" -Headers @{ Authorization = "Bearer $key" } -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($json))
