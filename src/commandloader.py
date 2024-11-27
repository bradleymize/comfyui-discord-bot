import importlib
import inspect
import discord

def load_commands(package_root: str, bot: discord.Bot):
    all_classes = []

    # Load the root module for all the commands
    package = importlib.import_module(package_root)

    # Get all the members of the module (specifically __all__, populated by package's __init__.py)
    contents = inspect.getmembers(package, lambda x: not inspect.isroutine(x))
    all_modules = [list(c[1]) for c in contents if c[0] == "__all__"][0]

    for module in all_modules:
        module_name = f"{package_root}.{module}"
        # Dynamically import the command module
        package = importlib.import_module(module_name)
        contents = inspect.getmembers(package, lambda x: not inspect.isroutine(x))
        # Get all the classes belonging directly to the module
        classes = [c[1] for c in contents if inspect.isclass(c[1]) and c[1].__module__ == module_name]
        # Add the classes to the list of all the classes in the module
        all_classes = all_classes + classes

    for c in all_classes:
        c(bot).init()


def load_listeners(package_root: str, bot: discord.Bot):
    load_commands(package_root, bot)