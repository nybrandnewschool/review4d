<div align="center">
  
# 🎥 review4d

**A python plugin and library for Cinema 4D R24+ allowing users to render previews to preset locations and perform actions after a render completes.**

[![Test status](https://img.shields.io/badge/Test-passing-green)](https://github.com/nybrandnewschool/review4d/actions)
[![ShotGrid status](https://github.com/nybrandnewschool/review4d/workflows/Publish%20to%20ShotGrid/badge.svg)](https://github.com/nybrandnewschool/review4d/actions)
[![Version](https://img.shields.io/github/v/tag/nybrandnewschool/review4d)](https://github.com/nybrandnewschool/review4d/releases)

*Developed at [Brand New School](https://brandnewschool.com).*

</div>

## Installation
### Git
You can use git to install review4d by cloning it into your c4d plugins directory.

### Download
Alternatively you can download a release and extract it into your c4d plugins directory.

## Usage
1. Use the **Render for Review** command in the Extensions menu to pull up the
render dialog.

    ![Extensions](https://github.com/nybrandnewschool/review4d/blob/main/res/extensions.png?raw=true) ![Dialog](https://github.com/nybrandnewschool/review4d/blob/main/res/render_for_review_dialog.png?raw=true)

2. Adjust the settings in the dialog. Review4d will add new render settings to your document called **Review Settings**. You can use the **Edit Review Settings** button to edit the viewport settings in the Render Settings window.

    ![Render Settings](https://github.com/nybrandnewschool/review4d/blob/main/res/render_settings.png?raw=true)

3. If you have [ShotGrid](https://www.shotgridsoftware.com) toolkit and the accompanying [tk-cinema](https://github.com/mikedatsik/tk-cinema) app running in your Cinema4D session you can enable the **Upload to ShotGrid** checkbox. After the render finishes a dialog will appear to let you upload it to ShotGrid.

    ![Upload to ShotGrid](https://github.com/nybrandnewschool/review4d/blob/main/res/upload_to_shotgrid.png)

## Plugins
review4d allows customization through the use of plugins. Create a python module and place it in the `review4d/plugins` folder. Alternatively, you can add a custom path to the environment variable `REVIEW4D_PLUGINS` and place your python modules there. Subclass one of the plugin types like PathPreset, ContextCollector, or PostRender and register them in a module level register function.

![Plugins](https://github.com/nybrandnewschool/review4d/blob/main/res/render_for_review_plugins.png)

ContextCollector plugins are used to extract useful data from document paths. But you can include any data in the context that you want. The extracted context is then passed to PathPreset plugins to generate output file paths.

    import review4d
    import getpass
    import datetime

    class MyContextCollector(review4d.ContextCollector):
        '''Adds user and date fields to context.'''

        def execute(self, file, ctx):
            ctx['user'] = getpass.getuser()
            ctx['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
            return ctx

    def register():
        review4d.register_plugin(ContextCollector)

Let's use the user and date context collected in MyContextCollector in a new
PathPreset plugin.

    ...
    class MyPathPreset(review4d.PathPreset):

        def execute(self, ctx):
            filename = '{}_{}.mp4'.format(
                ctx['filename'].rsplit('.', 1)[0],
                ctx['user'],
            )
            path = review4d.normalize(
                '/Project/Dailies/',
                ctx['date'],
                filename,
            )
            return path

    def register():
        ...
        review4d.register_plugin(MyPathPreset)

Finally we can create a PostRender plugin to show the rendered file in windows explorer or finder.

    ...
    import sys
    import subprocess
 
    ...
    class ShowInFileBrowser(review4d.PostRender):
    
        label = 'Show in File Browser'
        enabled = True  # Enable the checkbox in the UI by default
 
        def is_available(self):
            # You can return False here if your plugin has some required resources 
            # that are unavailable. See the `review4d/plugins/shotgrid.py` for an example.
            return True
    
        def execute(self, render_path):
            if sys.platform == 'darwin':
                subprocess.run(['open', '-R', render_path])
            elif sys.platform == 'linux2':
                subprocess.run(['xdg-open', os.path.dirname(render_path)])
            elif sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', render_path.replace('/', '\\')])

## Contibuting
Contributions are welcome.

1. Fork this repository.
2. Make your changes.
3. Add tests to validate your changes.
4. Run tests. `c4dpy -m tests`
5. Create a pull request.
