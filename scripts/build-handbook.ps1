$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
function Build-Tex($source, $build) {
    $buildPath = Join-Path $repoRoot $build
    New-Item -ItemType Directory -Force $buildPath | Out-Null
    Push-Location (Join-Path $repoRoot $source)
    try {
        & latexmk -norc -xelatex -interaction=nonstopmode -halt-on-error "-outdir=$buildPath" main.tex *> "$buildPath/build-console.log"
        if ($LASTEXITCODE -ne 0) {
            Get-Content "$buildPath/build-console.log" -Tail 40
            throw "Compilation failed: $source"
        }
    } finally { Pop-Location }
}
Push-Location $repoRoot
try {
    uv sync --locked
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency sync failed' }
    New-Item -ItemType Directory -Force latex/images, output/pdf | Out-Null
    $examples = @{
        'reimbursement-summary' = 'tmp/latex-summary'
        'cross-campus-summary' = 'tmp/latex-training-summary'
    }
    foreach ($name in $examples.Keys) {
        Build-Tex "latex/examples/$name" $examples[$name]
        Copy-Item "$($examples[$name])/main.pdf" "latex/images/$name.pdf" -Force
        Copy-Item "$($examples[$name])/main.pdf" "output/pdf/$name-example.pdf" -Force
        Build-Tex "latex/forms/$name" "tmp/latex-form-$name"
        uv run --no-sync scripts/prepare-pdf-form.py "tmp/latex-form-$name/main.pdf" "output/pdf/$name-form.pdf"
        if ($LASTEXITCODE -ne 0) { throw "Form preparation failed: $name" }
    }
    Build-Tex latex tmp/latex
    foreach ($check in @('verify-latex.py', 'verify-pdf-forms.py')) {
        uv run --no-sync "scripts/$check"
        if ($LASTEXITCODE -ne 0) { throw "PDF validation failed: $check" }
    }
    Copy-Item tmp/latex/main.pdf output/pdf/SYSU-Reimbursement-Handbook.pdf -Force
    Write-Output 'Built and validated the handbook, two examples, and two fillable forms in output/pdf.'
} finally { Pop-Location }
