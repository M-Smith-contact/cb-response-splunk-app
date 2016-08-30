from cbapi import CbApi
from cbapi.response import CbEnterpriseResponseAPI
from cbapi.errors import ApiError

from splunklib.searchcommands import GeneratingCommand, Option
import json
import time


def get_creds(splunk_service):
    api_credentials = splunk_service.storage_passwords["DA-ESS-CbResponse:apikey"]
    token = api_credentials.clear_password.split("``splunk_cred_sep``")[1]

    cb_server = splunk_service.confs["DA-ESS-CbResponse_customized"]["cburl"].content['content']

    return cb_server, token


def get_legacy_cbapi(splunk_service):
    cb_server, token = get_creds(splunk_service)
    return CbApi(cb_server, ssl_verify=False, token=token)


def get_cbapi(splunk_service):
    cb_server, token = get_creds(splunk_service)
    return CbEnterpriseResponseAPI(token=token, url=cb_server, ssl_verify=False)


class CbSearchCommand(GeneratingCommand):
    query = Option(name="query", require=True)
    max_result_rows = Option(name="maxresultrows", default=1000)

    field_names = []
    search_cls = None

    def __init__(self):
        super(CbSearchCommand, self).__init__()
        self.setup_complete = False
        self.cb = None

    def error_event(self, comment):
        error_text = {"Error": comment}

        return {'sourcetype': 'bit9:carbonblack:json', '_time': time.time(), 'source': self.cb.credentials.url,
                '_raw': json.dumps(error_text)}

    def prepare(self):
        try:
            self.cb = get_cbapi(self.service)
        except KeyError:
            self.logger.exception("API key not set")
        except ApiError:
            self.logger.exception("Could not contact Cb Response server")
        except Exception:
            self.logger.exception("Error reading API key from credential storage")
        else:
            self.setup_complete = True

    def generate_result(self, data):
        rawdata = dict((field_name, str(getattr(data, field_name, ""))) for field_name in self.field_names)
        return {'sourcetype': 'bit9:carbonblack:json', '_time': time.time(),
                'source': self.cb.credentials.url, '_raw': rawdata}

    def generate(self):
        try:
            for result in self.cb.select(self.search_cls).where(self.query)[:self.max_result_rows]:
                self.logger.info("yielding {0} {1}".format(self.search_cls.__name__, result._model_unique_id))
                yield self.generate_result(result)

        except Exception as e:
            yield self.error_event("error searching for {0} in Cb Response: {1}".format(self.query, str(e)))

