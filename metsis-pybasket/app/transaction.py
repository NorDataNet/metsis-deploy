import json
import uuid
from jinja2 import Template

from app.status import Status


class Transaction:
    def __init__(self,
                 id,
                 user_id,
                 email,
                 status,
                 site,
                 fimex_list):
        self.id = id
        self.user_id = user_id
        self.email = email
        self.status = status
        self.site = site
        self.fimex_list = fimex_list

    def set_status(self, status: Status):
        self.status = status

    def toSolrDocument(self):
        uri_list = []
        for fimex in self.fimex_list:
            uri_list.append(fimex.input_file)
        uris = ','.join(uri_list)

        doc = '''       
        {"add": {"doc": {"id": "{{transcation.id}}", "username": "{{transcation.user_id}}", "email": "{{transcation.email}}", "status": "{{transcation.status.value}}", "uris": "{{ uris}}", "site": "{{transcation.site}}", "request_time": "2019-01-28T09:18:41.611Z"}, "overwrite": true, "commitWithin": 1000}}
        '''
        tm = Template(doc)
        return tm.render(transcation=self, uris=uris)

    def toJson(self):
        uri_list = []
        for fimex in self.fimex_list:
            uri_list.append(fimex.input_file)
        #uris = ','.join(uri_list)

        doc = {"id": self.id, "username": self.user_id, "email": self.email, "status": self.status.value, "uris": uri_list,
               "site": self.site, "request_time": "2019-01-28T09:18:41.611Z"}

        return json.dumps(doc)



