import logging

from ansible_galaxy.models.collection_info import CollectionInfo

log = logging.getLogger(__name__)


def test_license_error():
    test_data = {
        'name': 'foo.foo',
        'authors': ['chouseknecht'],
        'license': 'GPLv2',
        'version': '0.0.1',
        'description': 'unit testing thing',
    }
    try:
        CollectionInfo(**test_data)
    except ValueError as exc:
        assert 'license' in str(exc)


def test_required_error():
    test_data = {
        'authors': ['chouseknecht'],
        'license': 'GPL-3.0-or-later',
        'version': '0.0.1',
        'description': 'unit testing thing'
    }
    try:
        CollectionInfo(**test_data)
    except ValueError as exc:
        assert 'name' in str(exc)
        assert 'required' in str(exc)


def test_name_parse_error():
    test_data = {
        'name': 'foo',
        'authors': ['chouseknecht'],
        'license': 'GPL-3.0-or-later',
        'version': '0.0.1',
        'description': 'unit testing thing'
    }
    try:
        CollectionInfo(**test_data)
    except ValueError as exc:
        assert 'name' in str(exc)
        assert 'format' in str(exc)


def test_type_list_error():
    test_data = {
        'name': 'foo.foo',
        'authors': 'chouseknecht',
        'license': 'GPL-3.0-or-later',
        'version': '0.0.1',
        'description': 'unit testing thing',
    }
    try:
        CollectionInfo(**test_data)
    except ValueError as exc:
        assert 'authors' in str(exc)
        assert 'list' in str(exc)


def test_semantic_version_error():
    test_data = {
        'name': 'foo.foo',
        'authors': ['chouseknecht'],
        'license': 'GPL-3.0-or-later',
        'version': 'foo',
        'description': 'unit testing thing',
    }
    try:
        CollectionInfo(**test_data)
    except ValueError as exc:
        assert 'version' in str(exc)
        assert 'semantic' in str(exc)


def test_namespace_property():
    test_data = {
        'name': 'foo.foo',
        'authors': ['chouseknecht'],
        'license': 'GPL-3.0-or-later',
        'version': '1.0.0',
        'description': 'unit testing thing',
    }
    info = CollectionInfo(**test_data)
    assert info.namespace == 'foo'
