#!/usr/bin/env bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"

# Change to project directory
cd "$PROJECT_DIR"

# Function to display usage instructions
usage() {
    echo "Usage: $0 <major.minor.patch> [environment]"
    echo
    echo "Examples:"
    echo "  $0 1.0.0          # Tag as v1.0.0"
    echo "  $0 1.0.1 prod     # Tag as v1.0.1-prod"
    echo "  $0 1.1.0 staging  # Tag as v1.1.0-staging"
    echo
    exit 1
}

# Validate version format
validate_version() {
    if ! echo "$1" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' > /dev/null; then
        echo "Error: Version must be in format major.minor.patch (e.g., 1.0.0)"
        exit 1
    fi
}

# Check arguments
if [ $# -lt 1 ]; then
    usage
fi

VERSION=$1
ENV=$2
validate_version "$VERSION"

# Create tag name with mcq prefix for monorepo
if [ -n "$ENV" ]; then
    TAG="mcq/v${VERSION}-${ENV}"
else
    TAG="mcq/v${VERSION}"
fi

# Create Docker tag names (without mcq/ prefix)
if [ -n "$ENV" ]; then
    DOCKER_TAG="v${VERSION}-${ENV}"
else
    DOCKER_TAG="v${VERSION}"
fi

# Build and tag Docker images
echo "Building Docker images..."
docker-compose build

echo "Tagging Docker images as ${DOCKER_TAG}..."
docker tag mcq_frontend:latest "mcq_frontend:${DOCKER_TAG}"
docker tag mcq_api:latest "mcq_api:${DOCKER_TAG}"

# Check if git tag exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Warning: Git tag ${TAG} already exists"
    read -p "Do you want to force update the tag? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Force updating git tag ${TAG} for apps/mcq directory only..."
        # Force update tag only including apps/mcq directory
        git tag -fa "${TAG}" -m "Release ${TAG}" -- apps/mcq
        git push --force origin "${TAG}"
    else
        echo "Skipping git tag creation"
    fi
else
    echo "Creating git tag ${TAG} for apps/mcq directory only..."
    # Create tag only including apps/mcq directory
    git tag -a "${TAG}" -m "Release ${TAG}" -- apps/mcq
    git push origin "${TAG}"
fi

echo "Successfully tagged version ${TAG}"
echo
echo "To deploy this version:"
echo "1. Update .env with:"
echo "   VERSION=${VERSION}"
echo "   ENV=${ENV:-prod}"
echo
echo "2. Pull and run the tagged images:"
echo "   docker pull mcq_frontend:${TAG}"
echo "   docker pull mcq_api:${TAG}"
echo
echo "3. Start the application:"
echo "   VERSION=${VERSION} ENV=${ENV:-prod} ./scripts/manage.sh start"
