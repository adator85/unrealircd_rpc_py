import json.scanner
import requests, json, urllib3, socket, re, os
from requests.auth import HTTPBasicAuth
import base64, ssl, time, logging, random
from typing import Literal, Union
from types import SimpleNamespace
from dataclasses import dataclass

class Connection:

    @dataclass
    class ErrorModel:
        """This model will contain the error if any"""
        code: int
        message: str

    def __init__(self, req_method:str, url: str, path_to_socket_file: str, username: str, password: str, debug_level: int) -> None:

        self.debug_level = debug_level
        self.Logs: logging
        self.__init_log_system()
        self.Error = self.ErrorModel(0, '')
        """This model will contain the error if any"""

        self.url = url
        self.path_to_socket_file = path_to_socket_file

        self.endpoint: str = None
        self.host: str = None
        self.port: int = 0
        self.username = username
        self.password = password

        self.request: str = ''
        self.req_method = req_method
        self.str_response = ''
        self.json_response = ''

        # Option 2 with Namespacescs
        self.json_response_np: SimpleNamespace
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
                self.Error.code = -1
                self.Error.message = 'You must provide the url in this format: https://your.rpcjson.link:port/api'

            return response
        except NameError as nameerr:
            self.Logs.critical(f'NameError: {nameerr}')

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
                self.Error.code = -1
                self.Error.message = 'The Path to your socket file is empty ? please be sure that you are providing the correct socket path'
                return response

            if not os.path.exists(path_to_socket_file):
                self.Error.code = -1
                self.Error.message = 'The Path to your socket file is wrong ? please make sure that you are providing the correct socket path'
                return response

            response = True

            return response
        except NameError as nameerr:
            self.Logs.critical(f'NameError: {nameerr}')

    def __is_error_connection(self, response: str) -> bool:
        """If True, it means that there is an error

        Args:
            response (str): The response to analyse

        Returns:
            bool: True if there is a connection error
        """
        if 'authentication required' == response.lower().strip():
            self.Error.code = -1
            self.Error.message = '>> Authentication required'
            return True
        else:
            return False

    def __send_to_unixsocket(self):
        try:

            sock = socket.socket(socket.AddressFamily.AF_UNIX, socket.SocketKind.SOCK_STREAM)

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
            self.json_response = json.loads(str_data)
            self.json_response_np: SimpleNamespace = json.loads(str_data, object_hook=lambda d: SimpleNamespace(**d))

            sock.close()

        except AttributeError as attrerr:
            self.Logs.critical(f'AF_Unix Error: {attrerr}')
            self.Error.code = -1
            self.Error.message = 'AF_UNIX Are you sure you want to use Unix socket ?'
        except OSError as oserr:
            self.Logs.critical(f'System Error: {oserr}')
        except Exception as err:
            self.Logs.error(f'General Error: {err}')

    def __send_srequest(self):
        """S For socket connection"""
        try:

            if not self.__check_url(self.url) and not self.url is None:
                self.Logs.critical('You must provide the url in this format: https://your.rpcjson.link:port/api')
                return None

            get_url = self.url
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

                    self.json_response = json.loads(body)
                    self.json_response_np: SimpleNamespace = json.loads(body, object_hook=lambda d: SimpleNamespace(**d))

        except (socket.error, ssl.SSLError) as serror:
            self.Logs.error(f'Socket Error: {serror}')
        except Exception as err:
            self.Logs.error(f'General Error: {err}')
            # self.Logs.error(f'General Error: {traceback.format_exc()}')

    def __send_request(self) :
        """Use requests module"""
        try:

            if not self.__check_url(self.url) and not self.url is None:
                self.Logs.critical('You must provide the url in this format: https://your.rpcjson.link:port/api')
                return None

            verify = False

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            credentials = HTTPBasicAuth(self.username, self.password)
            jsonrequest = self.request

            response = requests.post(url=self.url, auth=credentials, data=jsonrequest, verify=verify)

            if self.__is_error_connection(response.text):
                return None

            decodedResponse = json.dumps(response.text)

            self.str_response = decodedResponse
            self.json_response = json.loads(json.loads(decodedResponse))
            self.json_response_np: SimpleNamespace = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))

        except KeyError as ke:
            self.Logs.error(f"KeyError : {ke}")
            self.Logs.error(f"Initial request: {self.request}")
        except requests.ReadTimeout as rt:
            self.Logs.error(f"Timeout : {rt}")
            self.Logs.error(f"Initial request: {self.request}")
        except requests.ConnectionError as ce:
            self.Logs.critical(f"Connection Error : {ce}")
            self.Logs.critical(f"Initial request: {self.request}")
        except json.decoder.JSONDecodeError as jsonerror:
            self.Logs.error(f"jsonError {jsonerror}")
            self.Logs.error(f"Initial request: {self.request}")
        except Exception as err:
            self.Logs.error(f"General Error {err}")
            self.Logs.error(f"Initial request: {self.request}")

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
        self.Logs = logging
        self.Logs.basicConfig(level=self.debug_level,
                            encoding='UTF-8',
                            format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(funcName)s - %(message)s')

    def query(self, method: Union[Literal['stats.get', 'rpc.info','user.list'], str], param: dict = {}, id: int = 123, jsonrpc:str = '2.0') -> Union[str, any, None, bool]:
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

        if self.req_method == 'socket':
            self.__send_srequest()
        elif self.req_method == 'unixsocket':
            self.__send_to_unixsocket()
        elif self.req_method == 'requests':
            self.__send_request()
        else:
            print('No valid request method')

        if self.json_response == '':
            return False

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