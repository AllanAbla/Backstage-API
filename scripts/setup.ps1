param(
  [switch]$Docker = $false
)

Write-Host "== Backstage API setup =="

# 1) Python deps
if (!(Test-Path .venv)) {
  py -3 -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2) dotenv
if (!(Test-Path .env)) {
  Copy-Item ".env.example" ".env"
}

# 3) Mongo: Docker ou local
$envPath = Get-Content .env | Out-String
$uri = ($envPath -split "`n" | Where-Object {$_ -match "^MONGODB_URI="}) -replace "MONGODB_URI=", ""
if ($Docker) {
  Write-Host ">> Trying Docker..."
  try {
    docker version | Out-Null
    docker ps -a --format "{{.Names}}" | findstr /i "theaters-mongo" > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
      docker run -d --name theaters-mongo -p 27017:27017 mongo:7 | Out-Null
    } else {
      docker start theaters-mongo | Out-Null
    }
  } catch {
    Write-Host "Docker não está disponível. Inicie o Docker Desktop ou rode sem -Docker" -ForegroundColor Yellow
  }
} else {
  Write-Host ">> Usando Mongo local em $uri (certifique-se que o serviço está ativo)"
}

# 4) seed (teatros)
$env:MONGODB_URI = if ($uri) { $uri.Trim() } else { "mongodb://localhost:27017" }
$env:MONGODB_DB = "theatersdb"
python .\seeds\seed.py

Write-Host "`n== Pronto! Para iniciar:" -ForegroundColor Green
Write-Host "uv run app/main.py"