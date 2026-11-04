$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$latexRoot = Join-Path $projectRoot 'latex'
$buildRoot = Join-Path $projectRoot 'tmp\latex'
$pdfRoot = Join-Path $projectRoot 'output\pdf'
New-Item -ItemType Directory -Force $buildRoot, $pdfRoot | Out-Null
Get-Command latexmk,xelatex,uv -ErrorAction Stop | Out-Null
New-Item -ItemType Directory -Force (Join-Path $latexRoot 'images') | Out-Null
$exampleRoot = Join-Path $latexRoot 'examples\reimbursement-summary'
$exampleBuildRoot = Join-Path $projectRoot 'tmp\latex-summary'
New-Item -ItemType Directory -Force $exampleBuildRoot | Out-Null
Push-Location $exampleRoot
try {
    & latexmk -norc -xelatex -interaction=nonstopmode -halt-on-error "-outdir=$exampleBuildRoot" main.tex *> (Join-Path $exampleBuildRoot 'build-console.log')
    if ($LASTEXITCODE -ne 0) {
        Get-Content (Join-Path $exampleBuildRoot 'build-console.log') -Tail 35
        throw 'Summary example compilation failed.'
    }
} finally {
    Pop-Location
}
Copy-Item -LiteralPath (Join-Path $exampleBuildRoot 'main.pdf') -Destination (Join-Path $latexRoot 'images\reimbursement-summary.pdf') -Force
Copy-Item -LiteralPath (Join-Path $exampleBuildRoot 'main.pdf') -Destination (Join-Path $pdfRoot 'reimbursement-summary-example.pdf') -Force
$trainingExampleRoot = Join-Path $latexRoot 'examples\cross-campus-summary'
$trainingExampleBuildRoot = Join-Path $projectRoot 'tmp\latex-training-summary'
New-Item -ItemType Directory -Force $trainingExampleBuildRoot | Out-Null
Push-Location $trainingExampleRoot
try {
    & latexmk -norc -xelatex -interaction=nonstopmode -halt-on-error "-outdir=$trainingExampleBuildRoot" main.tex *> (Join-Path $trainingExampleBuildRoot 'build-console.log')
    if ($LASTEXITCODE -ne 0) {
        Get-Content (Join-Path $trainingExampleBuildRoot 'build-console.log') -Tail 35
        throw 'Training summary example compilation failed.'
    }
} finally {
    Pop-Location
}
Copy-Item -LiteralPath (Join-Path $trainingExampleBuildRoot 'main.pdf') -Destination (Join-Path $latexRoot 'images\cross-campus-summary.pdf') -Force
Copy-Item -LiteralPath (Join-Path $trainingExampleBuildRoot 'main.pdf') -Destination (Join-Path $pdfRoot 'cross-campus-summary-example.pdf') -Force
Push-Location $latexRoot
try {
    & latexmk -norc -xelatex -interaction=nonstopmode -halt-on-error -synctex=1 "-outdir=$buildRoot" main.tex *> (Join-Path $buildRoot 'build-console.log')
    if ($LASTEXITCODE -ne 0) {
        Get-Content (Join-Path $buildRoot 'build-console.log') -Tail 45
        throw "LaTeX compilation failed (exit $LASTEXITCODE)."
    }
} finally {
    Pop-Location
}
& uv run --project $projectRoot (Join-Path $PSScriptRoot 'verify-latex.py')
if ($LASTEXITCODE -ne 0) { throw 'PDF validation failed.' }
Copy-Item -LiteralPath (Join-Path $buildRoot 'main.pdf') -Destination (Join-Path $pdfRoot 'SYSU-Reimbursement-Handbook.pdf') -Force
Write-Output 'Published output/pdf/SYSU-Reimbursement-Handbook.pdf from LaTeX.'
