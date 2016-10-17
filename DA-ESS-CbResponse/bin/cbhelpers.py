from cbapi import CbApi
from cbapi.response import CbEnterpriseResponseAPI
from cbapi.errors import ApiError

from splunklib.searchcommands import GeneratingCommand, Option, Configuration
import json
import time
import logging

try:
    from splunk.clilib.bundle_paths import make_splunkhome_path
except ImportError:
    from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path


def get_creds(splunk_service):
    api_credentials = splunk_service.storage_passwords["DA-ESS-CbResponse:apikey"]
    token = api_credentials.clear_password.split("``splunk_cred_sep``")[1]

    cb_server = splunk_service.confs["DA-ESS-CbResponse_customized"]["cburl"].content['content']

    return cb_server, token


def get_legacy_cbapi(splunk_service):
    cb_server, token = get_creds(splunk_service)
    return CbApi(cb_server, ssl_verify=False, token=token)


def get_cbapi(splunk_service):
    if not splunk_service:
        return CbEnterpriseResponseAPI()
    else:
        cb_server, token = get_creds(splunk_service)
        return CbEnterpriseResponseAPI(token=token, url=cb_server, ssl_verify=False)


@Configuration(distributed=False)
class CbSearchCommand(GeneratingCommand):
    query = Option(name="query", require=False)
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

    def process_data(self, data_dict):
        """
        If you want to modify the data dictionary before returning to splunk, override this. // BSJ 2016-08-30
        """
        return data_dict

    def squash_data(self, data_dict):
        for x in data_dict.keys():
            v = data_dict[x]
            data_dict[x] = str(v)
        return data_dict

    def generate_result(self, data):
        rawdata = dict( (field_name, getattr(data, field_name, "")) for field_name in self.field_names)
        squashed_data = self.squash_data( self.process_data(rawdata) )
        return {'sourcetype': 'bit9:carbonblack:json', '_time': time.time(),
                'source': self.cb.credentials.url, '_raw': squashed_data}

    def generate(self):
        try:
            query = self.cb.select(self.search_cls)
            if self.query:
                query = query.where(self.query)

            for result in query[:self.max_result_rows]:
                self.logger.info("yielding {0} {1}".format(self.search_cls.__name__, result._model_unique_id))
                yield self.generate_result(result)

        except Exception as e:
            yield self.error_event("error searching for {0} in Cb Response: {1}".format(self.query, str(e)))


## Setup the logger
def setup_logger():
   """
   Setup a logger for the REST handler.
   """

   logger = logging.getLogger('da-ess-cbresponse')
   logger.setLevel(logging.DEBUG)

   file_handler = logging.handlers.RotatingFileHandler(
     make_splunkhome_path(['var', 'log', 'splunk', 'da-ess-cbresponse.log']),
     maxBytes=25000000, backupCount=5)
   formatter = logging.Formatter('%(asctime)s %(lineno)d %(levelname)s %(message)s')
   file_handler.setFormatter(formatter)

   logger.addHandler(file_handler)

   return logger
