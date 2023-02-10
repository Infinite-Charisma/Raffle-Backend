$CONTAINER_NAME="gcr.io/aslabs-raffles/raffles-api/main/raffles-api:latest"
docker build -t $CONTAINER_NAME -f ./raffles/api/Dockerfile .
docker push $CONTAINER_NAME
gcloud run deploy raffles-api-testnet `
    --project aslabs-raffles `
    --image $CONTAINER_NAME `
    --allow-unauthenticated `
    --region europe-west1 `
    --update-env-vars API_NEAR__ENVIRONMENT=testnet `
    --update-env-vars API_FIRESTORE__PROJECT_ID=aslabs-raffles `
    --update-env-vars API_DB__USER_COLLECTION=testnet-raffles-users `
    --update-env-vars API_RAFFLES__CONTRACT_ID=raffle.raffles.aslabs.testnet