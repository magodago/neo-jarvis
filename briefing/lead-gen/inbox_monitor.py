#!/usr/bin/env python3
"""Monitor de inbox: detecta respuestas a leads"""
import os, csv, json, datetime as dt
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
LEAD_DIR = "/home/dorti/neo-jarvis/briefing/lead-gen"
LOGS_DIR = os.path.join(LEAD_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def check_inbox():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("gmail", "v1", credentials=creds)
    yesterday = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)).strftime("%Y/%m/%d")
    q = f"after:{yesterday} is:inbox -from:dortizs76@gmail.com -category:promotions -category:social"
    results = service.users().messages().list(userId="me", q=q, maxResults=20).execute()
    msgs = results.get("messages", [])
    if not msgs:
        return {"status": "no_replies", "count": 0}
    replies = []
    for m in msgs:
        d = service.users().messages().get(userId="me", id=m["id"], format="metadata").execute()
        h = {x["name"]: x["value"] for x in d["payload"]["headers"]}
        replies.append({"id": m["id"], "from": h.get("From",""), "subject": h.get("Subject",""),
            "snippet": d.get("snippet",""), "date": h.get("Date","")})
    return {"status": "replies_found", "count": len(replies), "replies": replies}

def check_responses():
    result = check_inbox()
    if result["status"] == "no_replies":
        return {"new_leads": 0, "message": "Sin respuestas"}
    sent_path = os.path.join(LOGS_DIR, "sent.csv")
    sent = {}
    if os.path.exists(sent_path):
        with open(sent_path) as f:
            for row in csv.DictReader(f):
                sent[row.get("email_destino","")] = row
    new_responses = []
    for r in result["replies"]:
        f = r["from"]
        email = f.split("<")[1].split(">")[0] if "<" in f else f
        info = sent.get(email, {})
        if info:
            new_responses.append({"email": email, "nombre": info.get("nombre",email),
                "asunto": r["subject"], "snippet": r["snippet"][:200]})
    return {"new_leads": len(new_responses), "responses": new_responses}

if __name__ == "__main__":
    result = check_responses()
    if result["new_leads"] > 0:
        for r in result["responses"]:
            print(f"NUEVO LEAD: {r['nombre']} ({r['email']}) - {r['snippet']}")
