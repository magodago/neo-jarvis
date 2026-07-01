#!/usr/bin/env python3
import os, sys, datetime as dt
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

tok = os.path.expanduser("~/.hermes/google_token.json")
scopes = ["https://www.googleapis.com/auth/gmail.modify"]
creds = Credentials.from_authorized_user_file(tok, scopes)
service = build("gmail", "v1", credentials=creds)

def clean_bounces():
    yesterday = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).strftime("%Y/%m/%d")
    q = f"after:{yesterday} from:mailer-daemon@googlemail.com"
    results = service.users().messages().list(userId="me", q=q, maxResults=50).execute()
    msgs = results.get("messages", [])
    deleted = 0
    for msg in msgs:
        try:
            service.users().messages().trash(userId="me", id=msg["id"]).execute()
            deleted += 1
        except:
            pass
    return deleted

def archive_sent():
    yesterday = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).strftime("%Y/%m/%d")
    q = f"after:{yesterday} from:dortizs76@gmail.com subject:(NEO OR web OR plan OR 299 OR 599 OR 699)"
    results = service.users().messages().list(userId="me", q=q, maxResults=50).execute()
    msgs = results.get("messages", [])
    archived = 0
    for msg in msgs:
        try:
            service.users().messages().modify(userId="me", id=msg["id"],
                body={"removeLabelIds": ["INBOX"]}).execute()
            archived += 1
        except:
            pass
    return archived

if __name__ == "__main__":
    b = clean_bounces()
    a = archive_sent()
    if b > 0 or a > 0:
        print(f"Inbox cleanup: {b} bounces deleted, {a} sent archived")
