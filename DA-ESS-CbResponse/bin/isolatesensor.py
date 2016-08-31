import sys
import logging
import json
import gzip
import csv

try:
    from splunk.clilib.bundle_paths import make_splunkhome_path
except ImportError:
    from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path

sys.path.append(make_splunkhome_path(["etc", "apps", "Splunk_SA_CIM", "lib"]))
sys.path.append(make_splunkhome_path(["etc", "apps", "SA-Utils", "lib"]))

from cim_actions import ModularAction
from splunklib.client import Service
from cbhelpers import get_cbapi


## Setup the logger
def setup_logger():
   """
   Setup a logger for the REST handler.
   """

   logger = logging.getLogger('checkphish_modaction')
   logger.setLevel(logging.INFO)

   file_handler = logging.handlers.RotatingFileHandler(
     make_splunkhome_path(['var', 'log', 'splunk', 'checkphish_modalert.log']),
     maxBytes=25000000, backupCount=5)
   formatter = logging.Formatter('%(asctime)s %(lineno)d %(levelname)s %(message)s')
   file_handler.setFormatter(formatter)

   logger.addHandler(file_handler)

   return logger

logger = setup_logger()


class IsolateSensorAction(ModularAction):
    def __init__(self, settings, logger, action_name=None):
        super(IsolateSensorAction, self).__init__(settings, logger, action_name)
        self.service = Service(cookie=self.session_key)

    def dowork(self, result):
        ipaddress = result["ipaddress"]
        cb = get_cbapi(self.service)

        self.addevent("attempted to isolate {0}".format(ipaddress))
        self.logger.info("logging about {0}".format(ipaddress))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--execute":
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)

    try:
        modaction = IsolateSensorAction(sys.stdin.read(), logger, 'isolatesensor')
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

