"""
Docstring for unrealircd_rpc_py.connections.ConnectionFactory
"""
from unrealircd_rpc_py.exceptions.rpc_exceptions import RpcProtocolError
from unrealircd_rpc_py.connections.sync.unixsocket import UnixSocketConnection
from unrealircd_rpc_py.connections.sync.http import HttpConnection
from unrealircd_rpc_py.connections.sync.IConnection import IConnection
from typing import Literal


class ConnectionFactory:

    def __init__(self, debug_level: int = 20):
        self.debug_level = debug_level

    def get(self, connection: Literal['unixsocket', 'http']) -> IConnection:
        match connection:
            case 'unixsocket':
                return UnixSocketConnection(self.debug_level)
            case 'http':
                return HttpConnection(self.debug_level)
            case _:
                raise RpcProtocolError(
                    f'({connection}) is an invalid method! choose http '
                    f'or unixsocket instead!'
                )
