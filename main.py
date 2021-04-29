import email
import imaplib
import os
import re
import time
from email.header import decode_header, make_header

import requests
from bs4 import BeautifulSoup
import lxml

from model import User, Email


def get_mail():
    mail = imaplib.IMAP4_SSL(os.environ.get('imap_host'), 993)
    mail.login(os.environ.get('imap_user'), os.environ.get('password'))
    return mail


def create_token():
    auth_token = requests.post(os.environ.get('AUTH_HOST') + 'login/service',
                               json={'token': os.environ.get('TOKEN')})
    return auth_token.json()['access_token']


def get_new_messages_list(mail):
    mail.select('Inbox')
    status, data = mail.search(None, '(UNSEEN)')
    return data[0]


def get_recipients(email_message):
    recipients = dict()
    address_fields = ['From', 'Cc']
    for field in address_fields:
        rfield = email_message.get(field, "")
        rlist = re.findall(re.compile('<(.*?)>'), rfield)
        recipients[field] = rlist
    return recipients


def get_message(email_id, mail):
    typ, data = mail.fetch(email_id, '(RFC822)')
    return data


def get_email_message(message):
    raw_email = message[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)
    return email_message


def get_text(email_message):
    body = email_message.get_payload(decode=True)
    soup = BeautifulSoup(body, features="lxml")
    text = soup.get_text()
    return text


def send_file_to_the_file_stock(filename):
    file = {'file': open(filename, 'rb')}
    token = {'Authorization': 'Bearer ' + create_token()}
    res = requests.post(os.getenv('FILE_STOCK') + '/upload', files=file, headers=token)
    requests.post(os.getenv('FILE_STOCK') + f"/files/change_access_by_id/{res.json()['id']}")
    return {"id": res.json()['id'], "filename": filename}


def send_email_to_bpm(recipients, subject, text, to, files):
    json_email = {
        'mail_from': recipients['From'],
        'mail_to': to,
        'subject': subject,
        'body': text,
        'mail_cc': recipients['Cc'],
        'files': files
    }
    return Email.from_dict(json_email).save()


def save_files(email_message):
    result: list[dict] = []
    for part in email_message.walk():
        filename = part.get_filename()

        if bool(filename):
            _id_file = ''
            filename = str(make_header(decode_header(filename)))
            with open(filename, 'wb') as fp:
                fp.write(part.get_payload(decode=True))
            result.append(send_file_to_the_file_stock(filename))
            os.remove(filename)
    return result


def process_message(email_id, mail):
    message = get_message(email_id, mail)
    email_message = get_email_message(message)
    subject = str(make_header(decode_header(email_message.get('Subject', ''))))
    text = ''
    recipients = get_recipients(email_message)

    user = User.find_one({"notify_email": recipients['From']})
    if email_message.is_multipart():
        for part in email_message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                text = get_text(part)
                break
    else:
        text = get_text(email_message)
    id_name_lst = save_files(email_message)
    print('debug')


def listen(mail):
    while True:
        new_messages_list = get_new_messages_list(mail)

        for email_id in new_messages_list.split():
            process_message(email_id, mail)

        time.sleep(1)


def main():
    mail = get_mail()
    listen(mail)


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
