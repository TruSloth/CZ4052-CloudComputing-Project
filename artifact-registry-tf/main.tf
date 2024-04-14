variable "region" {
    type = string
    description = "Region used for services"
}

variable "service_account_name" {
    type = string
    description = "Name of service account to be used. Service account should be set up in the project beforehand."
}

variable "project_id" {
    type = string
    description = "ID of the project. Project should be created beforehand."
}

variable "workload_identity_pool_id" {
    type = string
    description = "ID of the workload identity pool to be created."
}

variable "workload_identity_pool_provider_id" {
    type = string
    description = "ID of the workload identity pool provider to be added."
}

variable "github_repository_owner" {
    type = string
    description = "Owner of the Github repository to allow workload identity pool access."
}

variable "github_repository_name" {
    type = string
    description = "Name of the Github repository to allow workload identity pool access for."
}

terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = ">= 5.24.0"
        } 
    }

    backend "gcs" {
        bucket = "cz4052-cloud-computing-project-bucket"
        prefix = "tofu/artifact-registry-state"
    }
}

provider "google" {
    project = var.project_id
    region = var.region
}

resource "google_project_service" "iam-service" {
    service = "iam.googleapis.com"
    disable_dependent_services = true
}

resource "google_project_service" "artifact-registry-service" {
    service = "artifactregistry.googleapis.com"
    disable_dependent_services = true
}



data "google_service_account" "sa" {
    account_id = var.service_account_name
}

resource "google_service_account_iam_binding" "editor-iam" {
    service_account_id = data.google_service_account.sa.name
    role = "roles/editor"

    members = [
        "serviceAccount:${var.service_account_name}@${var.project_id}.iam.gserviceaccount.com",
    ]
}

resource "google_project_iam_binding" "editor-iam-project-binding" {
    members = [
        "serviceAccount:${var.service_account_name}@${var.project_id}.iam.gserviceaccount.com",
    ]

    role = "roles/editor"
    project = var.project_id
}

resource "google_service_account_iam_binding" "workload-identity-user-iam" {
    service_account_id = data.google_service_account.sa
    role = "roles/iam.workloadIdentityUser"
    members = [
        "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.identity-pool.id}/attribute.repository/${var.github_repository_name}"
    ]
}

resource "google_artifact_registry_repository" "repo" {
    location      = var.region
    repository_id = "${var.project_id}-artifact-repo"
    description   = "Artifact Repository for Docker Images for CZ4052-CloudComputing Project"
    format        = "DOCKER"
}

output "artifact_repo_name" {
    value = google_artifact_registry_repository.repo.name
}

output "artifact_repo_location" {
    value = google_artifact_registry_repository.repo.location
}

resource "google_iam_workload_identity_pool" "identity-pool" {
    workload_identity_pool_id = var.workload_identity_pool_id
    display_name = "CZ4052 Cloud Computing Project Workload Identity Pool"
    description = "Workload identity pool for automated CI/CD"
}

resource "google_iam_workload_identity_pool_provider" "github-identity-pool-provider" {
    workload_identity_pool_id = google_iam_workload_identity_pool.identity-pool.workload_identity_pool_id
    workload_identity_pool_provider_id = var.workload_identity_pool_provider_id
    attribute_mapping = {
        "google.subject": "assertion.sub",
        "attribute.actor": "assertion.actor",
        "attribute.repository": "assertion.repository",
        "attribute.repository_owner": "assertion.repository_owner"
    }
    attribute_condition = "assertion.repository_owner == ${var.github_repository_owner}"
    oidc {
        issuer_uri = "https://token.actions.githubusercontent.com" 
    }
}

