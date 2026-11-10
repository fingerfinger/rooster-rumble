# ROOSTER RUMBLE Unified MVP Handoff Snapshot Tool
$rootDir = "d:\OneDrive\업무_진행\C\ROOSTER RUMBLE"

Write-Host "ROOSTER RUMBLE: Unified MVP handoff snapshot" -ForegroundColor Cyan
Write-Host "Root: $rootDir"
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')"
Write-Host ""

$files = @(
    "HANDOFF.md",
    "통합 MVP 구성안.md",
    "통합 MVP 마스터 데이터 테이블.md",
    "data/01_derby_race_daily_schedule_72.csv",
    "data/02_rumble_pit_daily_matches_48.csv",
    "data/03_roosters_base_stats_1st.csv",
    "data/04_roosters_derby_stats_2nd.csv",
    "data/05_roosters_pit_stats_2nd.csv",
    "data/06_egg_gacha_master_list_65.csv",
    "versions/CHANGELOG.md"
)

foreach ($f in $files) {
    $fullP = Join-Path $rootDir $f
    if (Test-Path $fullP) {
        $item = Get-Item $fullP
        Write-Host "OK     $f ($($item.Length) bytes)" -ForegroundColor Green
    } else {
        Write-Host "MISSING $f" -ForegroundColor Red
    }
}
