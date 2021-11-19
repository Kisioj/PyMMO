import argparse
import sys

from pymmo.core.management.base_command import BaseCommand


class RunServerCommand(BaseCommand):
    description = 'Run game server.'

    def run(self, args):
        print('args', args)
        print('port', args.port)

    def add_arguments(self, parser):
        parser.add_argument('port', type=int, nargs='?', help='optional port number', default=7000)
