# SHIELD Backend Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the SHIELD Backend application.

## Prerequisites

- Kubernetes cluster (local or remote)
- kubectl configured to access your cluster
- Docker for building images
- NGINX Ingress Controller (for ingress)

## Quick Start

### 1. Deploy to Kubernetes

```bash
# Deploy with default settings
make k8s-deploy

# Deploy with custom image tag
make k8s-deploy-tag TAG=v2.0.0

# Deploy with custom registry
make k8s-deploy-registry TAG=v1.0.0 REGISTRY=your-registry.com
```

### 2. Check deployment status

```bash
make k8s-status
```

### 3. View logs

```bash
make k8s-logs
```

### 4. Access the application

```bash
# Port forward to localhost
make k8s-port-forward

# Then access at http://localhost:8000
```

## Kubernetes Resources

### Files Overview

- `namespace.yaml` - Creates the `shield` namespace
- `rbac.yaml` - Service account and RBAC permissions
- `configmap.yaml` - Configuration data
- `deployment.yaml` - Main application deployment and service
- `ingress.yaml` - Ingress for external access

### Resource Details

- **Namespace**: `shield`
- **Deployment**: `shield-backend` (3 replicas)
- **Service**: `shield-backend-service` (ClusterIP on port 80)
- **Ingress**: `shield-backend-ingress` (nginx controller)
- **ServiceAccount**: `shield-backend-sa` (with minimal RBAC)

## Configuration

### Environment Variables

Add environment variables in `k8s/configmap.yaml`:

```yaml
data:
  DATABASE_URL: "mongodb://mongo-service:27017/shield"
  LOG_LEVEL: "info"
  # Add more as needed
```

### Secrets

For sensitive data, create a secret:

```bash
kubectl create secret generic shield-backend-secret \
  --from-literal=database-password=your-password \
  --namespace=shield
```

Then reference it in the deployment:

```yaml
env:
- name: DATABASE_PASSWORD
  valueFrom:
    secretKeyRef:
      name: shield-backend-secret
      key: database-password
```

### Resource Limits

Current resource configuration:

- **Requests**: 256Mi memory, 250m CPU, 1Gi storage
- **Limits**: 512Mi memory, 500m CPU, 2Gi storage

Adjust in `k8s/deployment.yaml` based on your needs.

### Health Checks

- **Liveness Probe**: `/health` endpoint (30s initial delay)
- **Readiness Probe**: `/health` endpoint (5s initial delay)

## Ingress Configuration

### Local Development

For local development, add to `/etc/hosts`:

```
127.0.0.1 shield-backend.local
```

### Production

Update `k8s/ingress.yaml` with your actual domain:

```yaml
rules:
- host: api.yourcompany.com
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make k8s-deploy` | Deploy to Kubernetes with default settings |
| `make k8s-deploy-tag TAG=v1.0.0` | Deploy with specific image tag |
| `make k8s-deploy-registry TAG=v1.0.0 REGISTRY=registry.com` | Deploy with custom registry |
| `make k8s-undeploy` | Remove all Kubernetes resources |
| `make k8s-status` | Check deployment status |
| `make k8s-logs` | View application logs |
| `make k8s-port-forward` | Port forward to localhost:8000 |
| `make k8s-restart` | Restart the deployment |

## Troubleshooting

### Pod not starting

```bash
# Check pod status
kubectl get pods -n shield

# Describe pod for events
kubectl describe pod <pod-name> -n shield

# Check logs
kubectl logs <pod-name> -n shield
```

### Service not accessible

```bash
# Check service endpoints
kubectl get endpoints -n shield

# Test service from within cluster
kubectl run test-pod --image=curlimages/curl -i --tty --rm -- sh
# Then: curl http://shield-backend-service.shield.svc.cluster.local
```

### Ingress issues

```bash
# Check ingress status
kubectl describe ingress shield-backend-ingress -n shield

# Ensure NGINX ingress controller is running
kubectl get pods -n ingress-nginx
```

## Security Considerations

- Service account with minimal RBAC permissions
- No automounting of service account tokens
- Resource limits to prevent resource exhaustion
- Health checks for reliability
- Separate namespace for isolation

## Monitoring

Consider adding:

- Prometheus metrics endpoint
- Grafana dashboards
- Log aggregation (ELK stack)
- Alert manager rules

## Updates

To update the deployment:

1. Build new image with updated tag
2. Update image tag in deployment
3. Apply changes: `kubectl apply -f k8s/deployment.yaml`
4. Monitor rollout: `kubectl rollout status deployment/shield-backend -n shield`
