from flask import Flask, jsonify, request, Response, send_from_directory
from database import add_event, add_snapshot, events_csv, get_events, get_snapshots, init_db
from monitor import check_local_services, collect_network_info, dns_check, get_devices, ping_host, scan_ports

app = Flask(__name__, static_folder="../frontend", static_url_path="")
init_db()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/dashboard")
def dashboard():
    network = collect_network_info()
    internet = ping_host("8.8.8.8")
    dns = dns_check("example.com")
    gateway_result = (
        ping_host(network["gateway"])
        if network["gateway"] not in ("Unavailable", "", None)
        else {"reachable": False, "latency_ms": None}
    )
    devices = get_devices()
    services = check_local_services()
    open_services = [x for x in services if x["status"] == "OPEN"]

    gateway_ok = gateway_result["reachable"]
    internet_ok = internet["reachable"]
    if internet_ok and dns and gateway_ok:
        health = "HEALTHY"
    elif gateway_ok or internet_ok or dns:
        health = "DEGRADED"
    else:
        health = "OFFLINE"

    snapshot = {
        "local_ip": network.get("local_ip"),
        "gateway": network.get("gateway"),
        "dns_server": network.get("dns_server"),
        "interface": network.get("interface"),
        "internet": internet_ok,
        "dns": dns,
        "device_count": len(devices),
        "open_service_count": len(open_services),
    }
    add_snapshot(snapshot)

    if not internet_ok:
        add_event("CONNECTIVITY", "Internet connectivity check failed for 8.8.8.8", "WARNING")
    if not dns:
        add_event("DNS", "DNS resolution check failed for example.com", "WARNING")
    if network["gateway"] != "Unavailable" and not gateway_ok:
        add_event("GATEWAY", f"Gateway {network['gateway']} did not respond to ping", "WARNING")

    return jsonify({
        "network": network,
        "internet": internet_ok,
        "latency_ms": internet["latency_ms"],
        "dns": dns,
        "gateway": gateway_result,
        "health": health,
        "ping_target": "8.8.8.8",
        "devices": devices,
        "services": services,
        "events": get_events(50),
        "snapshots": get_snapshots(20),
    })


@app.route("/api/ping", methods=["POST"])
def api_ping():
    data = request.get_json(silent=True) or {}
    host = str(data.get("host", "")).strip()
    if not host or len(host) > 253:
        return jsonify({"error": "Enter a valid host or IP address."}), 400
    result = ping_host(host)
    severity = "INFO" if result["reachable"] else "WARNING"
    message = (
        f"{host} reachable with {result['latency_ms']} ms latency"
        if result["reachable"]
        else f"{host} did not respond"
    )
    add_event("PING", message, severity)
    return jsonify(result)


@app.route("/api/test/<test_name>", methods=["POST"])
def api_test(test_name):
    network = collect_network_info()

    if test_name == "connectivity":
        result = ping_host("8.8.8.8")
        event_type = "CONNECTIVITY"
        message = (
            f"8.8.8.8 reachable with {result['latency_ms']} ms latency"
            if result["reachable"]
            else "Internet connectivity test failed"
        )
    elif test_name == "ping":
        data = request.get_json(silent=True) or {}
        host = str(data.get("host", "8.8.8.8")).strip()
        if not host or len(host) > 253:
            return jsonify({"error": "Enter a valid host or IP address."}), 400
        result = ping_host(host)
        event_type = "PING"
        message = f"{host} reachable with {result['latency_ms']} ms latency" if result["reachable"] else f"{host} did not respond"
    elif test_name == "dns":
        result = {"reachable": dns_check("example.com"), "host": "example.com"}
        event_type = "DNS"
        message = "DNS resolution succeeded for example.com" if result["reachable"] else "DNS resolution failed for example.com"
    elif test_name == "gateway":
        gateway = network.get("gateway")
        result = ping_host(gateway) if gateway not in ("Unavailable", "", None) else {
            "host": gateway, "reachable": False, "latency_ms": None
        }
        event_type = "GATEWAY"
        message = (
            f"Gateway {gateway} reachable with {result['latency_ms']} ms latency"
            if result["reachable"]
            else f"Gateway {gateway} did not respond"
        )
    else:
        return jsonify({"error": "Unknown test. Use connectivity, ping, dns, or gateway."}), 404

    add_event(event_type, message, "INFO" if result["reachable"] else "WARNING")
    return jsonify(result)


@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json(silent=True) or {}
    target = str(data.get("target", "")).strip()
    try:
        start_port = int(data.get("start_port", 1))
        end_port = int(data.get("end_port", 100))
        result = scan_ports(target, start_port, end_port)
        add_event(
            "PORT_SCAN",
            f"Scanned {result['target']} ports {start_port}-{end_port}; {len(result['open_ports'])} open",
            "INFO",
        )
        return jsonify(result)
    except (TypeError, ValueError) as exc:
        add_event("PORT_SCAN", f"Rejected scan: {exc}", "WARNING")
        return jsonify({"error": str(exc)}), 400


@app.route("/api/events")
def api_events():
    return jsonify(get_events(100))


@app.route("/api/events.csv")
def api_events_csv():
    return Response(
        events_csv(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=netguard_events.csv"},
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
