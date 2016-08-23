from cbapi import CbApi
import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import time

import logging
log = logging.getLogger(__name__)

@Configuration()
class BinarySearchCommand(GeneratingCommand):
    """Generates a binary search result from Carbon Black from a given MD5 or search query
        | binarysearch ${md5}
    """

    query = Option(name="query", require=True)
    field_names = ['digsig_publisher', 'digsig_result', 'digsig_sign_time', 'host_count', 'is_executable_image',
                   'last_seen', 'original_filename', 'os_type', 'product_name', 'product_version', 'md5']

    def __init__(self):
        super(BinarySearchCommand, self).__init__()
        self.setup_complete = False
        self.cb = None

    def prepare(self):
        splunk = self.service
        try:
            api_credentials = splunk.storage_passwords["DA-ESS-CbResponse:apikey"]
            token = api_credentials.clear_password.split("``splunk_cred_sep``")[1]

            self.cb_server = splunk.confs["DA-ESS-CbResponse_customized"]["cburl"].content['content']
        except KeyError:
            log.exception("API key not set")
        except Exception:
            log.exception("Error reading API key from credential storage")
        else:
            self.cb = CbApi(self.cb_server, token=token, ssl_verify=False)
            self.setup_complete = True

    def generate(self):
        for bindata in self.cb.binary_search_iter(self.query):
            self.logger.info("yielding binary %s" % bindata["md5"])
            rawdata = dict((field_name, bindata.get(field_name, "")) for field_name in self.field_names)
        try:
            rawdata
            synthevent = {'sourcetype': 'bit9:carbonblack:json', '_time': time.time(), 'source': self.cb_server,
                          '_raw': rawdata}
            yield synthevent
        except Exception:
            synthevent = {'sourcetype': 'bit9:carbonblack:json', '_time': time.time(), 'source': self.cb_server,
                          '_raw': '{"Error":"MD5 not found"}'}
            yield synthevent


if __name__ == '__main__':
    try:
        dispatch(BinarySearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
    except Exception as e:
        log.exception("during dispatch")