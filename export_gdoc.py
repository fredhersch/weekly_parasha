import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def get_google_creds():
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json',
        scopes=SCOPES
    )
    return creds


def export_to_gdoc(
    research: str,
    commentary: str,
    script: str,
    parsha: str = "Weekly Parasha"
) -> str:
    creds = get_google_creds()
    docs = build('docs', 'v1', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)

    # Create the document
    doc = docs.documents().create(
        body={"title": f"Torah Study - {parsha}"}
    ).execute()
    doc_id = doc['documentId']

    # Share it with your personal Google account so you can see it
    drive.permissions().create(
        fileId=doc_id,
        body={
            'type': 'user',
            'role': 'writer',
            'emailAddress': 'fredhersch@gmail.com'
        }
    ).execute()

    # Build full text
    full_text = (
        f"RESEARCH\n\n"
        f"{research}\n\n"
        f"---\n\n"
        f"COMMENTARY\n\n"
        f"{commentary}\n\n"
        f"---\n\n"
        f"PODCAST SCRIPT\n\n"
        f"{script}\n"
    )

    # Insert text
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': full_text
            }
        }
    ]

    docs.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"✅ Created: {doc_url}")
    return doc_url