# DevOps Demo App — Beginner's Guide

A Python Flask web app running in Docker with Nginx as a reverse proxy, Prometheus for metrics collection, and Grafana for visualization.

---

## Architecture

```
Your Browser
     |
     v
  Nginx (port 80)           ← reverse proxy & security
     |
     v
  Flask (port 5000)         ← web application
     |
     v
  Prometheus (port 9090)    ← scrapes /metrics every 15s
     |
     v
  Grafana (port 3000)       ← visualizes Prometheus data
```

---

## Project Structure

```
devops-demo-app/
├── app/
│   ├── app.py              # Flask application
│   ├── Dockerfile          # Multi-stage container build
│   └── requirements.txt    # Python dependencies
├── nginx/
│   └── nginx.conf          # Reverse proxy config
├── monitoring/
│   └── prometheus.yml      # Prometheus scrape config
├── k8s/
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── ingress.yaml
│   └── configMap.yaml
├── docker-compose.yml      # Runs all services together
└── .env                    # Environment variables (not committed)
```

---

## API Endpoints

| Endpoint   | Description                                      |
|------------|--------------------------------------------------|
| `GET /`    | Returns app status, environment, and pod name    |
| `GET /health` | Health check — returns `{"healthy": true}`    |
| `GET /version` | Returns version and environment info         |
| `GET /metrics` | Prometheus metrics (blocked at Nginx — internal only) |

### Example responses

```bash
curl http://localhost/
# {"environment":"development","message":"DevOps Demo App is running","pod":"abc123","status":"ok"}

curl http://localhost/health
# {"healthy":true}

curl http://localhost/version
# {"env":"development","pod":"abc123","version":"1.0.0"}

curl http://localhost/metrics
# 403 Forbidden  ← blocked by Nginx intentionally
```

---

## How to Run (Docker Compose)

### Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) installed
- Docker Desktop file sharing set to **gRPC FUSE** (Settings → General)

### Setup

1. Create a `.env` file:

```bash
APP_ENV=development
SECRET_KEY=my-secret-key
```

2. Start all services:

```bash
docker compose up -d
```

3. Verify everything is running:

```bash
docker compose ps
```

### Access the services

| Service    | URL                        | Credentials     |
|------------|----------------------------|-----------------|
| Flask app  | http://localhost/          | —               |
| Prometheus | http://localhost:9090      | —               |
| Grafana    | http://localhost:3000      | admin / admin   |

### Stop all services

```bash
docker compose down
```

---

## How to Run Locally (without Docker)

```bash
cd app
pip install -r requirements.txt
python app.py
# App runs on http://localhost:5000
```

> Note: On macOS, port 5000 is used by AirPlay Receiver.
> Disable it in System Settings → General → AirDrop & Handoff, or run Flask on a different port.

---

## Monitoring with Prometheus & Grafana

### How it works

1. Flask exposes metrics at `/metrics` (via `prometheus-flask-exporter`)
2. Prometheus scrapes `flask:5000/metrics` every 15 seconds
3. Grafana connects to Prometheus and visualizes the data

### Useful Prometheus queries

| Query | What it shows |
|-------|--------------|
| `flask_http_request_total` | Total requests per endpoint and status code |
| `rate(flask_http_request_total[1m])` | Requests per second (last 1 minute) |
| `flask_http_request_duration_seconds_bucket` | Response time histogram |

### Check Prometheus targets

Open http://localhost:9090 → Status → Targets

The `flask` job should show state **UP**.

### Security note

`/metrics` is blocked at the Nginx level (`403 Forbidden`) so external users cannot read internal metrics. Prometheus scrapes Flask directly on the internal Docker network, bypassing Nginx.

---

## Kubernetes (Minikube)

### Prerequisites

```bash
minikube start
eval $(minikube docker-env)          # point Docker CLI to Minikube
```

### Build and deploy

```bash
# Build image inside Minikube
docker build -t bunna44/flask-demo:v1 ./app

# Apply all manifests
kubectl apply -f k8s/
```

### Check status

```bash
kubectl get pods
kubectl get svc
kubectl describe deployment flask-deployment
```

### Access the app

```bash
# Via NodePort
curl http://$(minikube ip):30080/

# Or use port forwarding
kubectl port-forward svc/flask-service 8080:80
curl http://localhost:8080/
```

### Useful kubectl commands

```bash
kubectl logs deployment/flask-deployment    # view app logs
kubectl rollout restart deployment/flask-deployment  # rolling restart
kubectl scale deployment flask-deployment --replicas=3  # scale up
```

---

## Key Concepts in This Project

| Concept | Where to see it |
|---------|----------------|
| Multi-stage Docker build | [app/Dockerfile](app/Dockerfile) |
| Non-root container user | `Dockerfile` — `adduser appuser` |
| Gunicorn WSGI server | `Dockerfile` — CMD |
| Reverse proxy | [nginx/nginx.conf](nginx/nginx.conf) |
| Blocking endpoints at proxy | `nginx.conf` — `/metrics` location |
| Docker Compose networking | `docker-compose.yml` — services talk by name |
| Environment variables | `.env` + `app.py` |
| Prometheus scraping | [monitoring/prometheus.yml](monitoring/prometheus.yml) |
| Kubernetes Deployment | [k8s/flask-deployment.yaml](k8s/flask-deployment.yaml) |
| Liveness & readiness probes | `flask-deployment.yaml` |
| Resource limits | `flask-deployment.yaml` — `resources` block |
| NodePort service | [k8s/flask-service.yaml](k8s/flask-service.yaml) |

---

## Common Issues

**Port 80 already in use**
```bash
sudo lsof -i :80   # find what's using it
```

**Port 5000 in use on macOS**
Disable AirPlay Receiver: System Settings → General → AirDrop & Handoff

**Docker bind mount fails with "Is a directory"**
Switch Docker Desktop file sharing: Settings → General → gRPC FUSE → Apply & Restart

**Minikube `eval $(minikube docker-env)` pointing to wrong daemon**
```bash
eval $(minikube docker-env --unset)   # revert to Docker Desktop
```

**ImagePullBackOff in Kubernetes**
The image doesn't exist in the registry. Build it inside Minikube first:
```bash
eval $(minikube docker-env)
docker build -t bunna44/flask-demo:v1 ./app
kubectl patch deployment flask-deployment \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"flask","imagePullPolicy":"Never"}]}}}}'
```


**Tips**
```
Request rate normal + Error rate spiked = app is getting traffic but failing
  → look at logs for error messages

Request rate dropped to zero + Error rate zero = no traffic reaching app
  → check nginx, check DNS, check if pods are running

Request rate normal + Error rate normal + Response time spiked = app is slow
  → check database, check downstream services, check CPU/memory

```

** Example: Error rate spiking to 15%, request rate normal, response time normal**

```
1. Error rate high + request rate normal
   = app is receiving traffic but something in the code is failing
   = not a network problem, not a scaling problem

2. Check which endpoint is causing errors
   → Grafana: flask_http_request_total{status=~"5.."} grouped by path

3. Check logs for that pod
   → kubectl logs <pod-name>
   → kubectl logs <pod-name> --previous

4. Look for error messages, stack traces, exceptions

5. If it is a bad deployment → kubectl rollout undo
   If it is a code bug → fix, test, redeploy via CI/CD pipeline

```