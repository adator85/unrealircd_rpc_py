from logging import Logger
from typing import Optional
from abc import ABC, abstractmethod
import unrealircd_rpc_py.objects.Definition as Dfn
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

class IConnection(ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.Logs: Logger

        # Create Stats Instance
        self.Stats: Stats = Stats(self)
        """The Stats module instance"""

        # Create Rpc Instance
        self.Rpc: Rpc = Rpc(self)
        """The Rpc module instance"""

        # Create Log Instance
        self.Log: Log = Log(self)
        """This include mainly send method requires unrealIRCd 6.1.8 or higher"""

        # Create Whowas Instance
        self.Whowas: Whowas = Whowas(self)
        """The Whowas module instance"""

        # Create Server_ban_exception Instance
        self.Server_ban_exception: ServerBanException = ServerBanException(self)
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

    @abstractmethod
    def setup(self, params: dict) -> Optional[Dfn.RPCResult]:
        """Setup the connection by providing credentials or The path to the socket file

        Args:
            params (dict): The params
        """
        pass

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
            param (dict, optional): the paramaters to send to unrealircd. Defaults to None.
            query_id (int, optional): id of the request. Defaults to 123.
            jsonrpc (str, optional): jsonrpc. Defaults to '2.0'.

        Returns:
            dict: The response from the server
            None: no response from the server
        """
        pass

    @abstractmethod
    def get_response(self) -> Optional[dict]:
        """Get the response from the API call

        Returns:
            Optional[dict]: The response
        """
        pass
