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
from unrealircd_rpc_py.Definition import RPCError

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

def start_log_system(debug_level: int = 20) -> logging.Logger:
    """Init log system
    """
    # Init logs object
    logger: logging.Logger = logging.getLogger('unrealircd-liverpc-py')
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
            callback_method_name (str): The callback method name
            url (str, optional): The full url to connect https://your.rpcjson.link:port/api.
            username (str, optional): Default to None
            password (str, optional): Default to None
            debug_level (str, optional): NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50 - Default to 20
        """

        self.Logs = start_log_system(debug_level)
        """Starting logger system"""

        self.EngineError = EngineError()
        """Engine Error: should be used to set errors"""

        self.url = url
        self.username = username
        self.password = password
        self.request: str = ''
        self.connected: bool = True
        self.__response: Optional[dict] = {}
        self.__response_np: Optional[SimpleNamespace] = SimpleNamespace()

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

    def subscribe(self, sources: Optional[list] = None):
        """Subscribe to the rpc server stream
        sources exemple:
        \n ["!debug","all"] would give you all log messages except for debug messages
        see: https://www.unrealircd.org/docs/List_of_all_log_messages
        Args:
            sources (list, optional): The ressources you want to subscribe. Defaults to ["!debug","all"].
        """
        sources = ["!debug", "all"] if sources is None else sources
        asyncio.run(self.query('log.subscribe', param={"sources": sources}))

    def unsubscribe(self):
        """Run a del timer to trigger an event and then unsubscribe from the stream
        """
        self.connected = False
        asyncio.run(
            self.query(method='rpc.del_timer', param={"timer_id": "timer_impossible_to_find_as_i_am_not_a_teapot"}))
        asyncio.run(self.query(method='log.unsubscribe'))

    async def query(self, method: Union[Literal['log.subscribe', 'log.unsubscribe'], str],
                    param: Optional[dict] = None, query_id: int = 123,
                    jsonrpc: str = '2.0'
                    ) -> Optional[dict]:
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

        await asyncio.gather(self.__send_websocket())

        if self.get_response() == '' or self.get_response() is None:
            return None

        return self.get_response()

    async def __send_websocket(self):
        """Connect using websockets"""
        try:

            # Build credentials
            api_login = f'{self.username}:{self.password}'
            credentials = base64.b64encode(api_login.encode()).decode()

            # Override headers
            headers = {
                'Authorization': f"Basic {credentials}"
            }

            # Create an SSL context for wss
            sslctx = ssl.create_default_context()
            sslctx.check_hostname = False
            sslctx.verify_mode = ssl.CERT_NONE

            ws_uri = f'wss://{self.host}:{self.port}/'

            async with client.connect(uri=ws_uri, additional_headers=headers, ssl=sslctx) as ws:
                await ws.send(self.request)
                while self.connected:
                    response = await ws.recv()
                    decoded_response = json.dumps(response)
                    self.__set_responses(json.loads(decoded_response))
                    self.to_run(self.get_response_np())

        except KeyError as ke:
            self.Logs.error(f"KeyError : {ke}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=ke.__str__())
        except InvalidURI as URIError:
            self.Logs.error(f"Invalid URI : {URIError}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'Invalid URI {URIError}')
        except InvalidHandshake as HandshakeError:
            self.Logs.critical(f"Handshake Error : {HandshakeError}")
            self.Logs.critical(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'InvalidHandshake: {HandshakeError}')
        except json.decoder.JSONDecodeError as jsonerror:
            self.Logs.error(f"jsonError {jsonerror}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'Json Error: {jsonerror}')
        except TimeoutError as te:
            self.Logs.error(f"Timeout Error {te}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'Timeout Error: {te}')
        except OSError as oe:
            self.Logs.error(f"OS Error {oe}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'OS Error: {oe}')
        except Exception as err:
            self.Logs.error(f"General Error {err}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'General Error: {err}')

    @property
    def get_error(self) -> RPCError:
        return self.EngineError.Error

    def __set_responses(self, response: str):
        """Set response as dict and as simple name space"""
        # Set dict response
        self.__response_np: Optional[SimpleNamespace] = None
        self.__response: Optional[dict] = None

        if not response:
            self.Logs.error(f"Impossible to load response: {response}")
            return

        self.__response = json.loads(response)

        if not isinstance(self.__response, dict):
            self.__response = None
            self.__response_np = None
            self.Logs.error(f"Impossible to load response: {response}")

        # Set response name space
        self.__response_np = dict_to_namespace(self.__response)

    def get_response_np(self) -> Optional[SimpleNamespace]:
        return self.__response_np

    def get_response(self) -> Optional[dict]:
        return self.__response


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
                callback_method_name='your_callback_methode_name',
                path_to_socket_file='/path/to/unrealircd/socket/your_socket.socket'
            )
        ```

        Args:
            callback_object_instance (object): The callback class instance (could be "self" if the class is in the same class)
            callback_method_name (str): The callback method name
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


    def subscribe(self, sources: Optional[list] = None):
        """Subscribe to the rpc server stream
        sources exemple:
        \n ["!debug","all"] would give you all log messages except for debug messages
        see: https://www.unrealircd.org/docs/List_of_all_log_messages
        Args:
            sources (list, optional): The ressources you want to subscribe. Defaults to ["!debug","all"].
        """
        sources = ["!debug", "all"] if sources is None else sources
        asyncio.run(self.query('log.subscribe', param={"sources": sources}))

    def unsubscribe(self):
        """Run a del timer to trigger an event and then unsubscribe from the stream
        """
        self.connected = False
        asyncio.run(
            self.query(method='rpc.del_timer', param={"timer_id": "timer_impossible_to_find_as_i_am_not_a_teapot"}))
        asyncio.run(self.query(method='log.unsubscribe'))

    async def query(self, method: Union[Literal['log.subscribe', 'log.unsubscribe'], str],
                    param: Optional[dict] = None, query_id: int = 123,
                    jsonrpc: str = '2.0'
                    ) -> Union[dict, None]:
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

        await asyncio.gather(self.__send_to_permanent_unixsocket())

        if self.get_response() == '' or self.get_response() is None:
            return None

        return self.get_response()

    async def __send_to_permanent_unixsocket(self):
        sock = socket.socket(socket.AddressFamily.AF_UNIX, socket.SocketKind.SOCK_STREAM)
        try:
            sock.connect(self.path_to_socket_file)

            if not self.request:
                return None

            sock.sendall(f'{self.request}\r\n'.encode())

            # Init batch variable
            batch = b''

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

                # Clean batch variable
                batch = b''

                for bdata in response:
                    if bdata:
                        self.__set_responses(bdata)
                        self.to_run(self.get_response_np())

        except AttributeError as attrerr:
            self.Logs.critical(f'AF_Unix Error: {attrerr}')
            self.EngineError.set_error(code=-1, message=f'AF_UnixError: {attrerr}')
        except TimeoutError as timeouterr:
            self.Logs.critical(f'Timeout Error: {timeouterr}')
            self.EngineError.set_error(code=-1, message=f'TimeoutError: {timeouterr}')
        except OSError as oserr:
            self.Logs.critical(f'OSError: {oserr}')
            self.EngineError.set_error(code=-1, message=f'OSError: {oserr}')
        except json.decoder.JSONDecodeError as jsondecoderror:
            self.Logs.critical(f'JSONDecodeError: {jsondecoderror}')
            self.EngineError.set_error(code=-1, message=f'JSONDecodeError: {jsondecoderror}')
        except Exception as err:
            self.Logs.error(f'General Error: {err}')
            self.EngineError.set_error(code=-1, message=f'GeneralError: {err}')
        finally:
            sock.close()

    @property
    def get_error(self) -> RPCError:
        return self.EngineError.Error

    def __set_responses(self, response: str):
        """Set response as dict and as simple name space"""
        # Set dict response
        self.__response_np: Optional[SimpleNamespace] = None
        self.__response: Optional[dict] = None

        if not response:
            self.Logs.error(f"Impossible to load response: {response}")
            return

        self.__response = json.loads(response)

        if not isinstance(self.__response, dict):
            self.__response = None
            self.__response_np = None
            self.Logs.error(f"Impossible to load response: {response}")

        # Set response name space
        self.__response_np = dict_to_namespace(self.__response)

    def get_response_np(self) -> Union[SimpleNamespace, None]:
        return self.__response_np

    def get_response(self) -> Union[dict, None]:
        return self.__response

