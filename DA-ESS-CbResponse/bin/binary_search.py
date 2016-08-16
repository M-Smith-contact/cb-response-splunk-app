#!/usr/bin/python

from cbapi import CbApi
from ConfigParser import RawConfigParser
import os
import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import time


@Configuration()
class BinarySearchCommand(GeneratingCommand):
    """Generates a binary search result from Carbon Black from a given MD5 or search query
        | binarysearch ${md5}
    """

    query = Option(name="query", require=True)
    field_names = ['digsig_publisher', 'digsig_result', 'digsig_sign_time', 'host_count', 'is_executable_image',
                   'last_seen', 'original_filename', 'os_type', 'product_name', 'product_version', 'md5']

    def prepare(self):
        splunk = self.service
        token = splunk.storage_passwords.get("cbapikey")
        self.cb_server = splunk.storage_passwords.get("cburl")

        self.cb = CbApi(self.cb_server, token=token, ssl_verify=False)

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
    dispatch(BinarySearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)
