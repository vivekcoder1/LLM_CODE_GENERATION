Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PHIFLOW RAG PIPELINE + VALIDATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Generating simulations with LLM...`n" -ForegroundColor Yellow
python llm-querying.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Pipeline generation failed!`n" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/2] Validating generated scripts...`n" -ForegroundColor Yellow
python test_generated_scripts.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ All steps completed successfully!`n" -ForegroundColor Green
} else {
    Write-Host "`n✗ Validation step had failures.`n" -ForegroundColor Red
}
