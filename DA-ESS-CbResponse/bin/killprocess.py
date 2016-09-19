import sys
import logging
import json
import gzip
import csv
import pprint

try:
    from splunk.clilib.bundle_paths import make_splunkhome_path
except ImportError:
    from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path

sys.path.append(make_splunkhome_path(["etc", "apps", "Splunk_SA_CIM", "lib"]))
sys.path.append(make_splunkhome_path(["etc", "apps", "SA-Utils", "lib"]))

from cim_actions import ModularAction
from splunklib.client import Service
from cbhelpers import get_cbapi
from cbapi.response.models import Sensor
from time import sleep

import re
import struct

GUID_RE = re.compile("[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{8}")

def parse_42_guid(guid):
    guid_parts = guid.split('-')
    return struct.unpack('>IIQ', ''.join(guid_parts)[:32].decode('hex'))


class KillProcessAction(ModularAction):
    def __init__(self, settings, logger, action_name=None):
        super(KillProcessAction, self).__init__(settings, logger, action_name)
        self.service = Service(token=self.session_key)

    def dowork(self, result):
        cb = get_cbapi(self.service)

    def error(self, msg):
        self.addevent(msg, sourcetype="bit9:carbonblack:action")
        logger.error(msg)

    def do_kill(self, cb, guid):

        (sensor_id, proc_pid, proc_createtime) = parse_42_guid(guid)

        dryrun = self.configuration.get("dryrun", "1")
        try:
            dryrun = int(dryrun)
        except:
            dryrun = 1
        if dryrun == 1:
            logger.info("Dry run: would have killed process {0}.".format(guid))
            self.addevent("Dry run killing process {0}.".format(guid), sourcetype="bit9:carbonblack:action")
            return True

        #
        # Select the correct sensor
        #
        sensor = self.cb.select(Sensor, sensor_id)

        with sensor.lr_session() as self.lr_session:
            processes = self.lr_session.list_processes()

            match = False
            for p in processes:
                if p['proc_guid'] == guid:
                    #
                    # Process is running
                    #
                    match = True
                    break

            if match:
                #
                # Perform a kill process specified by the PID
                #
                logger.info("Guid: {0} was found on sensor".format(guid))
                self.addevent("Guid: {0} was found on sensor".format(guid), sourcetype="bit9.carbonblack:action")
                self.lr_session.kill_process(proc_pid)
            else:
                #
                # process guid was not running on sensor
                #
                logger.info("Guid: {0} was NOT found on sensor".format(guid))
                self.addevent("Guid: {0} was NOT found on sensor".format(guid), sourcetype="bit9.carbonblack:action")


        return True

    def do_genericevent(self, cb, result):
        """Attempt to ban an MD5 hash based on the field from the 'fieldname' in the Alert Action UI."""

        # attempt to retrieve the MD5 hash from the event
        field_name = self.configuration.get("fieldname")
        if not field_name:
            self.error("No field name specified in the configuration")
            return False

        guid = result.get(field_name, None)
        if not guid:
            self.error("No value found in the result for field name {0}".format(field_name))
            return False

        # at this time, Cb Response only supports IPv4 addresses. Make sure the IP address in this field
        # is a dotted quad. This simple RE just makes sure there are digits separated by dots...
        if not GUID_RE.match(guid):
            self.error("Field value {0} does not look like a process guid".format(guid))

        try:
            return self.do_kill(cb, guid)
        except Exception as e:
            #modaction.message('RESULT: ' + str(result), level=logging.ERROR)
            self.error("Could not kill guid: {0}".format(str(e)))
            logger.exception("Detailed error message")

        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--execute":
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)

    try:
        logger = ModularAction.setup_logger('killprocess_modalert')
        logger.info("Calling KillProcessAction.__init__")
        modaction = KillProcessAction(sys.stdin.read(), logger, 'processkill')
        logger.info("Returned KillProcessAction.__init__")
    except Exception as e:
        logger.critical(str(e))
        sys.exit(3)

    try:
        session_key = modaction.session_key

        modaction.addinfo()
        ## process results
        with gzip.open(modaction.results_file, 'rb') as fh:
            for num, result in enumerate(csv.DictReader(fh)):
                ## set rid to row # (0->n) if unset
                result.setdefault('rid', str(num))

                modaction.update(result)
                modaction.invoke()

                act_result = modaction.dowork(result)

                modaction.addevent(str(act_result), sourcetype="bit9:carbonblack:action")

                if act_result:
                    modaction.writeevents(index='main', source='carbonblackapi')
                    modaction.message('Successfully created splunk event', status='success', rids=modaction.rids)
                else:
                    modaction.writeevents(index='main', source='carbonblackapi')
                    modaction.message('Failed to create splunk event', status='failure', rids=modaction.rids,
                                      level=logging.ERROR)

    except Exception as e:
        ## adding additional logging since adhoc search invocations do not write to stderr
        try:
            logger.critical(modaction.message(e, 'failure'))
        except:
            logger.critical(e)
        print >> sys.stderr, "ERROR Unexpected error: %s" % e
        sys.exit(3)

