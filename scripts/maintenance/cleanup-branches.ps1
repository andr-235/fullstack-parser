# cleanup-branches.ps1
# Автоматическая чистка локальных и удалённых веток, смерженных в main (кроме main и develop)

Write-Host "[GIT CLEANUP] Обновляю информацию о ветках..."
git fetch --all --prune

Write-Host "[GIT CLEANUP] Удаляю локальные ветки, смерженные в main (кроме main и develop)..."
$mergedBranches = git branch --merged main | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne 'main' -and $_ -ne 'develop' -and $_ -ne '*' }
foreach ($branch in $mergedBranches) {
    Write-Host "  - Удаляю локальную ветку: $branch"
    git branch -d $branch
}

Write-Host "[GIT CLEANUP] Удаляю удалённые ветки, смерженные в main (кроме main и develop)..."
$remoteMerged = git branch -r --merged origin/main | ForEach-Object { $_.Trim() } | Where-Object { $_ -notmatch 'origin/(main|develop)$' }
foreach ($remoteBranch in $remoteMerged) {
    $branchName = $remoteBranch -replace 'origin/', ''
    Write-Host "  - Удаляю удалённую ветку: $branchName"
    git push origin --delete $branchName
}

Write-Host "[GIT CLEANUP] Очистка завершена!"
