from cbhelpers import CbSearchCommand
from cbapi.response import Process

import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import logging
log = logging.getLogger(__name__)


@Configuration()
class ProcessSearchCommand(CbSearchCommand):
    field_names = ['cmdline',
                   'comms_ip',
                   'hostname',
                   'id',
                   'interface_ip',
                   'last_update',
                   'os_type',
                   'parent_md5',
                   'parent_name',
                   'parent_pid',
                   'parent_unique_id',
                   'path',
                   'process_md5',
                   'process_name',
                   'process_pid',
                   'regmod_count',
                   'segment_id',
                   'sensor_id',
                   'start',
                   'unique_id',
                   'username',
                   'childproc_count',
                   'crossproc_count',
                   'modload_count',
                   'netconn_count',
                   'filemod_count',
                   'group',
                   'host_type']
    search_cls = Process

    def generate_result(self, data):
        result = super(ProcessSearchCommand, self).generate_result(data)
        result['link_process'] = data.webui_link
        return result


if __name__ == '__main__':
    try:
        dispatch(ProcessSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
    except Exception as e:
        log.exception("during dispatch")

