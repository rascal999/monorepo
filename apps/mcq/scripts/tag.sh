#!/bin/bash

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

# Create tag name
if [ -n "$ENV" ]; then
    TAG="v${VERSION}-${ENV}"
else
    TAG="v${VERSION}"
fi

# Tag Docker images
echo "Tagging Docker images as ${TAG}..."
docker tag mcq_frontend "mcq_frontend:${TAG}"
docker tag mcq_api "mcq_api:${TAG}"

# Create git tag with annotation
echo "Creating git tag ${TAG}..."
git tag -a "${TAG}" -m "Release ${TAG}"

# Push git tag
echo "Pushing git tag..."
git push origin "${TAG}"

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
