# review4d
A library and plugin for cinema4D allowing users to render previews to preset locations and perform actions after the render completes.

## Installation
You can use git to install this plugin by cloning it into your c4d plugins
directory.

Alternatively you can download a zip of this repo and extract it into your
c4d plugins directory.

## Usage
Use the **Render for Review** command in the Extensions menu to pull up the
render dialog.

img1 img2

Adjust the settings in the dialog. Review4d will add new render settings called **Review Settings** to your scene. You can use the **Edit Review Settings** button to edit the viewport settings in the Render Settings window.

img3

If you have ShotGrid toolkit and the accompanying tk-cinema app running in your Cinema4D session you can enable the **Upload to ShotGrid** checkbox. After the render finishes a dialog will appear to let you upload it to ShotGrid.

img4

## Plugins
review4d allows customization through the use of plugins. Create a python file and place it in the plugins folder. Subclass one of the plugin types like PathPreset or ContextCollector and register them in a module level register function.

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


## Contibuting
Contributions are welcome.

1. Fork this repository.
2. Make your changes.
3. Add tests.
4. Run tests. **c4dpy -m tests**
5. Create a pull request.
