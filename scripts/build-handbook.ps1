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
# Examples remain embedded in the handbook; downloads use blank interactive forms.
foreach ($formName in @('reimbursement-summary', 'cross-campus-summary')) {
    $formRoot = Join-Path $latexRoot "forms\$formName"
    $formBuildRoot = Join-Path $projectRoot "tmp\latex-form-$formName"
    New-Item -ItemType Directory -Force $formBuildRoot | Out-Null
    Push-Location $formRoot
    try {
        & latexmk -norc -xelatex -interaction=nonstopmode -halt-on-error "-outdir=$formBuildRoot" main.tex *> (Join-Path $formBuildRoot 'build-console.log')
        if ($LASTEXITCODE -ne 0) {
            Get-Content (Join-Path $formBuildRoot 'build-console.log') -Tail 35
            throw "Form compilation failed: $formName"
        }
    } finally {
        Pop-Location
    }
    & uv run --project $projectRoot (Join-Path $PSScriptRoot 'prepare-pdf-form.py') (Join-Path $formBuildRoot 'main.pdf') (Join-Path $pdfRoot "$formName-form.pdf")
    if ($LASTEXITCODE -ne 0) { throw "Form preparation failed: $formName" }
}
& uv run --project $projectRoot (Join-Path $PSScriptRoot 'verify-pdf-forms.py')
if ($LASTEXITCODE -ne 0) { throw 'Interactive PDF validation failed.' }
# Remove only the two superseded downloadable examples from earlier builds.
foreach ($oldName in @('reimbursement-summary-example.pdf', 'cross-campus-summary-example.pdf')) {
    $oldFile = Join-Path $pdfRoot $oldName
    if (Test-Path -LiteralPath $oldFile) { Remove-Item -LiteralPath $oldFile }
}
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
