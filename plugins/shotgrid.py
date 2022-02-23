import json
import os

import review4d

import c4d

try:
    import sgtk
    SHOTGRID_AVAILABLE = True
except ImportError:
    SHOTGRID_AVAILABLE = False


SHOTGRID_COMMAND_ID = 1058262


CTX = {
    'render_path': '',
}


class ShotGridUploaderDialog(c4d.gui.GeDialog):

    # UI Constants
    USER_DATA_NAME = 'c4dreview_sg_settings'
    GROUP_CONTEXT = 10001
    LABEL_ENTITY = 10002
    COMBO_ENTITY = 10003
    LABEL_TASK = 10004
    COMBO_TASK = 10005
    GROUP_VERSION = 20001
    GROUP_BROWSE = 30001
    LABEL_FILE = 30002
    EDIT_FILE = 30003
    BUTTON_BROWSE = 30004
    LABEL_NAME = 20002
    EDIT_NAME = 20003
    LABEL_COMMENT = 20004
    EDIT_COMMENT = 20005
    GROUP_BUTTONS = 40001
    BUTTON_UPLOAD = 40002

    def __init__(self, path):
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)
        self.SetFilepath(path)
        self.state = {
            'entities': {},
            'tasks': {},
            'entity': None,
            'task': None,
        }

    def SetFilepath(self, path):
        self.file_path = path
        self.file_folder = os.path.dirname(path)
        self.file_name = os.path.basename(path)

    def CreateLayout(self):
        self.SetTitle('Upload Preview to ShotGrid'.format(self.file_name))

        if self.GroupBegin(self.GROUP_CONTEXT, c4d.BFH_SCALEFIT, cols=2, rows=2, title='Context'):
            self.GroupBorder(c4d.BORDER_IN)
            self.GroupBorderSpace(4, 4, 4, 4)
            self.AddStaticText(self.LABEL_ENTITY, c4d.BFH_RIGHT, name='Entity')
            self.AddComboBox(self.COMBO_ENTITY, c4d.BFH_SCALEFIT, allowfiltering=True)
            self.AddStaticText(self.LABEL_TASK, c4d.BFH_RIGHT, name='Task')
            self.AddComboBox(self.COMBO_TASK, c4d.BFH_SCALEFIT, allowfiltering=True)
        self.GroupEnd()

        if self.GroupBegin(self.GROUP_VERSION, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=2, rows=2, title='Version Info'):
            self.GroupBorder(c4d.BORDER_IN)
            self.GroupBorderSpace(4, 4, 4, 4)
            self.AddStaticText(self.LABEL_FILE, c4d.BFH_RIGHT, name='File')
            if self.GroupBegin(self.GROUP_BROWSE, c4d.BFH_SCALEFIT, cols=2):
                self.AddEditText(self.EDIT_FILE, c4d.BFH_SCALEFIT)
                self.AddButton(self.BUTTON_BROWSE, c4d.BFH_RIGHT, name='Browse')
            self.GroupEnd()
            self.AddStaticText(self.LABEL_NAME, c4d.BFH_RIGHT, name='Name')
            self.AddEditText(self.EDIT_NAME, c4d.BFH_SCALEFIT)
            self.AddStaticText(self.LABEL_COMMENT, c4d.BFV_TOP | c4d.BFH_RIGHT, name='Comment')
            self.AddMultiLineEditText(self.EDIT_COMMENT, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        self.GroupEnd()

        if self.GroupBegin(self.GROUP_BUTTONS, c4d.BFH_RIGHT | c4d.BFV_BOTTOM, title=''):
            self.GroupBorderSpace(4, 10, 4, 4)
            self.AddButton(self.BUTTON_UPLOAD, c4d.BFH_RIGHT, name='Upload')
        self.GroupEnd()

        return True

    def InitValues(self):
        try:
            import sgtk
        except ImportError:
            return

        self.LoadShotGridState()

        self.SetString(self.EDIT_FILE, self.file_path)
        self.SetString(self.EDIT_NAME, self.file_name)

        self.LoadSettings()

        for entity_id, entity in self.state['entities'].items():
            self.AddChild(self.COMBO_ENTITY, entity_id, entity['code'])

        self.SetInt32(self.COMBO_ENTITY, self.state['entity']['id'])

        for task_id, task in self.state['tasks'].items():
            self.AddChild(self.COMBO_TASK, task_id, task['content'])

        self.SetInt32(self.COMBO_TASK, self.state['task']['id'])

    def Command(self, id, msg):
        if review4d.messages_suppressed(self):
            return True

        if id == self.BUTTON_UPLOAD:
            self.OnUploadClicked()

        elif id == self.BUTTON_BROWSE:
            self.OnBrowseClicked()

        elif id == self.EDIT_FILE:
            self.OnFileChanged(self.GetString(self.EDIT_FILE))

        elif id == self.COMBO_ENTITY:
            self.OnEntityChanged(self.GetInt32(self.COMBO_ENTITY))

        elif id == self.COMBO_TASK:
            self.OnTaskChanged(self.GetInt32(self.COMBO_TASK))

        return True

    def GetSettingsUserData(self):
        doc = c4d.documents.GetActiveDocument()
        for id, desc in doc.GetUserDataContainer():
            if self.USER_DATA_NAME in (desc[c4d.DESC_NAME], desc[c4d.DESC_SHORT_NAME]):
                return id, desc

    def GetValues(self):
        return {
            'file': self.GetString(self.EDIT_FILE),
            'name': self.GetString(self.EDIT_NAME),
            'entity': self.state['entity'],
            'task': self.state['task'],
            'comment': self.GetString(self.EDIT_COMMENT),
        }

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

        if settings['entity']:
            self.state['entity'] = settings['entity']
            tasks = self.shotgun.find(
                'Task',
                filters=[['entity', 'is', self.state['entity']]],
                fields=['id', 'content', 'step'],
            )
            self.state['tasks'] = {}
            for task in sorted(tasks, key=lambda e: e['content']):
                self.state['tasks'][task['id']] = task

        if settings['task']:
            self.state['task'] = settings['task']

        if settings['comment']:
            self.SetString(self.EDIT_COMMENT, settings['comment'])

        if settings['name'] and not self.file_name:
            self.SetString(self.EDIT_NAME, settings['name'])

        if settings['file'] and not self.file_path:
            self.SetFilepath(settings['file'])
            self.SetString(self.EDIT_FILE, settings['file'])

    @property
    def engine(self):
        import sgtk
        return sgtk.platform.current_engine()

    @property
    def context(self):
        return self.engine.context

    @property
    def shotgun(self):
        return self.engine.shotgun

    def LoadShotGridState(self):
        '''Load state from current ShotGrid context.'''

        assets = self.shotgun.find(
            'Asset',
            filters=[['project', 'is', self.context.project]],
            fields=['code'],
        )
        shots = self.shotgun.find(
            'Shot',
            filters=[['project', 'is', self.context.project]],
            fields=['code'],
        )
        self.state['entities'] = {}
        for entity in sorted(assets + shots, key=lambda e: e['code']):
            self.state['entities'][entity['id']] = entity

        if self.context.entity:
            self.state['entity'] = self.state['entities'][self.context.entity['id']]
        else:
            self.state['entity'] = list(self.state['entities'].values())[0]

        tasks = self.shotgun.find(
            'Task',
            filters=[['entity', 'is', self.state['entity']]],
            fields=['id', 'content', 'step'],
        )
        self.state['tasks'] = {}
        for task in sorted(tasks, key=lambda e: e['content']):
            self.state['tasks'][task['id']] = task

        if self.context.task:
            self.state['task'] = self.state['tasks'][self.context.task['id']]
        else:
            self.state['task'] = list(self.state['tasks'].values())[0]

    def OnEntityChanged(self, entity_id):
        self.state['entity'] = self.state['entities'][entity_id]
        tasks = self.shotgun.find(
            'Task',
            filters=[['entity', 'is', self.state['entity']]],
            fields=['id', 'content', 'step'],
        )

        with review4d.suppress_messages(self):
            # Remove existing child
            self.FreeChildren(self.COMBO_TASK)

            # Populate tasks from new entity selection
            self.state['tasks'] = {}
            for task in sorted(tasks, key=lambda e: e['content']):
                self.state['tasks'][task['id']] = task
                self.AddChild(self.COMBO_TASK, task['id'], task['content'])

            if self.state['task'] and self.state['task']['id'] in self.state['tasks']:
                self.SetInt32(self.COMBO_TASK, self.state['task']['id'])
            else:
                self.state['task'] = list(self.state['tasks'].values())[0]
                self.SetInt32(self.COMBO_TASK, self.state['task']['id'])

    def OnTaskChanged(self, task_id):
        self.state['task'] = self.state['tasks'][task_id]

    def OnFileChanged(self, path):
        name = os.path.basename(path)
        self.SetString(self.EDIT_NAME, name)

    def OnBrowseClicked(self):
        cur_path = self.GetString(self.EDIT_FILE)
        if cur_path:
            def_path = os.path.dirname(cur_path)
            def_file = os.path.basename(cur_path)
        else:
            doc = c4d.documents.GetActiveDocument()
            def_path = doc.GetDocumentPath()
            def_file = doc.GetDocumentName().rsplit('.', 1)[0] + '.mp4'

        path = c4d.storage.LoadDialog(
            c4d.FILESELECTTYPE_ANYTHING,
            title='Select a video to upload (mp4, mov, avi)',
            force_suffix='mp4',
            def_path=def_path,
            def_file=def_file,
        )
        if path and os.path.splitext(path)[-1] in ['.mp4', '.mov', '.avi']:
            path = review4d.normalize(path)
            self.SetFilepath(path)
            self.SetString(self.EDIT_FILE, path)
            self.OnFileChanged(path)

    def OnUploadClicked(self):
        self.SaveSettings()
        values = self.GetValues()
        self.UploadVersion(
            entity=values['entity'],
            task=values['task'],
            status='rev',
            comment=values['comment'],
            file=values['file'],
            name=values['name'],
        )
        CTX['render_path'] = ''
        self.Close()

    def CreateVersion(self, version_data):
        '''Get existing version or create a new one.'''

        version = self.shotgun.find_one(
            'Version',
            [
                ['project', 'is', version_data['project']],
                ['code', 'is', version_data['code']],
                ['sg_task', 'is', version_data['sg_task']],
                ['entity', 'is', version_data['entity']],
            ],
            ['id', 'code', 'sg_path_to_frames'],
        )

        if not version:
            version = self.shotgun.create('Version', version_data)
        else:
            self.shotgun.update(
                'Version',
                version['id'],
                version_data,
            )

        return version

    def UploadVersion(self, entity, task, status, comment, file, name):
        '''Upload a version to ShotGrid!'''

        version_data = {
            'project': self.context.project,
            'code': name.split('.')[0],
            'description': comment,
            'sg_status_list': status,
            'sg_path_to_frames': file,
            'entity': entity,
            'sg_task': task,
            # Fields restricted by Artist permissions...
            # 'user': self.context.user,
        }
        version = self.CreateVersion(version_data)
        media = self.shotgun.upload(
            'Version',
            version['id'],
            path=file,
            field_name='sg_uploaded_movie',
        )
        return media


class ShotGridPostRender(review4d.PostRender):

    label = 'Upload to ShotGrid'
    enabled = True

    def is_available(self):
        return SHOTGRID_AVAILABLE

    def execute(self, render_path):
        CTX['render_path'] = render_path
        c4d.CallCommand(ShotGridUploaderDialogCommand.pluginid)


class ShotGridUploaderDialogCommand(c4d.plugins.CommandData):

    pluginid = SHOTGRID_COMMAND_ID
    label = 'ShotGrid Uploader'
    info = 0
    tip = 'Upload media to ShotGrid for review.'
    icon = review4d.resource_path('shotgrid.png')
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ShotGridUploaderDialog(CTX.get('render_path', ''))

        self.dialog.SetFilepath(CTX.get('render_path', ''))
        return self.dialog.Open(
            dlgtype=c4d.DLG_TYPE_ASYNC,
            pluginid=self.pluginid,
            defaultw=400,
            defaulth=300,
        )

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ShotGridUploaderDialog(CTX.get('render_path', ''))

        self.dialog.SetFilepath(CTX.get('render_path', ''))
        return self.dialog.Restore(
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


def register():
    if SHOTGRID_AVAILABLE:
        review4d.register_plugin(ShotGridPostRender)
        ShotGridUploaderDialogCommand.register()
    else:
        print(
            'Review4d> ShotGrid plugin unavailable. '
            'Could not import the required "sgtk" module.'
        )
