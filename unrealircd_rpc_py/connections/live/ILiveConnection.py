from logging import Logger
from typing import Optional
from abc import ABC, abstractmethod
import unrealircd_rpc_py.objects.Definition as Dfn

class ILiveConnection(ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.Logs: Logger

    @abstractmethod
    def setup(self, params: dict) -> None:
        """Setup the connection by providing credentials or The path to the socket file

        Args:
            params (dict): The params
        """
        pass

    @abstractmethod
    def connect(self) -> None:
        """_summary_
        """
        pass

    @abstractmethod
    def subscribe(self, sources: Optional[list] = None) -> Dfn.LiveRPCResult:
        """Subscribe to the rpc server stream"""
        pass

    @abstractmethod
    def unsubscribe(self) -> Dfn.LiveRPCResult:
        """Unsubscribe from the rpc server stream"""
        pass

    @abstractmethod
    def send_to_method(self) -> Dfn.LiveRPCResult:
        """Send to the methode"""
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
