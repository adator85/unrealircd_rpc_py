import json.scanner
import json, socket, sys, os
import time, logging, random, asyncio
from typing import Literal, Union
from types import SimpleNamespace
from dataclasses import dataclass

class Live:

    @dataclass
    class ErrorModel:
        code: int
        message: str

    def __init__(self, path_to_socket_file: str, callback_object_instance: object, callback_method_name: str, debug_level: Literal[10, 20, 30, 40, 50] = 20) -> None:

        self.debug_level = debug_level
        self.Logs: logging
        self.__init_log_system()

        if not self.__check_unix_socket_file(path_to_socket_file=path_to_socket_file):
            self.Logs.critical(f'The socket file is not available, please check the full path of your socket file')
            sys.exit('please check the full path of your socket file')

        self.to_run = getattr(callback_object_instance, callback_method_name)

        self.path_to_socket_file = path_to_socket_file

        self.request: str = ''
        self.str_response = ''
        self.json_response = ''

        # Option 2 with Namespaces
        self.json_response_np: SimpleNamespace

        self.Error = self.ErrorModel(0, '')

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

    async def __send_to_permanent_unixsocket(self):
        try:

            sock = socket.socket(socket.AddressFamily.AF_UNIX, socket.SocketKind.SOCK_STREAM)
            sock.connect(self.path_to_socket_file)
            connected = True

            if not self.request:
                return None

            sock.sendall(f'{self.request}\r\n'.encode())

            while connected:
                # Recieve the data from the rpc server, decode it and split it
                response = sock.recv(4096).decode().split('\n')

                for bdata in response:
                    if bdata:
                        self.json_response = json.loads(bdata)
                        self.json_response_np: SimpleNamespace = json.loads(bdata, object_hook=lambda d: SimpleNamespace(**d))
                        self.to_run(self.json_response_np)

            sock.close()

        except AttributeError as attrerr:
            self.Logs.critical(f'AF_Unix Error: {attrerr}')
            sys.exit('AF_UNIX Are you sure you want to use Unix socket ?')
        except TimeoutError as timeouterr:
            self.Logs.critical(f'Timeout Error: {timeouterr}')
        except OSError as oserr:
            self.Logs.critical(f'System Error: {oserr}')
            sys.exit(3)
        except json.decoder.JSONDecodeError as jsondecoderror:
            self.Logs.critical(f'Json Decod Error: {jsondecoderror}')
        except Exception as err:
            self.Logs.error(f'General Error: {err}')

    def __init_log_system(self) -> None:
        """Init log system
        """
        # Init logs object
        self.Logs = logging
        self.Logs.basicConfig(level=self.debug_level,
                            encoding='UTF-8',
                            format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(funcName)s - %(message)s')

    def execute_async_method(self):
        asyncio.run(self.query('log.subscribe', param={"sources": ["all"]}))

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

        await asyncio.gather(self.__send_to_permanent_unixsocket())
        # self.__send_to_permanent_unixsocket()

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