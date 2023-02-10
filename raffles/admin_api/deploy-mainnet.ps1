$CONTAINER_NAME="gcr.io/aslabs-raffles/raffles-admin-api/main/raffles-admin-api:latest"
docker build -t $CONTAINER_NAME -f ./raffles/admin_api/Dockerfile .
docker push $CONTAINER_NAME
gcloud run deploy raffles-admin-api-mainnet `
    --project aslabs-raffles `
    --image $CONTAINER_NAME `
    --allow-unauthenticated `
    --region europe-west1 `
    --update-env-vars API_NEAR__ENVIRONMENT=mainnet `
    --update-env-vars API_NEAR__ACCOUNT_ID=antisociallabs.near `
    --update-env-vars API_NEAR__PROVIDER_URL=https://rpc.mainnet.near.org `
    --update-env-vars API_RAFFLES__CONTRACT_ID=raffles.antisociallabs.near