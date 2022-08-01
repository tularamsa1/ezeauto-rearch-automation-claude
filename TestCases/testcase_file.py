import time

import pytest

from Utilities import ResourceAssigner

def test_case01():
    appuser = ResourceAssigner.getAppUserCredentials("test_case01")
    portaluser = ResourceAssigner.getPortalUserCredentials("test_case01")
    if appuser and portaluser:
        print(f"TC 01 - {appuser}")
        print(f"TC 01 - {portaluser}")
    else:
        pytest.fail()
    time.sleep(5)
    print(ResourceAssigner.releaseAppUser("test_case01"))
    print(ResourceAssigner.releasePortalUser("test_case01"))

def test_case02():
    appuser = ResourceAssigner.getAppUserCredentials("test_case02")
    portaluser = ResourceAssigner.getPortalUserCredentials("test_case02")
    if appuser and portaluser:
        print(f"TC 02 - {appuser}")
        print(f"TC 02 - {portaluser}")
    else:
        pytest.fail()
    time.sleep(5)
    print(ResourceAssigner.releaseAppUser("test_case02"))
    print(ResourceAssigner.releasePortalUser("test_case02"))

def test_case03():
    appuser = ResourceAssigner.getAppUserCredentials("test_case03")
    portaluser = ResourceAssigner.getPortalUserCredentials("test_case03")
    if appuser and portaluser:
        print(f"TC 03 - {appuser}")
        print(f"TC 03 - {portaluser}")
    else:
        pytest.fail()
    time.sleep(2)
    print(ResourceAssigner.releaseAppUser("test_case03"))
    print(ResourceAssigner.releasePortalUser("test_case03"))

def test_case04():
    appuser = ResourceAssigner.getAppUserCredentials("test_case04")
    portaluser = ResourceAssigner.getPortalUserCredentials("test_case04")
    if appuser and portaluser:
        print(f"TC 04 - {appuser}")
        print(f"TC 04 - {portaluser}")
    else:
        pytest.fail()
    time.sleep(2)
    print(ResourceAssigner.releaseAppUser("test_case04"))
    print(ResourceAssigner.releasePortalUser("test_case04"))

def test_case05():
    appuser = ResourceAssigner.getAppUserCredentials("test_case05")
    portaluser = ResourceAssigner.getPortalUserCredentials("test_case05")
    if appuser and portaluser:
        print(f"TC 05 - {appuser}")
        print(f"TC 05 - {portaluser}")
    else:
        pytest.fail()
    time.sleep(2)
    print(ResourceAssigner.releaseAppUser("test_case05"))
    print(ResourceAssigner.releasePortalUser("test_case05"))

