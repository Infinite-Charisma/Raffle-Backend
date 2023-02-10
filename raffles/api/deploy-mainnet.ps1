$CONTAINER_NAME="gcr.io/aslabs-raffles/raffles-api/main/raffles-api:latest"
docker build -t $CONTAINER_NAME -f ./raffles/api/Dockerfile .
docker push $CONTAINER_NAME
gcloud run deploy raffles-api-mainnet `
    --project aslabs-raffles `
    --image $CONTAINER_NAME `
    --allow-unauthenticated `
    --region europe-west1 `
    --update-env-vars API_NEAR__ENVIRONMENT=mainnet `
    --update-env-vars API_FIRESTORE__PROJECT_ID=aslabs-raffles `
    --update-env-vars API_DB__USER_COLLECTION=raffles-users `
    --update-env-vars API_RAFFLES__CONTRACT_ID=raffles.antisociallabs.near