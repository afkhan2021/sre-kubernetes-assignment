# SRE Kubernetes Assignment

A small Kubernetes-based application that periodically collects system information, stores it in PostgreSQL, and displays the results through a web dashboard.

## Architecture

The application runs locally using Colima and K3s.

```text
                         macOS Laptop
                              |
                         Colima / K3s
                              |
              +---------------+---------------+
              |                               |
        NodePort :30080                Kubernetes CronJob
              |                               |
              v                               v
       Web Deployment                  System Collector
        2-5 replicas                         |
              |                               |
              +---------------+---------------+
                              |
                              v
                         PostgreSQL
                         StatefulSet
                              |
                             PVC
Components
FastAPI - Web application and REST API
PostgreSQL 16 - Persistent backend data store
Kubernetes CronJob - Collects system information every 6 hours
Deployment - Runs 2 web replicas by default
Horizontal Pod Autoscaler - Scales web pods from 2 to 5 replicas based on CPU
NodePort Service - Makes the application accessible from the local browser
PersistentVolumeClaim - Provides persistent PostgreSQL storage
Kubernetes Secret - Stores database credentials
Project Structure
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
Prerequisites

The following tools are required:

Docker
Colima
Kubernetes / kubectl
Python 3
Git

The Kubernetes environment used for this assignment is K3s running through Colima.

Start the Local Kubernetes Environment

Start Colima with Kubernetes enabled:

colima start --kubernetes --runtime docker

Verify the cluster:

kubectl get nodes

The expected node should show Ready.

Build the Application

Build the Docker image:

./scripts/build.sh

The image is:

sre-kubernetes-app:1.2
Configure Database Credentials

The actual Kubernetes Secret is stored locally in:

k8s/secret.yaml

This file is intentionally excluded from Git using .gitignore.

For a new environment, copy the example:

cp k8s/secret.example.yaml k8s/secret.yaml

Then replace the placeholder values with the desired PostgreSQL database, username, and password.

Deploy to Kubernetes

Run:

./scripts/deploy.sh

Verify the resources:

kubectl get pods -n sre-assignment
kubectl get services -n sre-assignment
kubectl get cronjobs -n sre-assignment
kubectl get hpa -n sre-assignment
Access the Web Application

The web application is exposed through a Kubernetes NodePort.

Open the following address in a normal browser:

http://localhost:30080

The dashboard displays:

Application status
Last collection time
Number of stored records
Collected hostname
CPU count
Memory
Disk usage
Load average

The dashboard automatically refreshes every 30 seconds.

API Endpoints
Health
GET /health

Used by the Kubernetes liveness probe.

Readiness
GET /ready

Checks that the application can connect to PostgreSQL.

Used by the Kubernetes readiness probe.

System Information
GET /api/system-info

Returns the most recent collected system information records.

CronJob

The Kubernetes CronJob runs every 6 hours:

0 */6 * * *

The collector gathers:

Collection timestamp
Hostname
CPU count
Total memory
Disk usage percentage
Load average

The information is stored in PostgreSQL.

Check the CronJob:

kubectl get cronjob -n sre-assignment

To manually trigger a test run:

kubectl create job \
  --from=cronjob/system-info-collector \
  cronjob-test \
  -n sre-assignment

Check the job:

kubectl get jobs -n sre-assignment

View the collector logs:

kubectl logs job/cronjob-test -n sre-assignment

After testing, the temporary Job can be removed:

kubectl delete job cronjob-test -n sre-assignment
PostgreSQL

PostgreSQL runs as a Kubernetes StatefulSet with:

PostgreSQL 16
PersistentVolumeClaim
1 GiB local persistent storage
Kubernetes Secret for credentials
Readiness and liveness checks

The database is only exposed internally through a ClusterIP Service.

Scalability

The web application runs with 2 replicas by default.

The Horizontal Pod Autoscaler is configured as:

Minimum replicas: 2
Maximum replicas: 5
CPU target: 70%

The HPA uses Kubernetes autoscaling/v2.

During testing, sustained CPU load caused the web Deployment to scale from:

2 replicas → 4 replicas

After the load was removed and the stabilization period elapsed, it scaled back:

4 replicas → 2 replicas

This demonstrates that the web application can scale horizontally under increased load.

Check HPA status:

kubectl get hpa -n sre-assignment
Self-Healing

Kubernetes automatically replaces failed web pods.

During testing, a running web pod was manually deleted. Kubernetes automatically created a replacement pod and restored the Deployment to the desired replica count.

This demonstrates Kubernetes self-healing behavior.

Reliability and Security

The application includes several reliability and security controls:

Multiple web replicas
Horizontal Pod Autoscaling
Readiness and liveness probes
CPU and memory resource requests and limits
PostgreSQL persistent storage
CronJob retry configuration
CronJob concurrency policy
Database credentials stored in a Kubernetes Secret
Secret file excluded from Git
Web container runs as a non-root user
Privilege escalation disabled
Linux capabilities dropped
RuntimeDefault seccomp profile
PostgreSQL is not externally exposed
Assignment Requirement

The required comment was added to the application:

# I completed the assignment.
Validation

The following functionality was tested successfully:

Test	Result
Kubernetes cluster	Passed
PostgreSQL StatefulSet	Passed
Persistent storage	Passed
System information collection	Passed
Kubernetes CronJob	Passed
Web application	Passed
Browser access	Passed
Database connectivity	Passed
HPA scale-up	Passed
HPA scale-down	Passed
Pod self-healing	Passed
Health endpoint	Passed
Readiness endpoint	Passed
Useful Commands

View all resources:

kubectl get all -n sre-assignment

View pods:

kubectl get pods -n sre-assignment

View HPA:

kubectl get hpa -n sre-assignment

View CronJob:

kubectl get cronjob -n sre-assignment

View recent collector logs:

kubectl logs -l job-name=system-info-collector -n sre-assignment

View resource usage:

kubectl top pods -n sre-assignment
Cleanup

To remove the Kubernetes environment created for this assignment:

./scripts/cleanup.sh
Design Considerations

The collector runs inside Kubernetes, so the system information collected represents the Kubernetes container environment rather than the physical macOS host.

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
