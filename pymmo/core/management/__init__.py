# import argparse
import sys
import os.path
import pkgutil
from pymmo.core.management import commands
from importlib import import_module

from pymmo.core.management.base_command import BaseCommand


def load_commands():
    commands_package_path = os.path.dirname(commands.__file__)
    modules_names = [name for _, name, _ in pkgutil.iter_modules(path=[commands_package_path])]
    for module_name in modules_names:
        import_module(name=f'{commands.__package__}.{module_name}')

    # print(sys.argv)
    # print(BaseCommand.registry)


def run_command():
    load_commands()

    if len(sys.argv) < 2:
        subommands = "\n".join(BaseCommand.registry)
        print("\n"
              "Type 'pymmo-admin help <subcommand>' for help on a specific subcommand."
              "\n\n"
              "Available subcommands:"
              "\n"
              f"{subommands}")
        sys.exit(0)

    command_name = sys.argv[1]
    if command_name not in BaseCommand.registry:
        print("No PyMMO settings specified."
              "\n"
              f"Unknown command_name: '{command_name}'"
              "\n"
              "Type 'pymmo-admin help' for usage.",
              file=sys.stderr)
        sys.exit(1)

    command = BaseCommand.registry[command_name](prog=command_name)
    command.execute()

if __name__ == '__main__':
    run_command()
