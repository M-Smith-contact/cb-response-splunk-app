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
        self.addevent(msg)
        logger.error(msg)

    ## Create splunk events for action updates
    def addevent(self, events):
        if modaction.makeevents(  events, index='main', source='bit9:carbonblack', sourcetype='bit9:carbonblack:action'):
            logger.info("Created splunk event for IsolateSensorAction.")
        else:
            logger.critical("Failed creating splunk event for IsolateSensorAction.")
        return

    def do_isolate(self, cb, sensor_id):
        dryrun = self.configuration.get("dryrun", "1")
        try:
            dryrun = int(dryrun)
        except:
            dryrun = 1
        if dryrun == 1:
            logger.info("Dry run: would have isolated sensor id {0}.".format(sensor_id))
            self.addevent("Identified sensor id {0}.".format(sensor_id))
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

        return self.do_isolate(cb, sensor_id)

    def do_genericevent(self, cb, result):
        """Attempt to isolate a sensor based on an IP address located inside the message.
        The field containing the IP address to isolate is specified in the 'ipaddress' field in the
        Alert Action UI."""

        # attempt to retrieve the IP address from the event
        ip_field_name = self.configuration.get("ipaddress")
        if not ip_field_name:
            self.error("No field name specified in the configuration")
            return False

        sensor_ip_address = result.get(ip_field_name, None)
        if not sensor_ip_address:
            self.error("No value found in the result for field name {0}".format(sensor_ip_address))
            return False

        # at this time, Cb Response only supports IPv4 addresses. Make sure the IP address in this field
        # is a dotted quad. This simple RE just makes sure there are digits separated by dots...
        if not IPv4_re.match(sensor_ip_address):
            self.error("Field {0} value {1} does not look like a valid IPv4 address".format(ip_field_name, sensor_ip_address))
            return False

        try:
            # note that we are only selecting the *first* sensor that matches. Multiple sensors may match, for a
            # variety of reasons.
            sensor_id = cb.select(Sensor).where("ip:{}".format(sensor_ip_address)).first().id
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

    except Exception as e:
        ## adding additional logging since adhoc search invocations do not write to stderr
        try:
            logger.critical(modaction.message(e, 'failure'))
        except:
            logger.critical(e)
        print >> sys.stderr, "ERROR Unexpected error: %s" % e
        sys.exit(3)

