# Forward arguments to the isolated combined-KG runner. Its default is cached
# retrieval only; execution and fresh generation require explicit CLI options.
$ErrorActionPreference = 'Stop'
$runnerPath = Join-Path $PSScriptRoot 'knowledge_context\run_combined_experiment.py'

Write-Host 'PhiFlow code + domain knowledge graph pipeline' -ForegroundColor Cyan
& python $runnerPath @args
$pipelineExitCode = $LASTEXITCODE

if ($pipelineExitCode -eq 0) {
    Write-Host 'Runner completed. Inspect the manifest and report for per-domain statuses.' -ForegroundColor Green
}
else {
    Write-Host "Runner exited with code $pipelineExitCode." -ForegroundColor Red
}

exit $pipelineExitCode
