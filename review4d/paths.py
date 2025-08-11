import os

import c4d

__all__ = [
    "desktop_path",
    "get_document_path",
    "library_path",
    "normalize",
    "plugin_path",
    "user_previews_path",
    "resource_path",
]


library_path = os.path.dirname(__file__)
plugin_path = os.path.dirname(library_path)
user_previews_path = c4d.storage.GeGetStartupWritePath() + "/prefs/pv"
if "USERPROFILE" in os.environ:
    desktop_path = os.path.expandvars("$USERPROFILE/Desktop")
else:
    desktop_path = os.path.expanduser("~/Desktop")


def normalize(*paths):
    """Like os.path.join but returns an absolute path separated with /."""

    return os.path.abspath(os.path.join(*paths)).replace("\\", "/")


def get_document_path(doc=None):
    """Get full path to a document. Defaults to active document."""

    doc = doc or c4d.documents.GetActiveDocument()
    path, name = doc.GetDocumentPath(), doc.GetDocumentName()
    if path and name:
        return normalize(doc.GetDocumentPath(), doc.GetDocumentName())
    if path:
        return normalize(path)
    if name:
        return name


def resource_path(*parts):
    """Get a path to a plugin res file."""

    return normalize(plugin_path, "res", *parts)
