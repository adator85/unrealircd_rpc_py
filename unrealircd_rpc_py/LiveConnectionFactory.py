"""
Docstring for unrealircd_rpc_py.connections.ConnectionFactory
"""
from unrealircd_rpc_py.exceptions.rpc_exceptions import RpcProtocolError
from unrealircd_rpc_py.connections.live.live_unixsocket import LiveUnixSocket
from unrealircd_rpc_py.connections.live.live_http import LiveWebsocket
from unrealircd_rpc_py.connections.live.ILiveConnection import ILiveConnection
from typing import Literal


class LiveConnectionFactory:

    def __init__(self, debug_level: int = 20):
        self.debug_level = debug_level

    def get(self, connection: Literal['unixsocket', 'http']
            ) -> ILiveConnection:
        match connection:
            case 'unixsocket':
                return LiveUnixSocket(self.debug_level)
            case 'http':
                return LiveWebsocket(self.debug_level)
            case _:
                raise RpcProtocolError('Invalid Live method!')
