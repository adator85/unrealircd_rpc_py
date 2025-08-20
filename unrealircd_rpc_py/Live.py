import json
import socket
import os
import base64
import ssl
import re
import time
import logging
import random
import asyncio
from typing import Literal, Union, Optional, Any
from types import SimpleNamespace
from websockets.asyncio import client
from websockets import InvalidURI, InvalidHandshake
from unrealircd_rpc_py.EngineError import EngineError, InvalidUrlFormat, UnixSocketFileNotFoundError
from unrealircd_rpc_py.Definition import RPCError, LiveRPCError, LiveRPCResult

def decompose_url(url: str) -> tuple[str, str, int]:
    """Check provided url if it follow the format
    and decompose it to host, endpoint and port

    >>> # If error it raises InvalidUrlFormat exception
    Args:
        url (str): Url to jsonrpc https://your.rpcjson.link:port/api

    Returns:
        tuple: Host, Endpoint, Port
    """
    if url is None or url == '':
        raise InvalidUrlFormat("The url provided is empty!")

    pattern = r'https?://([a-zA-Z0-9\.-]+):(\d+)/(.+)'

    match = re.match(pattern, url)

    if not match is None:
        host = match.group(1)
        port = match.group(2)
        endpoint = match.group(3)
        return host, endpoint, int(port)
    else:
        raise InvalidUrlFormat("You must provide the url in this format: https://your.rpcjson.link:port/api")

def dict_to_namespace(dictionary: Any) -> Union[SimpleNamespace, Any]:
    """Try to convert a dictionary to a SimpleNamespace object

    :param dictionary:
    :return: SimpleNamespace object or the object if it was impossible to convert
    """
    if isinstance(dictionary, dict):
        return SimpleNamespace(**{key: dict_to_namespace(value) for key, value in dictionary.items()})
    else:
        return dictionary

def verify_unix_socket_file(path_to_socket_file: str) -> bool:
    """Check provided full path to socket file if it exist

    Args:
        path_to_socket_file (str): Full path to unix socket file

    Returns:
        bool: True if path is correct else False
    """
    if path_to_socket_file is None or not os.path.exists(path_to_socket_file):
        raise UnixSocketFileNotFoundError("The socket file is not available, "
                                          "please check the full path of your socket file")

    return True

def remove_logger(logger_name: str) -> None:

    # Get the logger name
    logger = logging.getLogger(logger_name)

    # Delete handlers from the gestionary and close them
    for handler in logger.handlers[:]:  # Use a copy of the list
        # print(handler)
        logger.removeHandler(handler)
        handler.close()

    # Remove the logger from the dictionary
    logging.Logger.manager.loggerDict.pop(logger_name, None)

    return None

def start_log_system(debug_level: int = 20) -> logging.Logger:
    """Init log system
    """
    logger_name = 'unrealircd-liverpc-py'
    remove_logger(logger_name)

    # Init logs object
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(debug_level)

    # Add Handlers
    stdout_hanlder = logging.StreamHandler()
    stdout_hanlder.setLevel(debug_level)

    # Define log format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s (%(filename)s::%(funcName)s::%(lineno)d)')

    # Apply log format
    stdout_hanlder.setFormatter(formatter)

    # Add handler to logs
    logger.addHandler(stdout_hanlder)

    return logger

def convert_to_jsonrpc_result(result: Union[dict, Any]) -> LiveRPCResult:

    if not isinstance(result, dict):
        raise TypeError("Invalid jsonrpc response!")

    return LiveRPCResult(**result)

def convert_to_jsonrpc_error(error: Union[dict, Any]) -> LiveRPCError:

    if not isinstance(error, dict):
        raise TypeError("Invalid jsonrpc Error!")

    return LiveRPCError(**error)

