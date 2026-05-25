import json
import time
import random
import asyncio
from typing import TYPE_CHECKING, Literal, Optional
from unrealircd_rpc_py.objects.Definition import LiveRPCResult, RPCErrorModel
from unrealircd_rpc_py.connections.live.ILiveConnection import ILiveConnection
from unrealircd_rpc_py.exceptions.rpc_exceptions import (
    RpcConnectionError, RpcUnixSocketFileNotFoundError
)
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from logging import Logger


class LiveUnixSocket(ILiveConnection):

    def __init__(self, debug_level: Literal[10, 20, 30, 40, 50] = 20):
        """Initiate live connection to unrealircd

        Args:
            debug_level (str, optional): NOTSET=0 | DEBUG=10 | INFO=20
                | WARN=30 | ERROR=40 | CRITICAL=50 - Default to 20
        """

        self.Logs: Logger = utils.start_log_system(
            "unrealircd-liverpc-py", debug_level
        )
        """Starting logger system"""

        self.request: str = ''
        self.connected: bool = True
        self.is_setup: bool = False

    def setup(self, params: dict) -> None:
        """Setup the Live connection

        Args:
            params (dict): _description_

        Raises:
            Exception: _description_
        """
        path_to_socket_file = params.get('path_to_socket_file', None)
        callback_object_instance = params.get(
            'callback_object_instance', None
        )
        callback_method_or_function_name = params.get(
            'callback_method_or_function_name', None
        )
        self.is_setup = True

        try:
            if utils.verify_unix_socket_file(path_to_socket_file):
                self.path_to_socket_file = path_to_socket_file
                self.to_run = getattr(
                    callback_object_instance, callback_method_or_function_name
                )
                self.Logs.debug(
                    "Connexion Established using Live UnixSocket!"
                )

        except AttributeError as atterr:
            self.Logs.error(f'CallbackMehtodError: {atterr}')
            raise

        except RpcUnixSocketFileNotFoundError as err:
            self.Logs.critical(f'RpcUnixSocketFileNotFoundError: {err}')
            raise

        self.connect()

    def connect(self) -> None:
        if not self.is_setup:
            raise RpcConnectionError(
                "You must setup the Live Connection "
                "before call connect method!", -1
            )

    async def subscribe(self, sources: Optional[list] = None
                        ) -> LiveRPCResult:
        """Subscribe to the rpc server stream
        sources exemple:
        \n ["!debug","all"] would give you all log messages except
        for debug messages
        see: https://www.unrealircd.org/docs/List_of_all_log_messages

        Args:
            sources (list, optional): The ressources you want to subscribe.
                Defaults to ["!debug","all"].
        """
        self.connected = True
        sources = ["!debug", "all"] if sources is None else sources
        response = await self.query(
            method='log.subscribe', param={"sources": sources}
        )
        return response

    async def unsubscribe(self) -> LiveRPCResult:
        """Run a del timer to trigger an event and then
        unsubscribe from the stream"""

        response = await self.query(method='log.unsubscribe')
        await self.query(
            method='log.send',
            param={
                "msg": "JSONRPC UnixSocket has been "
                       "disconnected from the stream!",
                "level": "info",
                "subsystem": "connect",
                "event_id": "REMOTE_CLIENT_DISCONNECT"
            }
        )

        return response

    async def query(self,
                    method: str,
                    param: Optional[dict] = None,
                    query_id: int = 123,
                    jsonrpc: str = '2.0'
                    ) -> LiveRPCResult:
        """This method will use to run the queries

        Args:
            method (str): The method to send to unrealircd
            param (dict, optional): the paramaters to send to unrealircd.
                Defaults to {}.
            query_id (int, optional): id of the request. Defaults to 123.
            jsonrpc (str, optional): jsonrpc. Defaults to '2.0'.

        Returns:
            str: The correct response
            None: no response from the server
            bool: False if there is an error occured
        """

        # data = '{"jsonrpc": "2.0", "method": "stats.get",
        # "params": {}, "id": 123}'
        get_method = method
        get_param = {} if param is None else param

        if query_id == 123:
            rand = random.randint(1, 6000)
            get_id = int(time.time()) + rand
        else:
            get_id = query_id

        response = {
            "jsonrpc": jsonrpc,
            "method": get_method,
            "params": get_param,
            "id": get_id
        }

        self.request = json.dumps(response)

        response = await self.send_to_method()

        return response

    async def send_to_method(self) -> LiveRPCResult:
        reader, writer = await asyncio.open_unix_connection(
            self.path_to_socket_file
        )
        try:
            if not self.request:
                return LiveRPCResult(result=False)

            # Sending the request
            writer.write(f'{self.request}\r\n'.encode())
            await writer.drain()

            # Get the method
            method = json.loads(self.request).get('method')

            # Init batch variable
            batch = b''
            final_response: LiveRPCResult = LiveRPCResult()

            while self.connected:
                # Recieve the data from the rpc server, decode it
                # and split it
                response = await reader.readline()
                if response[-1:] != b"\n":
                    # If END not recieved then fill the batch and go to next
                    # itteration
                    batch += response
                    continue
                else:
                    # The EOF is found, include current response to the batch
                    # and continue the code
                    batch += response

                # Decode and split the response
                response = batch.decode().split("\n")

                if method == 'log.unsubscribe':
                    self.connected = False
                    unsubscribe_response = {
                        "msg": "UnixSocket normal closure",
                        "level": "info",
                        "subsystem": "disconnect",
                        "event_id": "UNSUBSCRIBE_FROM_STREAM",
                        "timestamp": utils.get_timestamp(),
                        "log_source": "_"
                    }
                    final_response = LiveRPCResult(
                        method=method,
                        result=utils.dict_to_namespace(unsubscribe_response),
                        error=RPCErrorModel(
                            code=0, message="UnixSocket normal closure!"
                        )
                    )

                    # support callbacks async et sync
                    await self.to_run(final_response) if (
                        asyncio.iscoroutinefunction(self.to_run)
                    ) else self.to_run(final_response)
                    break

                for bdata in response:
                    if bdata:
                        decoded_response = json.loads(bdata)
                        error = decoded_response.get(
                            'error', RPCErrorModel().to_dict()
                        )
                        result = decoded_response.get('result', None)
                        response_method = decoded_response.get('method', None)
                        final_response = LiveRPCResult(
                            method=response_method,
                            error=RPCErrorModel(**error),
                            result=utils.dict_to_namespace(result)
                        )

                        # support callbacks async et sync
                        await self.to_run(final_response) if (
                            asyncio.iscoroutinefunction(self.to_run)
                        ) else self.to_run(final_response)

                # Clean batch variable
                batch = b''

            return final_response

        except AttributeError as attrerr:
            self.Logs.critical(f'AF_Unix Error: {attrerr}')
            error = LiveRPCResult(
                result=False,
                error=RPCErrorModel(code=-1, message=attrerr.__str__())
            )
            await self.to_run(error) if (
                asyncio.iscoroutinefunction(self.to_run)
            ) else self.to_run(error)
            return error

        except (TimeoutError, OSError, json.decoder.JSONDecodeError,
                TypeError, Exception) as err:
            self.Logs.critical(f'UnixSocket Error: {err}')
            error = LiveRPCResult(
                result=False,
                error=RPCErrorModel(code=-1, message=err.__str__())
            )
            await self.to_run(error) if (
                asyncio.iscoroutinefunction(self.to_run)
            ) else self.to_run(error)
            return error

        finally:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
