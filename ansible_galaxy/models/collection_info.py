from __future__ import print_function

import attr
import json
import logging
import os
import semver

logger = logging.getLogger(__name__)


# see https://github.com/ansible/galaxy/issues/957
@attr.s(frozen=True)
class CollectionInfo(object):
    namespace = attr.ib(default=None)
    name = attr.ib(default=None)
    version = attr.ib(default=None)
    format_version = attr.ib(default=0.0)
    author = attr.ib(default=None)
    license = attr.ib(default=None)

    @namespace.validator
    @name.validator
    @version.validator
    @license.validator
    def _check_required(self, attribute, value):
        if value is None:
            raise ValueError("Invalid collection metadata. '%s' is required" % attribute.name)

    @version.validator
    def _check_version_format(self, attribute, value):
        try:
            semver.parse_version_info(value)
        except ValueError:
            raise ValueError("Invalid collection metadata. Expecting 'version' to be in "
                             "semantic version format.")

    @format_version.validator
    def _check_format_version(self, attribute, value):
        if value not in (0.0,):
            raise ValueError("Invalid collection metadata. Expecting 'format_version' to "
                             "be one of (0.0,)")

    @license.validator
    def _check_license(self, attribute, value):
        cwd = os.path.dirname(os.path.abspath(__file__))
        license_path = os.path.join(cwd, '..', 'data', 'spdx_licenses.json')
        license_data = json.load(open(license_path, 'r'))
        match = False
        for license in license_data['licenses']:
            if license['licenseId'] == value:
                match = True
                if license['isDeprecatedLicenseId']:
                    print ("Warning: collection metadata 'license' value %s is "
                           "deprecated." % value)
        if not match:
            raise ValueError("Invalid collection metadata. Expecting 'license' to be a valid "
                             "SPDX license ID. For more info, visit https://spdx.org")
