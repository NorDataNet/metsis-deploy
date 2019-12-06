from urllib.parse import urlparse

import requests


class SolrClient:
    def __init__(self,
                 base_url,
                 core_name):
        self.base_url = base_url
        self.core_name = core_name

    def update(self, solr_document):
        update_end_point = self.base_url + self.core_name + "/update?commit=true&wt=json"

        # if self.__is_url(upadte_end_point):

        resp = requests.post(update_end_point, data=solr_document,
                             headers={'Content-Type': 'application/json', 'accept': 'application/json'})

        return resp.json()["responseHeader"]["status"]

    # TODO: check if the method below is not used elsewhere
    def __is_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
