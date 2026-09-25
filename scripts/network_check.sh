#!/bin/bash
set +e

echo "=========================================="
echo "       NETGUARD LINUX / KALI DIAGNOSTICS"
echo "=========================================="
echo

run_if_available() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "$1 is not installed or not available."
    return
  }
  echo "[$2]"
  shift 2
  "$@"
  echo
}

run_if_available ip "INTERFACES" ip addr
run_if_available ip "DEFAULT ROUTE" ip route
run_if_available ip "NEIGHBOR DEVICES" ip neigh
run_if_available ping "INTERNET CONNECTIVITY" ping -c 2 8.8.8.8
run_if_available traceroute "TRACEROUTE" traceroute -m 8 -w 2 8.8.8.8
run_if_available tracepath "TRACEPATH" tracepath -m 8 8.8.8.8
run_if_available nslookup "DNS CHECK (NSLOOKUP)" nslookup example.com
run_if_available dig "DNS CHECK (DIG)" dig +short example.com

echo "Diagnostics complete."
