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
from cbapi.response.models import BannedHash

import re


MD5SUM_RE = re.compile("[A-Fa-f0-9]{32}")


class BanHashAction(ModularAction):
    def __init__(self, settings, logger, action_name=None):
        super(BanHashAction, self).__init__(settings, logger, action_name)
        self.service = Service(token=self.session_key)

    def dowork(self, result):
        cb = get_cbapi(self.service)
        return self.do_genericevent(cb, result)

    def error(self, msg):
        self.addevent(msg, sourcetype="bit9:carbonblack:action")
        logger.error(msg)

    def do_ban(self, cb, md5sum):
        dryrun = self.configuration.get("dryrun", "1")
        try:
            dryrun = int(dryrun)
        except:
            dryrun = 1
        if dryrun == 1:
            logger.info("Dry run: would have banned MD5 hash {0}.".format(md5sum))
            self.addevent("Dry run banning hash {0}.".format(md5sum), sourcetype="bit9:carbonblack:action")
            return True

        # check to see if this bannedHash already exists
        ban = cb.select(BannedHash).where("md5sum:{0}".format(md5sum)).first()
        if not ban:
            logger.info("Creating a new BannedHash for MD5 {0}".format(md5sum))
            new_ban = cb.create(BannedHash)
            new_ban.md5hash = md5sum
            new_ban.text = "Banned from Splunk"
            new_ban.enabled = True
            new_ban.save()
            logger.info("MD5 {0} now banned".format(md5sum))
        else:
            logger.info("BannedHash already exists for MD5 {0}".format(md5sum))
            ban.enabled = True
            ban.save()
            logger.info("MD5 {0} now banned".format(md5sum))

    def do_genericevent(self, cb, result):
        """Attempt to ban an MD5 hash based on the field from the 'fieldname' in the Alert Action UI."""

        # attempt to retrieve the MD5 hash from the event
        field_name = self.configuration.get("fieldname")
        if not field_name:
            self.error("No field name specified in the configuration")
            return False

        md5sum = result.get(field_name, None)
        if not md5sum:
            self.error("No value found in the result for field name {0}".format(field_name))
            return False

        # at this time, Cb Response only supports IPv4 addresses. Make sure the IP address in this field
        # is a dotted quad. This simple RE just makes sure there are digits separated by dots...
        if not MD5SUM_RE.match(md5sum):
            self.error("Field value {0} does not look like an md5sum".format(md5sum))

        try:
            return self.do_ban(cb, md5sum)
        except Exception as e:
            self.error("Could not ban hash: {0}".format(str(e)))
            logger.exception("Detailed error message")

        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--execute":
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)

    try:
        logger = ModularAction.setup_logger('banhash_modalert')
        logger.info("Calling BanHashAction.__init__")
        modaction = BanHashAction(sys.stdin.read(), logger, 'banhash')
        logger.info("Returned BanHashAction.__init__")
    except Exception as e:
        logger.critical(str(e))
        sys.exit(3)

    try:
        session_key = modaction.session_key
        ## process results
        with gzip.open(modaction.results_file, 'rb') as fh:
            for num, result in enumerate(csv.DictReader(fh)):
                ## set rid to row # (0->n) if unset
                result.setdefault('rid', num)
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

