# AWS Self-Healing Application Platform

A Terraform-managed AWS capstone for testing whether an application instance can fail without taking the service or its data with it.

The implementation uses **CloudSentinel** as an internal application codename. The public project name is **AWS Self-Healing Application Platform**.

## Status

This repository contains the local application and the initial Terraform foundation. AWS deployment, the controlled instance-failure drill, and cloud recovery evidence are intentionally pending.

No AWS resources have been created by this project yet.

## Target architecture

- Application Load Balancer across two Availability Zones
- Private EC2 Auto Scaling Group
- RDS MySQL for durable incident records
- Secrets Manager for database credentials
- S3 for versioned application artifacts
- IAM role and Systems Manager for administration
- NAT Gateway or a documented lower-cost egress alternative
- CloudWatch health visibility

The intended request path is:

```text
Internet → Internet Gateway → public subnet → ALB
       → private application subnet → EC2
       → private database subnet → RDS
```

The application instances are replaceable. RDS is the durable data boundary. The recovery proof will deliberately terminate one application instance, confirm that Auto Scaling replaces it, verify that the replacement becomes healthy through the ALB, and read the original incident record back from the database.

## Current implementation

The local application is a dependency-free Python HTTP service with:

- `/healthz` and `/readyz` health endpoints
- `/api/status` for service metadata
- `/api/incidents` for recent events
- `/api/heartbeat` for recording an event
- SQLite-backed local persistence for development and tests

The AWS implementation will replace the local SQLite store with RDS-backed storage while preserving the HTTP contract used by health checks and the evidence workflow.

## Local verification

Run the application locally:

```bash
python3 app/app.py
```

The default endpoint is `http://127.0.0.1:8080/`.

Run the tests:

```bash
python3 -m unittest discover -s app -p 'test_*.py' -v
```

Run the Terraform foundation checks:

```bash
terraform fmt -check
terraform init -backend=false -input=false
terraform validate
```

The current local verification includes three passing Python tests and successful Terraform initialization and validation. These checks do not prove AWS deployment or recovery behavior.

## Project boundaries

- No AWS plan or apply is included in the current evidence.
- No AWS account identifiers, credentials, state files, or private infrastructure details belong in this repository.
- The failure drill will be documented only after it has been executed and read back from AWS.
- Cost controls and cleanup are part of the eventual deployment workflow.
