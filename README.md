# 🌊 FlowGuard

**FlowGuard** is a robust API gateway that intelligently distributes incoming requests to backend servers while enforcing per-key rate limits and tracking real-time system metrics. It is built with FastAPI, Redis, PostGreSQL and Docker. It also includes a custom async load tester to validate performance under pressure.

## 🚀 Features

- **Smart Load Balancer**  
  Round-robin routing with real-time health checks and automatic failover

- **Rate Limiting per API Key**  
  Configurable limits with Redis-based counters and token bucket support

- **Custom Load Tester**  
  Async `httpx`-powered CLI tool to simulate high-concurrency usage and log response metrics

- **Metrics Endpoints**  
  Live backend stats: latency, health status, success/429/5xx ratios (via `/metrics` endpoint)

- **Fault Tolerant Backends**  
  Random health failures to test routing resilience

- **Contanerized in docker**  
  One-command setup with `docker-compose`

---

## ⚙️ Tech Stack

- **FastAPI** — High-performance web framework
- **Redis** — Rate limiting & health check state
- **PostgreSQL** - For table storage
- **HTTPX** — Async client for proxying and load testing
- **Docker + Compose** — Full environment with gateway + multiple backends
- **Python 3.11+**

---

## 🧪 Endpoints

| Method | Endpoint           | Description                   |
|--------|--------------------|-------------------------------|
| GET   | `/proxy`     | Endpoint for continuous testing |
| POST    | `/register`   | Get user-specific API-Key      |
| GET | `/metrics/{api-key}`  | To get user-specific metrics |
| GET | `/all_keys`  | To get the list of all keys(Testing)  |
| GET | `/view_logs`  | View logs of recent activity  |
| GET | `/server`  | To visualize the servers  |
| GET | `/server_stats`  | Get all server statuses  |

---

## 🛠️How to Run?

### 1. Clone the repo and change directory

```
git clone https://github.com/ShoumoPal/FlowGuard.git
cd FlowGuard
```
### 3. Build and run with Docker
```
docker-compose up --build
```
### 4. Manually test the endpoint
```
curl -H "X-API-Key: test-api-key" "http://localhost:8000/proxy"
```
### 5. Can also see JSON object from these endpoints
```
curl http://localhost:8000/status
curl http://localhost:8000/metrics
```
### 6. Run the load tester

Step 1: Configure config.json
```
{
  "tries": 10,
  "api_key": "test-api-key",
  "proxy_url": "http://localhost:8000/proxy"
}
```

Step 2: Run it
```
python -m load_tester_run_tester
```

Step 3: Check ratelimit.log for an output

<img width="835" height="468" alt="image" src="https://github.com/user-attachments/assets/42cadd2f-5b2e-4f73-a548-012a78f2fb87" />

---

## Small demo

[FlowGuard Demo](https://drive.google.com/file/d/1FpVm2G1FiNlL-FdGJZx5D8lNYKS5jX4E/view?usp=sharing)



