# Setup

The following variables need to be set in order for `tofu plan` and `tofu apply` to work. The variables can either be exported as environment variables prefixed with `TF_VAR_` *(these will be automaticaly picked up by `tofu`)* for the current shell session or input on request from `tofu`.

```{bash}
# Project
export TF_VAR_project_id="${PROJECT_ID}" 
export TF_VAR_service_account_name="${SERVICE_ACCOUNT_NAME}"

# Artifact Registry
export TF_VAR_repo_name="${artifact_repo_name}"
export TF_VAR_repo_location="${artifact_repo_location}"

# Workload Identity Pool for Github Actions
export TF_VAR_workload_identity_pool_id="${WORKLOAD_IDENTITY_POOL_ID}"
export TF_VAR_workload_identity_pool_provider_id="${WORKLOAD_IDENTITY_POOL_PROVIDER_ID}"
export TF_VAR_github_repository_owner="${github_repository_owner}"
export TF_VAR_github_repository_name="${github_repository_name}"
```
## Setting up google_project

```{bash}
gcloud projects create $TF_VAR_project_id --name="${PROJECT_NAME}"
```

Enable billing for the project
```{bash}
gcloud billing projects link $TF_VAR_project_id -billing-account=${BILLING_ACCOUNT}
```

### Configuring `gcloud`
Set the created project as the current project
```
gcloud config set project $TF_VAR_project_id
```

## Create service account
```{bash}
gcloud iam service-accounts create $TF_VAR_service_account_name
gcloud iam service-accounts keys create key.json --iam-account="$TF_VAR_service_account_name"@"$TF_VAR_project_id".iam.gserviceaccount.com

gcloud auth activate-service-account "$TF_VAR_service_account_name"@"$TF_VAR_project_id".iam.gserviceaccount.com --key-file=key.json --project=$TF_VAR_project_id
```

## Create GCS bucket for storing tf state
`{BUCKET_NAME}` needs to be manually entered into `.tf` files for backend configuration.

```{bash}
gcloud storage buckets create "gs://${BUCKET_NAME}" --location=asia 
gcloud storage buckets update "gs://${BUCKET_NAME}" --versioning
```

## Setup artifact repository infrastructure using `tofu`
```{bash}
cd ${PROJECT_ROOT}/artifact-registry-tf
tofu init
tofu plan -out=plan
tofu apply plan
```

## Setup artifact repository infrastructure using `tofu`
```{bash}
cd ${PROJECT_ROOT}/artifact-registry-tf
tofu init
tofu plan -out=plan
tofu apply plan
```

Choose an image name
```{bash}
export TF_VAR_image_name="${IMAGE_NAME}"
```

Build and push Docker Image
```{bash}
cd ${PROJECT_ROOT}
docker build . --platform linux/amd64 -t "$TF_VAR_repo_location"-docker.pkg.dev/"$TF_VAR_project_id"/"$TF_VAR_repo_name"/"$TF_VAR_image_name":latest
docker push "$TF_VAR_repo_location"-docker.pkg.dev/"$TF_VAR_project_id"/"$TF_VAR_repo_name"/"$TF_VAR_image_name":latest
```
