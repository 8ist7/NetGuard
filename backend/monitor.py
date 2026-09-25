import ipaddress
import platform
import re
import socket
import subprocess
import time
from typing import Optional

# The scanner is deliberately limited to IPv4 localhost/private ranges.
ALLOWED_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
)

LOCAL_SERVICES = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    5000: "NetGuard",
    8080: "HTTP-Alt",
}


def run(command, timeout=8):
    """Run a fixed system/network diagnostic command safely."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            shell=isinstance(command, str),
        )
        return result.stdout + "\n" + result.stderr
    except (OSError, subprocess.SubprocessError, ValueError):
        return ""


def get_local_ip():
    # UDP connect does not send application data; it lets the OS select the
    # interface it would use for the supplied route.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(2)
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        try:
            host = socket.gethostname()
            candidate = socket.gethostbyname(host)
            return candidate if candidate else "Unavailable"
        except OSError:
            return "Unavailable"
    finally:
        sock.close()


def get_gateway():
    if platform.system() == "Windows":
        output = run(["route", "print", "0.0.0.0"])
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] == "0.0.0.0" and re.fullmatch(r"\d+\.\d+\.\d+\.\d+", parts[2]):
                return parts[2]
    else:
        output = run(["ip", "route"])
        match = re.search(r"default via ([0-9.]+)", output)
        if match:
            return match.group(1)
    return "Unavailable"


def get_dns_server():
    if platform.system() == "Windows":
        output = run(["ipconfig", "/all"])
        for line in output.splitlines():
            if "DNS Servers" in line:
                value = line.split(":", 1)[-1].strip()
                if value and re.fullmatch(r"[0-9a-fA-F:.]+", value):
                    return value
        # Some Windows builds put the first DNS address on a continuation line.
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if "DNS Servers" in line:
                for candidate in lines[i + 1:i + 5]:
                    candidate = candidate.strip()
                    if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", candidate):
                        return candidate
    else:
        output = run(["cat", "/etc/resolv.conf"])
        match = re.search(r"^\s*nameserver\s+([0-9a-fA-F:.]+)", output, re.M)
        if match:
            return match.group(1)
    return "Unavailable"


def get_interface():
    if platform.system() == "Windows":
        # Prefer the adapter whose IPv4 address matches the detected local IP.
        output = run(["ipconfig"])
        blocks = re.split(r"\r?\n(?=[A-Za-z0-9].*adapter .*:)", output)
        local_ip = get_local_ip()
        for block in blocks:
            if local_ip != "Unavailable" and local_ip in block:
                first = block.splitlines()[0].strip()
                return re.sub(r"^.*adapter\s+", "", first, flags=re.I).rstrip(":")
        return "Windows network adapter"
    output = run(["ip", "-o", "route", "show", "default"])
    match = re.search(r"\bdev\s+(\S+)", output)
    return match.group(1) if match else "Unavailable"


def collect_network_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.platform(),
        "local_ip": get_local_ip(),
        "gateway": get_gateway(),
        "dns_server": get_dns_server(),
        "interface": get_interface(),
    }


def ping_host(host):
    """Perform one real OS ping. The UI only reports this real result."""
    host = str(host).strip()
    if not host or len(host) > 253:
        return {"host": host, "reachable": False, "latency_ms": None, "error": "Invalid host"}

    system = platform.system()
    command = (
        ["ping", "-n", "1", "-w", "2500", host]
        if system == "Windows"
        else ["ping", "-c", "1", "-W", "2", host]
    )
    start = time.perf_counter()
    try:
        result = subprocess.run(command, capture_output=True, text=True, errors="replace", timeout=5)
        elapsed = round((time.perf_counter() - start) * 1000, 1)
        output = result.stdout + result.stderr
        match = re.search(r"(?:time[=<]\s*|Average\s*=\s*)(\d+(?:\.\d+)?)\s*ms", output, re.I)
        latency = round(float(match.group(1)), 1) if match else (elapsed if result.returncode == 0 else None)
        return {"host": host, "reachable": result.returncode == 0, "latency_ms": latency}
    except (OSError, subprocess.SubprocessError):
        return {"host": host, "reachable": False, "latency_ms": None, "error": "Ping command unavailable or timed out"}


def dns_check(host):
    try:
        socket.getaddrinfo(host, 80, type=socket.SOCK_STREAM)
        return True
    except OSError:
        return False


def _valid_visible_ipv4(ip):
    try:
        addr = ipaddress.ip_address(ip)
        return (
            addr.version == 4
            and not addr.is_multicast
            and not addr.is_unspecified
            and not addr.is_reserved
            and not addr.is_loopback
            and not str(addr).endswith(".255")
        )
    except ValueError:
        return False


def get_devices():
    system = platform.system()
    output = run(["arp", "-a"]) if system == "Windows" else run(["ip", "neigh"])
    devices = []
    seen = set()

    if system == "Windows":
        # Typical: 192.168.1.1  aa-bb-cc-dd-ee-ff  dynamic
        pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17})\s+(\w+)")
        for line in output.splitlines():
            match = pattern.search(line)
            if not match:
                continue
            ip, mac, state = match.groups()
            if not _valid_visible_ipv4(ip):
                continue
            key = (ip, mac.lower())
            if key not in seen:
                devices.append({"ip": ip, "mac": mac, "state": state.upper(), "interface": "ARP", "vendor": "Unknown"})
                seen.add(key)
    else:
        # Typical: 192.168.1.5 dev eth0 lladdr aa:bb:... REACHABLE
        pattern = re.compile(
            r"(\d+\.\d+\.\d+\.\d+)\s+dev\s+(\S+)(?:\s+lladdr\s+([0-9a-fA-F:]{17}))?.*?\b(REACHABLE|STALE|DELAY|PROBE|FAILED|INCOMPLETE|NOARP|PERMANENT)?\b"
        )
        for line in output.splitlines():
            match = pattern.search(line)
            if not match:
                continue
            ip, interface, mac, state = match.groups()
            if not _valid_visible_ipv4(ip):
                continue
            mac = mac or "Unknown"
            key = (ip, mac.lower())
            if key not in seen:
                devices.append({
                    "ip": ip,
                    "mac": mac,
                    "state": (state or "UNKNOWN").upper(),
                    "interface": interface,
                    "vendor": "Unknown",
                })
                seen.add(key)

    return devices


def check_local_services():
    results = []
    for port, name in LOCAL_SERVICES.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.35)
        start = time.perf_counter()
        try:
            open_state = sock.connect_ex(("127.0.0.1", port)) == 0
            elapsed = round((time.perf_counter() - start) * 1000, 1)
        except OSError as exc:
            open_state = False
            elapsed = round((time.perf_counter() - start) * 1000, 1)
        finally:
            sock.close()
        results.append({
            "port": port,
            "service": name,
            "status": "OPEN" if open_state else "CLOSED",
            "response_ms": elapsed,
            "result": "TCP connection accepted" if open_state else "Connection refused/unreachable",
        })
    return results


def _is_allowed_private_target(addr):
    return any(addr in network for network in ALLOWED_NETWORKS)


def validate_scan_target(target):
    target = str(target).strip()
    if not target:
        raise ValueError("Target is required")

    if target.lower() == "localhost":
        return "127.0.0.1"

    try:
        addr = ipaddress.ip_address(target)
    except ValueError:
        # Hostnames are allowed only when they resolve to one of the explicitly
        # permitted IPv4 private/loopback ranges.
        if len(target) > 253 or any(c.isspace() for c in target):
            raise ValueError("Invalid IP address or hostname")
        try:
            resolved = socket.gethostbyname(target)
            addr = ipaddress.ip_address(resolved)
            if _is_allowed_private_target(addr):
                return resolved
        except (OSError, ValueError):
            pass
        raise ValueError("Only localhost and private-network targets are allowed.")

    if addr.version != 4 or not _is_allowed_private_target(addr):
        raise ValueError("Only localhost and private-network targets are allowed.")
    return str(addr)


def scan_ports(target, start_port, end_port):
    target = validate_scan_target(target)
    try:
        start_port = int(start_port)
        end_port = int(end_port)
    except (TypeError, ValueError):
        raise ValueError("Port numbers must be integers")

    if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
        raise ValueError("Port numbers must be between 1 and 65535")
    if start_port > end_port:
        raise ValueError("Start port must be less than or equal to end port")
    count = end_port - start_port + 1
    if count > 100:
        raise ValueError("Maximum scan range is 100 ports")

    results = []
    started = time.perf_counter()
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.25)
        port_started = time.perf_counter()
        try:
            state = sock.connect_ex((target, port)) == 0
            elapsed = round((time.perf_counter() - port_started) * 1000, 1)
            results.append({
                "port": port,
                "status": "OPEN" if state else "CLOSED",
                "service": LOCAL_SERVICES.get(port, "Unknown"),
                "latency_ms": elapsed,
            })
        finally:
            sock.close()

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    open_ports = [x["port"] for x in results if x["status"] == "OPEN"]
    return {
        "target": target,
        "start_port": start_port,
        "end_port": end_port,
        "duration_ms": duration_ms,
        "open_ports": open_ports,
        "closed_ports": [x["port"] for x in results if x["status"] == "CLOSED"],
        "results": results,
    }
