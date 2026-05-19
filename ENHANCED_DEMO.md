# VibeBalancer Enhanced Demo

This demo is separate from the assignment submission files. It uses
`enhanced_load_balancer.py` instead of `Task6-submission/task6.py` or
`Task7-submission/task7.py`.

## What It Adds

- Per-backend request metrics
- Per-backend active connection metrics
- Per-backend health metrics
- Per-algorithm request metrics
- Load balancer latency metrics
- A separate Grafana dashboard named `VibeBalancer Enhanced Demo`

## Run It

Start the two backend servers:

```bash
uvicorn --app-dir Task3_submission api1:server_1 --host 127.0.0.1 --port 8001
uvicorn --app-dir Task3_submission api1:server_2 --host 127.0.0.1 --port 8003
```

Start the enhanced load balancer:

```bash
uvicorn enhanced_load_balancer:lb --host 0.0.0.0 --port 8000
```

Start Prometheus and Grafana:

```bash
docker compose -f docker-compose.monitoring.yml up
```

Open Grafana:

```text
http://localhost:3000
```

Login:

```text
username: admin
password: admin
```

Open:

```text
Dashboards -> VibeBalancer -> VibeBalancer Enhanced Demo
```

Generate traffic:

```bash
python3 demo_traffic.py
```

## Demo Talking Points

Round robin:

```text
Traffic Split by Backend should rise evenly for server1 and server2.
```

Least connections:

```text
Active Connections by Backend shows which backend is busier.
The load balancer should favor the less busy healthy backend.
```

Backend failure:

```text
Stop one backend server.
Backend Health drops from 1 to 0.
Traffic continues through the remaining healthy backend.
```
