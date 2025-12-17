from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("broadcastio")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
