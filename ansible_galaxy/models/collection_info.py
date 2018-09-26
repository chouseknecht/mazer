from __future__ import print_function

import attr
import json
import logging
import os
import re
import semver

log = logging.getLogger(__name__)

TAG_REGEXP = re.compile('^[a-z0-9]+$')

# see https://github.com/ansible/galaxy/issues/957


@attr.s(frozen=True)
class CollectionInfo(object):
    name = attr.ib(default=None)
    version = attr.ib(default=None)
    authors = attr.ib(default=[])
    license = attr.ib(default=None)
    description = attr.ib(default=None)
    keywords = attr.ib(default=[])
    readme = attr.ib(default='README.md')
    dependencies = attr.ib(default=[])

    @property
    def namespace(self):
        return self.name.split('.', 1)[0]

    @name.validator
    @version.validator
    @license.validator
    @description.validator
    def _check_required(self, attribute, value):
        if value is None:
            raise ValueError("Invalid collection metadata. '%s' is required" % attribute.name)

    @version.validator
    def _check_version_format(self, attribute, value):
        try:
            semver.parse_version_info(value)
        except ValueError:
            raise ValueError("Invalid collection metadata. Expecting 'version' to be in "
                             "semantic version format, instead found '%s'." % value)

    @license.validator
    def _check_license(self, attribute, value):
        cwd = os.path.dirname(os.path.abspath(__file__))
        license_path = os.path.join(cwd, '..', 'data', 'spdx_licenses.json')
        license_data = json.load(open(license_path, 'r'))
        for license_dict in license_data['licenses']:
            if license_dict['licenseId'] == value:
                if license_dict['isDeprecatedLicenseId']:
                    print("Warning: collection metadata 'license' value %s is "
                          "deprecated." % value)
                return True
        raise ValueError("Invalid collection metadata. Expecting 'license' to be a valid "
                         "SPDX license ID. For more info, visit https://spdx.org")

    @keywords.validator
    @dependencies.validator
    def _check_list_type(self, attribute, value):
        if not isinstance(value, list):
            raise ValueError("Invalid collection metadata. Expecting '%s' to be a list" % attribute.name)

    @keywords.validator
    def _check_keywords(self, attribute, value):
        for k in value:
            if not re.match(TAG_REGEXP, k):
                raise ValueError("Invalid collection metadata. Expecting keywords to contain "
                                 "alphanumeric characters only. Found '%s'" % k)

    @name.validator
    def _check_name(self, attribute, value):
        if len(value.split('.', 1)) != 2:
            raise ValueError("Invalid collection metadata. Expecting 'name' to be in Galaxy name "
                             "format: <namespace>.<collection_name>")
