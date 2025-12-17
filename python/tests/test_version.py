import broadcastio


def test_package_has_version():
    assert hasattr(broadcastio, "__version__")
    assert isinstance(broadcastio.__version__, str)
    assert broadcastio.__version__ != "unknown"
