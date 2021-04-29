import datetime

import jsonpickle as jsonpickle
from bson import ObjectId
from validate_email import validate_email

from config import db


class Email:

    def __init__(self, _id=None, mail_from=None, mail_to=None, mail_cc=None, mail_bcc=None, subject=None,
                 body=None, file_ocr_str=None, json=None, create_datetime=None, tracker=None):
        self._id = _id
        self.mail_from = mail_from
        self.mail_to = mail_to
        self.mail_cc = mail_cc
        self.mail_bcc = mail_bcc
        self.subject = subject
        self.body = body
        self.file_ocr_str = file_ocr_str
        self.create_datetime = create_datetime
        self.json = json
        self.tracker = tracker

    def save(self):
        self.status = 1
        self.create_datetime = datetime.datetime.now()
        raw = self.to_dict()
        raw.pop('_id', None)
        _id = db.email.insert_one(raw).inserted_id
        return self.find_one({'_id': ObjectId(_id)})

    @classmethod
    def find(cls, params=None):
        if params is None:
            params = {}
        emails = db.email.find(params)
        if emails.count() == 0:
            return []
        result = []
        for email in emails:
            email_obj = cls.from_dict(email)
            result.append(email_obj)
        return result

    @classmethod
    def find_one(cls, param=None):
        if param is None:
            param = {}
        email = db.email.find_one(param)
        if email is None:
            return None
        return cls.from_dict(email)

    def to_dict(self):
        return {
            '_id': self._id,
            'mail_from': self.mail_from,
            'create_datetime': str(self.create_datetime),
            'mail_to': self.mail_to,
            'mail_cc': self.mail_cc,
            'mail_bcc': self.mail_bcc,
            'subject': self.subject,
            'body': self.body,
            'file_ocr_str': self.file_ocr_str,
            'json': self.json,
            'tracker': self.tracker
        }

    def to_json(self):
        return {
            '_id': str(self._id),
            'mail_from': self.mail_from,
            'create_datetime': self.create_datetime.isoformat() if self.create_datetime else None,
            'mail_to': self.mail_to,
            'mail_cc': self.mail_cc,
            'mail_bcc': self.mail_bcc,
            'subject': self.subject,
            'body': self.body,
            'file_ocr_str': {str(i): j for i, j in self.file_ocr_str.items()},
            'json': {str(i): j for i, j in self.json.items()},
            'tracker': self.tracker
        }

    @classmethod
    def from_dict(cls, _dict):
        result = cls()
        result._id = ObjectId(_dict['_id']) if _dict.get('_id', None) else _dict.get('_id', None)
        result.mail_from = _dict.get('mail_from', '')
        result.mail_to = _dict.get('mail_to', '')
        result.mail_cc = _dict.get('mail_cc', '')
        result.mail_bcc = _dict.get('mail_bcc', '')
        result.subject = _dict.get('subject', '')
        result.body = _dict.get('body', '')
        result.tracker = _dict.get('tracker', '')
        if _dict.get('json', {}):
            result.json = {str(i): j for i, j in _dict.get('json').items()}
        else:
            result.json = {}
        if _dict.get('file_ocr_str', {}):
            result.file_ocr_str = {str(i): j for i, j in _dict.get('file_ocr_str').items()}
        else:
            result.file_ocr_str = {}
        if _dict.get('create_datetime', None):
            if isinstance(_dict['create_datetime'], str):
                result.create_datetime = datetime.datetime.fromisoformat(_dict['create_datetime'])
            else:
                result.create_datetime = _dict['create_datetime']
        return result

    @classmethod
    def create(cls, _dict):
        new_email = cls.from_dict(_dict)
        return new_email.save()


class User(object):
    def __init__(self, _id=None, cso_id=None, name_view=None, email=None, create_datetime=None,
                 telegram_id=None, token=None, password=None, notify_telegram=None, notify_email=None,
                 super_admin=False, kf_ext_id=None):
        self._id = _id
        self.cso_id = cso_id
        self.kf_ext_id = kf_ext_id
        self.name_view = name_view
        self.email = email
        self.create_datetime = create_datetime
        self.telegram_id = telegram_id
        self.token = token
        self.password = password
        self.notify_telegram = notify_telegram
        self.notify_email = notify_email
        self.super_admin = super_admin
        self.is_deleted = False

        self.__load = False

    @classmethod
    def find_one(cls, param=None):
        if param is None:
            param = {}
        email = db.user.find_one(param)
        if email is None:
            return None
        return cls.from_dict(email)

    def save(self):
        self.create_datetime = datetime.datetime.now()
        raw = self.to_dict()
        raw.pop('_id', None)
        _id = db.user.insert_one(raw).inserted_id
        return self.find_one({'_id': ObjectId(_id)})

    @classmethod
    def to_obj(cls, _dict, load=True):
        result = cls()

        result._id = ObjectId(_dict['_id'])
        result.cso_id = _dict['cso_id']
        result.kf_ext_id = _dict.get('kf_ext_id', None)
        result.name_view = _dict['name_view']
        result.email = _dict['email']
        result.create_datetime = _dict['create_datetime']
        result.telegram_id = _dict['telegram_id']
        result.token = _dict['token']
        result.password = _dict['password']
        result.notify_telegram = _dict['notify_telegram']
        result.notify_email = _dict['notify_email']
        result.super_admin = _dict['super_admin']
        result.is_deleted = _dict['is_deleted']
        result.__load = load
        return result

    def to_dict(self):
        return {
            '_id': self._id,
            'cso_id': self.cso_id,
            'kf_ext_id': self.kf_ext_id,
            'name_view': self.name_view,
            'email': self.email,
            'create_datetime': self.create_datetime,
            'telegram_id': self.telegram_id,
            'token': self.token,
            'password': self.password,
            'notify_telegram': self.notify_telegram,
            'notify_email': self.notify_email,
            'super_admin': self.super_admin,
            'is_deleted': self.is_deleted
        }

    def to_json(self):
        result = jsonpickle.decode(jsonpickle.encode(self, unpicklable=False))
        result['_id'] = str(self._id)
        return result

    def simplified_json(self):
        return {
            '_id': str(self._id),
            'cso_id': self.cso_id,
            'kf_ext_id': self.kf_ext_id,
            'name_view': self.name_view,
            'email': self.email,
            'is_deleted': self.is_deleted
        }

    def check_data(self):
        if not isinstance(self.cso_id, int):
            raise Exception('cso_id not valid')
        if not isinstance(self.name_view, str) or not self.name_view:
            raise Exception('name_view not valid')
        if not isinstance(self.kf_ext_id, (str, type(None))):
            raise Exception('kf_ext_id not valid')
        if not isinstance(self.email, str) or not validate_email(self.email):
            raise Exception('mail not valid')
        if not isinstance(self.create_datetime, datetime.datetime):
            raise Exception('create_datetime not valid')
        if not isinstance(self.telegram_id, (int, type(None))):
            raise Exception('telegram_id not valid')
        if not isinstance(self.token, str):
            raise Exception('token not valid')
        if not isinstance(self.password, str):
            raise Exception('password not valid')
        if not isinstance(self.notify_telegram, bool):
            raise Exception('notify_telegram not valid')
        if not isinstance(self.notify_email, bool):
            raise Exception('notify_email not valid')
        if not isinstance(self.super_admin, bool):
            raise Exception('super_admin not valid')
        if not isinstance(self.is_deleted, bool):
            raise Exception('is_deleted not valid')

    @classmethod
    def from_dict(cls, user: dict):
        result = cls(*user.values())
        return result