class LiveWebsocket:

    def __init__(self,
                 url: str,
                 username: str,
                 password: str,
                 callback_object_instance: object,
                 callback_method_or_function_name: str,
                 debug_level: Literal[10, 20, 30, 40, 50] = 20
                 ):
        """Initiate live connection to unrealircd

            websocket:

            ```
            If you use websocket you must have:
                url: https://your.rpcjson.link:port/api
                username: API_RPC_USERNAME
                password: API_RPC_PASSWORD
            ```

            ## Exemples:
            If you want to use websocket you need to provide 6 parameters:
            ```python
                Live(
                    callback_object_instance=YourCallbackClass,
                    callback_method_name='your_callback_methode_name',
                    url='https://your.rpcjson.link:8600/api',
                    userame='API_RPC_USERNAME',
                    password='API_RPC_PASSWORD'
                )
            ```

            Args:
                callback_object_instance (object): The callback class instance (could be "self" if the class is in the same class)
                callback_method_or_function_name (str): The callback method name
                url (str, optional): The full url to connect https://your.rpcjson.link:port/api.
                username (str, optional): Default to None
                password (str, optional): Default to None
                debug_level (str, optional): NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50 - Default to 20
        """

        self.Logs = start_log_system(debug_level)
        self.EngineError = EngineError()

        self.url = url
        self.username = username
        self.password = password
        self.request: str = ''
        self.connected: bool = True

        self.EngineError.init_error()

        try:
            self.host, self.endpoint, self.port = decompose_url(url)
            self.to_run = getattr(callback_object_instance, callback_method_or_function_name)
            self.Logs.debug("Connexion Established using Live Websocket!")

        except AttributeError as atterr:
            self.EngineError.set_error(code=-1, message=f'CallbackMethodError: {atterr}')
            self.Logs.error(f'CallbackMehtodError: {atterr}')
            return

        except InvalidUrlFormat as iuf:
            self.EngineError.set_error(code=-1, message=iuf.__str__())
            self.Logs.critical(iuf)
            return

    # No more asyncio.run
    async def subscribe(self, sources: Optional[list] = None) -> dict[str, Any]:
        """Subscribe to the rpc server stream"""
        self.connected = True
        sources = ["!debug", "all"] if sources is None else sources
        response = await self.query('log.subscribe', param={"sources": sources})
        return response

    async def unsubscribe(self) -> dict[str, Any]:
        """Unsubscribe from the rpc server stream"""

        response = await self.query(method='log.unsubscribe')

        await self.query(method='log.send',
                         param={"msg": f"{self.username} JSONRPC User has been disconnected from the stream!",
                                "level": "info",
                                "subsystem": "connect",
                                "event_id": "REMOTE_CLIENT_DISCONNECT"}
                         )

        return response

    async def query(self, method: Union[Literal['log.subscribe', 'log.unsubscribe'], str],
                    param: Optional[dict] = None, query_id: int = 123,
                    jsonrpc: str = '2.0'
                    ) -> dict[str, Any]:

        get_param = {} if param is None else param
        get_id = int(time.time()) + random.randint(1, 6000) if query_id == 123 else query_id

        response = {
            "jsonrpc": jsonrpc,
            "method": method,
            "params": get_param,
            "id": get_id
        }

        self.request = json.dumps(response)

        response = await self.__send_websocket()

        return response

    async def __send_websocket(self) -> dict[str, Any]:
        """Connect using websockets"""
        try:
            api_login = f'{self.username}:{self.password}'
            credentials = base64.b64encode(api_login.encode()).decode()

            headers = {'Authorization': f"Basic {credentials}"}

            sslctx = ssl.create_default_context()
            sslctx.check_hostname = False
            sslctx.verify_mode = ssl.CERT_NONE

            ws_uri = f'wss://{self.host}:{self.port}/'
            method = json.loads(self.request).get('method')
            final_response: Optional[Union[LiveRPCResult, LiveRPCError]] = LiveRPCResult()

            async with client.connect(uri=ws_uri, additional_headers=headers, ssl=sslctx) as ws:
                await ws.send(self.request)
                while self.connected:
                    srv_response = await ws.recv()
                    decoded_response: dict[str, Any] = json.loads(json.loads(json.dumps(srv_response)))

                    if decoded_response.get('result', None):
                        final_response = convert_to_jsonrpc_result(decoded_response)

                    if decoded_response.get('error', None):
                        final_response = convert_to_jsonrpc_error(decoded_response)

                    if method == 'log.unsubscribe':
                        self.connected = False
                        final_response = LiveRPCError(error=RPCError(code=0, message="Websocket Normal Closure!"))

                    # support callbacks async et sync
                    result = self.to_run(dict_to_namespace(final_response.to_dict()))
                    if asyncio.iscoroutine(result):
                        await result

                    self.EngineError.init_error()

            return final_response.to_dict()

        except asyncio.CancelledError:
            self.Logs.info("Websocket task cancelled, closing connection")
            self.EngineError.set_error(code=-1, message='Websocket task cancelled!')
            error = LiveRPCError(error=RPCError(code=-1, message="Websocket task cancelled, closing connection")).to_dict()
            result = self.to_run(dict_to_namespace(error))
            if asyncio.iscoroutine(result):
                await result

            return LiveRPCError(error=RPCError(code=-1, message="Websocket task cancelled, closing connection")).to_dict()

        except AttributeError as ae:
            self.Logs.critical(f"Attribute Error: {ae.__str__()} Check your callback function or method")
            self.EngineError.set_error(code=-1, message='Attribute Error, Check your callback function or method!')
            return LiveRPCError(error=RPCError(code=-1, message=ae.__str__())).to_dict()

        except (KeyError, InvalidURI, InvalidHandshake, json.decoder.JSONDecodeError,
                TimeoutError, OSError, TypeError, Exception) as err:
            self.Logs.error(f"Websocket Error: {err}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'Websocket Error {err}')

            error = LiveRPCError(error=RPCError(code=-1, message=err)).to_dict()
            result = self.to_run(dict_to_namespace(error))
            if asyncio.iscoroutine(result):
                await result

            return error

    @property
    def get_error(self) -> RPCError:
        return self.EngineError.Error

class LiveUnixSocket:

    def __init__(self,
                 callback_object_instance: object,
                 callback_method_or_function_name: str,
                 path_to_socket_file: str = None,
                 debug_level: Literal[10, 20, 30, 40, 50] = 20
                 ):
        """Initiate live connection to unrealircd

        unixsocket:
        ```
        If you use unixsocket as req_method you must provide:
            path_to_socket_file
        ```

        ## Exemples:
        If you want to use unixsocket you need to provide 4 parameters:
        ```python
            Live(
                req_method='unixsocket',
                callback_object_instance=YourCallbackClass,
                callback_method_or_function_name='your_callback_methode_name',
                path_to_socket_file='/path/to/unrealircd/socket/your_socket.socket'
            )
        ```

        Args:
            callback_object_instance (object): The callback class instance (could be "self" if the class is in the same class)
            callback_method_or_function_name (str): The callback method name
            path_to_socket_file (str, optional): The full path to your unix socket file
            debug_level (str, optional): NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50 - Default to 20
        """

        self.Logs = start_log_system(debug_level)
        """Starting logger system"""

        self.EngineError = EngineError()
        """Engine Error: should be used to set errors"""

        self.request: str = ''
        self.connected: bool = True
        self.__response: Optional[dict] = {}
        self.__response_np: Optional[SimpleNamespace] = SimpleNamespace()

        try:
            if verify_unix_socket_file(path_to_socket_file):
                self.path_to_socket_file = path_to_socket_file
                self.to_run = getattr(callback_object_instance, callback_method_or_function_name)
                self.Logs.debug("Connexion Established using Live UnixSocket!")

        except AttributeError as atterr:
            self.EngineError.set_error(code=-1, message=f'CallbackMethodError: {atterr}')
            self.Logs.error(f'CallbackMehtodError: {atterr}')
            return

        except UnixSocketFileNotFoundError as err:
            self.EngineError.set_error(code=-1, message=err.__str__())
            self.Logs.critical(f'UnixSocketFileNotFoundError: {err}')
            return


    async def subscribe(self, sources: Optional[list] = None) -> dict[str, Any]:
        """Subscribe to the rpc server stream
        sources exemple:
        \n ["!debug","all"] would give you all log messages except for debug messages
        see: https://www.unrealircd.org/docs/List_of_all_log_messages

        Args:
            sources (list, optional): The ressources you want to subscribe. Defaults to ["!debug","all"].
        """
        self.connected = True
        sources = ["!debug", "all"] if sources is None else sources
        response = await self.query(method='log.subscribe', param={"sources": sources})
        return response

    async def unsubscribe(self) -> dict[str, Any]:
        """Run a del timer to trigger an event and then unsubscribe from the stream
        """
        response = await self.query(method='log.unsubscribe')
        await self.query(method='log.send',
                         param={"msg": f"JSONRPC UnixSocket has been disconnected from the stream!",
                                "level": "info",
                                "subsystem": "connect",
                                "event_id": "REMOTE_CLIENT_DISCONNECT"}
                         )

        return response

    async def query(self, method: Union[Literal['log.subscribe', 'log.unsubscribe'], str],
                    param: Optional[dict] = None, query_id: int = 123,
                    jsonrpc: str = '2.0'
                    ) -> dict[str, Any]:
        """This method will use to run the queries

        Args:
            method (Union[Literal[&#39;stats.get&#39;, &#39;rpc.info&#39;,&#39;user.list&#39;], str]): The method to send to unrealircd
            param (dict, optional): the paramaters to send to unrealircd. Defaults to {}.
            query_id (int, optional): id of the request. Defaults to 123.
            jsonrpc (str, optional): jsonrpc. Defaults to '2.0'.

        Returns:
            str: The correct response
            None: no response from the server
            bool: False if there is an error occured
        """

        # data = '{"jsonrpc": "2.0", "method": "stats.get", "params": {}, "id": 123}'
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

        response = await self.__send_to_permanent_unixsocket()

        return response

    async def __send_to_permanent_unixsocket(self) -> dict[str, Any]:
        sock = socket.socket(socket.AddressFamily.AF_UNIX, socket.SocketKind.SOCK_STREAM)
        try:
            sock.connect(self.path_to_socket_file)

            if not self.request:
                return {}

            # Sending the request
            sock.sendall(f'{self.request}\r\n'.encode())

            # Get the method
            method = json.loads(self.request).get('method')

            # Init batch variable
            batch = b''
            final_response: Optional[Union[LiveRPCResult, LiveRPCError]] = LiveRPCResult()

            while self.connected:
                # Recieve the data from the rpc server, decode it and split it
                response = sock.recv(4096)
                if response[-1:] != b"\n":
                    # If END not recieved then fill the batch and go to next itteration
                    batch += response
                    continue
                else:
                    # The EOF is found, include current response to the batch and continue the code
                    batch += response

                # Decode and split the response
                response = batch.decode().split("\n")

                if method == 'log.unsubscribe':
                    self.connected = False
                    final_response = LiveRPCError(error=RPCError(code=0, message="Websocket Normal Closure!"))

                    # support callbacks async et sync
                    result = self.to_run(dict_to_namespace(final_response.to_dict()))
                    if asyncio.iscoroutine(result):
                        await result

                    break

                for bdata in response:
                    if bdata:
                        decoded_response = json.loads(bdata)

                        if decoded_response.get('result', None):
                            final_response = convert_to_jsonrpc_result(decoded_response)
                        elif decoded_response.get('error', None):
                            final_response = convert_to_jsonrpc_error(decoded_response)

                        # support callbacks async et sync
                        result = self.to_run(dict_to_namespace(final_response.to_dict()))
                        if asyncio.iscoroutine(result):
                            await result

                # Clean batch variable
                batch = b''

                # Clean error
                self.EngineError.init_error()

            return final_response.to_dict()

        except AttributeError as attrerr:
            self.Logs.critical(f'AF_Unix Error: {attrerr}')
            self.EngineError.set_error(code=-1, message=f'AF_UnixError: {attrerr}')

            error = LiveRPCError(error=RPCError(code=-1, message=attrerr.__str__())).to_dict()
            result = self.to_run(dict_to_namespace(error))
            if asyncio.iscoroutine(result):
                await result

            return error
        except (TimeoutError, OSError, json.decoder.JSONDecodeError, TypeError, Exception) as err:
            self.Logs.critical(f'UnixSocket Error: {err}')
            self.EngineError.set_error(code=-1, message=f'UnixSocket Error: {err}')

            error = LiveRPCError(error=RPCError(code=-1, message=err)).to_dict()
            result = self.to_run(dict_to_namespace(error))
            if asyncio.iscoroutine(result):
                await result

            return error
        finally:
            sock.close()

    @property
    def get_error(self) -> RPCError:
        return self.EngineError.Error
