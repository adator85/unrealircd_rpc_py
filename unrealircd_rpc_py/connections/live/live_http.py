import json
import base64
import ssl
import time
import random
import asyncio
import requests
import urllib3
from typing import TYPE_CHECKING, Literal, Union, Optional, Any
from requests.auth import HTTPBasicAuth
from websockets.asyncio import client
from websockets import InvalidURI, InvalidHandshake
from unrealircd_rpc_py.objects.Definition import LiveRPCResult, RPCErrorModel
from unrealircd_rpc_py.connections.live.ILiveConnection import ILiveConnection
from unrealircd_rpc_py.connections.exceptions.rpc_exceptions import RpcConnectionError, RpcInvalidUrlFormat
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from logging import Logger

class LiveWebsocket(ILiveConnection):

    def __init__(self, debug_level: Literal[10, 20, 30, 40, 50] = 20):
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

        self.Logs: 'Logger' = utils.start_log_system('unrealircd-liverpc-py', debug_level)
        self.url = ''
        self.username = ''
        self.password = ''
        self.request: str = ''
        self.connected: bool = True

    def setup(self, params: dict) -> None:
        self.url = params.get('url', None)
        self.username = params.get('username', None)
        self.password = params.get('password', None)
        callback_object_instance = params.get('callback_object_instance', None)
        callback_method_or_function_name = params.get('callback_method_or_function_name', None)
        self.is_setup = True

        test = self.establish_first_connection()
        if test.error.code != 0:
            self.Logs.error(f"Connexion failed to the server: {test.error.message} ({test.error.code})")
            raise Exception(f"{test.error.message} ({test.error.code})")

        try:
            self.host, self.endpoint, self.port = utils.decompose_url(self.url)
            self.to_run = getattr(callback_object_instance, callback_method_or_function_name)
            self.Logs.debug("Connexion Established using Live Websocket!")

        except AttributeError as atterr:
            self.Logs.error(f'CallbackMehtodError: {atterr}')
            raise Exception(f'CallbackMehtodError: {atterr}')

        except RpcInvalidUrlFormat as iuf:
            self.Logs.critical(iuf)
            raise Exception(f'RpcInvalidUrlFormat: {iuf}')

        self.connect()

    def connect(self) -> None:
        if not self.is_setup:
            raise RpcConnectionError("You must setup the Live Connection before call connect method!", -1)

    def establish_first_connection(self) -> LiveRPCResult:
        if not self.is_setup:
            self.Logs.critical('You must call "setup" method before anything.')
            return None

        url_info = utils.check_url(self.url)

        if url_info is None:
            self.Logs.critical('You must provide the url in this format: https://your.rpcjson.link:port/api')
            return None

        verify = False
        url: Optional[str] = self.url

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        credentials = HTTPBasicAuth(self.username, self.password)
        response = requests.get(url=url, auth=credentials, verify=verify)
        
        if response.status_code >= 300:
            return LiveRPCResult(error=RPCErrorModel(response.status_code, response.text.strip()))
        else:
            return LiveRPCResult()

    async def subscribe(self, sources: Optional[list] = None) -> LiveRPCResult:
        """Subscribe to the rpc server stream"""
        self.connected = True
        sources = ["!debug", "all"] if sources is None else sources
        response = await self.query('log.subscribe', param={"sources": sources})
        print(f"First Subscribe response: {response}")
        if response.method is None:
            response.method = 'log.subscribe'

        return response

    async def unsubscribe(self) -> LiveRPCResult:
        """Unsubscribe from the rpc server stream"""

        response = await self.query(method='log.unsubscribe')

        await self.query(method='log.send',
                         param={"msg": f"{self.username} JSONRPC User has been disconnected from the stream!",
                                "level": "info",
                                "subsystem": "connect",
                                "event_id": "REMOTE_CLIENT_DISCONNECT"}
                         )
        
        if response.method is None:
            response.method = 'log.unsubscribe'

        return response

    async def query(self, method: Union[Literal['log.subscribe', 'log.unsubscribe'], str],
                    param: Optional[dict] = None, query_id: int = 123,
                    jsonrpc: str = '2.0'
                    ) -> LiveRPCResult:

        get_param = {} if param is None else param
        get_id = int(time.time()) + random.randint(1, 6000) if query_id == 123 else query_id

        response = {
            "jsonrpc": jsonrpc,
            "method": method,
            "params": get_param,
            "id": get_id
        }

        self.request = json.dumps(response)

        response = await self.send_to_method()

        return response

    async def send_to_method(self) -> LiveRPCResult:
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
            final_response: LiveRPCResult = LiveRPCResult()

            async with client.connect(uri=ws_uri, additional_headers=headers, ssl=sslctx) as ws:
                await ws.send(self.request)
                while self.connected:
                    srv_response = await ws.recv()
                    decoded_response: dict[str, Any] = json.loads(json.loads(json.dumps(srv_response)))
                    error = decoded_response.get('error', RPCErrorModel().to_dict())
                    response_method = decoded_response.get('method', None)
                    result = decoded_response.get('result', None)
                    final_response = LiveRPCResult(method=response_method, error=RPCErrorModel(**error), result=utils.dict_to_namespace(result))

                    if method == 'log.unsubscribe':
                        self.connected = False
                        unsubscribe_response = {"msg": "WebSocket normal closure", "level": "info", "subsystem": "disconnect","event_id": "UNSUBSCRIBE_FROM_STREAM"
                                                ,"timestamp": utils.get_timestamp(), "log_source": "_"
                                                }
                        final_response = LiveRPCResult(method=response_method, 
                                                       result=utils.dict_to_namespace(unsubscribe_response), 
                                                       error=RPCErrorModel(code=0, message="Websocket Normal Closure!"))

                    # support callbacks async et sync
                    result = self.to_run(final_response)
                    if asyncio.iscoroutine(result):
                        await result

            return final_response

        except asyncio.CancelledError:
            self.Logs.info("Websocket task cancelled, closing connection")
            error = LiveRPCResult(result=False, error=RPCErrorModel(code=-1, message="Websocket task cancelled, closing connection"))
            result = self.to_run(error)
            if asyncio.iscoroutine(result):
                await result

            return error

        except AttributeError as ae:
            self.Logs.critical(f"Attribute Error: {ae.__str__()} Check your callback function or method")
            error = LiveRPCResult(result=False, error=RPCErrorModel(code=-1, message="Attribute Error, Check your callback function or method!"))
            result = self.to_run(error)
            if asyncio.iscoroutine(result):
                await result

            return error

        except (KeyError, InvalidURI, InvalidHandshake, json.decoder.JSONDecodeError,
                TimeoutError, OSError, TypeError, Exception) as err:
            self.Logs.error(f"Websocket Error: {err}")
            self.Logs.error(f"Initial request: {self.request}")
            error = LiveRPCResult(result=False, error=RPCErrorModel(code=-1, message=err))
            result = self.to_run(error)
            if asyncio.iscoroutine(result):
                await result

            return error
