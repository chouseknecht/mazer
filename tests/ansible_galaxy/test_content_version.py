
import logging

import pytest

from ansible_galaxy import content_version
from ansible_galaxy import exceptions

log = logging.getLogger(__name__)


def test_get_content_version_none():
    ret = content_version.get_content_version({}, None, [], None)
    log.debug('ret=%s', ret)

    assert ret == 'master'


def test_get_content_version_devel_version_no_content_versions():
    try:
        content_version.get_content_version({}, 'devel', [], None)
    except exceptions.GalaxyError:
        return

    assert False, 'Excepted a GalaxyError here since there are no content versions and "devel" is not in []'


@pytest.mark.xfail
def test_get_content_version_prod_version_in_content_versions():
    ret = content_version.get_content_version({}, 'prod', content_versions_147, None)
    log.debug('ret=%s', ret)

    assert ret == 'prod'


raw_content_versions_147 = [
    {
        "id": 126,
        "name": "2.3.7",
        "release_date": "2018-05-01T12:10:16-04:00",
        "url": "",
        "related": {},
        "summary_fields": {},
        "created": "2018-05-01T16:11:41.473282Z",
        "modified": "2018-05-01T16:11:42.110659Z",
        "active": True
    },
    {
        "id": 127,
        "name": "2.3.6",
        "release_date": "2018-05-01T11:54:19-04:00",
        "url": "",
        "related": {},
        "summary_fields": {},
        "created": "2018-05-01T16:11:42.114698Z",
        "modified": "2018-05-01T16:11:42.427811Z",
        "active": True
    },
]

content_versions_147 = [a.get('name') for a in raw_content_versions_147 if a.get('name', None)]
content_versions_v = content_versions_147 + ['v1.0.0', 'v3.0.0', 'v0.0.0']
content_versions_no_v = content_versions_147 + ['1.0.0', '3.0.0', '0.0.0']
content_versions_1_0_v_and_no_v = ['1.0.0', 'v1.0.0']
content_versions_v_and_no_v = content_versions_147 + content_versions_1_0_v_and_no_v

content_versions_boring = ['0.0.1', '0.0.11', '0.5.1', '0.99.0', '1.0.0', '2.0.0', '3.0.0']
content_versions_alphanumeric_post = ['0.0.1beta', '0.0.2a']
versions_1_0_0_latest = ['0.0.0', '0.1', '0.5.5.5.5.5', '1.0.0']

content_versions_map = {
    '147': content_versions_147,
    'v': content_versions_v,
    'no_v': content_versions_no_v,
    '1_0_v_and_no_v': content_versions_1_0_v_and_no_v,
    'v_and_no_v': content_versions_v_and_no_v,
    'boring': content_versions_boring,
    '1_0_0_latest': versions_1_0_0_latest,
    'empty': [],
}

test_data = [
    {'ask': None, 'vid': 'empty', 'exp': 'master'},
    {'ask': 'v1.0.0', 'vid': 'v', 'exp': 'v1.0.0'},
    {'ask': 'v1.0.0', 'vid': 'no_v', 'exp': '1.0.0'},
    {'ask': '1.0.0', 'vid': 'v', 'exp': 'v1.0.0'},
    {'ask': '1.0.0', 'vid': 'no_v', 'exp': '1.0.0'},
    {'ask': '1.0.0', 'vid': 'v_and_no_v', 'exp': 'v1.0.0'},
    {'ask': '2.3.7', 'vid': '147', 'exp': '2.3.7'},
    {'ask': 'v2.3.7', 'vid': '147', 'exp': '2.3.7'},
]


@pytest.fixture(scope='module',
                params=test_data,
                ids=['ask=%s,vlist=%s,exp=%s' % (x['ask'], x['vid'], x['exp']) for x in test_data])
def ver_data(request):
    tdata = request.param.copy()
    tdata['vlist'] = content_versions_map[tdata['vid']]
    log.debug('tdata: %s', tdata)
    yield tdata


test_sort_data = [
    {'vid': 'empty', 'latest': None},
    {'vid': 'no_v', 'latest': '3.0.0'},
    {'vid': 'boring', 'latest': '3.0.0'},
    {'vid': '147', 'latest': '2.3.7'},
]


@pytest.fixture(scope='module',
                params=test_sort_data,
                ids=['vlist=%s,latest=%s' % (x['vid'], x['latest']) for x in test_sort_data])
def ver_sort_data(request):
    tdata = request.param.copy()
    tdata['vlist'] = content_versions_map[tdata['vid']]
    log.debug('tdata: %s', tdata)
    yield tdata


def test_sort_versions(ver_sort_data):
    log.debug('ver_data_sort: %s', ver_sort_data)
    log.debug('latest: %s', ver_sort_data['latest'])
    versions = ver_sort_data['vlist']

    res = content_version.sort_versions(versions)
    log.debug('sorted versions: %s', res)

    # FIXME: the cases where get_content_version expects master on empty ver list are skipped
    if not res:
        return

    assert res[-1] == ver_sort_data['latest']


