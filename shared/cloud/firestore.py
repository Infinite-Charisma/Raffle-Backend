import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from dataclasses import dataclass


@dataclass
class FirestoreConfig:
    sa_file: str
    project_id: str
    token_data_collection: str
    channel_collection: str
    historical_data_collection: str
    upcoming_projects_collection: str
    api_key_collection: str


def firestore_client_factory(config: FirestoreConfig, client_id: str = "sniper") -> firestore.firestore.Client:
    json = config.sa_file
    project_id = config.project_id
    app = None
    if json:
        cred = credentials.Certificate(json)
        app = firebase_admin.initialize_app(cred, name=client_id)
    elif firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        app = firebase_admin.initialize_app(cred, options={
            'projectId': project_id,
        })

    return firestore.client(app=app)
