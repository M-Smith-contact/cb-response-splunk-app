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
from cbhelpers import get_cbapi, setup_logger
from cbapi.response.models import Sensor
from time import sleep

import re


logger = setup_logger()

IPv4_re = re.compile("(\d+)\.(\d+)\.(\d+)\.(\d+)")


class IsolateSensorAction(ModularAction):
    def __init__(self, settings, logger, action_name=None):
        super(IsolateSensorAction, self).__init__(settings, logger, action_name)
        self.service = Service(token=self.session_key)

    def dowork(self, result):
        cb = get_cbapi(self.service)

        if self.configuration.get("inputtype", "cbevent") == "cbevent":
            return self.do_cbevent(cb, result)
        else:
            return self.do_genericevent(cb, result)

    def error(self, msg):
        self.addevent(msg, sourcetype="bit9:carbonblack:action")
        logger.error(msg)

    def do_isolate(self, cb, sensor_id):
        dryrun = self.configuration.get("dryrun", "1")
        try:
            dryrun = int(dryrun)
        except:
            dryrun = 1
        if dryrun == 1:
            logger.info("Dry run: would have isolated sensor id {0}.".format(sensor_id))
            self.addevent("Identified sensor id {0}.".format(sensor_id), sourcetype="bit9:carbonblack:action")
            return True

        try:
            logger.info("Attempting to isolate sensor id {0} from Cb Response server {1}".format(sensor_id, cb.url))
            sensor = cb.select(Sensor, int(sensor_id))
            sensor.network_isolation_enabled = True
            sensor.save()
            logger.info("Sensor id {0} isolation enabled".format(sensor_id))
        except Exception as e:
            self.error("Error isolating sensor id {0}: {1}".format(sensor_id, str(e)))
            logger.exception("Detailed error message")
            return False
        else:
            retries_left = 100
            while not sensor.is_isolating and retries_left:
                logger.info("Sensor id {0} waiting for isolation, {1} retries left...".format(sensor_id, retries_left))
                sleep(10)
                sensor.refresh()
                retries_left -= 1

            if sensor.is_isolating:
                logger.info("Sensor id {0} successfully isolated!".format(sensor_id))
                return True
            else:
                logger.info("Sensor id {0} not isolated; retries exceeded".format(sensor_id))
                return False

    def do_cbevent(self, cb, result):
        """Attempt to isolate a sensor based on the sensor_id located inside the message.
        This assumes the event originated from Cb Response."""

        # perform some sanity checks to make sure the event is from Cb Response
        sourcetype = result.get("sourcetype")
        if sourcetype == "stash":
            logger.debug("replacing 'stashed result' with the actual content of the alert/event")
            logger.debug(result.get("orig_raw", "{}"))
            result = json.loads(result.get("orig_raw", "{}"))
        elif result.get("sourcetype") != "bit9:carbonblack:json":
            self.error("The original message did not originate from Cb Response (sourcetype was {0}; expected {1}".format(
                result.get("sourcetype", "<unspecified>"), "bit9:carbonblack:json"))
            self.error(pprint.pformat(result))
            return False

        sensor_id = result.get("sensor_id", None) or result.get("docs{}.sensor_id", None)
        if not sensor_id:
            self.error("Could not retrieve a sensor_id from the message.")
            return False

        logger.info("Calling do_isolate from a Cb event with sensor id {0}.".format(sensor_id))
        return self.do_isolate(cb, sensor_id)

    def do_genericevent(self, cb, result):
        """Attempt to isolate a sensor based on an IP address or hostname located inside the message.
        The field containing the IP address or hostname to isolate is specified in the 'ipaddress' field in the
        Alert Action UI."""

        # attempt to retrieve the IP address from the event
        ip_field_name = self.configuration.get("ipaddress")
        if not ip_field_name:
            self.error("No field name specified in the configuration")
            return False

        ip_or_hostname = result.get(ip_field_name, None)
        if not ip_or_hostname:
            self.error("No value found in the result for field name {0}".format(ip_field_name))
            return False

        # at this time, Cb Response only supports IPv4 addresses. Make sure the IP address in this field
        # is a dotted quad. This simple RE just makes sure there are digits separated by dots...
        if IPv4_re.match(ip_or_hostname):
            field_type = "ip"
        else:
            field_type = "hostname"

        try:
            # note that we are only selecting the *first* sensor that matches. Multiple sensors may match, for a
            # variety of reasons.
            logger.info("Looking for a sensor with {0} of {1}...".format(field_type, ip_or_hostname))
            sensor_id = cb.select(Sensor).where("{0}:{1}".format(field_type, ip_or_hostname)).first().id
            logger.info("Found a sensor with a {0} of {1}: Calling do_isolate with sensor id {2}."
                        .format(field_type, ip_or_hostname, sensor_id))
            return self.do_isolate(cb, sensor_id)
        except Exception as e:
            self.error("Could not isolate sensor: {0}".format(str(e)))
            logger.exception("Detailed error message")

        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--execute":
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)

    try:
        logger.info("Calling IsolateSensorAction.__init__")
        modaction = IsolateSensorAction(sys.stdin.read(), logger, 'isolatesensor')
        logger.info("Returned IsolateSensorAction.__init__")
    except Exception as e:
        logger.critical(str(e))
        sys.exit(3)

    try:
        session_key = modaction.session_key
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('%s', json.dumps(modaction.settings, sort_keys=True,
                indent=4, separators=(',', ': ')))

        ## process results
        with gzip.open(modaction.results_file, 'rb') as fh:
            for num, result in enumerate(csv.DictReader(fh)):
                ## set rid to row # (0->n) if unset
                result.setdefault('rid', num)
                modaction.update(result)
                modaction.invoke()
                modaction.dowork(result)
                modaction.writeevents(index='main', source='bit9:carbonblack')

    except Exception as e:
        ## adding additional logging since adhoc search invocations do not write to stderr
        try:
            logger.critical(modaction.message(e, 'failure'))
        except:
            logger.critical(e)
        print >> sys.stderr, "ERROR Unexpected error: %s" % e
        sys.exit(3)

