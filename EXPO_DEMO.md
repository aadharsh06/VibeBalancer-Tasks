# VibeBalancer Expo Demo

This folder includes a ready-to-open Grafana dashboard for the Prometheus metrics exposed by `Task6-submission/task6.py` and `Task7-submission/task7.py`.

Run these commands from inside the `VibeBalancer-Tasks` folder.

## 1. Install Python packages

```bash
python3 -m pip install -r requirements.txt
```

## 2. Start the two backend servers

```bash
uvicorn --app-dir Task3_submission api1:server_1 --host 127.0.0.1 --port 8001
uvicorn --app-dir Task3_submission api1:server_2 --host 127.0.0.1 --port 8003
```

## 3. Start the monitored load balancer

Use Task 7 for the final demo:

```bash
uvicorn --app-dir Task7-submission task7:lb --host 127.0.0.1 --port 8000
```

The Prometheus metrics endpoint will be available at:

```text
http://127.0.0.1:8000/metrics
```

## 4. Start Prometheus and Grafana

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

The dashboard is provisioned automatically at:

```text
Dashboards -> VibeBalancer -> VibeBalancer Live Demo
```

## 5. Generate live demo traffic

In another terminal:

```bash
python3 demo_traffic.py
```

The script sends normal traffic and also starts one background timeout request every 12 load-balancer requests. Those timeout requests make the load balancer's error counter move, while normal traffic continues flowing on the dashboard.

To run without intentional errors:

```bash
python3 demo_traffic.py --error-every 0
```

The Grafana panels should update every 2 seconds with total requests, request rate, active connections, errors, CPU usage, memory usage, and Prometheus scrape status.
