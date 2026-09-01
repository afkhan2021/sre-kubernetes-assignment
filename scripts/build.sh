#!/bin/bash

set -e

IMAGE="sre-kubernetes-app:1.2"

echo "Building Docker image: ${IMAGE}"

docker build -t "${IMAGE}" .

echo "Build completed successfully."
