from logging import Logger
from typing import Optional
from abc import ABC, abstractmethod
from unrealircd_rpc_py.objects.Channel import Channel
from unrealircd_rpc_py.objects.Log import Log
from unrealircd_rpc_py.objects.Name_ban import NameBan
from unrealircd_rpc_py.objects.Rpc import Rpc
from unrealircd_rpc_py.objects.Server import Server
from unrealircd_rpc_py.objects.Server_ban import ServerBan
from unrealircd_rpc_py.objects.Server_ban_exeption import ServerBanException
from unrealircd_rpc_py.objects.Spamfilter import Spamfilter
from unrealircd_rpc_py.objects.Stats import Stats
from unrealircd_rpc_py.objects.User import User
from unrealircd_rpc_py.objects.Whowas import Whowas
from unrealircd_rpc_py.objects.Message import Message
from unrealircd_rpc_py.objects.Connthrottle import ConnThrottle
from unrealircd_rpc_py.objects.Security_group import SecurityGroup


class IConnection(ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.Logs: Optional[Logger] = None
        self.unrealircd_version: Optional[tuple] = None

        # Create Stats Instance
        self.Stats: Stats = Stats(self)
        """The Stats module instance"""

        # Create Rpc Instance
        self.Rpc: Rpc = Rpc(self)
        """The Rpc module instance"""

        # Create Whowas Instance
        self.Whowas: Whowas = Whowas(self)
        """The Whowas module instance"""

        # Create Server_ban_exception Instance
        self.Server_ban_exception: ServerBanException = ServerBanException(
            self
        )
        """The ServerBanException module instance"""

        # Create Server_ban Instance
        self.Server_ban: ServerBan = ServerBan(self)
        """The ServerBan module instance"""

        # Create Server Instance
        self.Server: Server = Server(self)
        """The Server module instance"""

        # Create User Instance
        self.User: User = User(self)
        """The User module instance"""

        # Create Name_ban Instance
        self.Name_ban: NameBan = NameBan(self)
        """The Name_ban module instance"""

        # Create Channel Instance
        self.Channel: Channel = Channel(self)
        """The Channel module instance"""

        # Create Spamfilter Instance
        self.Spamfilter: Spamfilter = Spamfilter(self)
        """The Spamfilter module instance"""

        # Create Log Instance
        self.Log: Log = Log(self)
        """Allow you to subscribe and unsubscribe to log events
        (real-time streaming of JSON logs)
        (Requires unrealIRCd 6.1.8 or higher)"""

        # Create Message Instance
        self.Message: Message = Message(self)
        """Allow you to send a messages to users.
        (Require unrealIRCD 6.2.2 or higher)"""

        # Create Connthrottle Instance
        self.Connthrottle: ConnThrottle = ConnThrottle(self)
        """Allow you to control the Connthrottle module.
        (Require unrealIRCD 6.2.2 or higher)"""

        # Create Security Group Instance
        self.SecurityGroup: SecurityGroup = SecurityGroup(self)
        """Allow you to control the security group module.
        (Require unrealIRCD 6.2.2 or higher)"""

    @abstractmethod
    def setup(self, params: dict) -> None:
        """Setup the connection by providing credentials or
        The path to the socket file

        Exemple Method WebSocket (http):
        ```python
            {
                'url': 'https://your.rpc.link:PORT/api',
                'username': 'Your-rpc-username',
                'password': 'Your-rpc-password'
            }
        ```

        Exemple Method UnixSocket (unixsocket):
        ```python
            {
                'path_to_socket_file': '/path/to/unrealircd/data/rpc.socket'
            }
        ```
        Args:
            params (dict): The params

        Raises:
            RpcConnectionError: RCP Connection Error related to credentials.
            RpcSetupError: When Connect method is called before setup method.
            RpcInvalidUrlFormat: When the url format is not valid.
        """
        raise NotImplementedError()

    @abstractmethod
    def query(self,
              method: str,
              param: Optional[dict] = None,
              query_id: int = 123,
              jsonrpc: str = '2.0'
              ) -> Optional[dict]:
        """This method will use to run the queries

        Args:
            method (str): The method to send to unrealircd
            param (dict, optional): the paramaters to send to unrealircd.
                Defaults to None.
            query_id (int, optional): id of the request. Defaults to 123.
            jsonrpc (str, optional): jsonrpc. Defaults to '2.0'.

        Returns:
            dict: The response from the server
            None: no response from the server
        """
        raise NotImplementedError()

    @abstractmethod
    def get_response(self) -> Optional[dict]:
        """Get the response from the API call

        Returns:
            Optional[dict]: The response
        """
        raise NotImplementedError()
