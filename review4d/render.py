'''Methods for rendering previews.'''
import time
import threading

import c4d


__all__ = [
    'await_render',
    'create_render_settings',
    'edit_render_settings_dialog',
    'execute_after_render',
    'get_render_settings',
    'render_to_pictureviewer',
]


def get_render_settings(name, doc=None):
    '''Get RenderData object by name.'''

    doc = doc or c4d.documents.GetActiveDocument()

    rd = doc.GetFirstRenderData()
    if not rd:
        return

    while rd:
        if rd.GetName() == name:
            return rd

        rd = rd.GetNext()


def edit_render_settings_dialog():
    c4d.CallCommand(12161)


def create_render_settings(name, doc=None, **settings):
    '''Create and activate a new set of Render Settings by name.

    Keyword Arguments:
        xres (int): Image X resolution
        yres (int): Image Y resolution
        framerate (int): FPS
        framesequence (int): 1 Current Frame, 2 All Frames, 3 Preview Frames
        format (int): File format defaults to c4d.FILTER_MOVIE
        path (str): Output filepath
    '''

    doc = doc or c4d.documents.GetActiveDocument()

    rd = get_render_settings(name)
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
    rd_data[c4d.RDATA_XRES] = float(settings.get('xres', rd_data[c4d.RDATA_XRES]))
    rd_data[c4d.RDATA_YRES] = float(settings.get('yres', rd_data[c4d.RDATA_YRES]))
    rd_data[c4d.RDATA_FRAMERATE] = float(settings.get('framerate', rd_data[c4d.RDATA_FRAMERATE]))
    rd_data[c4d.RDATA_FRAMESEQUENCE] = settings.get('framesequence', rd_data[c4d.RDATA_FRAMESEQUENCE])
    rd_data[c4d.RDATA_FORMAT] = settings.get('format', c4d.FILTER_MOVIE)

    # Only set these settings on first creation of Review Render Settings.
    if not rd_exists:
        rd_data[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE

    rd_data.SetFilename(c4d.RDATA_PATH, settings.get('path', rd_data[c4d.RDATA_PATH]))

    doc.SetActiveRenderData(rd)
    c4d.EventAdd()
    return rd


def await_render():
    '''Wait for external rendering to complete.'''

    while c4d.CheckIsRunning(c4d.CHECKISRUNNING_EXTERNALRENDERING):
        time.sleep(2)


def execute_after_render(callback):
    '''Execute a callback after external rendering is completed.'''

    await_render()
    callback()


def render_to_pictureviewer(callback=None):
    '''Call the Render To PictureViewer command.'''

    # Render to pictureviewer
    c4d.CallCommand(12099)

    if callback:
        # Start thread to wait for render to finish then execute callback
        thread = threading.Thread(
            target=execute_after_render,
            args=(callback,),
        )
        thread.start()
