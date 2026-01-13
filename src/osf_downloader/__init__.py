"""
OSF Downloader.

A small utility for downloading files and projects from osf.io.
"""

from .download import OSFDownloader, OSFError, OSFNotFoundError, OSFRequestError

__all__ = [
    "OSFDownloader",
    "OSFError",
    "OSFNotFoundError",
    "OSFRequestError",
]

__version__ = "0.1.0"
