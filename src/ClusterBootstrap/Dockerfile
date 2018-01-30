# The Dockerfile to build a cluster-autoscaler.
FROM jinl/dlworkspacedevdocker

# Copy src/ClusterBootstrap in container
COPY . /ClusterBootstrap

# Assume non-iterative az cli is configured and installed.

# TODO(harry): Download clusterautoscaler binary
# ADD https://github.com/resouer/clusterautoscaler/releases/download/v0.1/clusterautoscaler /ClusterBootstrap/clusterautoscaler

# Set work directory
WORKDIR /ClusterBootstrap
