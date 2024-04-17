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

variable "repo_location" {
    type = string
    description = "Location (region) in which the artifact registry is located. Artifact repository should be created using the artifact-registry-tf module."
}

variable "repo_name" {
    type = string
    description = "Repository name of the artifact registry repository. Repository should be created using the artifact-registry-tf module."
}

variable "image_name" {
    type = string
    description = "The image name of the docker image found in artifact registry that should be deployed by cloud-run."
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
        prefix = "tofu/main-state"
    }
}

provider "google" {
    project = var.project_id
    region = var.region
}


resource "google_project_service" "cloudrun-service" {
    service = "run.googleapis.com"
    disable_dependent_services = true
}


resource "google_project_service" "ai-service" {
    service = "aiplatform.googleapis.com"
    disable_dependent_services = true
}

resource "google_project_service" "ml-service" {
    service = "ml.googleapis.com"
    disable_dependent_services = true
}

resource "google_service_account_iam_binding" "aiplatform-user-iam" {
    service_account_id = data.google_service_account.sa.name
    role = "roles/aiplatform.serviceAgent"

    members = [
        "serviceAccount:${var.service_account_name}@${var.project_id}.iam.gserviceaccount.com",
    ]
}

resource "google_cloud_run_v2_service" "cloud_run" {
    name = "${var.project_id}-app-ui"
    location = var.region
    template {
        containers {
            image = "${var.repo_location}-docker.pkg.dev/${var.project_id}/${var.repo_name}/${var.image_name}:latest"   
                resources {
                    limits = {
                        memory = "4Gi"
                    }
                }
            }
        service_account = "${var.service_account_name}@${var.project_id}.iam.gserviceaccount.com"
        }
}

resource "google_cloud_run_v2_service_iam_binding" "cloudrun-service-public-binding" {
    project = google_cloud_run_v2_service.cloud_run.project
    location = google_cloud_run_v2_service.cloud_run.location
    name = google_cloud_run_v2_service.cloud_run.name
    role = "roles/run.invoker"
    members = [
        "allUsers"
    ]
}

data "google_service_account" "sa" {
    account_id = var.service_account_name
}

resource "google_service_account_iam_binding" "workload-identity-user-iam" {
    service_account_id = data.google_service_account.sa.name
    role = "roles/iam.workloadIdentityUser"
    members = [
        "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.identity-pool.name}/attribute.repository/${var.github_repository_name}"
    ]
}

resource "google_iam_workload_identity_pool" "identity-pool" {
    workload_identity_pool_id = var.workload_identity_pool_id
    display_name = "CZ4052 CCP WIP"
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
    attribute_condition = "assertion.repository_owner == '${var.github_repository_owner}'"
    oidc {
        issuer_uri = "https://token.actions.githubusercontent.com" 
    }
}

