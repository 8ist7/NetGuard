# NetGuard — Network Monitoring & Security Dashboard

NetGuard is a local network monitoring portfolio project built with **Python, Flask, HTML, CSS, JavaScript and SQLite**. It performs real checks on the machine where the Flask application is running and provides a controlled scanner for localhost/private IPv4 targets.

## Project Overview

The dashboard combines:

- Network Monitoring
- IP & Gateway Monitoring
- DNS Monitoring
- Ping & Latency Monitoring
- Active Device Discovery
- Local Service Monitoring
- Controlled Private-Network Port Scanning
- Security & Monitoring Event Logging
- SQLite persistence
- CSV export
- Fixed Windows CMD diagnostics
- Linux/Kali Bash diagnostics

**No fake network devices, scan results or security events are generated.**

## Features

### Network Monitoring

The dashboard reads the local operating system/network state and checks:

- Local IPv4 address
- Network interface
- Default gateway
- Configured DNS server
- Internet reachability using a real ping to `8.8.8.8`
- DNS resolution of `example.com`
- Gateway reachability
- Ping latency

Health states are:

- **HEALTHY** — internet, DNS and gateway checks are working
- **DEGRADED** — at least one check works, but another check needs attention
- **OFFLINE** — the connectivity checks are not responding

### IP & Gateway Monitoring

The IP, interface and default route are collected from the local operating system. The dashboard does not invent an address when detection fails; it displays `Unavailable`.

### DNS Monitoring

The configured DNS server is read from the local operating system. A real DNS resolution test is also performed for `example.com`.

### Ping & Latency Monitoring

The Ping control performs a real operating-system ICMP ping. The result and measured latency are returned to the dashboard and logged as a `PING` event.

### Active Device Discovery

The dashboard reads:

- Windows `arp -a`
- Linux/Kali `ip neigh`

It filters invalid, broadcast, multicast and duplicate entries.

The UI description is intentionally limited:

> Displays devices currently visible through the local ARP/neighbor table.

It does **not** claim that every device on the LAN is discovered. Vendor identification is shown as `Unknown` unless a safe local method provides it.

### Local Service Monitoring

NetGuard checks TCP connectivity on localhost for:

| Service | Port |
|---|---:|
| SSH | 22 |
| HTTP | 80 |
| HTTPS | 443 |
| MySQL | 3306 |
| NetGuard | 5000 |
| HTTP-Alt | 8080 |

These are real TCP connection tests. NetGuard itself should show **OPEN** on port `5000` while the Flask application is running.

MySQL is only monitored as a local service. SQLite remains the application's database.

## Private Network Port Scanner

The scanner performs real TCP connection tests.

Inputs:

- Target IP / hostname
- Start Port
- End Port
- Scan
- Clear

Results:

| Port | Status | Service | TCP Response |
|---|---|---|---|

The scanner also reports:

- Scan status
- Open ports count
- Closed ports count
- Scan duration

### Security Restrictions

Only these IPv4 ranges are allowed:

- `127.0.0.0/8`
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

`localhost` is accepted and normalized to `127.0.0.1`.

The scanner rejects:

- Public Internet targets
- Invalid IP addresses
- Hostnames that resolve outside the permitted ranges
- Invalid port numbers
- Port ranges larger than 100 ports
- Reversed port ranges

Error example:

> Only localhost and private-network targets are allowed.

This scanner is intended only for systems and networks you own or are authorized to test.

## Security & Monitoring Event Logging

Events are stored in SQLite and include:

- Timestamp
- Event Type
- Severity
- Description

Event types include:

- `CONNECTIVITY`
- `DNS`
- `GATEWAY`
- `PING`
- `PORT_SCAN`
- `SERVICE_STATUS`
- `DEVICE_DISCOVERY`
- `DIAGNOSTIC`

Severity levels used by the application are:

- `INFO`
- `WARNING`
- `ERROR`

The event log is **Security & Monitoring Event Logging**. It is not a full intrusion detection system.

NetGuard does not claim:

- Full IDS
- Enterprise SOC
- Malware detection
- Antivirus
- Full vulnerability scanning
- Internet-wide scanning
- Attack detection
- Complete network visibility

## SQLite Database

The application automatically creates:

`database/netguard.db`

It creates the required tables automatically and stores monitoring snapshots and security/monitoring events.

Events are loaded from SQLite when the dashboard is opened and remain after Flask is restarted.

## CSV Export

The **Export CSV** button downloads:

`netguard_events.csv`

The CSV contains:

- Timestamp
- Event Type
- Severity
- Description

## Windows Diagnostics

Run the Windows diagnostic script:

`scripts\windows_network.bat`

The fixed diagnostic script uses:

- `ipconfig`
- `route`
- `arp`
- `nslookup`
- `ping`

It does not accept arbitrary dashboard commands.

## Linux/Kali Diagnostics

Run:

```bash
chmod +x scripts/network_check.sh
./scripts/network_check.sh
```

The script uses the commands available on the system:

- `ip addr`
- `ip route`
- `ip neigh`
- `ping`
- `traceroute`
- `tracepath`
- `nslookup`
- `dig`

Missing commands are reported instead of crashing the script.

## Automatic Refresh

The dashboard automatically refreshes every **30 seconds**.

It updates:

- Connectivity
- Latency
- Gateway
- DNS
- Local services
- Active devices
- Stored events

The UI displays a **Last Updated** timestamp.

## Manual Testing

Buttons are available for:

