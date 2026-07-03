#!/usr/bin/env python3
"""
Inbox Cleaner: Delete bounced emails and archive sent ones from Gmail inbox.
Runs via cron after each pipeline execution to keep inbox clean.

Uses Gmail API with existing OAuth token.
"""
import os, sys, json, pickle, base64, datetime, re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_PATH = os.path.expanduser('~/.hermes/google_token.json')
CREDS_PATH = os.path.expanduser('~/.hermes/gmail-credentials.json')

def get_service():
    """Get authenticated Gmail service."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(CREDS_PATH):
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                print("❌ No credentials file found")
                sys.exit(1)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def mark_as_read(service, msg_ids):
    """Mark messages as READ (remove from inbox prominence)."""
    if not msg_ids:
        return 0
    batch = service.users().messages().batchModify(
        userId='me',
        body={'ids': msg_ids, 'removeLabelIds': ['UNREAD']}
    )
    batch.execute()
    return len(msg_ids)

def archive_sent(service, days=1):
    """Archive sent emails older than `days` days (remove from INBOX, keep in Sent)."""
    query = f'in:inbox label:sent older_than:{days}d'
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=100).execute()
        msg_ids = [m['id'] for m in results.get('messages', [])]
        if msg_ids:
            service.users().messages().batchModify(
                userId='me',
                body={'ids': msg_ids, 'removeLabelIds': ['INBOX', 'UNREAD']}
            ).execute()
            print(f"  📦 Archivados {len(msg_ids)} emails enviados")
        return len(msg_ids)
    except HttpError as e:
        print(f"  ⚠️ Error archiving: {e}")
        return 0

def delete_bounced(service):
    """Find bounced emails and delete them."""
    # Bounce detection patterns
    bounce_queries = [
        'subject:(No se ha podido entregar) OR subject:(Mail Delivery Failed) OR subject:(Delivery Status Notification) OR subject:(Returned mail) OR subject:(Undelivered)',
        'subject:(bounce) OR subject:(rebote) OR from:(mailer-daemon) OR from:(postmaster)',
        'subject:(failure) from:(MAILER-DAEMON)',
    ]
    
    total_deleted = 0
    for query in bounce_queries:
        try:
            results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
            for msg in results.get('messages', []):
                try:
                    service.users().messages().delete(userId='me', id=msg['id']).execute()
                    total_deleted += 1
                except:
                    pass
        except:
            pass
    
    if total_deleted:
        print(f"  🗑️ Eliminados {total_deleted} emails de rebote")
    return total_deleted

def find_and_remove_bounces_from_sent(service):
    """Find sent emails that bounced by checking for bounce-back messages."""
    # Find our sent emails (from NEO)
    results = service.users().messages().list(
        userId='me', 
        q='from:dortizs76@gmail.com in:inbox',
        maxResults=200
    ).execute()
    
    sent_msgs = results.get('messages', [])
    
    # For each sent email, check if there's a bounce response
    deleted_count = 0
    for msg in sent_msgs[:50]:  # limit to 50
        try:
            full = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
            headers = {h['name']: h['value'] for h in full.get('payload', {}).get('headers', [])}
            to_addr = headers.get('To', '')
            subject = headers.get('Subject', '')
            
            # Check if it's one of our NEO emails
            if 'NEO' in subject or 'Web' in subject or 'marca' in subject.lower() or 'presencia' in subject.lower():
                # Check if there's a corresponding bounce in the same thread
                thread_id = full.get('threadId')
                thread = service.users().threads().get(userId='me', id=thread_id).execute()
                for tmsg in thread.get('messages', []):
                    theaders = {h['name']: h['value'] for h in tmsg.get('payload', {}).get('headers', [])}
                    tfrom = theaders.get('From', '').lower()
                    if 'mailer-daemon' in tfrom or 'postmaster' in tfrom:
                        # Bounce detected! Delete our sent message too
                        service.users().messages().delete(userId='me', id=msg['id']).execute()
                        deleted_count += 1
                        print(f"    🗑️ Eliminado enviado a {to_addr} (rebotó)")
                        break
        except:
            pass
    
    if deleted_count:
        print(f"  🗑️ Eliminados {deleted_count} emails enviados que rebotaron")
    return deleted_count

def list_bounced_and_sent(service):
    """List all bounced messages for logging."""
    results = service.users().messages().list(
        userId='me',
        q='from:(mailer-daemon OR postmaster) in:inbox',
        maxResults=20
    ).execute()
    
    bounces = []
    for msg in results.get('messages', []):
        try:
            full = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
            headers = {h['name']: h['value'] for h in full.get('payload', {}).get('headers', [])}
            bounces.append({
                'id': msg['id'],
                'from': headers.get('From', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
            })
        except:
            pass
    
    return bounces

def mark_bounced_in_db(db_path, bounced_list):
    """Update the DB to mark bounced leads."""
    if not os.path.exists(db_path):
        return
    
    import sqlite3
    conn = sqlite3.connect(db_path)
    
    for bounce in bounced_list:
        # Try to extract the original recipient from the bounce message
        subj = bounce.get('subject', '')
        # Common patterns: "No se ha podido entregar a <email>"
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', subj)
        if email_match:
            email = email_match.group(0)
            conn.execute('UPDATE leads SET estado_envio="bounced" WHERE email=?', (email,))
            print(f"    📝 Marcado como rebotado: {email}")
    
    conn.commit()
    conn.close()

def main():
    print(f"🧹 INBOX CLEANER — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    service = get_service()
    
    # 1. Delete bounce messages
    print("\n1️⃣ Buscando y eliminando rebotes...")
    bounced = list_bounced_and_sent(service)
    print(f"   Encontrados {len(bounced)} mensajes de rebote")
    
    deleted = delete_bounced(service)
    
    # 2. Delete sent emails that bounced
    print("\n2️⃣ Eliminando enviados que rebotaron...")
    removed = find_and_remove_bounces_from_sent(service)
    
    # 3. Archive old sent emails
    print("\n3️⃣ Archivando enviados antiguos...")
    archived = archive_sent(service, days=1)
    
    # 4. Mark bounced in DB
    db_path = '/home/dorti/neo-jarvis/briefing/lead-gen/data/leads.db'
    print("\n4️⃣ Actualizando base de datos...")
    mark_bounced_in_db(db_path, bounced)
    
    print(f"\n✅ INBOX CLEANER COMPLETADO")
    print(f"   Rebotes eliminados: {deleted}")
    print(f"   Enviados rebotados eliminados: {removed}")
    print(f"   Enviados archivados: {archived}")

if __name__ == '__main__':
    main()
