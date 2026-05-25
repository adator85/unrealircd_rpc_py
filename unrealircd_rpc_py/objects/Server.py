from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Server:

    DB_SERVER: list[Dfn.ClientServer] = []
    DB_MODULES: list[Dfn.ServerModule] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self) -> list[Dfn.ClientServer]:
        """List servers.

        Returns:
            list[ClientServer]: List with an object contains all Servers
                information
        """
        try:
            self.DB_SERVER = []
            response: dict[str, dict] = self.Connection.query('server.list')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_SERVER.append(
                    Dfn.ClientServer(error=response_model.error)
                )
                return self.DB_SERVER

            servers: list[dict] = response_model.result.get('list', [])

            for server in servers:
                client_server: dict = server.copy()
                server_for_client_server: dict = server.get(
                    'server', {}).copy()
                features_for_server: dict = server.get('server', {}).get(
                    'features', {}).copy()

                for key in ['server', 'tls']:
                    client_server.pop(key, None)

                for key in ['features']:
                    server_for_client_server.pop(key, None)

                for key in ['rpc_modules']:
                    features_for_server.pop(key, None)

                features_object = Dfn.ServerFeatures(
                    **features_for_server,
                    rpc_modules=[
                        Dfn.ServerRpcModules(**rpcmod) for rpcmod
                        in server.get(
                            'server', {}).get(
                            'features', {}).get(
                            'rpc_modules', [])
                    ]
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

    def get(self, serverorsid: str = None) -> Dfn.ClientServer:
        """Retrieve all details of a single server.

        Args:
            serverorsid (str, optional): the server name (or the SID).
                If not specified then the current server is assumed
                (the one you connect to via the JSON-RPC API).
                Defaults to None.

        Returns:
            ClientServer (ClientServer, None):
                The ClientServer if success | None if error
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'server.get', {'server': serverorsid})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.ClientServer(error=response_model.error)

            server: dict = response_model.result.get('server', {})

            client_server: dict = server.copy()
            server_for_client_server: dict = server.get('server', {}).copy()
            features_for_server: dict = server.get(
                'server', {}).get('features', {}).copy()

            for key in ['server', 'tls']:
                client_server.pop(key, None)

            for key in ['features']:
                server_for_client_server.pop(key, None)

            for key in ['rpc_modules']:
                features_for_server.pop(key, None)

            features_object = Dfn.ServerFeatures(
                **features_for_server,
                rpc_modules=[
                    Dfn.ServerRpcModules(**rpcmod) for rpcmod in
                    server.get(
                        'server', {}).get(
                        'features', {}).get(
                        'rpc_modules', [])
                ]
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
            return Dfn.ClientServer(
                error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.ClientServer(
                error=Dfn.RPCErrorModel(-1, err.__str__()))

    def rehash(self, serverorsid: str = None) -> Dfn.ServerRehash:
        """Rehash the server.

        IMPORTANT: If all servers on your network have
        rpc.modules.default.conf included then this can return an object with
        full rehash details.
        Otherwise, for remote rehashes a simple boolean 'true' result is
        returned.

        Args:
            serverorsid (str, optional): the server name (or SID).
                If not specified then the current server is assumed
                (the one you connect to via the JSON-RPC API).
                Defaults to None.

        Returns:
            ServerRehash: True if success or False if failed
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'server.rehash', {'server': serverorsid})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.ClientServer(error=response_model.error)

            rehash: dict = response_model.result

            rehash_log: list[dict] = rehash.get('log', []).copy()

            db_rehash_log: list[Dfn.ServerRehashLog] = []

            for rlog in rehash_log:
                rlog_copy = rlog.copy()
                rlog_copy.pop('source', None)
                db_rehash_log.append(
                    Dfn.ServerRehashLog(
                        **rlog_copy,
                        source=Dfn.ServerRehashLogSource(
                            **rlog.get('source', {})
                        )
                    )
                )

            rehash_object = Dfn.ServerRehash(
                rehash_client=Dfn.ServerRehashClient(
                    **rehash.get("rehash_client", {})),
                log=db_rehash_log,
                success=rehash.get('success', '')
            )

            return rehash_object

        except TypeError as te:
            self.Logs.error(f'Type Error: {te}')
            return Dfn.ServerRehash(
                error=Dfn.RPCErrorModel(-1, te.__str__())
            )
        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.ServerRehash(
                error=Dfn.RPCErrorModel(-1, ke.__str__())
            )
        except Exception as err:
            self.Logs.error(f'General Error: {err}')
            return Dfn.ServerRehash(
                error=Dfn.RPCErrorModel(-1, err.__str__())
            )

    def connect(self, link: str) -> Dfn.RPCResult:
        """Make server link (connect) to another server.

        Right now you can only tell to link to servers from the directly
        connected server (the one you are issuing JSON-RPC calls to),
        you cannot (yet) tell remote server B to link to server C.

        Args:
            link (str): the server name to link to

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'server.connect', {'link': link})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def disconnect(self, link: str) -> Dfn.RPCResult:
        """Terminate a server link (disconnect).

        This works for both directly connected servers and remote servers
        further up the network.

        Args:
            link (str): the server name to unlink from

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'server.disconnect', {'link': link})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def module_list(self, serverorsid: str = None) -> list[Dfn.ServerModule]:
        """Get the module list (list of loaded modules) on a server.

        IMPORTANT: This only works with remote servers if all servers on your
        network have rpc.modules.default.conf included.
        This is because then the JSON-RPC request/response is forwarded over
        the IRC network.

        Args:
            serverorsid (str, optional): The server name (or the SID).
                If not specified then the current server is assumed
                (the one you connect to via the JSON-RPC API).
                Defaults to None.

        Returns:
            ServerModule (ServerModule): if success you will find the object
                ServerModule
        """
        try:
            self.DB_MODULES = []
            response: dict[str, dict] = self.Connection.query(
                'server.module_list', {'server': serverorsid})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_MODULES.append(
                    Dfn.ServerModule(error=response_model.error)
                )
                return self.DB_MODULES

            modules: list = response_model.result.get('list', [])

            for module in modules:
                self.DB_MODULES.append(Dfn.ServerModule(**module))

            return self.DB_MODULES

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []
