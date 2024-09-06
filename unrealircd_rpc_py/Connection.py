import requests, json, urllib3, socket
from requests.auth import HTTPBasicAuth
import base64, ssl, time, logging, random
from typing import Literal, Union

from dataclasses import dataclass, fields

class Connection:
    
    @dataclass
    class ErrorModel:
        code: int
        message: str

    def __init__(self, url: str, endpoint: str, host: str, port: int, username: str, password: str,  req_method: str, debug_level: Literal[10, 20, 30, 40, 50] = 20) -> None:

        self.url = url
        self.endpoint = endpoint
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.debug_level = debug_level

        self.request: str = ''
        self.req_method = req_method
        self.str_response = ''
        self.json_response = ''

        self.Logs: logging
        self.__init_log_system()

        self.Error = self.ErrorModel(0, '')

    def __send_srequest(self):
        """S For socket connection"""

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
                # Send the HTTP request

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

                self.json_response = json.loads(body)

    def __send_request(self) :
        """Use requests module"""

        verify = False

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        credentials = HTTPBasicAuth(self.username, self.password)
        jsonrequest = self.request

        response = requests.post(url=self.url, auth=credentials, data=jsonrequest, verify=verify)

        decodedResponse = json.dumps(response.text)
        try:
            self.str_response = decodedResponse
            self.json_response = json.loads(json.loads(decodedResponse))

        except KeyError as ke:
            self.Logs.error(f"KeyError : {ke}")
            self.Logs.error(f"Initial request: {self.request}")
        except requests.ReadTimeout as rt:
            self.Logs.error(f"Timeout : {rt}")
            self.Logs.error(f"Initial request: {self.request}")
        except requests.ConnectionError as ce:
            self.Logs.error(f"Connection Error : {ce}")
            self.Logs.error(f"Initial request: {self.request}")
        except json.decoder.JSONDecodeError as jsonerror:
            self.Logs.error(f"jsonError {jsonerror}")
            self.Logs.error(f"Initial request: {self.request}")
        except Exception as err:
            self.Logs.error(f"General Error {err}")
            self.Logs.error(f"Initial request: {self.request}")

    def __build_headers(self, credentials, data:str) -> str:

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
            method (Union[Literal[&#39;stats.get&#39;, &#39;rpc.info&#39;,&#39;user.list&#39;], str]): _description_
            param (dict, optional): _description_. Defaults to {}.
            id (int, optional): _description_. Defaults to 123.
            jsonrpc (str, optional): _description_. Defaults to '2.0'.

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