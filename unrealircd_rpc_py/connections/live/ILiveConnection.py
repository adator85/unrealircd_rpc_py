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
        """Setup the connection by providing credentials or The path to the
        socket file

        Exemple Method WebSocket (http):
        ```python
            {
                'url': 'https://your.rpc.link:PORT/api',
                'username': 'Your-rpc-username',
                'password': 'Your-rpc-password',
                'callback_object_instance' : THE_CLASS_INSTANCE,
                'callback_method_or_function_name': 'callback_method_name'
            }
        ```

        Exemple Method UnixSocket (unixsocket):
        ```python
            {
                'path_to_socket_file': '/path/to/unrealircd/data/rpc.socket',
                'callback_object_instance' : THE_CLASS_INSTANCE,
                'callback_method_or_function_name': 'callback_method_name'
            }
        ```
        Args:
            params (dict): The params

        Raises:
            RpcConnectionError: RCP Connection Error related to credentials.
            RpcInvalidUrlFormat: Invalid url.
            RpcSetupError: When connect method is called before setup method.
        """
        raise NotImplementedError()

    @abstractmethod
    def connect(self) -> None:
        """Perform some actions to simulate connection.
        """
        raise NotImplementedError()

    @abstractmethod
    async def subscribe(self, sources: Optional[list] = None
                        ) -> Dfn.LiveRPCResult:
        """Subscribe to the rpc server stream"""
        raise NotImplementedError()

    @abstractmethod
    async def unsubscribe(self) -> Dfn.LiveRPCResult:
        """Unsubscribe from the rpc server stream"""
        raise NotImplementedError()

    @abstractmethod
    async def send_to_method(self) -> Dfn.LiveRPCResult:
        """Send to the methode"""
        raise NotImplementedError()

    @abstractmethod
    async def query(self,
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
