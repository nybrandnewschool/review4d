# Standard library imports
import sys
import contextlib
import json
import os
import re
from functools import partial

# Third party imports
import c4d
from c4d import gui, plugins

# Local imports
sys.path.insert(1, os.path.dirname(__file__))
import review4d


RENDER_TO_PICTUREVIEWER = 12099
RENDER_SETTINGS_NAME = 'Review Settings'


class Review4dDialog(gui.GeDialog):

    # UI Constants
    USER_DATA_NAME = 'c4dreview_ui_settings'
    GROUP_PATH = 10001
    COMBO_PRESET = 10002
    EDIT_PATH = 10003
    BUTTON_BROWSE = 10004
    GROUP_SETTINGS = 20001
    LABEL_RESOLUTION = 20002
    EDIT_XRES = 20003
    EDIT_YRES = 20004
    LABEL_FPS = 20005
    EDIT_FPS = 20006
    SPACE_FPS = 20007
    LABEL_FRAMESEQUENCE = 20008
    COMBO_FRAMESEQUENCE = 20009
    COMBO_FRAMESEQUENCE_ENUM = {
        1: 'Current Frame',
        2: 'All Frames',
        3: 'Preview Frames',
    }
    COMBO_FRAMESEQUENCE_DEFAULT = 2
    SPACE_FRAMES = 20010
    LABEL_TAKES = 20011
    COMBO_TAKES = 20012
    COMBO_TAKES_ENUM = {
        1: 'Active',
        2: 'All',
        3: 'Marked',
    }
    COMBO_TAKES_DEFAULT = 1
    SPACE_TAKES = 20013
    GROUP_POSTRENDER = 30001
    GROUP_BUTTONS = 40001
    BUTTON_RENDER_SETTINGS = 40001
    BUTTON_RENDER = 40003

    def __init__(self):
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)
        self.post_renderers = review4d.get_available_post_renderers()

    def CreateLayout(self):
        self.SetTitle('Render for Review')

        if self.GroupBegin(self.GROUP_PATH, c4d.BFH_SCALEFIT, title='Path'):
            self.GroupBorder(c4d.BORDER_IN)
            self.GroupBorderSpace(4, 4, 4, 4)
            self.AddComboBox(self.COMBO_PRESET, c4d.BFH_LEFT, initw=120)
            self.AddEditText(self.EDIT_PATH, c4d.BFH_SCALEFIT)
            self.AddButton(self.BUTTON_BROWSE, c4d.BFH_RIGHT, name='Browse')
        self.GroupEnd()

        if self.GroupBegin(self.GROUP_SETTINGS, c4d.BFH_SCALEFIT, cols=3, rows=3, title='Settings'):
            self.GroupBorder(c4d.BORDER_IN)
            self.GroupBorderSpace(4, 4, 4, 4)
            self.AddStaticText(self.LABEL_RESOLUTION, c4d.BFH_RIGHT, name='Resolution')
            self.AddEditNumberArrows(self.EDIT_XRES, c4d.BFH_LEFT, initw=120)
            self.AddEditNumberArrows(self.EDIT_YRES, c4d.BFH_LEFT, initw=120)
            self.AddStaticText(self.LABEL_FPS, c4d.BFH_RIGHT, name='FPS')
            self.AddEditNumberArrows(self.EDIT_FPS, c4d.BFH_LEFT, initw=120)
            self.AddStaticText(self.SPACE_FPS, c4d.BFH_LEFT, name='')
            self.AddStaticText(self.LABEL_FRAMESEQUENCE, c4d.BFH_RIGHT, name='Frames')
            self.AddComboBox(self.COMBO_FRAMESEQUENCE, c4d.BFH_LEFT, initw=128)
            self.AddStaticText(self.SPACE_FRAMES, c4d.BFH_LEFT, name='')
            self.AddStaticText(self.LABEL_TAKES, c4d.BFH_RIGHT, name='Takes')
            self.AddComboBox(self.COMBO_TAKES, c4d.BFH_LEFT, initw=128)
            self.AddStaticText(self.SPACE_TAKES, c4d.BFH_LEFT, name='')
            # self.AddCheckbox(self.CBOX_PICTUREVIEWER, c4d.BFH_LEFT, initw=0, inith=0, name='Send to Picture Viewer')
        self.GroupEnd()

        if self.post_renderers:
            if self.GroupBegin(self.GROUP_POSTRENDER, c4d.BFH_SCALEFIT, cols=2, title='Post Render'):
                self.GroupBorder(c4d.BORDER_IN)
                self.GroupBorderSpace(4, 4, 4, 4)
                self.GroupSpace(20, 10)
                for post_renderer in self.post_renderers:
                    self.AddCheckbox(post_renderer.id, c4d.BFH_LEFT, initw=0, inith=0, name=post_renderer.label)
                    if post_renderer.enabled:
                        self.SetBool(post_renderer.id, True)
            self.GroupEnd()

        if self.GroupBegin(self.GROUP_BUTTONS, c4d.BFH_RIGHT | c4d.BFV_SCALE | c4d.BFV_BOTTOM, title=''):
            self.GroupBorderNoTitle(c4d.BORDER_GROUP_OUT)
            self.GroupBorderSpace(4, 10, 4, 4)
            self.AddButton(self.BUTTON_RENDER_SETTINGS, c4d.BFH_RIGHT, name='Edit Review Settings')
            self.AddButton(self.BUTTON_RENDER, c4d.BFH_RIGHT, name='Render')
        self.GroupEnd()

        return True

    def InitValues(self):
        doc = c4d.documents.GetActiveDocument()

        # Set UI Defaults
        for id, label in self.COMBO_FRAMESEQUENCE_ENUM.items():
            self.AddChild(self.COMBO_FRAMESEQUENCE, id, label)

        for id, label in self.COMBO_TAKES_ENUM.items():
            self.AddChild(self.COMBO_TAKES, id, label)

        presets = review4d.get_path_presets()
        for preset in presets:
            self.AddChild(self.COMBO_PRESET, preset.id, preset.label)

        self.SetInt32(self.COMBO_FRAMESEQUENCE, self.COMBO_FRAMESEQUENCE_DEFAULT)
        self.SetInt32(self.COMBO_TAKES, self.COMBO_TAKES_DEFAULT)
        self.SetInt32(self.COMBO_PRESET, presets[0].id)
        self.SetInt32(self.EDIT_XRES, 1920, min=256, max=8192, step=2)
        self.SetInt32(self.EDIT_YRES, 1080, min=256, max=8192, step=2)
        self.SetInt32(self.EDIT_FPS, doc[c4d.DOCUMENT_FPS])
        # self.SetBool(self.CBOX_PICTUREVIEWER, True)

        # Load settings from document
        self.LoadSettings()

        # Refresh path
        self.RefreshPath()

    def Command(self, id, msg):
        if review4d.messages_suppressed(self):
            return True

        if id == self.BUTTON_BROWSE:
            self.OnBrowseClicked()

        elif id == self.BUTTON_RENDER:
            self.OnRenderClicked()

        elif id == self.BUTTON_RENDER_SETTINGS:
            self.OnRenderSettingsClicked()

        elif id in (self.COMBO_PRESET, self.COMBO_TAKES):
            self.RefreshPath()

        elif id == self.EDIT_PATH:
            self.OnPathChanged(self.GetString(self.EDIT_PATH))

        return True

    def GetSettingsUserData(self):
        doc = c4d.documents.GetActiveDocument()
        for id, desc in doc.GetUserDataContainer():
            if self.USER_DATA_NAME in (desc[c4d.DESC_NAME], desc[c4d.DESC_SHORT_NAME]):
                return id, desc

    def GetValues(self):
        values = {
            'preset': review4d.get_path_preset(
                self.GetInt32(self.COMBO_PRESET)
            ).label,
            'path': self.GetString(self.EDIT_PATH),
            'xres': self.GetInt32(self.EDIT_XRES),
            'yres': self.GetInt32(self.EDIT_YRES),
            'fps': self.GetInt32(self.EDIT_FPS),
            'framesequence': self.GetInt32(self.COMBO_FRAMESEQUENCE),
            'takes': self.GetInt32(self.COMBO_TAKES),
        }
        for post_renderer in self.post_renderers:
            values[post_renderer.label] = self.GetBool(post_renderer.id)
        return values

    def SaveSettings(self):
        doc = c4d.documents.GetActiveDocument()
        user_data = self.GetSettingsUserData()
        if user_data:
            id, desc = user_data
        else:
            desc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_STRING)
            desc[c4d.DESC_NAME] = self.USER_DATA_NAME
            desc[c4d.DESC_SHORT_NAME] = self.USER_DATA_NAME
            desc[c4d.DESC_DEFAULT] = ''
            desc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_STATICTEXT
            id = doc.AddUserData(desc)

        doc[id] = json.dumps(self.GetValues())
        c4d.EventAdd()

    def LoadSettings(self):
        user_data = self.GetSettingsUserData()
        if not user_data:
            return

        doc = c4d.documents.GetActiveDocument()
        data = doc[user_data[0]]
        if not data:
            return

        settings = json.loads(data)

        preset_label = settings.get('preset')
        if preset_label:
            preset = review4d.get_path_preset(preset_label)
            self.SetInt32(self.COMBO_PRESET, preset.id)

        path = settings.get('path')
        if path and preset_label == 'Custom':
            self.SetString(self.EDIT_PATH, path)

        xres = settings.get('xres')
        if xres:
            self.SetInt32(self.EDIT_XRES, xres, min=256, max=4096, step=2)

        yres = settings.get('yres')
        if yres:
            self.SetInt32(self.EDIT_YRES, yres, min=256, max=4096, step=2)

        fps = settings.get('fps')
        if fps:
            self.SetInt32(self.EDIT_FPS, fps)

        frames = settings.get('frames')
        if frames:
            self.SetInt32(self.COMBO_FRAMESEQUENCE, frames)

        takes = settings.get('takes')
        if takes:
            self.SetInt32(self.COMBO_TAKES, takes)

        for post_renderer in self.post_renderers:
            try:
                value = settings.get(post_renderer.label)
                if value:
                    self.SetBool(post_renderer.id, value)
            except:
                continue

    def OnBrowseClicked(self):
        cur_path = self.GetString(self.EDIT_PATH)
        if cur_path:
            def_path = os.path.dirname(cur_path)
            def_file = os.path.basename(cur_path)
        else:
            doc = c4d.documents.GetActiveDocument()
            def_path = doc.GetDocumentPath()
            def_file = doc.GetDocumentName().rsplit('.', 1)[0] + '.mp4'

        path = c4d.storage.SaveDialog(
            c4d.FILESELECTTYPE_ANYTHING,
            title='Select an output path (.mp4)',
            force_suffix='mp4',
            def_path=def_path,
            def_file=def_file,
        )
        if path:
            path = review4d.normalize(path)
            self.SetString(self.EDIT_PATH, path)
            self.OnPathChanged(path)

    def RefreshPath(self):
        preset = review4d.get_path_preset(self.GetInt32(self.COMBO_PRESET))
        if preset.label != 'Custom':
            self.OnPresetChanged(preset.id)

    def OnPresetChanged(self, preset_id):
        doc_path = review4d.get_document_path()
        try:
            path = self.GetPathPresetValue(preset_id, doc_path)
            if path:
                with review4d.suppress_messages(self):
                    self.SetString(self.EDIT_PATH, path)
        except review4d.PathPresetError as e:
            self.SetString(self.TEXT_MSG, str(e))

    def GetPathPresetValue(self, preset_id, doc_path):
        return review4d.get_preset_path(preset_id, doc_path)

    def OnPathChanged(self, path):
        doc_path = review4d.get_document_path()
        for preset in review4d.get_path_presets():
            try:
                preset_path = self.GetPathPresetValue(preset.id, doc_path)
                if path == preset_path:
                    with review4d.suppress_messages(self):
                        self.SetInt32(self.COMBO_PRESET, preset.id)
            except review4d.PathPresetError:
                continue
        else:
            with review4d.suppress_messages(self):
                self.SetInt32(
                    self.COMBO_PRESET,
                    review4d.get_path_preset('Custom').id
                )

    def OnRenderSettingsClicked(self):
        self.CreateRenderSettings()
        review4d.edit_render_settings_dialog()

    def OnRenderClicked(self):
        self.SaveSettings()
        self.CreateRenderSettings()
        self.Render()
        self.Close()

    def CreateRenderSettings(self):
        state = self.GetValues()
        review4d.create_render_settings(
            RENDER_SETTINGS_NAME,
            path=state['path'],
            xres=state['xres'],
            yres=state['yres'],
            framerate=state['fps'],
            framesequence=state['framesequence'],
            takes=state['takes'],
        )

    def Render(self):
        state = self.GetValues()

        post_render_functions = [
            pr().execute for pr in self.post_renderers
            if state.get(pr.label, False)
        ]
        args = (state['path'],)
        if post_render_functions:
            callback = partial(
                execute_all,
                post_render_functions,
                args
            )
        else:
            callback = None

        review4d.render_to_pictureviewer(callback)


