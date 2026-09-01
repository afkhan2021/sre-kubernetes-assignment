#!/bin/bash

set -e

NAMESPACE="sre-assignment"

echo "Applying Kubernetes resources..."

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/web-deployment.yaml
kubectl apply -f k8s/web-service.yaml
kubectl apply -f k8s/cronjob.yaml
kubectl apply -f k8s/hpa.yaml

echo "Waiting for PostgreSQL..."
kubectl rollout status statefulset/postgres -n "${NAMESPACE}" --timeout=120s

echo "Waiting for web deployment..."
kubectl rollout status deployment/web -n "${NAMESPACE}" --timeout=120s

echo ""
echo "Deployment completed."
echo ""
kubectl get pods -n "${NAMESPACE}"
echo ""
kubectl get services -n "${NAMESPACE}"
echo ""
kubectl get hpa -n "${NAMESPACE}"
