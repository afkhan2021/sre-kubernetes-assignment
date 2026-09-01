# AI Prompts and Engineering Thought Process

## Purpose

AI was used as an engineering assistant during the development of this assignment.

The AI helped with architecture suggestions, Kubernetes manifest structure, application design, troubleshooting, documentation, and validation ideas.

All implementation steps were reviewed and tested locally before being considered complete.

## Prompt 1 — Architecture

### Representative prompt

> I am completing an SRE take-home assignment. I need a small Kubernetes environment running locally that contains a simple web application and a Kubernetes CronJob. The CronJob should collect useful system information, store it in a backend data store, and the web application should display the collected information and the CronJob's last run time. The application should also demonstrate scalability under heavy load.

### Decision

The resulting architecture uses:

- Colima
- K3s Kubernetes
- FastAPI
- PostgreSQL
- Kubernetes CronJob
- Kubernetes Deployment
- Kubernetes Service
- Horizontal Pod Autoscaler
- PersistentVolumeClaim

The design was intentionally kept small enough to run on a laptop while demonstrating important SRE concepts.

## Prompt 2 — Web Application

### Representative prompt

> Help design a minimal FastAPI application that reads system information collected by a Kubernetes CronJob from PostgreSQL and displays it in a browser.

### Decision

The application provides:

- Web dashboard at `/`
- Health endpoint at `/health`
- Readiness endpoint at `/ready`
- REST endpoint at `/api/system-info`

The dashboard displays the latest collection time and the collected system information.

## Prompt 3 — System Information Collector

### Representative prompt

> Design a Python collector that gathers useful system information such as hostname, CPU count, memory, disk usage, load average, and collection timestamp, then stores the information in PostgreSQL.

### Decision

The collector uses:

- Python
- `psutil`
- PostgreSQL
- UTC timestamps

The collector is packaged into the same Docker image as the web application and executed by the Kubernetes CronJob.

## Prompt 4 — Kubernetes Design

### Representative prompt

> Create Kubernetes manifests for the FastAPI application, PostgreSQL database, CronJob, Service, persistent storage, Secret, and Horizontal Pod Autoscaler.

### Decision

The Kubernetes configuration was separated into individual YAML files so that each component can be understood and managed independently.

The web application uses:

- 2 replicas by default
- CPU and memory requests/limits
- Readiness probe
- Liveness probe
- Non-root container execution
- Dropped Linux capabilities
- RuntimeDefault seccomp profile

The PostgreSQL database uses:

- StatefulSet
- PersistentVolumeClaim
- Internal ClusterIP Service
- Kubernetes Secret
- Readiness and liveness checks

## Prompt 5 — Scalability

### Representative prompt

> How can I demonstrate that the Kubernetes web application can scale under load without needing to build a complex load-testing system?

### Decision

A Kubernetes Horizontal Pod Autoscaler was configured with:

- Minimum replicas: 2
- Maximum replicas: 5
- CPU target: 70%

A temporary Kubernetes load generator was used during testing.

The web Deployment successfully scaled from:

```text
2 replicas → 4 replicas

After the load was removed, the Deployment returned to:

4 replicas → 2 replicas
Prompt 6 — Reliability Testing
Representative prompt

What reliability tests should I perform on this Kubernetes assignment to demonstrate self-healing, health checks, CronJob execution, database persistence, and autoscaling?

Decision

The following tests were performed:

PostgreSQL readiness was verified.
The collector was executed successfully.
A Kubernetes Job was created from the CronJob.
Collector output was verified in PostgreSQL.
The web application was accessed through the browser.
Health and readiness endpoints were tested.
HPA metrics were verified.
Load was generated to trigger horizontal scaling.
Load was removed and scale-down was observed.
A running web pod was deleted.
Kubernetes automatically created a replacement pod.
Temporary test Jobs were removed.
Prompt 7 — Security and Repository Hygiene
Representative prompt

What basic security controls should be included in a small Kubernetes assignment and what files should not be committed to GitHub?

Decision

The implementation includes:

Kubernetes Secret for database credentials
.gitignore entry for the local Secret
secret.example.yaml containing placeholders
Non-root web container
Disabled privilege escalation
Dropped Linux capabilities
RuntimeDefault seccomp profile
Resource limits
Internal PostgreSQL service

The real local Secret file is intentionally excluded from Git.

Engineering Decisions
Colima and K3s

Colima and K3s were selected because they provide a lightweight local Kubernetes environment suitable for development on a laptop.

FastAPI

FastAPI provides a simple way to implement the web application and REST endpoint without introducing unnecessary application complexity.

PostgreSQL

PostgreSQL provides a real backend data store and allows the CronJob and web application to communicate through a persistent database.

CronJob

A Kubernetes CronJob was used instead of an application-level scheduler so that scheduling is handled by Kubernetes.

The schedule is:

0 */6 * * *

This runs the collector every six hours.

StatefulSet and PersistentVolumeClaim

PostgreSQL uses a StatefulSet and persistent storage so that database data is not tied to the lifetime of an individual PostgreSQL pod.

Horizontal Pod Autoscaler

The web application is stateless, allowing multiple replicas to serve requests.

The HPA scales the Deployment based on CPU utilization.

NodePort

A NodePort Service was selected because it provides a straightforward way to access the application from a browser on the local laptop without requiring an ingress controller.

AI-Assisted vs. Human Validation

AI was used to assist with:

Architecture design
Code structure
Kubernetes configuration
Troubleshooting approaches
Testing strategies
Documentation

The implementation was not accepted based only on AI suggestions.

Commands were executed locally and the Kubernetes resources, application behavior, database records, CronJob execution, autoscaling, and pod self-healing were independently verified.

The final configuration reflects changes made during testing and troubleshooting.

Lessons Learned

This assignment demonstrated several practical SRE concepts:

Kubernetes workload management
Containerization
Persistent storage
Scheduled workloads
Application health checks
Horizontal scaling
Self-healing
Resource management
Secrets management
Local Kubernetes development
Operational validation

The main goal was to keep the implementation simple while demonstrating production-oriented reliability and operational practices.
