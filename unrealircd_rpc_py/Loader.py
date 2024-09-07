from typing import Union, Literal
from unrealircd_rpc_py.Connection import Connection
from unrealircd_rpc_py.User import User
from unrealircd_rpc_py.Stats import Stats
from unrealircd_rpc_py.Whowas import Whowas
from unrealircd_rpc_py.Server import Server
from unrealircd_rpc_py.Channel import Channel
from unrealircd_rpc_py.Server_ban import Server_ban
from unrealircd_rpc_py.Server_ban_exeption import Server_ban_exception
from unrealircd_rpc_py.Spamfilter import Spamfilter
from unrealircd_rpc_py.Name_ban import Name_ban
from unrealircd_rpc_py.Rpc import Rpc

class Loader:

    def __init__(self, url: str, endpoint: Union[Literal['api'], str], host: str, port: int, username: str, password: str,  req_method: Literal['requests', 'socket'] = 'requests') -> None:

        # Init the connection
        self.Connection = Connection(
            url=url,
            endpoint=endpoint,
            host=host,
            port=port,
            username=username,
            password=password,
            req_method=req_method,
            debug_level=10
        )

        # Create ErrorModel Instance
        self.Error = self.Connection.Error

        # Create User Instance
        self.User = User(self.Connection)

        # Create Server Instance
        self.Server = Server(self.Connection)

        # Create Server_ban Instance
        self.Server_ban = Server_ban(self.Connection)

        # Create Server_ban_exception Instance
        self.Server_ban_exception = Server_ban_exception(self.Connection)

        # Create Name_ban Instance
        self.Name_ban = Name_ban(self.Connection)

        # Create Rpc Instance
        self.Rpc = Rpc(self.Connection)

        # Create Spamfilter Instance
        self.Spamfilter = Spamfilter(self.Connection)

        # Create Channel Instance
        self.Channel = Channel(self.Connection)

        # Create Stats Instance
        self.Stats = Stats(self.Connection)

        # Create Whowas Instance
        self.Whowas = Whowas(self.Connection)