# SRE Kubernetes Assignment

A small Kubernetes-based application that periodically collects system information, stores it in PostgreSQL, and displays the results through a web dashboard.

## Architecture

The application runs locally using **Colima + K3s Kubernetes**.

```text
                         macOS Laptop
                              |
                         Colima / K3s
                              |
               +--------------+--------------+
               |                             |
        NodePort :30080              Kubernetes CronJob
               |                             |
               v                             v
        Web Deployment                System Collector
         2-5 replicas                        |
               |                             |
               +-------------+---------------+
                             |
                             v
                        PostgreSQL
                        StatefulSet
                             |
                            PVC
```

## Components
| Component | Purpose |
|---|---|
| FastAPI | Web application and REST API |
| PostgreSQL 16 | Persistent backend data store |
| Kubernetes CronJob | Collects system information every 6 hours |
| Deployment | Runs the web application |
| Horizontal Pod Autoscaler | Scales web pods from 2 to 5 replicas |
| NodePort Service | Provides browser access on the local machine |
| PersistentVolumeClaim | Provides persistent PostgreSQL storage |
| Kubernetes Secret | Stores database credentials |
## Project Structure
sre-kubernetes-assignment/
├── app/
│   ├── main.py
│   └── db.py
├── cron/
│   └── collector.py
├── k8s/
│   ├── namespace.yaml
│   ├── secret.example.yaml
│   ├── postgres.yaml
│   ├── postgres-service.yaml
│   ├── web-deployment.yaml
│   ├── web-service.yaml
│   ├── cronjob.yaml
│   └── hpa.yaml
├── scripts/
│   ├── build.sh
│   ├── deploy.sh
│   └── cleanup.sh
├── docs/
├── Dockerfile
├── requirements.txt
├── AI_PROMPTS.md
├── README.md
└── .gitignore
## Prerequisites
- Docker
- Colima
- Kubernetes / kubectl
- Python 3
- Git

The Kubernetes environment used for this assignment is K3s running through Colima.

## Getting Started
### 1. Start Kubernetes
colima start --kubernetes --runtime docker
kubectl get nodes

The node should show Ready.

### 2. Configure Database Credentials

The real Kubernetes Secret is stored locally as:

k8s/secret.yaml

This file is intentionally excluded from Git using .gitignore.

For a new environment:

cp k8s/secret.example.yaml k8s/secret.yaml

Then replace the placeholder values with the desired PostgreSQL database, username, and password.

### 3. Build the Application
./scripts/build.sh

Docker image:

sre-kubernetes-app:1.2
### 4. Deploy to Kubernetes
./scripts/deploy.sh

Verify the deployment:

kubectl get pods -n sre-assignment
kubectl get services -n sre-assignment
kubectl get cronjobs -n sre-assignment
kubectl get hpa -n sre-assignment
## Web Application

The application is exposed through a Kubernetes NodePort.

Open in your browser:

http://localhost:30080

The dashboard displays:

- Application status
- Last collection time
- Number of stored records
- Hostname
- CPU count
- Memory
- Disk usage
- Load average

The dashboard automatically refreshes every 30 seconds.

## API Endpoints
### Health Check
GET /health

Used by the Kubernetes liveness probe.

### Readiness Check
GET /ready

Checks database connectivity and is used by the Kubernetes readiness probe.

### System Information
GET /api/system-info

Returns the most recent system information records stored in PostgreSQL.

## Kubernetes CronJob

The collector runs every 6 hours:

0 */6 * * *

The collector gathers:

- Collection timestamp
- Hostname
- CPU count
- Total memory
- Disk usage percentage
- Load average

The collected information is stored in PostgreSQL and displayed by the web application.

Check the CronJob
kubectl get cronjob -n sre-assignment
Manually Trigger a Test
kubectl create job --from=cronjob/system-info-collector cronjob-test -n sre-assignment
View Logs
kubectl logs job/cronjob-test -n sre-assignment
Clean Up the Test Job
kubectl delete job cronjob-test -n sre-assignment
## PostgreSQL

PostgreSQL runs as a Kubernetes StatefulSet with:

- PostgreSQL 16
- PersistentVolumeClaim
- 1 GiB local persistent storage
- Kubernetes Secret for credentials
- Readiness and liveness checks

PostgreSQL is exposed only internally through a Kubernetes ClusterIP Service.

## Scalability

The web application is designed to scale horizontally.

### HPA Configuration
| Setting | Value |
|---|---:|
| Minimum replicas | 2 |
| Maximum replicas | 5 |
| CPU target | 70% |
| HPA API | `autoscaling/v2` |

Check the HPA:

kubectl get hpa -n sre-assignment
### Scalability Test

A temporary Kubernetes load generator was used to validate horizontal scaling.

Under sustained CPU load:

2 replicas → 4 replicas

After the load was removed and the stabilization period elapsed:

4 replicas → 2 replicas

This demonstrates that the web application can scale horizontally under increased load.

## Self-Healing

Kubernetes automatically maintains the desired number of web replicas.

During testing, a running web pod was manually deleted. Kubernetes automatically created a replacement pod and restored the Deployment to the desired replica count.

## Reliability and Security

The implementation includes:

- Two web replicas by default
- Horizontal Pod Autoscaling
- Readiness and liveness probes
- CPU and memory requests and limits
- Persistent PostgreSQL storage
- CronJob retry configuration
- CronJob concurrency policy
- Kubernetes Secret for database credentials
- Real Secret excluded from Git
- `secret.example.yaml` provided for deployment
- Web container runs as a non-root user
- Privilege escalation disabled
- Linux capabilities dropped
- RuntimeDefault seccomp profile
- PostgreSQL exposed only internally
## Assignment Requirement

The required comment was added to the application:

# I completed the assignment.
## Validation
| Test | Result |
|---|---|
| Kubernetes cluster | Passed |
| PostgreSQL StatefulSet | Passed |
| Persistent storage | Passed |
| System information collection | Passed |
| Kubernetes CronJob | Passed |
| Web application | Passed |
| Browser access | Passed |
| Database connectivity | Passed |
| HPA scale-up | Passed |
| HPA scale-down | Passed |
| Pod self-healing | Passed |
| Health endpoint | Passed |
| Readiness endpoint | Passed |
## Useful Commands
### View All Resources
kubectl get all -n sre-assignment
### View Pods
kubectl get pods -n sre-assignment
### View HPA
kubectl get hpa -n sre-assignment
### View CronJob
kubectl get cronjob -n sre-assignment
### View Resource Usage
kubectl top pods -n sre-assignment
## Cleanup

To remove the Kubernetes resources created for this assignment:

./scripts/cleanup.sh
## Design Considerations

The collector runs inside Kubernetes. Therefore, the system information represents the Kubernetes container environment rather than the physical macOS host.

For a production implementation, additional improvements could include:

- Managed PostgreSQL
- TLS/HTTPS
- Ingress
- External Secrets management
- NetworkPolicies
- Prometheus and Grafana monitoring
- Structured application logging
- Database migrations
- CI/CD pipeline
- Multi-node Kubernetes cluster
- PodDisruptionBudget
- Automated database backups
## AI-Assisted Development

AI was used as an engineering assistant for:

- Architecture design
- Application structure
- Kubernetes manifests
- Troubleshooting
- Scalability testing strategy
- Security considerations
- Documentation

See AI_PROMPTS.md for the documented prompts and engineering thought process.

All implementation steps were reviewed and tested locally before being considered complete.
