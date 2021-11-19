from collections import namedtuple

from pymmo.core.management.base_command import BaseCommand


AddrPort = namedtuple('AddrPort', ['addr', 'port'])


def addrport(value):
    addr, port = value.split(':')
    return AddrPort(addr=addr, port=int(port))


class JoinServerCommand(BaseCommand):
    description = 'Join game server.'

    def run(self, args):
        print('args', args)
        print('addrport', args.addrport)

    def add_arguments(self, parser):
        parser.add_argument('addrport', type=addrport, nargs=1, help='server addr:port')

