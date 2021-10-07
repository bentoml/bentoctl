import click
from bcdt.plugin_mng import add_plugin, list_plugins, install_plugin


def get_plugin_management_subcommands():
    @click.group(name="plugins")
    def plugin_management():
        """
        Commands to manage the various plugins.
        """
        pass

    @plugin_management.command()
    def list():
        """
        List all the available plugins.
        """
        list_plugins()

    @plugin_management.command()
    @click.argument('name', type=click.STRING)
    def add(name):
        """
        Add plugins.
        """
        add_plugin(name)

    @plugin_management.command()
    @click.argument('plugin-path', type=click.Path(exists=True))
    def install(plugin_path):
        """
        Install a plugin ie. add it to the plugin_list.json
        """
        install_plugin(plugin_path)

    @plugin_management.command()
    def remove():
        """
        Remove plugins.
        """
        print("removing plugin")

    return plugin_management
