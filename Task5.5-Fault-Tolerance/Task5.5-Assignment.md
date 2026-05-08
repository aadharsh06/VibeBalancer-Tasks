# Task 5.5: Learning - Fault Tolerance

## Background

In Task 5, your load balancer learned how to distribute requests across multiple backend servers. That is the first job of a load balancer.

The next job is reliability. In real systems, backend servers can crash, restart, become slow, or stop responding. If the load balancer keeps sending requests to a failed server, users will see errors even though another backend server may still be working.

Fault tolerance means designing the load balancer so that the system can continue working even when part of it fails.

---

## Topics to Learn

### 1. Health Checks

A health check is a small request used to check whether a backend server is alive and ready to receive traffic.

In this task, each backend server will expose:

```url
GET /health
```

The load balancer will call this endpoint periodically and decide whether each backend is healthy or unhealthy.

### 2. Skipping Unhealthy Servers

Once a server is marked unhealthy, the load balancer should stop sending normal user requests to it.

This is how real load balancers avoid broken or crashed backend servers.

### 3. Retry Logic

Sometimes a backend may fail after the load balancer has already selected it. Retry logic allows the load balancer to try another healthy backend instead of immediately failing the user request.

### 4. Graceful Failure

If all backend servers are down, the load balancer should not crash. It should return a clear error response such as:

```text
503 Service Unavailable
```

---

## Recommended Learning Resources: Fault Tolerance

The following video resources are highly recommended for understanding the core concepts implemented in this phase of the project:

### 1. Active Health Checks and Traffic Routing
* **[What is load balancing in networking | How load balancer works?](https://www.youtube.com/watch?v=fW1tVxOYXnI)**
  * **Overview:** Provides a clear architectural breakdown of how load balancers route traffic and utilize health checks to identify and isolate unresponsive backend servers.

### 2. Failure Handling and Retries
* **[Introduction to Circuit Breaker in Microservices](https://www.youtube.com/watch?v=HRS9mIfiNn4)**
  * **Overview:** Details the mechanisms for safely managing request retries and implementing circuit breakers to prevent cascading system failures when a backend node becomes unavailable.


---

## After Learning

Once you understand why health checks and retries are needed, proceed to the assignment below. You will upgrade your existing Task 5 load balancer instead of creating a new application.

---

# Task 5.5: Assignment - Fault Tolerance

## Objective

Improve your VibeBalancer load balancer so that it can continue serving requests even when one backend server fails.

In the previous task, your load balancer distributed requests across multiple backend servers. However, real servers can crash, become slow, or stop responding. A good load balancer should detect these failures and avoid sending traffic to unhealthy servers.

By the end of this task, you should still have one main VibeBalancer load balancer running on port `8000`. This task does not require a separate application. You are upgrading the same load balancer from Task 5 with reliability features.

---

## Setup

You will build on your Task 5 load balancer.

Use the same backend servers:

* `server_1` -> `http://localhost:8001`
* `server_2` -> `http://localhost:8002`
* Load balancer -> `http://localhost:8000`

Make sure both backend servers and the load balancer are running before starting.

---

## Part 1: Observe the Current Failure Behavior

Before adding fault tolerance, test what happens when one backend goes down.

1. Start both backend servers.
2. Start your load balancer.
3. Send requests to:

```url
http://localhost:8000/work?delay=2
```

4. Stop one backend server manually.
5. Send requests again through the load balancer.

Write down your observation:

* Does the load balancer still try to send requests to the stopped server?
* What error do you see?
* Does the client get a useful response?

---

## Part 2: Add a Health Check Endpoint to Backend Servers

Add a simple health check endpoint to each backend server.

### Endpoint

`GET /health`

### Expected Response

```json
{
  "status": "ok",
  "server": "server_1"
}
```

Use a different server name for each backend so that you can identify which server responded.

---

## Part 3: Track Backend Health in the Load Balancer

In your load balancer, maintain a dictionary that stores whether each backend is healthy.

Example:

```python
server_health = {
    "http://localhost:8001": True,
    "http://localhost:8002": True
}
```

Your load balancer should periodically call `/health` on each backend server and update this dictionary.

### Requirements

* If a backend responds successfully, mark it as healthy.
* If a backend does not respond or gives an error, mark it as unhealthy.
* Use a timeout so the load balancer does not wait forever for a dead backend.

---

## Part 4: Skip Unhealthy Servers

Update your load balancing logic so that requests are forwarded only to healthy backend servers.

### Expected Behavior

| Situation | Expected Load Balancer Behavior |
| :--- | :--- |
| Both servers healthy | Use normal Round Robin or Least Connections |
| `server_1` down | Send all traffic to `server_2` |
| `server_2` down | Send all traffic to `server_1` |
| Both servers down | Return `503 Service Unavailable` |

---

## Part 5: Retry Failed Requests

Sometimes a server may fail after being selected. Add retry logic to handle this.

### Requirements

* Select a healthy backend server.
* Forward the request.
* If the request fails, mark that backend as unhealthy.
* Retry the request once using another healthy backend.
* If no healthy backend is available, return `503 Service Unavailable`.

---

## Part 6: Testing

### Test 1: One Backend Failure

1. Start both backend servers and the load balancer.
2. Send multiple requests through the load balancer.
3. Stop `server_1`.
4. Send requests again.

**Observe:**

* Does the load balancer avoid `server_1`?
* Are requests still handled by `server_2`?

### Test 2: Server Recovery

1. Start `server_1` again.
2. Wait for the health checker to detect it.
3. Send requests again.

**Observe:**

* Does `server_1` become available again?
* Does traffic get distributed across both servers again?

### Test 3: All Backends Down

1. Stop both backend servers.
2. Send a request to the load balancer.

**Expected Result:**

The load balancer should return a clear `503 Service Unavailable` response instead of crashing.

---

## Deliverables

* Updated backend server code with `/health`.
* Updated load balancer code with:
  * existing Round Robin and Least Connections support from Task 5
  * health checks
  * unhealthy server skipping
  * retry logic
  * `503` handling when all backends are down
* Screenshots or logs showing:
  * one server going down
  * load balancer continuing with the healthy server
  * failed server becoming healthy again after restart
* Short write-up explaining:
  * what happened before fault tolerance
  * what changed after adding health checks and retries

---

## Bonus (Optional)

Add an endpoint to view current backend health:

`GET /backends`

Example response:

```json
{
  "backends": [
    {
      "url": "http://localhost:8001",
      "healthy": true
    },
    {
      "url": "http://localhost:8002",
      "healthy": false
    }
  ]
}
```

---

## Key Insight

Load balancing is not only about distributing traffic. It is also about reliability.

Fault tolerance ensures that when one backend fails, users can still get responses from the remaining healthy servers.

After completing this task, your project should behave like a basic real-world load balancer:

* It accepts client requests on one public port.
* It distributes requests across multiple backend servers.
* It avoids backend servers that are down.
* It retries failed requests when another healthy backend is available.
* It returns a proper error when no backend can serve the request.

This prepares you for the next step: collecting metrics to monitor request counts, failures, active connections, and system health.

## Important!

Update your progress in the excel sheet shared after you are completed with the assignment.