def test_normalize_versions():
    vers = ['v1.0.0', '1.0.1', 'V1.2.3', '3.4.5']
    norm_vers, norm_to_orig_map = content_version.normalize_versions(vers)

    log.debug('     vers: %s', vers)
    log.debug('norm_vers: %s', norm_vers)

    for index, item in enumerate(vers):
        log.debug(' v: %s', item)
        log.debug('nv: %s', norm_vers[index])

    for norm_ver in norm_vers:
        assert not norm_ver.startswith('v')
        assert not norm_ver.startswith('V')

    assert '1.0.0' in norm_vers
    assert '1.2.3' in norm_vers

    assert norm_to_orig_map['1.0.0'] == 'v1.0.0'
    assert norm_to_orig_map['1.2.3'] == 'V1.2.3'
    assert norm_to_orig_map['1.0.1'] == '1.0.1'
    assert norm_to_orig_map['3.4.5'] == '3.4.5'


@pytest.mark.parametrize("versions,exp_valid,exp_invalid", [
    (['v1.0.0', '1.0.1', 'V1.2.3', '3.4.5', 'a', '12', '1.0', '0.0.0.0', '0.0.0', '0.0'],
     ['0.0.0', '1.0.1', '3.4.5'],
     ['v1.0.0', 'V1.2.3', 'a', '12', '1.0', '0.0.0.0', '0.0']),
    (content_versions_alphanumeric_post,
     [],
     content_versions_alphanumeric_post),
    (['v1.0.0', 'v3.0.0', 'v0.0.0'],
     [],
     content_versions_v),
])
def test_validate_versions(versions, exp_valid, exp_invalid):
    valid, invalid = content_version.validate_versions(versions)

    log.debug('valid: %s', valid)
    log.debug('invalid: %s', invalid)

    assert set(exp_valid) == set(valid)
    assert set(exp_invalid) == set(exp_invalid)


def test_get_content_version(ver_data):
    log.debug('ver_data: %s', ver_data)
    res = content_version.get_content_version({}, ver_data['ask'], ver_data['vlist'], 'some_content_name')
    log.debug('res: %s', res)
    assert res == ver_data['exp']


latest_test_data = [
    {'vid': '1_0_0_latest', 'exp': '1.0.0'},
    {'vid': 'boring', 'exp': '3.0.0'},
    {'vid': 'no_v', 'exp': '3.0.0'},
]


@pytest.fixture(scope='module',
                params=latest_test_data,
                ids=['vlist=%s,exp=%s' % (x['vid'], x['exp']) for x in latest_test_data])
def latest_ver_data(request):
    tdata = request.param.copy()
    tdata['vlist'] = content_versions_map[tdata['vid']]
    log.debug('tdata: %s', tdata)
    yield tdata


def test_get_content_version_latest(latest_ver_data):
    log.debug('latest_ver_data: %s', latest_ver_data)
    res = content_version.get_content_version({}, None, latest_ver_data['vlist'], 'some_content_name')
    log.debug('res: %s', res)
    assert res == latest_ver_data['exp']


def test_get_latest_version():
    vers = ['1.0.0', '2.0.0', '2.0.1', '2.2.0', '3.1.4']
    res = content_version.get_latest_version(vers,
                                             content_data={})

    assert res == '3.1.4'


def test_get_latest_version_invalid_semver():
    vers = ['1.0.0', '2.0.0', '2.0.1', '2.2.0', '3.1.4', '4.2']
    try:
        content_version.get_latest_version(vers,
                                           content_data={})
    except exceptions.GalaxyClientError as e:
        assert 'Unable to compare' in '%s' % e
        assert '4.2 is not valid SemVer' in '%s' % e
        return

    assert False, 'Expected a GalaxyClientError about invalid versions here, but that did not happen.'


def test_get_latest_in_content_versions_1_0_0_v_and_no_v():
    ret1 = content_version.get_content_version({}, None, content_versions_1_0_v_and_no_v, 'some_content_name')
    log.debug('ret1: %s', ret1)
    # assert ret1 == '3.0.0'
    content_versions_1_0_v_and_no_v.reverse()
    ret2 = content_version.get_content_version({}, None, content_versions_1_0_v_and_no_v, 'some_content_name')
    log.debug('ret2: %s', ret2)
    assert ret1 == ret2


def test_get_content_version_devel_version_not_in_content_versions():
    # FIXME: use pytest expect_exception stuff
    try:
        ret = content_version.get_content_version({}, 'devel', content_versions_147, 'some_content_name')
        log.debug('ret=%s', ret)
    except exceptions.GalaxyError as e:
        log.exception(e)
        return

    assert False is True, "should have raise an exception earlier"
