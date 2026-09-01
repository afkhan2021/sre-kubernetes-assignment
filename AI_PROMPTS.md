# AI Prompts and Engineering Thought Process

## Purpose

AI was used as an engineering assistant during the development of this assignment.

I used AI mainly to help think through the architecture, Kubernetes configuration, application structure, troubleshooting steps, testing approach, security considerations, and documentation.

The suggestions were reviewed and tested locally. The final implementation was adjusted based on what actually worked in the local Kubernetes environment.

## Prompt 1 — Choosing the Architecture

### Prompt

> I need to complete an SRE take-home assignment on my laptop. I need a small Kubernetes setup with a web application and a CronJob. The CronJob needs to collect useful system information and save it somewhere the web application can read. The web page should show the collected information and the last time the job ran. I also need to demonstrate that the web application can scale when there is increased traffic. What would be a simple architecture that covers these requirements without making the project unnecessarily complicated?

### Decision

I chose a lightweight local Kubernetes environment using Colima and K3s.

The main components are:

- Colima
- K3s
- FastAPI
- PostgreSQL
- Kubernetes CronJob
- Kubernetes Deployment
- Kubernetes Service
- Horizontal Pod Autoscaler
- PersistentVolumeClaim

The goal was to keep the environment small enough to run comfortably on a laptop while still demonstrating common SRE practices.

## Prompt 2 — Designing the Web Application

### Prompt

> I want to keep the web application very simple. Can you suggest a minimal FastAPI application that reads the system information from PostgreSQL and displays it in a browser? I also need health and readiness endpoints because this will run in Kubernetes.

### Decision

The application was implemented with four main endpoints:

- `/` — Web dashboard
- `/health` — Liveness check
- `/ready` — Database readiness check
- `/api/system-info` — Returns collected system information

The dashboard shows the latest collection time along with the collected system information.

I kept the frontend inside the FastAPI application rather than introducing a separate frontend framework.

## Prompt 3 — Collecting System Information

### Prompt

> For the CronJob, what system information would be useful to collect for a simple SRE demonstration? I want something that is easy to collect with Python and useful enough to show on the dashboard.

### Decision

I decided to collect:

- Hostname
- CPU count
- Total memory
- Disk usage percentage
- Load average
- Collection timestamp

Python `psutil` was used for the system information.

The timestamp is stored in UTC so that the database records have a consistent time reference.

## Prompt 4 — Designing the Database

### Prompt

> I need a simple PostgreSQL schema for storing the information collected by the Kubernetes CronJob. What would be a reasonable table structure for this assignment?

### Decision

A single `system_info` table was sufficient for the assignment.

The table stores:

- Record ID
- Collection timestamp
- Hostname
- CPU count
- Memory
- Disk usage
- Load average

The web application retrieves the most recent records from PostgreSQL.

The database initialization is handled by the application when it starts.

## Prompt 5 — Kubernetes Manifests

### Prompt

> Can you help me break this Kubernetes application into separate YAML files? I want the manifests to be easy to understand and maintain. I need a namespace, PostgreSQL, persistent storage, web deployment, service, CronJob, Secret, and HPA.

### Decision

The Kubernetes configuration was separated into individual files:

- `namespace.yaml`
- `postgres.yaml`
- `postgres-service.yaml`
- `web-deployment.yaml`
- `web-service.yaml`
- `cronjob.yaml`
- `hpa.yaml`
- `secret.yaml`

A `secret.example.yaml` file was also created so that the repository does not need to contain the real database password.

## Prompt 6 — Kubernetes Health Checks

### Prompt

> What health checks should I add to the FastAPI application when running it in Kubernetes? I want Kubernetes to know when the application is alive and when it is ready to receive traffic.

### Decision

Two endpoints were implemented.

The `/health` endpoint is used for the liveness probe.

The `/ready` endpoint checks the PostgreSQL connection and is used for the readiness probe.

This allows Kubernetes to distinguish between an application that is running and an application that is actually ready to serve requests.

## Prompt 7 — Security Improvements

### Prompt

> This is a small local Kubernetes assignment, but I still want to demonstrate some basic security practices. What should I include without making the project overly complicated?

### Decision

The following controls were added:

- Database credentials stored in a Kubernetes Secret
- Real Secret excluded from Git
- `secret.example.yaml` provided as a template
- Web container runs as a non-root user
- Privilege escalation disabled
- Linux capabilities dropped
- RuntimeDefault seccomp profile
- CPU and memory limits
- PostgreSQL exposed only through an internal ClusterIP Service

The intention was to demonstrate practical baseline security rather than add unnecessary complexity.

## Prompt 8 — Demonstrating Horizontal Scaling

### Prompt

> The assignment says the web application should be able to scale under heavy load. I don't need to create a complicated load-testing system, but I do need to demonstrate that Kubernetes can scale the application. What is the simplest way to do this?

### Decision

I used a Kubernetes Horizontal Pod Autoscaler.

The HPA configuration is:

- Minimum replicas: 2
- Maximum replicas: 5
- CPU target: 70%

