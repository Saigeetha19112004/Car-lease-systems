# Deployment Guide

This document contains basic templates and notes for deploying the Car Lease System.

- Build & publish images: see `.github/workflows/deploy.yml` which shows a template for building images and pushing to GHCR.
- Secrets: configure database credentials, PayPal IDs (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), SENTRY_DSN, and any cloud provider keys.
- Runtime considerations: use an object store (S3) for images and contracts, use managed DB (Cloud SQL/RDS), and configure background jobs for long-running tasks.
- Observability: add Sentry for error tracking and a metrics exporter / Prometheus + Grafana for metrics.
