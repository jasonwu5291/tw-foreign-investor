# Daily 17:00 Taiwan refresh: scrape Wantgoo and publish to GitHub Pages.
$ErrorActionPreference = "Stop"
Set-Location "C:\Users\Dennis\Downloads\Cursor_foreign"

$env:GIT_AUTHOR_NAME = "jasonwu5291"
$env:GIT_AUTHOR_EMAIL = "jasonwu5291@users.noreply.github.com"
$env:GIT_COMMITTER_NAME = "jasonwu5291"
$env:GIT_COMMITTER_EMAIL = "jasonwu5291@users.noreply.github.com"

& "C:\Users\Dennis\AppData\Local\Programs\Python\Python311\python.exe" scripts/update_data.py
if ($LASTEXITCODE -ne 0) {
  throw "Wantgoo fetch failed with exit $LASTEXITCODE"
}

git add data/foreign.json
if (git diff --cached --quiet) {
  Write-Output "No data change"
  exit 0
}

git commit -m "Refresh 20-day foreign net-buy data (Taiwan 17:00)"
git push origin main
