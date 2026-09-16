$log = "C:\repos\ratiot-scada-doc\install_100tags_log.txt"
"=== $(Get-Date) начало установки в режиме 100 тегов ===" | Out-File $log

$svc = Get-Service | Where-Object { $_.DisplayName -like "RatioT*" } | Select-Object -First 1
if ($svc) {
    "Останавливаем службу: $($svc.Name)" | Out-File $log -Append
    Stop-Service -Name $svc.Name -Force
    Start-Sleep -Seconds 5
}

"Запуск установщика с varfile license=1" | Out-File $log -Append
& "C:\Users\Andrey\Downloads\RatioT_SCADA_full_6.41.12_windows-x64.exe" -q -varfile "C:\Users\Andrey\AppData\Local\Temp\response_100tags.varfile" | Out-File $log -Append
"Код возврата установщика: $LASTEXITCODE" | Out-File $log -Append

if ($svc) {
    Start-Service -Name $svc.Name
    Start-Sleep -Seconds 15
    $svc2 = Get-Service -Name $svc.Name
    "Состояние службы: $($svc2.Status)" | Out-File $log -Append
}
"=== $(Get-Date) конец ===" | Out-File $log
