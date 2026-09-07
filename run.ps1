Set-Location $PSScriptRoot
python verification\run_cross_proof.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python firmware\host_observer.py
