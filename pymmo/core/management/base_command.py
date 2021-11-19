import argparse
import sys


class CommandError(Exception):
    pass


class BaseCommand:
    registry = {}

    def __init__(self, prog):
        self.prog = prog
        self.description = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        module_name = cls.__module__.split('.')[-1]
        if module_name in BaseCommand.registry:
            raise CommandError(f'command {module_name} already registered')
        BaseCommand.registry[module_name] = cls

    def execute(self):
        parser = argparse.ArgumentParser(description=self.description, prog=self.prog)
        self.add_arguments(parser)
        args = parser.parse_args(sys.argv[2:])
        self.run(args)

    def run(self, args):
        raise NotImplementedError

    def add_arguments(self, parser):
        raise NotImplementedError
