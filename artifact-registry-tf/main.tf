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

