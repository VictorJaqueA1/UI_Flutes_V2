param(
    [int]$Port = 8001,
    [int]$BackendPort = 8000,
    [int]$BackendStartupTimeoutSeconds = 20
)

$projectRoot = $PSScriptRoot
$frontendPath = Join-Path $projectRoot "frontend_2"
$backendLogPath = Join-Path $projectRoot ".run_ui_backend.log"

if (-not (Test-Path -LiteralPath $frontendPath)) {
    throw "No se encontro la carpeta frontend_2 en: $frontendPath"
}

$pythonCandidates = @(
    "C:\Users\victo\AppData\Local\Programs\Python\Python312\python.exe",
    "python",
    "py"
)

$pythonCommand = $null

foreach ($candidate in $pythonCandidates) {
    if ($candidate -like "*\*") {
        if (Test-Path -LiteralPath $candidate) {
            $pythonCommand = $candidate
            break
        }
    } else {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            $pythonCommand = $candidate
            break
        }
    }
}

if (-not $pythonCommand) {
    throw "No encontre Python. Instala Python o ajusta run_ui.ps1 con la ruta correcta."
}

function Test-BackendHealth {
    param(
        [int]$Port
    )

    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 2
        return $response.status -eq "ok"
    } catch {
        return $false
    }
}

$backendJob = $null
$backendManagedByScript = $false

if (Test-BackendHealth -Port $BackendPort) {
    Write-Host ""
    Write-Host "Backend ya disponible en: http://127.0.0.1:$BackendPort/api/health" -ForegroundColor DarkCyan
} else {
    if (Test-Path -LiteralPath $backendLogPath) {
        Remove-Item -LiteralPath $backendLogPath -Force -ErrorAction SilentlyContinue
    }

    $backendJob = Start-Job -Name "flute-backend-$PID" -ArgumentList $projectRoot, $pythonCommand, $BackendPort, $backendLogPath -ScriptBlock {
        param(
            [string]$ProjectRoot,
            [string]$PythonCommand,
            [int]$BackendPort,
            [string]$BackendLogPath
        )

        Set-Location -LiteralPath $ProjectRoot

        if ($PythonCommand -eq "py") {
            & $PythonCommand -3 -m uvicorn backend.api.app:app --host 127.0.0.1 --port $BackendPort *>> $BackendLogPath
        } else {
            & $PythonCommand -m uvicorn backend.api.app:app --host 127.0.0.1 --port $BackendPort *>> $BackendLogPath
        }
    }
    $backendManagedByScript = $true

    Write-Host ""
    Write-Host "Levantando backend en: http://127.0.0.1:$BackendPort/api/health" -ForegroundColor Cyan

    $deadline = (Get-Date).AddSeconds($BackendStartupTimeoutSeconds)
    $backendReady = $false

    while ((Get-Date) -lt $deadline) {
        if (Test-BackendHealth -Port $BackendPort) {
            $backendReady = $true
            break
        }

        if ($backendJob.State -in @("Completed", "Failed", "Stopped")) {
            break
        }

        Start-Sleep -Milliseconds 500
    }

    if (-not $backendReady) {
        $jobState = if ($backendJob) { $backendJob.State } else { "desconocido" }
        $logTail = ""

        if (Test-Path -LiteralPath $backendLogPath) {
            $logTail = (Get-Content -LiteralPath $backendLogPath -Tail 40 -ErrorAction SilentlyContinue) -join [Environment]::NewLine
        }

        if ($backendJob) {
            Receive-Job -Job $backendJob -Keep -ErrorAction SilentlyContinue | Out-Null
        }

        throw @"
No se pudo levantar el backend en el puerto $BackendPort.
Estado del job: $jobState
Log: $backendLogPath

$logTail
"@
    }

    Write-Host "Backend listo." -ForegroundColor Green
}

Write-Host ""
Write-Host "UI disponible en: http://127.0.0.1:$Port/" -ForegroundColor Cyan
Write-Host "Backend disponible en: http://127.0.0.1:$BackendPort/api/health" -ForegroundColor DarkCyan
Write-Host "Para detener el servidor: Ctrl + C" -ForegroundColor DarkGray
Write-Host ""

Set-Location -LiteralPath $frontendPath

try {
    if ($pythonCommand -eq "py") {
        & $pythonCommand -3 -m http.server $Port
    } else {
        & $pythonCommand -m http.server $Port
    }
} finally {
    if ($backendManagedByScript -and $backendJob) {
        Stop-Job -Job $backendJob -ErrorAction SilentlyContinue | Out-Null
        Remove-Job -Job $backendJob -Force -ErrorAction SilentlyContinue | Out-Null
    }
}
