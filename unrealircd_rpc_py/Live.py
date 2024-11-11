import json.scanner
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
from typing import Literal, Union
from types import SimpleNamespace
from websockets.asyncio import client
from websockets import InvalidURI, InvalidHandshake
from unrealircd_rpc_py.EngineError import EngineError

class Live:

    def __init__(self, req_method: Literal['unixsocket', 'websocket'], 
                 callback_object_instance: object, 
                 callback_method_name: str, 
                 url: str = None,
                 username: str = None,
                 password: str = None,
                 path_to_socket_file: str = None, 
                 debug_level: Literal[10, 20, 30, 40, 50] = 20
                 ) -> None:
        """Initiate live connection to unrealircd

        unixsocket:
        ```
        If you use unixsocket as req_method you must provide:
            path_to_socket_file
        ```

        websocket:
        ```
        If you use websocket as req_method you must provide:
            url: https://your.rpcjson.link:port/api
            username: API_RPC_USERNAME
            password: API_RPC_PASSWORD
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

        If you want to use websocket you need to provide 5 parameters:
        ```python
            Live(
                req_method='websocket',
                callback_object_instance=YourCallbackClass,
                callback_method_name='your_callback_methode_name',
                url='https://your.rpcjson.link:8600/api',
                userame='API_RPC_USERNAME',
                password='API_RPC_PASSWORD'
            )
        ```

        Args:
            req_method (str): The method you want to use, 2 options are available [unixsocket | websocket]
            callback_object_instance (object): The callback class instance (could be "self" if the class is in the same class)
            callback_method_name (str): The callback method name
            url (str, optional): The full url to connect https://your.rpcjson.link:port/api.
            path_to_socket_file (str, optional): The full path to your unix socket file
            username (str, optional): Default to None 
            password (str, optional): Default to None 
            debug_level (str, optional): NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50 - Default to 20 
        """

        self.debug_level = debug_level
        self.Logs: logging
        self.__init_log_system()

        self.EngineError = EngineError()
        """Engine Error: should be used to set errors"""
        self.Error = self.EngineError.Error
        """Error attribut: to be used to print errors"""

        self.req_method = req_method
        self.url = url
        self.username = username
        self.password = password

        if req_method == 'unixsocket' and not self.__check_unix_socket_file(path_to_socket_file):
            self.Logs.critical(f'The socket file is not available, please check the full path of your socket file')
            self.EngineError.set_error(
                code=-1,
                message='The socket file is not available, please check the full path of your socket file'
                )
            return None

        if req_method == 'websocket' and not self.__check_url(url):
            self.Logs.critical(f'You must provide the url in this format: https://your.rpcjson.link:port/api')
            self.EngineError.set_error(
                code=-1,
                message='You must provide the url in this format: https://your.rpcjson.link:port/api'
                )
            return None

        self.to_run = getattr(callback_object_instance, callback_method_name)

        self.path_to_socket_file = path_to_socket_file

        self.request: str = ''
        self.str_response = ''
        self.json_response = ''

        self.connected: bool = True

        # Option 2 with Namespaces
        self.json_response_np: SimpleNamespace

    def __check_unix_socket_file(self, path_to_socket_file: str) -> bool:
        """Check provided full path to socket file if it exist

        Args:
            path_to_socket_file (str): Full path to unix socket file

        Returns:
            bool: True if path is correct else False
        """
        try:
            response = False

            if path_to_socket_file is None:
                return response
            
            if not os.path.exists(path_to_socket_file):
                return response

            response = True

            return response
        except NameError as nameerr:
            self.Logs.critical(f'NameError: {nameerr}')

    def __check_url(self, url: str) -> bool:
        """Check provided url if it follow the format

        Args:
            url (str): Url to jsonrpc https://your.rpcjson.link:port/api

        Returns:
            bool: True if url is correct else False
        """
        try:
            response = False

            if url is None:
                return response

            pattern = r'https?://([a-zA-Z0-9\.-]+):(\d+)/(.+)'

            match = re.match(pattern, url)

            if not match is None:
                self.host = match.group(1)
                self.port = match.group(2)
                self.endpoint = match.group(3)
                response = True
            else:
                self.EngineError.set_error(
                    code=-1,
                    message='You must provide the url in this format: https://your.rpcjson.link:port/api'
                )

            return response
        except NameError as nameerr:
            self.Logs.critical(f'NameError: {nameerr}')

    async def __send_to_permanent_unixsocket(self):
        try:
            self.json_response = None
            self.json_response_np: SimpleNamespace = None

            sock = socket.socket(socket.AddressFamily.AF_UNIX, socket.SocketKind.SOCK_STREAM)
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
                        self.json_response = json.loads(bdata)
                        self.json_response_np: SimpleNamespace = json.loads(bdata, object_hook=lambda d: SimpleNamespace(**d))
                        self.to_run(self.json_response_np)

            sock.close()

        except AttributeError as attrerr:
            self.Logs.critical(f'AF_Unix Error: {attrerr}')
        except TimeoutError as timeouterr:
            self.Logs.critical(f'Timeout Error: {timeouterr}')
        except OSError as oserr:
            self.Logs.critical(f'System Error: {oserr}')
        except json.decoder.JSONDecodeError as jsondecoderror:
            self.Logs.critical(f'Json Decod Error: {jsondecoderror}')
        except Exception as err:
            self.Logs.error(f'General Error: {err}')

    async def __send_websocket(self):
        """Connect using websockets"""
        try:
            if not self.__check_url(self.url) and not self.url is None:
                self.Logs.critical('You must provide the url in this format: https://your.rpcjson.link:port/api')
                return None

            # Build credentials
            api_login = f'{self.username}:{self.password}'
            credentials = base64.b64encode(api_login.encode()).decode()

            # Override headers
            headers = {
                'Authorization' : f"Basic {credentials}"
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

                    decodedResponse = json.dumps(response)

                    self.str_response = decodedResponse
                    self.json_response = json.loads(json.loads(decodedResponse))
                    self.json_response_np: SimpleNamespace = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
                    self.to_run(self.json_response_np)

        except KeyError as ke:
            self.Logs.error(f"KeyError : {ke}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=ke)
        except InvalidURI as URIError:
            self.Logs.error(f"Invalid URI : {URIError}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'Invalid URI {URIError}')
        except InvalidHandshake as HandshakeError:
            self.Logs.critical(f"Handshake Error : {HandshakeError}")
            self.Logs.critical(f"Initial request: {self.request}")
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

    def __init_log_system(self) -> None:
        """Init log system
        """
        # Init logs object
        self.Logs: logging.Logger = logging.getLogger('unrealircd-liverpc-py')
        self.Logs.setLevel(self.debug_level)

        # Add Handlers
        stdout_hanlder = logging.StreamHandler()
        stdout_hanlder.setLevel(self.debug_level)

        # Define log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(funcName)s - %(message)s')

        # Apply log format
        stdout_hanlder.setFormatter(formatter)

        # Add handler to logs
        self.Logs.addHandler(stdout_hanlder)

    def subscribe(self, sources: list = ["!debug", "all"]):
        """Subscribe to the rpc server stream
        param exemple: 
        \n ["!debug","all"] would give you all log messages except for debug messages
        see: https://www.unrealircd.org/docs/List_of_all_log_messages
        Args:
            param (list, optional): The ressources you want to subscribe. Defaults to ["!debug","all"].
        """
        asyncio.run(self.query('log.subscribe', param={"sources": sources}))

    def unsubscribe(self):
        """Run a del timer to trigger an event and then unsubscribe from the stream
        """
        self.connected = False
        asyncio.run(self.query(method='rpc.del_timer', param={"timer_id":"timer_impossible_to_find_as_i_am_not_a_teapot"}))
        asyncio.run(self.query(method='log.unsubscribe'))

    async def query(self, method: Union[Literal['log.subscribe', 'log.unsubscribe'], str], param: dict = {}, id: int = 123, jsonrpc:str = '2.0') -> Union[str, any, None, bool]:
        """This method will use to run the queries

        Args:
            method (Union[Literal[&#39;stats.get&#39;, &#39;rpc.info&#39;,&#39;user.list&#39;], str]): The method to send to unrealircd
            param (dict, optional): the paramaters to send to unrealircd. Defaults to {}.
            id (int, optional): id of the request. Defaults to 123.
            jsonrpc (str, optional): jsonrpc. Defaults to '2.0'.

        Returns:
            str: The correct response
            None: no response from the server
            bool: False if there is an error occured
        """

        # data = '{"jsonrpc": "2.0", "method": "stats.get", "params": {}, "id": 123}'
        get_method = method
        get_param = param

        if id == 123:
            rand = random.randint(1, 6000)
            get_id = int(time.time()) + rand

        else:
            get_id = id

        response = {
            "jsonrpc": jsonrpc,
            "method": get_method,
            "params": get_param,
            "id": get_id
        }

        self.request = json.dumps(response)

        if self.req_method == 'unixsocket':
            await asyncio.gather(self.__send_to_permanent_unixsocket())
        elif self.req_method == 'websocket':
            await asyncio.gather(self.__send_websocket())
        else:
            self.Logs.error('No valid request method')
            self.EngineError.set_error(code=-1, message='<< Invalid Live method >>')

        if self.json_response == '' or self.json_response is None:
            return None

        return self.json_response

    def set_error(self, json_error: dict):
        """set the error

        Args:
            code (int): the error code
            message (str): the message of the error
        """
        try:
            if 'error' in json_error:
                self.Error.code=json_error['error']['code']
                self.Error.message=json_error['error']['message']

        except KeyError as ke:
            self.Logs.error(ke)
        except Exception as err:
            self.Logs.error(err)
