import importlib.metadata

try:
    __version__ = importlib.metadata.version("treetop")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
