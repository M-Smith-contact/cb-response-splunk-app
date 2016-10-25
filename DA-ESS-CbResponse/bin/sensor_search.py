from cbhelpers import CbSearchCommand
from cbapi.response import Sensor

import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import logging
log = logging.getLogger(__name__)


@Configuration(distributed=False)
class SensorSearchCommand(CbSearchCommand):
    field_names = [
                    'build_version_string',
                    'clock_delta',
                    'computer_dns_name',
                    'computer_name',
                    'computer_sid',
                    'dns_name',
#                    'event_log_flush_time', ### SYNC
                    'group_id',
                    'hostname',
                    'id',
                    'is_isolating',
                    'last_checkin_time',
                    'last_update',
                    'license_expiration',
                    'network_interfaces',
                    'network_isolation_enabled',
                    'next_checkin_time',
                    'node_id',
                    'notes',
                    'num_eventlog_bytes',
                    'num_storefiles_bytes',
                    'os',
                    'os_environment_display_string',
                    'os_environment_id',
                    'os_type',
                    'parity_host_id',
                    'physical_memory_size',
                    'power_state',
                    'registration_time',
                    'restart_queued',
                    'sensor_health_message',
                    'sensor_health_status',
                    'sensor_uptime',
                    'shard_id',
                    'sid',
                    'status',
                    'supports_2nd_gen_modloads',
                    'supports_cblr',
                    'supports_isolation',
                    'systemvolume_free_size',
                    'systemvolume_total_size',
                    'uninstall',
                    'uninstalled',
                    'uptime',
                    'webui_link']

    search_cls = Sensor

    def generate_result(self, data):
        result = super(SensorSearchCommand, self).generate_result(data)
        return result

    def process_data(self, data_dict):
        """
        If you want to modify the data dictionary before returning to splunk, override this. // BSJ 2016-08-30
        """
        nics = data_dict.get('network_interfaces', None)
        if nics:
            i = 0
            for nic in nics:
                ## TODO -- WOULD BE MUCH NICER TO RETURN MULTI-VALUE FIELD HERE // BSJ 2016-08-30
                data_dict['network_interface_%.2d_macaddr' % i] = nic.macaddr
                data_dict['network_interface_%.2d_ipaddr' % i] = nic.ipaddr
                i += 1
            del data_dict['network_interfaces']
        return data_dict


if __name__ == '__main__':
    try:
        dispatch(SensorSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
    except Exception as e:
        log.exception("during dispatch")

