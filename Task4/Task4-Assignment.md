# Task-4: Assignment

### Blocking vs Non-blocking + Concurrency (Threading)

#### Objective

Understand what happens when multiple users hit a server at the same time and fix performance issues using concurrency.

---

#### Assignment

1. **Observe Blocking Behavior**
   - Use your Week 3 server.
   - Call `/work?delay=3` multiple times simultaneously (e.g., using multiple tabs or Postman).
   - Observe whether requests finish together or one after another.
   - Write a short answer: Is the server blocking or non-blocking?

2. **Simulate Multiple Users (Client Side)**
   - Write a Python script to send 3–5 requests to `http://localhost:8001/work?delay=3`.
   - Measure the total time taken.

3. **Improve Using Threading**
   - Modify your client script to use threading and send requests concurrently.
   - Measure the total time taken again.

4. **Add Logging to Server**
   - Update your server to log request start and end times.
   - Observe overlapping requests in the logs.

---

#### Deliverables

- Python script for sequential and threaded requests.
- Observations on blocking vs non-blocking behavior.
- Updated server logs showing concurrency.

---

#### Key Insight

One server can only handle so much. This naturally leads to the need for a load balancer to distribute requests across multiple servers.
