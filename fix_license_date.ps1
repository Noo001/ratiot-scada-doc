$log = "C:\repos\ratiot-scada-doc\license_fix_log.txt"
$ms = [DateTimeOffset]::Now.ToUnixTimeMilliseconds()
"=== $(Get-Date) новый tag=$ms ===" | Out-File $log

$svc = Get-Service | Where-Object { $_.DisplayName -like "RatioT*" } | Select-Object -First 1
if ($svc) {
    Stop-Service -Name $svc.Name -Force
    Start-Sleep -Seconds 5
    "Служба остановлена: $($svc.Name)" | Out-File $log -Append
}

Set-ItemProperty -Path "HKLM:\SOFTWARE\JavaSoft\Prefs" -Name "tag" -Value "$ms"
Set-ItemProperty -Path "HKCU:\SOFTWARE\JavaSoft\Prefs" -Name "tag" -Value "$ms"
"Реестр обновлён (HKLM + HKCU): tag=$ms" | Out-File $log -Append

[System.IO.File]::WriteAllText("C:\Program Files\RatioTScada\.tag\tag", "$ms")
"Файл .tag\tag записан" | Out-File $log -Append

if ($svc) {
    Start-Service -Name $svc.Name
    Start-Sleep -Seconds 15
    "Служба: $((Get-Service -Name $svc.Name).Status)" | Out-File $log -Append
}
"=== $(Get-Date) конец ===" | Out-File $log -Append
