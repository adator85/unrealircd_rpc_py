import requests
import json
import urllib3
import socket
import re
import os
import base64
import ssl
import time
import logging
import random
from requests.auth import HTTPBasicAuth
from typing import Literal, Union, Optional, Any
from types import SimpleNamespace
from unrealircd_rpc_py.EngineError import EngineError

class Connection:

    def __init__(self, req_method:str, url: str, path_to_socket_file: str, username: str, password: str, debug_level: int) -> None:

        self.debug_level = debug_level
        self.Logs: logging.Logger
        self.__init_log_system()

        self.EngineError = EngineError()
        """Engine Error: should be used to set errors"""
        self.Error = self.EngineError.Error
        """Error attribut: to be used to print errors"""

        self.url: Optional[str] = url
        self.path_to_socket_file = path_to_socket_file

        self.endpoint: Optional[str] = None
        self.host: Optional[str] = None
        self.port: int = 0
        self.username = username
        self.password = password

        self.request: str = ''
        self.req_method = req_method

        # Option 2 with Namespacescs
        self.__response: Optional[dict] = {}
        self.__response_np: Optional[SimpleNamespace] = SimpleNamespace()

        self.query('stats.get')

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
            return False

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
                self.EngineError.set_error(
                    code=-1,
                    message='The Path to your socket file is empty ? please be sure that you are providing the correct socket path'
                )
                return response

            if not os.path.exists(path_to_socket_file):
                self.EngineError.set_error(
                    code=-1,
                    message='The Path to your socket file is wrong ? please make sure that you are providing the correct socket path'
                )
                return response

            response = True

            return response
        except NameError as nameerr:
            self.Logs.critical(f'NameError: {nameerr}')
            return False

    def __is_error_connection(self, response: str) -> bool:
        """If True, it means that there is an error

        Args:
            response (str): The response to analyse

        Returns:
            bool: True if there is a connection error
        """
        if 'authentication required' == response.lower().strip():
            self.EngineError.set_error(
                code=-1,
                message='>> Authentication required <<'
            )
            return True
        elif 'authentication required' in response.lower().strip():
            self.EngineError.set_error(
                code=-1,
                message='>> Authentication required <<'
            )
            return True
        elif "('Connection aborted.'," in response.lower().strip():
            self.EngineError.set_error(
                code=-1,
                message='>> Connection aborted <<'
            )
            return True
        else:
            return False

    def __send_to_unixsocket(self):
        sock = socket.socket(socket.AddressFamily.AF_UNIX, socket.SocketKind.SOCK_STREAM)
        try:

            if not self.__check_unix_socket_file(self.path_to_socket_file):
                return None

            sock.connect(self.path_to_socket_file)
            sock.settimeout(10)

            if not self.request:
                return None

            sock.sendall(f'{self.request}\r\n'.encode())

            response = b""
            chunk = b""
            pattern = b'\n$'

            while True:
                chunk = sock.recv(4096)
                response += chunk
                if re.findall(pattern, chunk):
                    break

            str_data = response.decode()
            self.__set_responses(str_data)

        except AttributeError as attrerr:
            self.Logs.critical(f'AF_Unix Error: {attrerr}')
            self.EngineError.set_error(code=-1, message=attrerr.__str__())
        except OSError as oserr:
            self.Logs.critical(f'System Error: {oserr}')
            self.EngineError.set_error(code=-1, message=oserr.__str__())
        except Exception as err:
            self.Logs.error(f'General Error: {err}')
            self.EngineError.set_error(code=-1, message=err.__str__())
        finally:
            sock.close()

    def __send_srequest(self):
        """S For socket connection"""
        try:

            if not self.__check_url(self.url) and not self.url is None:
                self.Logs.critical('You must provide the url in this format: https://your.rpcjson.link:port/api')
                return None

            get_host = self.host
            get_port = self.port
            get_username = self.username
            get_password = self.password
            credentials = base64.b64encode(f"{get_username}:{get_password}".encode()).decode()

            # Create a socket and wrap it in an SSL context for HTTPS
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((get_host, get_port)) as sock:
                with context.wrap_socket(sock, server_hostname=get_host) as ssock:
                    # Send the HTTPS

                    json_request = self.request
                    request = self.__build_headers(credentials, str(json_request))
                    ssock.sendall(request.encode('utf-8'))

                    # Receive the response
                    response = b""
                    while True:
                        chunk = ssock.recv(4096)
                        if not chunk:
                            break
                        response += chunk

                    # Decode and print the response
                    response_str = response.decode('utf-8')
                    header_end = response_str.find("\r\n\r\n")
                    if header_end != -1:
                        body = response_str[header_end + 4:]  # Extract the body
                    else:
                        body = response_str

                    if self.__is_error_connection(body):
                        return None

                    self.__set_responses(body)

        except (socket.error, ssl.SSLError) as serror:
            self.Logs.error(f'Socket Error: {serror}')
            self.EngineError.set_error(code=-1, message=f'Socket Error: {serror}')
        except json.JSONDecodeError as jdecErr:
            self.Logs.error(f'JSONDecodeError: {jdecErr}')
            self.EngineError.set_error(code=-1, message=f'Json Decode Error: {jdecErr}')
        except Exception as err:
            self.Logs.error(f'General Error: {err}')
            self.EngineError.set_error(code=-1, message=f'General Error: {err}')

    def __send_request(self):
        """Use requests module"""
        try:

            if not self.__check_url(self.url) and not self.url is None:
                self.Logs.critical('You must provide the url in this format: https://your.rpcjson.link:port/api')
                return None

            verify = False
            url: Optional[str] = self.url

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            credentials = HTTPBasicAuth(self.username, self.password)
            jsonrequest = self.request

            response = requests.post(url=url, auth=credentials, data=jsonrequest, verify=verify)

            if response.status_code != 200:
                self.EngineError.set_error(code=-1, message=f"Status code {response.status_code} | {response.reason}")
                return None
            
            if self.__is_error_connection(response.text):
                return None

            decoded_response = json.dumps(response.text)
            self.__set_responses(json.loads(decoded_response))

        except KeyError as ke:
            self.Logs.error(f"KeyError : {ke}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=ke.__str__())
        except requests.ReadTimeout as rt:
            self.Logs.error(f"Timeout : {rt}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'Timeout: {rt}')
        except requests.ConnectionError as ce:
            self.Logs.error(f"Connection Error : {ce}")
            self.Logs.error(f"Initial request: {self.request}")
            if 'connection aborted.' in str(ce).lower().strip():
                self.EngineError.set_error(code=-1, message=f'>> Connection Aborted <<')
        except json.decoder.JSONDecodeError as jsonerror:
            self.Logs.error(f"jsonError {jsonerror}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'Json Error: {jsonerror}')
        except Exception as err:
            self.Logs.error(f"General Error {err}")
            self.Logs.error(f"Initial request: {self.request}")
            self.EngineError.set_error(code=-1, message=f'General Error: {err}')

    def __build_headers(self, credentials: str, data:str) -> str:
        """Build the header for socket connection only

        Args:
            credentials (str): crypted credentials
            data (str): data we need to send to the server

        Returns:
            str: Returd the built header
        """
        headers: str = (
                    f"POST /{self.endpoint} HTTP/1.1\r\n"
                    f"Host: {self.host}\r\n"
                    "Content-Type: application/json\r\n"
                    f"Authorization: Basic {credentials}\r\n"
                    f"Content-Length: {len(data)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    f"{data}"
                )

        return headers

    def __init_log_system(self) -> None:
        """Init log system
        """
        # Init logs object
        self.Logs: logging.Logger = logging.getLogger('unrealircd-rpc-py')
        self.Logs.propagate = False
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

    def query(self,
              method: Union[Literal['stats.get', 'rpc.info','user.list'], str],
              param: Optional[dict] = None,
              query_id: int = 123,
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

        if self.req_method == 'socket':
            self.__send_srequest()
        elif self.req_method == 'unixsocket':
            self.__send_to_unixsocket()
        elif self.req_method == 'requests':
            self.__send_request()
        else:
            self.Logs.warning('No valid request method')
            self.EngineError.set_error(code=-1, message='<< Invalid method >>')

        if self.__response == '' or self.__response is None:
            return None

        return self.get_response()

    def get_keys_levels(self, data: Any, prefix=''):
        """Parse the Json output and list all available keys
        """

        if isinstance(data, dict):
            for key, value in data.items():
                complete_key = f"{prefix}.{key}" if prefix else key
                print(f"Key : {complete_key}, Type : {type(value).__name__}")
                self.get_keys_levels(value, complete_key)

        elif isinstance(data, list):
            for index, element in enumerate(data):
                complete_key = f"{prefix}[{index}]"
                print(f"Key : {complete_key}, Type : list")
                self.get_keys_levels(element, complete_key)

    def dict_to_namespace(self, dictionary: dict):

        if isinstance(dictionary, dict):
            return SimpleNamespace(**{key: self.dict_to_namespace(value) for key, value in dictionary.items()})

        return dictionary

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
        self.__response_np = self.dict_to_namespace(self.__response)

    def get_response_np(self) -> Union[SimpleNamespace, None]:
        return self.__response_np

    def get_response(self) -> Union[dict, None]:
        return self.__response