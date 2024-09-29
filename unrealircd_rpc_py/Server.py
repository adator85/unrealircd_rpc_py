from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Server:

    DB_SERVER: list[dfn.ClientServer] = []
    DB_MODULES: list[dfn.ServerModule] = []

    def __init__(self, Connection: Connection) -> None:

        # Store the original response
        self.response_raw: str
        """Original response used to see available keys."""

        self.response_np: SimpleNamespace
        """Parsed JSON response providing access to all keys as attributes."""

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def list_(self) -> list[dfn.ClientServer]:
        """List servers.

        Returns:
            list[ClientServer]: List with an object contains all Servers information
        """
        try:
            self.Connection.EngineError.init_error()

            self.DB_SERVER = []
            response = self.Connection.query('server.list')

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            servers = response['result']['list']

            for server in servers:
                ClientServer: dict = server.copy()
                ServerForClientServer: dict = server.get('server', {}).copy()
                FeaturesForServer: dict = server.get('server', {}).get('features', {}).copy()

                for key in ['server', 'tls']:
                    ClientServer.pop(key, None)

                for key in ['features']:
                    ServerForClientServer.pop(key, None)

                for key in ['rpc_modules']:
                    FeaturesForServer.pop(key, None)

                FeaturesObject = dfn.ServerFeatures(
                    **FeaturesForServer,
                    rpc_modules=[dfn.ServerRpcModules(**rpcmod) for rpcmod in server.get('server', {}).get('features', {}).get('rpc_modules', [])]
                    )

                ServerObject = dfn.Server(
                    **ServerForClientServer,
                    features=FeaturesObject
                )

                ClientServerObject = dfn.ClientServer(
                    **ClientServer,
                    server=ServerObject,
                    tls=dfn.Tls(**server.get('tls', {}))
                )

                self.DB_SERVER.append(ClientServerObject)

            return self.DB_SERVER

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return self.DB_SERVER
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return self.DB_SERVER

    def get(self, serverorsid: str = None) -> Union[dfn.ClientServer, None]:
        """Retrieve all details of a single server.

        Args:
            serverorsid (str, optional): the server name (or the SID). If not specified then the current server is assumed (the one you connect to via the JSON-RPC API). Defaults to None.

        Returns:
            ClientServer (ClientServer, None): The ClientServer if success | None if error
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query('server.get', {'server': serverorsid})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            server = response['result']['server']

            ClientServer: dict = server.copy()
            ServerForClientServer: dict = server.get('server', {}).copy()
            FeaturesForServer: dict = server.get('server', {}).get('features', {}).copy()

            for key in ['server', 'tls']:
                ClientServer.pop(key, None)

            for key in ['features']:
                ServerForClientServer.pop(key, None)

            for key in ['rpc_modules']:
                FeaturesForServer.pop(key, None)

            FeaturesObject = dfn.ServerFeatures(
                **FeaturesForServer,
                rpc_modules=[dfn.ServerRpcModules(**rpcmod) for rpcmod in server.get('server', {}).get('features', {}).get('rpc_modules', [])]
                )

            ServerObject = dfn.Server(
                **ServerForClientServer,
                features=FeaturesObject
            )

            ClientServerObject = dfn.ClientServer(
                **ClientServer,
                server=ServerObject,
                tls=dfn.Tls(**server.get('tls', {}))
            )

            return ClientServerObject

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None

    def rehash(self, serverorsid: str = None) -> Union[dfn.ServerRehash, None]:
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

            response = self.Connection.query('server.rehash', {'server': serverorsid})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

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

            DB_REHASH_LOG: list[dfn.ServerRehashLog] = []
            for rlog in rehash_log:
                rlog_copy = rlog.copy()
                rlog_copy.pop('source', None)
                DB_REHASH_LOG.append(
                    dfn.ServerRehashLog(
                        **rlog_copy,
                        source=dfn.ServerRehashLogSource(**rlog.get('source', {}))
                    )
                )

            rehashObject = dfn.ServerRehash(
                rehash_client=dfn.ServerRehashClient(**rehash.get("rehash_client", {})),
                log=DB_REHASH_LOG,
                success=rehash.get('success', None)
            )

            return rehashObject

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

            response = self.Connection.query('server.connect', {'link': link})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

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
        except Exception as err:
            self.Logs.error(f'General error: {err}')

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

            response = self.Connection.query('server.disconnect', {'link': link})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

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
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def module_list(self, serverorsid: str = None) -> list[dfn.ServerModule]:
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

            response = self.Connection.query('server.module_list', {'server': serverorsid})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

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
                self.DB_MODULES.append(dfn.ServerModule(**module))

            return self.DB_MODULES

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return self.DB_MODULES
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return self.DB_MODULES
