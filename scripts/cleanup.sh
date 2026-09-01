#!/bin/bash

set -e

NAMESPACE="sre-assignment"

echo "Removing Kubernetes resources from ${NAMESPACE}..."

kubectl delete namespace "${NAMESPACE}" --ignore-not-found

echo "Cleanup completed."
