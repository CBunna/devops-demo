# DevOps Demo App — Beginner's Guide

A simple web app that shows how Docker, Flask, Nginx, and Docker Compose work together.

---

## What Is This App?

This is a small Python web server (Flask) that runs inside Docker containers. Nginx sits in front of it and handles incoming web requests, then forwards them to the Flask app.

```
Your Browser
     |
     v
  Nginx (port 80)       <-- the "front door"
     |
     v
  Flask (port 5000)     <-- the actual app
```

---

## Project Structure

```
devops-demo-app/
├── app/
│   ├── app.py            # The Flask web application
│   ├── Dockerfile        # Instructions to build the Flask container
│   └── requirements.txt  # Python packages needed
├── nginx/
│   └── nginx.conf        # Nginx configuration (reverse proxy)
└── docker-compose.yml    # Wires everything together
```

---

## Key Files Explained

### `app/app.py` — The Web App

A minimal Flask app with two endpoints:

| URL | What it does |
|-----|-------------|
| `/` | Returns app status and environment info as JSON |
| `/health` | Returns `{"healthy": true}` — used to check if the app is alive |

### `app/Dockerfile` — How to Build the Container

Uses a **multi-stage build** (a best practice):

1. **Stage 1 (builder):** Installs Python packages
2. **Stage 2 (runtime):** Copies only what's needed — keeps the image small

Also runs the app as a non-root user for security, and uses **Gunicorn** (a production-grade server) instead of Flask's built-in development server.

### `nginx/nginx.conf` — Nginx Config

Nginx acts as a **reverse proxy** — it receives requests on port 80 and forwards them to Flask on port 5000. This is a common real-world pattern.

### `docker-compose.yml` — The Glue

Defines two services and how they connect:

| Service | Description |
|---------|-------------|
| `flask` | Builds and runs the Python app |
| `nginx` | Runs the Nginx proxy in front of Flask |

---

## How to Run It

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/) installed (included with Docker Desktop)

### Steps

1. Create a `.env` file in the `devops-demo-app/` directory:

```bash
APP_ENV=development
SECRET_KEY=my-secret-key
```

2. Start everything:

```bash
cd devops-demo-app
docker compose up --build
```

3. Open your browser and visit:

- `http://localhost/` — see the app response
- `http://localhost/health` — check if the app is healthy

### Stop the app

```bash
docker compose down
```

---

## Concepts You'll Learn Here

| Concept | Where to see it |
|---------|----------------|
| Docker containers | `Dockerfile` |
| Multi-stage builds | `Dockerfile` (Stage 1 & 2) |
| Non-root user in containers | `Dockerfile` (adduser) |
| Gunicorn (WSGI server) | `Dockerfile` (CMD) |
| Reverse proxy | `nginx.conf` |
| Docker Compose | `docker-compose.yml` |
| Environment variables | `.env` + `app.py` |
| Health checks | `/health` endpoint |

---

## Common Questions

**Why is Nginx in front of Flask?**
Flask's built-in server is not meant for production. Nginx handles things like slow clients, TLS (HTTPS), and load balancing. Flask just focuses on application logic.

**What is a reverse proxy?**
It's a server that receives requests on behalf of another server. The client talks to Nginx, Nginx talks to Flask. The client never connects to Flask directly.

**Why multi-stage Docker builds?**
The final image only contains what the app needs to run — not build tools, pip cache, etc. This makes the image smaller and more secure.

**What is Gunicorn?**
A Python WSGI server that can handle multiple requests at the same time using workers. This app runs with 2 workers.
