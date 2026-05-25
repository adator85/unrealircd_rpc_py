import json
import logging
import random
import time
import requests
import urllib3
import unrealircd_rpc_py.objects.Definition as Dfn
import unrealircd_rpc_py.utils.utils as utils
from types import SimpleNamespace
from typing import Optional
from requests.auth import HTTPBasicAuth
from unrealircd_rpc_py.connections.sync import __version_required__
from unrealircd_rpc_py.exceptions.rpc_exceptions import (
    RpcConnectionError, RpcSetupError, RpcInvalidUrlFormat
)
from unrealircd_rpc_py.objects.Channel import Channel
from unrealircd_rpc_py.objects.Name_ban import NameBan
from unrealircd_rpc_py.objects.Server import Server
from unrealircd_rpc_py.objects.Server_ban import ServerBan
from unrealircd_rpc_py.objects.Server_ban_exeption import ServerBanException
from unrealircd_rpc_py.objects.User import User
from unrealircd_rpc_py.objects.Log import Log
from unrealircd_rpc_py.objects.Rpc import Rpc
from unrealircd_rpc_py.objects.Stats import Stats
from unrealircd_rpc_py.objects.Whowas import Whowas
from unrealircd_rpc_py.objects.Spamfilter import Spamfilter
from unrealircd_rpc_py.objects.Message import Message
from unrealircd_rpc_py.objects.Connthrottle import ConnThrottle
from unrealircd_rpc_py.objects.Security_group import SecurityGroup
from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class HttpConnection(IConnection):

    def __init__(self, debug_level: int) -> None:

        self.debug_level = debug_level
        self.Logs: logging.Logger = utils.start_log_system(
            name='unrealircd-rpc-py', debug_level=debug_level
        )
        self.__url = None
        self.__username = None
        self.__password = None
        self.unrealircd_version: Optional[tuple] = None

        self.is_setup: bool = False

        # Create User Instance
        self.User: User = User(self)
        """The User module instance"""

        # Create Server Instance
        self.Server: Server = Server(self)
        """The Server module instance"""

        # Create Server_ban Instance
        self.Server_ban: ServerBan = ServerBan(self)
        """The ServerBan module instance"""

        # Create Server_ban_exception Instance
        self.Server_ban_exception: ServerBanException = ServerBanException(
            self
        )
        """The ServerBanException module instance"""

        # Create Name_ban Instance
        self.Name_ban: NameBan = NameBan(self)
        """The Name_ban module instance"""

        # Create Rpc Instance
        self.Rpc: Rpc = Rpc(self)
        """The Rpc module instance"""

        # Create Spamfilter Instance
        self.Spamfilter: Spamfilter = Spamfilter(self)
        """The Spamfilter module instance"""

        # Create Channel Instance
        self.Channel: Channel = Channel(self)
        """The Channel module instance"""

        # Create Stats Instance
        self.Stats: Stats = Stats(self)
        """The Stats module instance"""

        # Create Whowas Instance
        self.Whowas: Whowas = Whowas(self)
        """The Whowas module instance"""

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

        # Option 2 with Namespacescs
        self.__response: Optional[dict] = {}
        self.__response_np: Optional[SimpleNamespace] = SimpleNamespace()

    def setup(self, params: dict) -> None:
        self.url = params.get('url', None)
        self.username = params.get('username', None)
        self.password = params.get('password', None)
        self.is_setup = True

        test = self.establish_first_connection()
        if test.error.code != 0:
            self.Logs.error(
                f"Connexion failed to the server: {test.error.message} "
                f"({test.error.code})"
            )
            raise RpcConnectionError(
                f"{test.error.message} ({test.error.code})"
            )

        self.connect()

    def connect(self) -> None:
        if not self.is_setup:
            self.Logs.critical(
                'You must call "setup" method before anything.'
            )
            raise RpcConnectionError('The "setup" method must be executed '
                                     'before "connect" method.',
                                     -1)

        _server = self.Server.get()
        _version = _server.server.features.software
        try:
            # UnrealIRCd-6.2.1
            _version = _version.split('-')[1].split('.')
            self.unrealircd_version = tuple(map(lambda x: int(x), _version))
        except KeyError:
            self.Logs.warning('Impossible to define the server version!')

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
        # data = '{"jsonrpc": "2.0", "method": "stats.get", "params": {},
        # "id": 123}'
        _method_impacted_by_version = [key for key in __version_required__]
        _method = method.split('.')[0]
        if _method in _method_impacted_by_version:
            _req_ver = __version_required__.get(_method, None)
            if not utils.is_version_ircd_ok(
                    self.unrealircd_version,
                    _req_ver
            ):
                return {
                    "jsonrpc": jsonrpc,
                    "method": method,
                    "error": {
                        'message': f'This object {_method} is not '
                                   f'available for this ircd version. '
                                   f'must be {_req_ver} or higher',
                        'code': -1},
                    "id": query_id}

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

        request = json.dumps(response)
        response_str = self.send_to_method(request)
        self.__set_responses(response_str)
        response = self.get_response()

        if response is None:
            return None

        return response

    def send_to_method(self, request: dict) -> Optional[str]:
        """Use requests module"""
        try:
            if not self.is_setup:
                self.Logs.critical(
                    'You must call "setup" method before anything.'
                )
                return None

            url_info = utils.check_url(self.url)

            if url_info is None:
                self.Logs.critical(
                    'You must provide the url in this format: '
                    'https://your.rpcjson.link:port/api'
                )
                return None

            verify = False
            url: Optional[str] = self.url

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            credentials = HTTPBasicAuth(self.username, self.password)
            jsonrequest = request

            response = requests.post(
                url=url, auth=credentials, data=jsonrequest, verify=verify
            )

            if response.status_code != 200:
                self.Logs.error(
                    f"Status code {response.status_code} | {response.reason}"
                )
                err = Dfn.RPCResult(
                    error=Dfn.RPCErrorModel(
                        response.status_code, f"{response.text}"
                    )
                )
                return str(err.to_dict())

            return response.text

        except KeyError as ke:
            self.Logs.error(f"KeyError : {ke}")
            self.Logs.error(f"Initial request: {request}")
        except requests.ReadTimeout as rt:
            self.Logs.error(f"Timeout : {rt}")
            self.Logs.error(f"Initial request: {request}")
        except requests.ConnectionError as ce:
            self.Logs.error(f"Connection Error : {ce}")
            self.Logs.error(f"Initial request: {request}")
            if 'connection aborted.' in str(ce).lower().strip():
                raise RpcConnectionError(">> Connection Aborted! <<")
        except json.decoder.JSONDecodeError as jsonerror:
            self.Logs.error(f"jsonError {jsonerror}")
            self.Logs.error(f"Initial request: {request}")
        except Exception as err:
            self.Logs.error(f"General Error {err}")
            self.Logs.error(f"Initial request: {request}")

    def establish_first_connection(self) -> Dfn.RPCResult:
        if not self.is_setup:
            self.Logs.critical(
                'You must call "setup" method before anything.'
            )
            raise RpcSetupError(
                'You must call "setup" method before anything.'
            )

        url_info = utils.check_url(self.url)

        if url_info is None:
            self.Logs.critical(
                'You must provide the url in this format:'
                'https://your.rpcjson.link:port/api'
            )
            raise RpcInvalidUrlFormat(
                'You must provide the url in this format: '
                'https://your.rpcjson.link:port/api'
            )

        verify = False
        url: Optional[str] = self.url

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        credentials = HTTPBasicAuth(self.username, self.password)
        response = requests.get(url=url, auth=credentials, verify=verify)

        if response.status_code >= 300:
            return Dfn.RPCResult(
                error=Dfn.RPCErrorModel(
                    response.status_code, response.text.strip()
                )
            )
        else:
            return Dfn.RPCResult()

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
        self.__response_np = utils.dict_to_namespace(self.__response)

    def get_response_np(self) -> Optional[SimpleNamespace]:
        return self.__response_np

    def get_response(self) -> Optional[dict]:
        return self.__response

    @property
    def url(self) -> str:
        return self.__url

    @url.setter
    def url(self, url: str) -> None:
        self.__url = url

    @property
    def username(self) -> str:
        return self.__username

    @username.setter
    def username(self, username: str) -> None:
        self.__username = username

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, password: str) -> None:
        self.__password = password
