from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as Dfn

class Server:

    DB_SERVER: list[Dfn.ClientServer] = []
    DB_MODULES: list[Dfn.ServerModule] = []

    def __init__(self, connection: Connection) -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs
        self.Error = connection.Error

    @property
    def get_error(self) -> Dfn.RPCError:
        return self.Error

    @property
    def get_response(self) -> Union[dict, None]:
        return self.Connection.get_response()

    @property
    def get_response_np(self) -> Union[SimpleNamespace, None]:
        return self.Connection.get_response_np()

    def list_(self) -> list[Dfn.ClientServer]:
        """List servers.

        Returns:
            list[ClientServer]: List with an object contains all Servers information
        """
        try:
            self.Connection.EngineError.init_error()
            self.DB_SERVER = []

            response: dict[str, dict] = self.Connection.query('server.list')

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return []

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return []

            servers = response['result']['list']

            for server in servers:
                client_server: dict = server.copy()
                server_for_client_server: dict = server.get('server', {}).copy()
                features_for_server: dict = server.get('server', {}).get('features', {}).copy()

                for key in ['server', 'tls']:
                    client_server.pop(key, None)

                for key in ['features']:
                    server_for_client_server.pop(key, None)

                for key in ['rpc_modules']:
                    features_for_server.pop(key, None)

                features_object = Dfn.ServerFeatures(
                    **features_for_server,
                    rpc_modules=[Dfn.ServerRpcModules(**rpcmod) for rpcmod in server.get('server', {}).get('features', {}).get('rpc_modules', [])]
                    )

                server_object = Dfn.Server(
                    **server_for_client_server,
                    features=features_object
                )

                client_server_object = Dfn.ClientServer(
                    **client_server,
                    server=server_object,
                    tls=Dfn.Tls(**server.get('tls', {}))
                )

                self.DB_SERVER.append(client_server_object)

            return self.DB_SERVER

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, serverorsid: str = None) -> Union[Dfn.ClientServer, None]:
        """Retrieve all details of a single server.

        Args:
            serverorsid (str, optional): the server name (or the SID). If not specified then the current server is assumed (the one you connect to via the JSON-RPC API). Defaults to None.

        Returns:
            ClientServer (ClientServer, None): The ClientServer if success | None if error
        """
        try:
            self.Connection.EngineError.init_error()

            response:dict[str, dict] = self.Connection.query('server.get', {'server': serverorsid})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return None

            server = response['result']['server']

            client_server: dict = server.copy()
            server_for_client_server: dict = server.get('server', {}).copy()
            features_for_server: dict = server.get('server', {}).get('features', {}).copy()

            for key in ['server', 'tls']:
                client_server.pop(key, None)

            for key in ['features']:
                server_for_client_server.pop(key, None)

            for key in ['rpc_modules']:
                features_for_server.pop(key, None)

            features_object = Dfn.ServerFeatures(
                **features_for_server,
                rpc_modules=[Dfn.ServerRpcModules(**rpcmod) for rpcmod in server.get('server', {}).get('features', {}).get('rpc_modules', [])]
                )

            server_object = Dfn.Server(
                **server_for_client_server,
                features=features_object
            )

            client_server_object = Dfn.ClientServer(
                **client_server,
                server=server_object,
                tls=Dfn.Tls(**server.get('tls', {}))
            )

            return client_server_object

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None

    def rehash(self, serverorsid: str = None) -> Union[Dfn.ServerRehash, None]:
        """Rehash the server.

        IMPORTANT: If all servers on your network have rpc.modules.default.conf included then this can return an object with full rehash details.
        Otherwise, for remote rehashes a simple boolean 'true' result is returned.

        Args:
            serverorsid (str, optional): the server name (or SID). If not specified then the current server is assumed (the one you connect to via the JSON-RPC API). Defaults to None.

        Returns:
            ServerRehash: True if success or False if failed
        """
        try:
            self.Connection.EngineError.init_error()

            response:dict[str, dict] = self.Connection.query('server.rehash', {'server': serverorsid})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return None

            rehash: dict = response['result']

            rehash_log: list[dict] = rehash.get('log', []).copy()

            db_rehash_log: list[Dfn.ServerRehashLog] = []

            for rlog in rehash_log:
                rlog_copy = rlog.copy()
                rlog_copy.pop('source', None)
                db_rehash_log.append(
                    Dfn.ServerRehashLog(
                        **rlog_copy,
                        source=Dfn.ServerRehashLogSource(**rlog.get('source', {}))
                    )
                )

            rehash_object = Dfn.ServerRehash(
                rehash_client=Dfn.ServerRehashClient(**rehash.get("rehash_client", {})),
                log=db_rehash_log,
                success=rehash.get('success', '')
            )

            return rehash_object

        except TypeError as te:
            self.Logs.error(f'Type Error: {te}')
            return None
        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General Error: {err}')
            return None

    def connect(self, link: str) -> bool:
        """Make server link (connect) to another server.

        Right now you can only tell to link to servers from the directly connected server 
        (the one you are issuing JSON-RPC calls to), 
        you cannot (yet) tell remote server B to link to server C.

        Args:
            link (str): the server name to link to

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response:dict[str, dict] = self.Connection.query('server.connect', {'link': link})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return False
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return False

    def disconnect(self, link: str) -> bool:
        """Terminate a server link (disconnect).

        This works for both directly connected servers and remote servers further up the network.

        Args:
            link (str): the server name to unlink from

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response:dict[str, dict] = self.Connection.query('server.disconnect', {'link': link})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return False
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return False

    def module_list(self, serverorsid: str = None) -> list[Dfn.ServerModule]:
        """Get the module list (list of loaded modules) on a server.

        IMPORTANT: This only works with remote servers if all servers on your network have rpc.modules.default.conf included.
        This is because then the JSON-RPC request/response is forwarded over the IRC network.

        Args:
            serverorsid (str, optional): The server name (or the SID). If not specified then the current server is assumed (the one you connect to via the JSON-RPC API). Defaults to None.

        Returns:
            ServerModule (ServerModule): if success you will find the object ServerModule
        """
        try:
            self.DB_MODULES = []
            self.Connection.EngineError.init_error()

            response:dict[str, dict] = self.Connection.query('server.module_list', {'server': serverorsid})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return self.DB_MODULES

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return self.DB_MODULES

            modules = response['result']['list']

            for module in modules:
                self.DB_MODULES.append(Dfn.ServerModule(**module))

            return self.DB_MODULES

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []
