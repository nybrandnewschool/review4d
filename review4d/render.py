import threading
import time
from functools import partial

import c4d
import mxutils

__all__ = [
    "await_render",
    "create_render_settings",
    "edit_render_settings_dialog",
    "execute_after_render",
    "expand_render_paths",
    "get_render_settings",
    "iter_takes",
    "render_to_pictureviewer",
    "set_active_render_settings",
    "Takes",
]


def get_render_settings(name, *, doc=None):
    """Get RenderData object by name."""

    doc = doc or c4d.documents.GetActiveDocument()

    rd = doc.GetFirstRenderData()
    if not rd:
        return

    while rd:
        if rd.GetName() == name:
            return rd

        rd = rd.GetNext()


def set_active_render_settings(name, *, doc=None):
    """Set the active RenderData object by name."""

    doc = doc or c4d.documents.GetActiveDocument()

    if rd := get_render_settings(name, doc=doc):
        doc.SetActiveRenderData(rd)
        c4d.EventAdd()
        c4d.gui.GeUpdateUI()


def edit_render_settings_dialog():
    """Opens the Render Settings dialog."""

    c4d.CallCommand(12161)


def create_render_settings(name, *, doc=None, **settings):
    """Create and activate a new set of Render Settings by name.

    Keyword Arguments:
        xres (int): Image X resolution
        yres (int): Image Y resolution
        framerate (int): FPS
        framesequence (int): 1 Current Frame, 2 All Frames, 3 Preview Frames
        format (int): File format defaults to c4d.FILTER_MOVIE
        path (str): Output filepath
    """

    doc = doc or c4d.documents.GetActiveDocument()

    rd = get_render_settings(name, doc=doc)
    rd_exists = bool(rd)
    if not rd_exists:
        rd = c4d.documents.RenderData()
        rd.SetName(name)
        doc.InsertRenderDataLast(rd)

        hw_vp = c4d.BaseList2D(c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE)
        hw_vp[c4d.VP_PREVIEWHARDWARE_ENHANCEDOPENGL] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_SHADOW] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_POSTEFFECT] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_NOISE] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_TESSELLATION] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_SSAO] = False
        hw_vp[c4d.VP_PREVIEWHARDWARE_REFLECTIONS] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_ANTIALIASING] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_SUPERSAMPLING_16] = True
        hw_vp[c4d.VP_PREVIEWHARDWARE_ONLY_GEOMETRY] = True
        rd.InsertVideoPost(hw_vp)

    rd_data = rd.GetDataInstance()
    rd_data[c4d.RDATA_XRES] = float(settings.get("xres", rd_data[c4d.RDATA_XRES]))
    rd_data[c4d.RDATA_YRES] = float(settings.get("yres", rd_data[c4d.RDATA_YRES]))
    rd_data[c4d.RDATA_FRAMERATE] = float(
        settings.get("framerate", rd_data[c4d.RDATA_FRAMERATE])
    )
    rd_data[c4d.RDATA_FRAMESEQUENCE] = settings.get(
        "framesequence", rd_data[c4d.RDATA_FRAMESEQUENCE]
    )
    rd_data[c4d.RDATA_FORMAT] = settings.get("format", c4d.FILTER_MOVIE)

    # Only set these settings on first creation of Review Render Settings.
    if not rd_exists:
        rd_data[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE

    rd_data.SetFilename(c4d.RDATA_PATH, settings.get("path", rd_data[c4d.RDATA_PATH]))

    doc.SetActiveRenderData(rd)
    c4d.EventAdd()
    c4d.gui.GeUpdateUI()
    return rd


def await_render():
    """Wait for external rendering to complete."""

    while c4d.CheckIsRunning(c4d.CHECKISRUNNING_EXTERNALRENDERING):
        time.sleep(2)


def execute_after_render(callback):
    """Execute a callback after external rendering is completed."""

    from .queue import execute_in_main_thread

    await_render()
    execute_in_main_thread(callback)


class Takes:
    """Takes Enum."""

    active = 1
    all = 2
    marked = 3

    @staticmethod
    def is_valid(value):
        return value in [Takes.active, Takes.all, Takes.marked]


def render_to_pictureviewer(render_settings, takes=Takes.active, callback=None, *, doc=None):
    """Call the Render To PictureViewer command."""

    doc = doc or c4d.documents.GetActiveDocument()

    # Validate parameters
    if get_render_settings(render_settings) is None:
        raise ValueError(f"Render Settings named '{render_settings}' do not exist.")

    if not Takes.is_valid(takes):
        raise ValueError(f"Got '{takes}' for takes expected one of [1, 2, 3] or [Takes.active, Takes.all, Takes.marked].")

    # Render to pictureviewer
    if takes == Takes.active:
        c4d.CallCommand(12099)
        if callback:
            # Start thread to wait for render to finish then execute callback
            thread = threading.Thread(
                target=execute_after_render,
                args=(callback,),
            )
            thread.start()
        return

    # Build pipeline to render all takes sequentially.
    # We start with the final callback, and create
    # render_take partials in reverse order.
    # This allows us to await each render before finally
    # executing the original callback functions.
    pipeline = partial(
        execute_funcs,
        callback,
        partial(set_take, render_settings, get_active_take(doc=doc)),
    )
    for take in list(iter_takes(marked=takes == Takes.marked, doc=doc))[::-1]:
        pipeline = partial(render_take, render_settings, take, callback=pipeline, doc=doc)

    # Execute pipeline
    pipeline()


def execute_funcs(*tasks):
    """Execute a bunch of functions sequentially."""

    for task in tasks:
        if task is not None:
            task()


def get_active_take(doc=None):
    """Get the active Take."""

    doc = doc or c4d.documents.GetActiveDocument()
    data = mxutils.CheckType(doc.GetTakeData())
    return data.GetCurrentTake()


def set_take(render_settings, take, *, doc=None):
    """Set the active Take."""

    doc = doc or c4d.documents.GetActiveDocument()
    data = mxutils.CheckType(doc.GetTakeData())
    data.SetCurrentTake(take)
    c4d.EventAdd()

    set_active_render_settings(render_settings)


def render_take(render_settings, take, *, callback=None, doc=None):
    """Render a Take.

    Waits for the render to finish, then execute the callback function.
    """

    doc = doc or c4d.documents.GetActiveDocument()
    set_take(render_settings, take, doc=doc)
    c4d.CallCommand(12099)
    if callback:
        thread = threading.Thread(
            target=execute_after_render,
            args=(callback,),
        )
        thread.start()


def iter_takes(marked=False, *, doc=None):
    """Iterate over the Takes in a document."""

    doc = doc or c4d.documents.GetActiveDocument()
    take_data = mxutils.CheckType(doc.GetTakeData())
    main_take = take_data.GetMainTake()

    for take in mxutils.IterateTree(main_take):
        if not marked or marked and take.IsChecked():
            yield take


def expand_render_paths(path, render_settings, takes=Takes.active, *, doc=None):
    """Expand the tokens in a render path.

    Returns:
        List of filepaths with tokens resolved.
    """

    doc = doc or c4d.documents.GetActiveDocument()
    rdata = get_render_settings(render_settings, doc=doc)
    rpd = {
        "_doc": doc,
        "_rData": rdata,
        "_rBc": rdata.GetDataInstance(),
        "_frame": 1,
    }

    paths = []
    if takes == Takes.active:
        filename = c4d.modules.tokensystem.StringConvertTokens(path, rpd)
        paths.append(filename)
    else:
        for take in iter_takes(marked=takes == Takes.marked, doc=doc):
            take_rpd = dict(_take=take, **rpd)
            filename = c4d.modules.tokensystem.StringConvertTokens(path, take_rpd)
            paths.append(filename)
    return paths
