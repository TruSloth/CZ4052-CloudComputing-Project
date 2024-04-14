# Setup

Decide on a `project_id`, `service_account_name` and export as environment variables for the current shell.
Environment variables prefixed with `TF_VAR_` will be automatically picked up by open-tofu when running `tofu plan` and `tofu apply`.
```{bash}
export TF_VAR_project_id="${PROJECT_ID}"
export TF_VAR_service_account_name="${SERVICE_ACCOUNT_NAME}"
```

Manually create a google_project
```{bash}
gcloud projects create $TF_VAR_project_id --name="${PROJECT_NAME}"
```

Enable billing for the project
```
gcloud billing projects link $TF_VAR_project_id -billing-account=${BILLING_ACCOUNT}
```

Set the created project as the current project
```
gcloud config set project $TF_VAR_project_id
```

Create service account
```{bash}
gcloud iam service-accounts create $TF_VAR_service_account_name
gcloud iam service-accounts keys create key.json --iam-account="$TF_VAR_service_account_name"@"$TF_VAR_project_id".iam.gserviceaccount.com

gcloud auth activate-service-account "$TF_VAR_service_account_name"@"$TF_VAR_project_id".iam.gserviceaccount.com --key-file=key.json --project=cz4052-cloud-computing-project
```

Create GCS bucket for storing tf state
```{bash}
gcloud storage buckets create "gs://${BUCKET_NAME}" --location=asia 
gcloud storage buckets update "gs://${}BUCKET_NAME" --versioning
```

## Setup artifact repository infrastructure
```{bash}
cd ${PROJECT_ROOT}/artifact-registry-tf
tofu init
tofu plan -out=plan
tofu apply plan
```

Store the outputs of `tofu apply` as environment variables
```{bash}
export TF_VAR_repo_name="${artifact_repo_name}"
export TF_VAR_repo_location="${artifact_repo_location}"
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

Set up CI/CD to Cloud Run using Github Actions
```{bash}
export TF_VAR_workload_identity_pool_id="${WORKLOAD_IDENTITY_POOL_ID}"
export TF_VAR_workload_identity_pool_provider_id="${WORKLOAD_IDENTITY_POOL_PROVIDER_ID}"
export TF_VAR_github_repository_owner="${github_repository_owner}"
export TF_VAR_github_repository_name="${github_repository_name}"
```
