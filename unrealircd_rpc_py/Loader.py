from typing import Literal
from unrealircd_rpc_py.Connection import Connection
from unrealircd_rpc_py.Definition import RPCError
from unrealircd_rpc_py.User import User
from unrealircd_rpc_py.Stats import Stats
from unrealircd_rpc_py.Whowas import Whowas
from unrealircd_rpc_py.Server import Server
from unrealircd_rpc_py.Channel import Channel
from unrealircd_rpc_py.Server_ban import ServerBan
from unrealircd_rpc_py.Server_ban_exeption import ServerBanException
from unrealircd_rpc_py.Spamfilter import Spamfilter
from unrealircd_rpc_py.Name_ban import NameBan
from unrealircd_rpc_py.Rpc import Rpc
from unrealircd_rpc_py.Log import Log

class Loader:

    def __init__(self, req_method: Literal['requests', 'socket', 'unixsocket'], 
                 url: str = None, 
                 path_to_socket_file: str = None, 
                 username: str = None, 
                 password: str = None, 
                 debug_level: Literal[10, 20, 30, 40, 50] = 20
                 ) -> None:
        """Initiate connection to unrealircd

        requests and socket:
        If you use request or socket as req_method you must provide:
            \n url, username and password

        unixsocket:
        If you use request or socket as req_method you must provide:
            \n path_to_socket_file: /path/to/unrealircd/socket/your_socket.socket

        ## Exemples:
        If you want to use unix socket you need to provide 2 parameters:
            \n Loader(
                req_method='unixsocket',
                path_to_socket_file='/path/to/unrealircd/socket/your_socket.socket'
                )

        If you want to use remote connexion you need to provide 4 parameters:
            \n Loader(
                req_method='requests',
                url='https://your.rpcjson.link:port/api',
                username='readonly',
                password='azerty'
                )

        Args:
            req_method (str): The method you want to use, 3 options are available requests | socket | unixsocket
            url (str, optional): The full url to connect https://your.rpcjson.link:port/api.
            path_to_socket_file (str, optional): The full path to your unix socket file
            username (str, optional): Default to None 
            password (str, optional): Default to None 
            debug_level (str, optional): NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50 - Default to 20 
        """
        self.Connection = Connection(
            url=url,
            path_to_socket_file=path_to_socket_file,
            username=username,
            password=password,
            req_method=req_method,
            debug_level=debug_level
        )

        # Create User Instance
        self.User: User = User(self.Connection)
        """The User module instance"""

        # Create Server Instance
        self.Server: Server = Server(self.Connection)
        """The Server module instance"""

        # Create Server_ban Instance
        self.Server_ban: ServerBan = ServerBan(self.Connection)
        """The ServerBan module instance"""

        # Create Server_ban_exception Instance
        self.Server_ban_exception: ServerBanException = ServerBanException(self.Connection)
        """The ServerBanException module instance"""

        # Create Name_ban Instance
        self.Name_ban: NameBan = NameBan(self.Connection)
        """The Name_ban module instance"""

        # Create Rpc Instance
        self.Rpc: Rpc = Rpc(self.Connection)
        """The Rpc module instance"""

        # Create Spamfilter Instance
        self.Spamfilter: Spamfilter = Spamfilter(self.Connection)
        """The Spamfilter module instance"""

        # Create Channel Instance
        self.Channel: Channel = Channel(self.Connection)
        """The Channel module instance"""

        # Create Stats Instance
        self.Stats: Stats = Stats(self.Connection)
        """The Stats module instance"""

        # Create Whowas Instance
        self.Whowas: Whowas = Whowas(self.Connection)
        """The Whowas module instance"""

        # Create Log Instance
        self.Log: Log = Log(self.Connection)
        """This include mainly send method requires unrealIRCd 6.1.8 or higher"""

    @property
    def get_error(self) -> RPCError:
        return self.Connection.Error