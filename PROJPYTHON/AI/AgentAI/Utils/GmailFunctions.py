import base64
import os.path

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import parsedate_to_datetime

def extractBody(payloads):
    body="none"
    if "parts" in payloads:
        for part in payloads["parts"]:
            if "multipart/alternative" in part["mimeType"]:
                for subpart in part["parts"]:
                    if subpart["mimeType"] =='text/plain' and "data" in subpart["body"]:
                        body = base64.urlsafe_b64decode(subpart["body"]["data"]).decode('utf-8')
                        break
            elif part['mimeType'] =='text/plain' and "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode('utf-8')
                        break
    elif 'body' in payloads and 'data' in payloads['body']:
            body = base64.urlsafe_b64decode(payloads["body"]["data"]).decode('utf-8')
    return body
def get_email_messages(services,user_id='me',label_ids=None,folder_name='INBOX',max_result=5):
    messages=[]
    next_page_token = None
    if folder_name:
        label_result = services.users().labels().list(userId=user_id).execute()
        labels = label_result.get("labels",[])
        folder_label_id = next((label['id']for label in labels if label['name'].lower()==folder_name.lower()),None)
        if folder_label_id:
            if label_ids:
                label_ids.append(folder_label_id)
            else:
                label_ids=[folder_label_id]
        else:
            raise ValueError(f"Folder {folder_name}")
    while True:
        result = services.users().messages().list(
            userId=user_id,
            labelIds=label_ids,
            maxResults=min(500,max_result-len(messages)) if max_result else 500,
            pageToken = next_page_token
        ).execute()
        messages.extend(result.get('messages',[]))
        next_page_token=result.get('nextPageToken')
        if not next_page_token or (max_result and  len(messages)>=max_result):
            break
    return messages[:max_result]if max_result else messages



def get_email_messages_details(service,msg_id):
    message = service.users().messages().get(userId='me',id=msg_id,format='full').execute()
    payloads = message['payload']
    headers=payloads.get("headers",[])
    subject = next((header["value"] for header in headers if header["name"].lower()=="subject"),None)
    if not subject:
        subject = message.get('subject','no subject')
    sender = next((header["value"] for header in  headers if header["name"]=='From'),'No sender')
    recipients = next((header["value"] for header in  headers if header["name"]=='To'),'recipient')
    snippet = message.get('snippet','No snippet')
    has_attachements =any(part.get('filename') for part in payloads.get("parts",[]) if part.get('filename'))
    date=next((header["value"] for header in  headers if header["name"]=='Date'),'date')
    if date!="no date":
        try:
            date=parsedate_to_datetime(date)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            date=date
    else:
        date="no date"

    start = message.get('labelIds',[]).count('STARRED')>0
    label = ", ".join(message.get('labelIds',[]))

    body=extractBody(payloads)

    return {
        "subject":subject,
        "sender":sender,
        "recipients":recipients,
        "snippet":snippet,
        "has_attachments":has_attachements,
        "date":date,
        "body":body,
        "start":start,
        'label':label

    }
def send_email(service,to,subject,body,body_type='plain',attachment_paths=None):
    message = MIMEMultipart()
    message['to']=to
    message['subject']=subject
    if body_type.lower() not in ['plain','html']:
        raise ValueError("body_type msut be either plain or html")
    message.attach(MIMEText(body,body_type.lower()))
    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)
                with open(attachment_path,"rb") as att:
                    part = MIMEBase("application","octet-stream")
                    part.set_payload(att.read())
                encoders.encode_base64(part) #part is still MIME what inside PART convert to base64 .. binary=>base64 with encode()
                part.add_header("Content-Disposition",f"attachment; filename= {filename}")
                message.attach(part)
            else:
                raise FileNotFoundError("not found path")
    raw_messgae = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8') #take the bytes from message do encode then decode make text then go encode
    sent_message = service.users().messages().send(
        userId='me',
        body={"raw":raw_messgae}
    ).execute()
    return sent_message
def download_attachments_parent(service,user_id,msg_id,target_dir):
    message = service.users().messages().get(userId=user_id,id=msg_id).execute()
    for part in message["payload"]['parts']:
        if part.get('filename') and part.get('body', {}).get('attachmentId'):
            att_id = part["body"]["attachmentId"]
            att = service.users().messages().attachments().get(userId=user_id,messageId=msg_id,id=att_id).execute()
            data = att["data"]
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            file_path = os.path.join(target_dir,part['filename'])
            with open(file_path,"wb") as f:
                f.write(file_data)
def search_emails(service,query,user_id='me',max_result=5):
    messages=[]
    next_page_token=None
    while True:
        result = service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=min(500,max_result-len(messages)) if max_result else 500,
            pageToken = next_page_token
        ).execute()
        messages.extend(result.get('messages',[]))
        next_page_token = result.get('nextPageToken')
        if not next_page_token or (max_result and len(messages))>= max_result:
            break
    return messages[:max_result] if max_result else messages


def search_email_conversation(service, query, user_id='me', max_result=5):
    """
    Optimized for LLM agents: Returns a clean structure with actual thread metadata
    so the agent can immediately understand what conversations exist.
    """
    threads = []
    next_page_token = None
    while True:
        result = service.users().threads().list(
            userId=user_id,
            q=query,
            maxResults=min(500, max_result - len(threads)) if max_result else 500,
            pageToken=next_page_token
        ).execute()
        threads.extend(result.get('threads', []))
        next_page_token = result.get('nextPageToken')
        if not next_page_token or (max_result and len(threads) >= max_result):
            break

    # Enrich simple thread objects with clean metadata names for the LLM tool context
    detailed_threads = []
    for t in threads[:max_result] if max_result else threads:
        detailed_threads.append({
            "thread_id": t.get("id"),
            "snippet": t.get("snippet")
        })
    return detailed_threads
def get_message_and_replies(service,message_id):
    message = service.users().messages().get(userId='me',id=message_id,format='full').execute()
    thread_id = message['threadId']
    thread = service.users().threads().get(userId='me',id=thread_id).execute()
    processed_messages= []
    for msg in thread['messages']:
        subject = next((header['value'] for header in msg["payload"]["headers"] if header['name'].lower()=='subject'),"no subject")
        from_header = next((header['value'] for header in msg["payload"]["headers"] if header['name'].lower()=='from'),"unknown sender")
        date = next((header['value'] for header in msg["payload"]["headers"] if header['name'].lower()=='date'),"no date")
        if date != "no date":
            try:
                date = parsedate_to_datetime(date)
                date = date.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                date = date

        content = extractBody(msg['payload'])

        processed_messages.append({
            'id':msg['id'],
            'subject':subject,
            'from':from_header,
            'date':date,
            'body':content
        })
    return processed_messages


def reply_email(service, msg_id, body, body_type='plain'):

    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    thread_id = message['threadId']
    headers = message['payload']['headers']


    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
    msg_id_header = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), '')
    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')


    reply = MIMEMultipart()
    reply['to'] = sender
    reply['subject'] = subject if subject.startswith('Re:') else f'Re: {subject}'
    reply['In-Reply-To'] = msg_id_header
    reply['References'] = msg_id_header
    reply.attach(MIMEText(body, body_type))


    raw = base64.urlsafe_b64encode(reply.as_bytes()).decode('utf-8')
    return service.users().messages().send(
        userId='me',
        body={
            'raw': raw,
            'threadId': thread_id
        }
    ).execute()