A temporary Kubernetes load generator was used during testing.

The web Deployment scaled from:

    2 replicas → 4 replicas

After the load was removed and the stabilization period elapsed, it returned to:

    4 replicas → 2 replicas

This provided a simple way to demonstrate horizontal scaling.

## Prompt 9 — Testing Self-Healing

### Prompt

> What simple tests can I run to demonstrate that Kubernetes is actually managing the application properly? I want to test things like pod recovery, health checks, the CronJob, database connectivity, and HPA behavior.

### Decision

I tested the following:

- PostgreSQL readiness
- Database connectivity
- Collector execution
- CronJob execution
- Database records created by the collector
- Web application browser access
- Health endpoint
- Readiness endpoint
- HPA metrics
- HPA scale-up
- HPA scale-down
- Pod self-healing

During the self-healing test, a running web pod was manually deleted.

Kubernetes automatically created a replacement pod and restored the Deployment to the desired replica count.

## Prompt 10 — Troubleshooting

### Prompt

> I am running the application locally using Colima and K3s. If a Kubernetes pod is not starting or the application cannot connect to PostgreSQL, what should I check first?

### Decision

The troubleshooting process focused on checking the Kubernetes resources in stages:

1. Check node status.
2. Check pod status.
3. Check pod logs.
4. Check Services.
5. Check Secrets.
6. Check PostgreSQL readiness.
7. Check application readiness.
8. Check resource usage.
9. Check the HPA metrics.

This made troubleshooting easier than trying to debug the entire environment at once.

## Prompt 11 — CronJob Testing

### Prompt

> The CronJob runs every six hours, so I don't want to wait six hours to test it. How can I trigger the same CronJob manually and verify that it actually writes a record to PostgreSQL?

### Decision

I used a Kubernetes Job created from the existing CronJob definition.

The test confirmed that:

- The collector container started successfully.
- System information was collected.
- PostgreSQL was reachable.
- A record was inserted into the database.
- The web API could retrieve the new record.

This allowed the CronJob functionality to be tested without changing the production schedule.

## Prompt 12 — README and Documentation

### Prompt

> I need to submit this as an SRE assignment. What information should the README contain so that someone reviewing the repository can understand the architecture, how to run it, how to test it, and what reliability and security features were implemented?

### Decision

The README was structured around:

- Architecture
- Components
- Project structure
- Prerequisites
- Deployment instructions
- Web application
- API endpoints
- CronJob
- PostgreSQL
- Scalability
- Self-healing
- Reliability and security
- Validation
- Cleanup
- Design considerations
- AI-assisted development

The goal was to make it possible for another engineer to clone the repository and understand how the solution works without needing additional explanation.

# Engineering Decisions

## Colima and K3s

Colima and K3s were selected because they provide a lightweight Kubernetes environment suitable for running locally on a laptop.

## FastAPI

FastAPI was selected because it provides a simple way to build the web application and REST endpoint without introducing unnecessary application complexity.

## PostgreSQL

PostgreSQL provides a real backend data store shared by the CronJob and web application.

Using a database also demonstrates persistence rather than simply writing collected information to a local file.

## Kubernetes CronJob

A Kubernetes CronJob was used instead of an application-level scheduler.

This keeps the scheduling responsibility with Kubernetes and allows the collector to run independently from the web application.

The schedule is:

    0 */6 * * *

This runs the collector every six hours.

## StatefulSet and PersistentVolumeClaim

PostgreSQL uses a StatefulSet with persistent storage.

The PersistentVolumeClaim prevents database data from being tied to the lifetime of the PostgreSQL pod.

## Horizontal Pod Autoscaler

The web application is stateless, so multiple replicas can serve requests.

The HPA scales the web Deployment based on CPU utilization.

The minimum replica count is two so that the application has more than one web pod during normal operation.

## NodePort

A NodePort Service was selected because it provides a simple way to access the application from a browser on the local Kubernetes environment without introducing an ingress controller.

# AI-Assisted vs. Human Validation

AI was used to assist with:

- Architecture ideas
- Code structure
- Kubernetes configuration
- Troubleshooting approaches
- Testing strategies
- Security considerations
- Documentation

The implementation was not accepted simply because an AI suggestion looked correct.

Commands were executed locally and the actual Kubernetes environment was used to verify the behavior.

The following were independently validated:

- Kubernetes resources
- PostgreSQL connectivity
- Persistent storage
- Database records
- CronJob execution
- Web application
- Health checks
- HPA metrics
- Horizontal scaling
- Pod self-healing

The final configuration reflects changes made during actual testing and troubleshooting.

# Lessons Learned

This assignment provided practical experience with several SRE concepts:

- Kubernetes workload management
- Containerization
- Persistent storage
- Scheduled workloads
- Application health checks
- Horizontal scaling
- Self-healing
- Resource management
- Secrets management
- Local Kubernetes development
- Operational validation

The main goal was to keep the implementation simple while still demonstrating production-oriented reliability, scalability, security, and operational practices.
