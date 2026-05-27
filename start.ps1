#!/usr/bin/env pwsh

Write-Output "Parando containers antigos..."
docker compose down -v

Write-Output "Rebuildando imagens..."
docker compose build --no-cache

Write-Output "Treinando o modelo..."
docker compose run --rm trainer

Write-Output "Iniciando API..."
docker compose up -d api

Write-Output "Verificando API..."

do {
    Write-Output "Aguardando API..."
    Start-Sleep -Seconds 2
}
until (Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet)

Write-Output "Iniciando Streamlit..."
docker compose up -d streamlit

Write-Output "Tudo iniciado com sucesso!"