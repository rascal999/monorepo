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

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Committing changes..."
    git add .
    git commit -m "Release ${VERSION}${ENV:+ for $ENV}"
    git push origin HEAD
fi

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

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Check if we should push Docker images
if [ "${PUSH_DOCKER_IMAGES,,}" = "true" ]; then
    echo "Pushing Docker images..."
    docker push "mcq_frontend:${DOCKER_TAG}"
    docker push "mcq_api:${DOCKER_TAG}"
else
    echo "Skipping Docker image push (PUSH_DOCKER_IMAGES not set to true)"
fi

# Check if git tag exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Warning: Git tag ${TAG} already exists"
    read -p "Do you want to force update the tag? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Force updating git tag ${TAG} for apps/mcq directory only..."
        # Create a tree object containing only apps/mcq
        TREE=$(git write-tree --prefix=apps/mcq)
        # Create a commit object with the tree
        COMMIT=$(echo "Release ${TAG}" | git commit-tree $TREE -p HEAD)
        # Force update tag to point to the new commit
        git tag -fa "${TAG}" $COMMIT
        git push --force origin "${TAG}"
        git push --tags
        
        if [ "${PUSH_DOCKER_IMAGES,,}" = "true" ]; then
            echo "Re-pushing Docker images..."
            docker push "mcq_frontend:${DOCKER_TAG}"
            docker push "mcq_api:${DOCKER_TAG}"
        else
            echo "Skipping Docker image push (PUSH_DOCKER_IMAGES not set to true)"
        fi
    else
        echo "Skipping git tag creation"
    fi
else
    echo "Creating git tag ${TAG} for apps/mcq directory only..."
    # Create a tree object containing only apps/mcq
    TREE=$(git write-tree --prefix=apps/mcq)
    # Create a commit object with the tree
    COMMIT=$(echo "Release ${TAG}" | git commit-tree $TREE -p HEAD)
    # Create tag pointing to the new commit
    git tag -a "${TAG}" $COMMIT -m "Release ${TAG}"
    git push origin "${TAG}"
    git push --tags
    
    if [ "${PUSH_DOCKER_IMAGES,,}" = "true" ]; then
        echo "Pushing Docker images..."
        docker push "mcq_frontend:${DOCKER_TAG}"
        docker push "mcq_api:${DOCKER_TAG}"
    else
        echo "Skipping Docker image push (PUSH_DOCKER_IMAGES not set to true)"
    fi
fi

echo "Successfully tagged version ${TAG}"
echo
echo "IMPORTANT: When pulling on another machine, run:"
echo "   git pull"
echo "   git fetch --tags"
echo
echo "To deploy this version:"
echo "1. Update .env with:"
echo "   VERSION=${VERSION}"
echo "   ENV=${ENV:-prod}"
echo
echo "2. Pull and run the tagged images:"
echo "   docker pull mcq_frontend:${DOCKER_TAG}"
echo "   docker pull mcq_api:${DOCKER_TAG}"
echo
echo "3. Start the application:"
echo "   VERSION=${VERSION} ENV=${ENV:-prod} ./scripts/manage.sh start"