- Test Connectivity
- Test DNS
- Test Gateway
- Ping a supplied host/IP

A loading state is shown while a manual test runs so the browser remains responsive.

## Installation

### Requirements

- Python 3.10+ recommended
- Flask 3.x
- Windows, Linux or Kali Linux
- Network commands appropriate to the operating system

The project intentionally has only the required Python dependency in `requirements.txt`.

## How to Run on Windows

### Easiest method

1. Extract the ZIP.
2. Open the `NetGuard_Master_Final` folder.
3. Double-click **`RUN_NETGUARD.bat`**.
4. The single master launcher enters `NetGuard_V2`, creates a virtual environment if needed, and installs the requirements.
5. Flask starts on `127.0.0.1:5000`.
6. Open:

`http://127.0.0.1:5000`

### Manual method

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python backend\app.py
```

Then open `http://127.0.0.1:5000`.

## How to Run on Linux/Kali

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 backend/app.py
```

Then open `http://127.0.0.1:5000`.

## Project Architecture

```text
Browser Dashboard
       |
       v
Flask API
       |
       +--> Network monitoring functions
       |       +--> IP / interface / gateway / DNS
       |       +--> ping / latency
       |       +--> ARP / neighbor discovery
       |       +--> local TCP service checks
       |       +--> controlled TCP port scanner
       |
       +--> SQLite
               +--> security_events
               +--> monitoring_snapshots
```

## Folder Structure

```text
NetGuard_V2/
├── backend/
│   ├── app.py
│   ├── database.py
│   └── monitor.py
├── database/
│   └── .gitkeep
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── scripts/
│   ├── network_check.sh
│   └── windows_network.bat
├── .gitignore
├── README.md
├── requirements.txt
└── (launcher is the master-folder `RUN_NETGUARD.bat`)
```

The SQLite database is created automatically in `database/netguard.db`.

## README Demo Test

### STEP 1

Start NetGuard.

### STEP 2

Open the dashboard.

### STEP 3

Go to:

**Private Network Port Scanner**

### STEP 4

Enter:

**Target:**

`127.0.0.1`

**Start Port:**

`5000`

**End Port:**

`5000`

### STEP 5

Click **Scan**.

### Expected

**Port:** `5000`

**Status:** `OPEN`

**Service:** `NetGuard`

The result is produced by a real TCP connection test against the running Flask application.

### STEP 6

Scan an unused local port.

For example, if port `4999` is unused:

`127.0.0.1` → `4999` → `4999`

### Expected

**Status:** `CLOSED`

The exact result depends on what is actually running on the computer.

### STEP 7

Check:

**Security & Monitoring Events**

### Expected

A `PORT_SCAN` event is present with the scanned target/range and the number of open ports.

## Functional Validation Checklist

Before presentation, verify:

- [ ] Application starts successfully
- [ ] Dashboard loads
- [ ] Local IP detected
- [ ] Network interface detected
- [ ] Gateway detected
- [ ] DNS detected
- [ ] Internet status checked
- [ ] Ping works
- [ ] Latency displayed
- [ ] Active devices displayed from ARP/neighbor data
- [ ] Broadcast/multicast entries filtered
- [ ] Local services checked
- [ ] NetGuard port 5000 detected as OPEN while Flask is running
- [ ] MySQL 3306 detected if actually running
- [ ] Port scanner accepts private targets
- [ ] Port scanner rejects public targets
- [ ] Port scanner detects OPEN ports
- [ ] Port scanner detects CLOSED ports
- [ ] Port range is limited to 100 ports
- [ ] `PORT_SCAN` event created
- [ ] Events stored in SQLite
- [ ] Events remain after restart
- [ ] CSV export works
- [ ] Windows diagnostics work
- [ ] Linux/Kali diagnostics script exists
- [ ] Automatic refresh works
- [ ] No fake data
- [ ] No fake devices
- [ ] No fake security events
- [ ] Application handles network errors without crashing
- [ ] README is updated
- [ ] requirements.txt is correct
- [ ] run_netguard.bat works

## Interview Demonstration Flow

1. Start NetGuard with `run_netguard.bat`.
2. Explain that the dashboard uses real local operating-system/network checks.
3. Point out the detected local IP, interface, gateway and DNS.
4. Show Internet/DNS/Gateway health and the real latency measurement.
5. Show Local Services and explain that each status is a TCP connection test.
6. Point out **NetGuard : 5000 OPEN** while the application is running.
7. Open **Private Network Port Scanner**.
8. Run the required `127.0.0.1:5000` test.
9. Explain that the scanner is restricted to localhost/private IPv4 ranges and 100 ports.
10. Scan another unused localhost port to demonstrate `CLOSED`.
11. Open Security & Monitoring Events and show the persistent `PORT_SCAN` entry.
12. Click Export CSV and show the downloaded event file.
13. Show the Windows diagnostic batch file.
14. If using Kali, run `scripts/network_check.sh`.
15. Finish by explaining the SQLite persistence and the limitations of ARP-based device visibility.

## Resume Claim

The implemented project supports this factual resume description:

> **NetGuard — Network Monitoring & Security Dashboard**  
> Developed a Python/Flask dashboard for network connectivity, IP/gateway monitoring, DNS checks, ping/latency measurement, active-device discovery, local service monitoring and controlled private-network port scanning. Integrated SQLite-based event logging with severity and CSV export, along with Windows CMD and Linux Bash network diagnostic scripts.

The project should only be described using features that are actually implemented and tested.
