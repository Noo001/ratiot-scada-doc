$log = "C:\repos\ratiot-scada-doc\install_log.txt"
"=== $(Get-Date) начало ===" | Out-File $log

$svc = Get-Service | Where-Object { $_.DisplayName -like "RatioT*" } | Select-Object -First 1
if ($svc) {
    "Останавливаем службу: $($svc.Name) / $($svc.DisplayName)" | Out-File $log -Append
    Stop-Service -Name $svc.Name -Force
    Start-Sleep -Seconds 5
} else {
    "Служба RatioT не найдена" | Out-File $log -Append
}

"=== Запуск установщика (тихий режим) ===" | Out-File $log -Append
& "C:\Users\Andrey\Downloads\RatioT_SCADA_full_6.41.12_windows-x64.exe" -q -varfile "C:\Program Files\RatioTScada\.install4j\response.varfile" | Out-File $log -Append
"Код возврата установщика: $LASTEXITCODE" | Out-File $log -Append

if ($svc) {
    "Запускаем службу: $($svc.Name)" | Out-File $log -Append
    Start-Service -Name $svc.Name
    Start-Sleep -Seconds 10
    $svc2 = Get-Service -Name $svc.Name
    "Состояние службы: $($svc2.Status)" | Out-File $log -Append
}
"=== $(Get-Date) конец ===" | Out-File $log -Append
