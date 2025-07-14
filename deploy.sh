#!/bin/bash

# Shield Backend Kubernetes Deployment Script
set -e

# Configuration
NAMESPACE="shield"
APP_NAME="shield-backend"
IMAGE_TAG=${1:-"0.0.0"}
REGISTRY=${2:-""}

echo "🚀 Deploying Shield Backend to Kubernetes..."
echo "Namespace: $NAMESPACE"
echo "Image Tag: $IMAGE_TAG"

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl is not installed or not in PATH"
        exit 1
    fi
}

# Function to check if cluster is accessible
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        echo "❌ Cannot connect to Kubernetes cluster"
        exit 1
    fi
    echo "✅ Connected to Kubernetes cluster"
}

# Function to build and tag Docker image
build_image() {
    echo "🔨 Building Docker image..."
    docker build -t ${APP_NAME}:${IMAGE_TAG} .
    
    if [ ! -z "$REGISTRY" ]; then
        echo "🏷️  Tagging image for registry..."
        docker tag ${APP_NAME}:${IMAGE_TAG} ${REGISTRY}/${APP_NAME}:${IMAGE_TAG}
        echo "📤 Pushing image to registry..."
        docker push ${REGISTRY}/${APP_NAME}:${IMAGE_TAG}
    fi
}

# Function to update image tag in deployment
update_image_tag() {
    local image_name="${APP_NAME}:${IMAGE_TAG}"
    if [ ! -z "$REGISTRY" ]; then
        image_name="${REGISTRY}/${APP_NAME}:${IMAGE_TAG}"
    fi
    
    echo "🔄 Updating deployment image to $image_name..."
    sed -i.bak "s|image: .*|image: $image_name|g" k8s/deployment.yaml
}

# Function to deploy to Kubernetes
deploy_k8s() {
    echo "📋 Applying Kubernetes manifests..."
    
    # Apply in order
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/rbac.yaml
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/ingress.yaml
    
    echo "⏳ Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/${APP_NAME} -n ${NAMESPACE}
    
    echo "✅ Deployment completed successfully!"
}

# Function to show deployment status
show_status() {
    echo "📊 Deployment Status:"
    kubectl get pods -n ${NAMESPACE} -l app=${APP_NAME}
    echo ""
    kubectl get services -n ${NAMESPACE}
    echo ""
    kubectl get ingress -n ${NAMESPACE}
}

# Main execution
main() {
    check_kubectl
    check_cluster
    build_image
    update_image_tag
    deploy_k8s
    show_status
    
    echo ""
    echo "🎉 Shield Backend deployed successfully!"
    echo "📝 Access the API documentation at: http://shield-backend.local/docs"
    echo "💡 To port-forward locally: kubectl port-forward svc/${APP_NAME}-service 8000:80 -n ${NAMESPACE}"
}

# Run main function
main "$@"
