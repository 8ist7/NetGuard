@echo off
title NetGuard - Windows Network Diagnostics
echo ==========================================
echo       NETGUARD WINDOWS DIAGNOSTICS
echo ==========================================
echo.

echo [IP CONFIGURATION]
where ipconfig >nul 2>&1 && ipconfig /all || echo ipconfig is unavailable.
echo.

echo [DEFAULT ROUTE]
where route >nul 2>&1 && route print 0.0.0.0 || echo route is unavailable.
echo.

echo [ARP / NEIGHBOR TABLE]
where arp >nul 2>&1 && arp -a || echo arp is unavailable.
echo.

echo [DNS CHECK]
where nslookup >nul 2>&1 && nslookup example.com || echo nslookup is unavailable.
echo.

echo [INTERNET CONNECTIVITY]
where ping >nul 2>&1 && ping -n 2 8.8.8.8 || echo ping is unavailable.
echo.

echo Diagnostics complete.
pause
