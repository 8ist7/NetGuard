# NetGuard — Network Monitoring & Security Dashboard

NetGuard is a local network monitoring and diagnostics dashboard built with **Python, Flask, SQLite, HTML5, CSS3, and JavaScript**.

It provides a centralized interface for viewing network information, checking connectivity, discovering devices on the local network, monitoring local services, performing controlled TCP port checks, and recording monitoring and security-related events.

---

## Features

### 🌐 Network Information

NetGuard provides information about the current network environment, including:

- Local IP address
- Network interface
- Default gateway
- DNS information
- Connectivity status
- Network health information
- Ping and latency information

### 🔎 Local Device Discovery

NetGuard can inspect the local ARP/neighbor table to identify devices visible to the system.

The discovery information can include:

- IP address
- MAC address
- Network state
- Neighbor information
- Discovered devices

### 🖥️ Local Service Monitoring

NetGuard can monitor selected TCP services and determine whether they are reachable.

The application can check:

- NetGuard Flask service
- Local development services
- Other configured TCP services

Service monitoring provides information such as:

- Service name
- Host
- Port
- Availability
- Response status

### 🔐 Controlled TCP Port Scanner

NetGuard includes a controlled TCP port scanning feature for network diagnostics.

Capabilities include:

- TCP connectivity checks
- Configurable target IP
- Configurable port range
- Open/closed port detection
- Maximum scan limits
- Input validation

The scanner is intended for authorized systems and local network troubleshooting.

### 🚨 Security & Monitoring Events

NetGuard records monitoring and security-related events using a local SQLite database.

Events can include:

- Network status changes
- Service availability changes
- Monitoring alerts
- Diagnostic events
- Security-related observations

Each event can contain:

- Timestamp
- Event type
- Severity
- Description

### 📊 Dashboard

The web dashboard provides a centralized view of network monitoring information.

It brings together:

- Network information
- Connectivity status
- Device discovery
- Service monitoring
- Port scanning
- Security events
- Monitoring information

### 🔄 Automatic Updates

The dashboard supports automatic refresh of monitoring information.

### 📁 CSV Export

Monitoring and event information can be exported in CSV format.

---

## Architecture

```text
┌───────────────────────────────┐
│        Web Dashboard          │
│       HTML / CSS / JS         │
└───────────────┬───────────────┘
                │
                │ HTTP / JSON
                ▼
┌───────────────────────────────┐
│        Flask Backend          │
│            Python             │
├───────────────────────────────┤
│ Network Monitoring            │
│ Device Discovery              │
│ Service Monitoring            │
│ TCP Port Scanner              │
│ Event Management              │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│            SQLite             │
│       Local Event Storage     │
└───────────────────────────────┘
```

---

## Technology Stack

### Backend

- Python
- Flask
- SQLite

### Frontend

- HTML5
- CSS3
- JavaScript

### Networking

- TCP socket checks
- ICMP/ping diagnostics
- ARP/neighbor-table inspection
- Network interface information

### Platform Support

- Windows
- Linux
- Kali Linux

---

## Project Structure

```text
NetGuard/
│
├── backend/
│   ├── app.py
│   ├── database.py
│   └── monitor.py
│
├── database/
│   └── .gitkeep
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── scripts/
│   ├── network_check.sh
│   └── windows_network.bat
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Requirements

- Python 3.x
- pip
- Git

### Windows

- Command Prompt or PowerShell

### Linux / Kali Linux

- Terminal
- Python 3
- pip

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/8ist7/NetGuard.git
cd NetGuard
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / Kali Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running NetGuard

Start the Flask application:

```bash
python backend/app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## Network Monitoring

The dashboard provides information about the current system's network configuration.

Typical information includes:

```text
Local IP
Network Interface
Gateway
DNS
Connectivity
Latency
```

---

## Device Discovery

NetGuard uses the system's local ARP/neighbor information to identify devices visible to the host.

The results may include:

```text
IP Address
MAC Address
State
```

Device discovery is limited to information available to the local operating system.

---

## Service Monitoring

NetGuard can check configured TCP services and determine whether they are reachable.

Example:

```text
Service: NetGuard
Host: 127.0.0.1
Port: 5000
Status: Available
```

---

## TCP Port Scanner

The built-in port scanner performs controlled TCP connection checks.

Example:

```text
Target: 192.168.1.10

Ports:
22
80
443
8080
```

### Scanner Restrictions

- Private IPv4 network targeting
- Maximum port limits
- Input validation
- Controlled TCP checks

Only scan systems and networks that you own or have explicit permission to test.

---

## Event Logging

NetGuard stores monitoring events locally using SQLite.

The event system records:

```text
Timestamp
Event Type
Severity
Description
```

Example event categories:

```text
Network
Service
Monitoring
Security
Diagnostic
```

---

## Database

NetGuard uses **SQLite** for local data storage.

The database can store:

- Monitoring events
- Security events
- Diagnostic information
- Event timestamps
- Severity information

---

## CSV Export

Monitoring records can be exported to CSV format.

CSV files can be opened using:

- Microsoft Excel
- LibreOffice Calc
- Google Sheets
- Python
- Other data-analysis tools

---

## Windows Diagnostics

NetGuard includes Windows-specific diagnostic support through:

```text
scripts/windows_network.bat
```

The script can be used for common Windows network diagnostics.

---

## Linux / Kali Diagnostics

Linux-based systems can use:

```text
scripts/network_check.sh
```

The script provides basic network diagnostic information from the Linux environment.

---

## Security Scope

NetGuard is designed as a **local network monitoring and diagnostics project**.

The project focuses on:

- Network visibility
- Connectivity diagnostics
- Local device discovery
- Service monitoring
- Controlled TCP checks
- Security event logging

NetGuard does not claim to provide:

- Full enterprise network monitoring
- Complete network visibility
- Full vulnerability assessment
- Malware detection
- Full intrusion detection
- Enterprise SOC functionality
- Complete attack detection
- Endpoint detection and response
- Automated exploitation

---

## Privacy

NetGuard is designed for local operation.

The application does not require:

- A cloud backend
- A third-party monitoring server
- A remote database

Network monitoring information is processed locally by the application.

SQLite is used for local event storage.

---

## Responsible Use

NetGuard's networking and scanning functionality should only be used on systems and networks where you have authorization.

Do not use the port scanner or network discovery features against unauthorized systems.

The project is intended for:

- Personal labs
- Cybersecurity learning
- Network troubleshooting
- Authorized testing
- Local development
- Educational environments

---

## License

This project is provided for educational and authorized network-monitoring purposes.

Use the project responsibly and only against systems and networks you are permitted to monitor or test.

---

## Repository

GitHub:

https://github.com/8ist7/NetGuard
