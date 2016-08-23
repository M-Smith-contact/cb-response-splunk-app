from cbhelpers import get_cbapi
from cbapi.errors import ApiError
from cbapi.response import Binary

import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import time

import json

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

    def error_event(self, comment):
        error_text = {"Error": comment}

        return {'sourcetype': 'bit9:carbonblack:json', '_time': time.time(), 'source': self.cb.credentials.url,
                '_raw': json.dumps(error_text)}

    def prepare(self):
        try:
            self.cb = get_cbapi(self.service)
        except KeyError:
            log.exception("API key not set")
        except ApiError:
            log.exception("Could not contact Cb Response server")
        except Exception:
            log.exception("Error reading API key from credential storage")
        else:
            self.setup_complete = True

    def generate(self):
        try:
            for bindata in self.cb.select(Binary).where(self.query):
                self.logger.info("yielding binary %s" % bindata.md5)
                rawdata = dict((field_name, getattr(bindata, field_name, "")) for field_name in self.field_names)
                yield {'sourcetype': 'bit9:carbonblack:json', '_time': time.time(), 'source': self.cb.credentials.url,
                       '_raw': rawdata}

        except Exception as e:
            yield self.error_event("error searching for {0} in Cb Response: {1}".format(self.query, str(e)))


if __name__ == '__main__':
    try:
        dispatch(BinarySearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
    except Exception as e:
        log.exception("during dispatch")