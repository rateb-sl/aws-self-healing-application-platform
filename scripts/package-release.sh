#!/usr/bin/env bash
set -euo pipefail

# Local release placeholder. AWS packaging will add the application artifact
# to the private S3 release bucket after the local app and Terraform checks pass.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${ROOT_DIR}/build"
mkdir -p "${OUTPUT_DIR}"
tar -czf "${OUTPUT_DIR}/cloudsentinel-${1:-dev}.tar.gz" -C "${ROOT_DIR}" app
printf 'Created local artifact: %s\n' "${OUTPUT_DIR}/cloudsentinel-${1:-dev}.tar.gz"
