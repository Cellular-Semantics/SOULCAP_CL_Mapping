"""SOULCAP ↔ Cell Ontology mapping utilities."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("soulcap-cl-mapping")
except PackageNotFoundError:
    __version__ = "unknown"
