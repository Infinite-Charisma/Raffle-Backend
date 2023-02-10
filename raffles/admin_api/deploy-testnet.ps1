$CONTAINER_NAME="gcr.io/aslabs-raffles/raffles-admin-api/main/raffles-admin-api:latest"
docker build -t $CONTAINER_NAME -f ./raffles/admin_api/Dockerfile .
docker push $CONTAINER_NAME
gcloud run deploy raffles-admin-api-testnet `
    --project aslabs-raffles `
    --image $CONTAINER_NAME `
    --allow-unauthenticated `
    --region europe-west1 `
    --update-env-vars API_NEAR__ENVIRONMENT=testnet `
    --update-env-vars API_NEAR__ACCOUNT_ID=aslabs.testnet `
    --update-env-vars API_NEAR__PROVIDER_URL=https://rpc.testnet.near.org `
    --update-env-vars API_RAFFLES__CONTRACT_ID=raffle.raffles.aslabs.testnet