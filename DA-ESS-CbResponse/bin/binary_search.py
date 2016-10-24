from cbhelpers import CbSearchCommand
from cbapi.response import Binary

import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import logging
log = logging.getLogger(__name__)


@Configuration(distributed=False)
class BinarySearchCommand(CbSearchCommand):
    field_names = ['digsig_publisher', 'digsig_result', 'digsig_sign_time', 'host_count', 'is_executable_image',
                   'last_seen', 'original_filename', 'os_type', 'product_name', 'product_version', 'md5']
    search_cls = Binary


if __name__ == '__main__':
    try:
        dispatch(BinarySearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
    except Exception as e:
        log.exception("during dispatch")