def execute_all(functions, args):
    for func in functions:
        review4d.execute_in_main_thread(func, *args)


class Review4dDialogContext(review4d.ContextCollector):

    def execute(self, file, ctx):
        if Session.dialog is None:
            return ctx

        options = Session.dialog.GetValues()
        for opt in ["path", "preset"]:
            options.pop(opt)

        ctx.update(options)
        return ctx


class Review4dDialogCommand(c4d.plugins.CommandData):

    pluginid = review4d.RENDER_COMMAND_ID
    label = 'Render for Review'
    info = 0
    tip = 'Render previews using presets.'
    icon = review4d.resource_path('icon.png')
    dialog = None

    def Execute(self, doc):
        if Session.dialog is None:
            Session.dialog = Review4dDialog()

        return Session.dialog.Open(
            dlgtype=c4d.DLG_TYPE_ASYNC,
            pluginid=self.pluginid,
            defaultw=400,
            defaulth=100,
        )

    def RestoreLayout(self, sec_ref):
        if Session.dialog is None:
            Session.dialog = Review4dDialog()

        return Session.dialog.Restore(
            pluginid=self.pluginid,
            secret=sec_ref,
        )

    @classmethod
    def register(cls):
        icon = c4d.bitmaps.BaseBitmap()
        icon.InitWith(cls.icon)
        c4d.plugins.RegisterCommandPlugin(
            id=cls.pluginid,
            str=cls.label,
            info=cls.info,
            help=cls.tip,
            icon=icon,
            dat=cls(),
        )


class Review4dCommandQueue(c4d.plugins.MessageData):

    pluginid = review4d.COMMAND_QUEUE_ID
    label = 'Review4d Command Queue'
    info = 0
    tip = 'Execute python callbacks in the main thread.'
    icon = None

    def CoreMessage(self, id, msg):
        if id == review4d.COMMAND_QUEUE_ID:
            review4d.execute_queued_commands()
        return True

    @classmethod
    def register(cls):
        c4d.plugins.RegisterMessagePlugin(
            id=cls.pluginid,
            str=cls.label,
            info=cls.info,
            dat=cls(),
        )


class Session:
    dialog = None


if __name__ == "__main__":
    # Register dialog context
    review4d.register_plugin(Review4dDialogContext)

    # Load review4d plugins
    review4d.load_plugins()

    # Register c4d plugins
    Review4dDialogCommand.register()
    Review4dCommandQueue.register()
