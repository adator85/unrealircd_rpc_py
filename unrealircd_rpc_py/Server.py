from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Server:

    @dataclass
    class ModelServer:
        name: str
        id: str
        hostname: str
        ip: str
        details: str
        server_port: int
        client_port: int
        connected_since: str
        idle_since: str

        server_info: str
        server_uplink: str
        server_num_users: int
        server_boot_time: str
        server_synced: bool
        server_ulined: bool

        server_features_software: str
        server_features_protocol: int
        server_features_usermodes: str
        server_features_chanmodes: list[str]
        server_features_rpc_modules: list[dict[str, any]]

        tls_cipher: str
        tls_certfp: str
   
    @dataclass
    class ModelRehash:
        name: str
        id: str
        hostname: str
        ip: str
        server_port: int
        details: str
        connected_since: str
        idle_since: str
        log: list[dict]
        success: bool

    @dataclass
    class ModelModules:
        name: str
        version: str
        author: str
        description: str
        third_party: bool
        permanent: bool
        permanent_but_reloadable: bool

    DB_SERVER: list[ModelServer] = []
    DB_MODULES: list[ModelModules] = []

    def __init__(self, Connection: Connection) -> None:

        # Record the original response
        self.original_response: str = ''

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def list_(self) -> Union[list[ModelServer], None, bool]:
        """List servers.

        Returns:
            list[ModelServer]: List with an object contains all Servers information
        """
        try:
            response = self.Connection.query('server.list')
            self.original_response = response

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            servers = response['result']['list']

            for server in servers:
                self.DB_SERVER.append(
                        self.ModelServer(
                            name=server['name'] if 'name' in server else None,
                            id=server['id'] if 'id' in server else None,
                            hostname=server['hostname'] if 'hostname' in server else None,
                            ip=server['ip'] if 'ip' in server else None,
                            details=server['details'] if 'details' in server else None,
                            server_port=server['server_port'] if 'server_port' in server else 0,
                            client_port=server['client_port'] if 'client_port' in server else 0,
                            connected_since=server['connected_since'] if 'connected_since' in server else None,
                            idle_since=server['idle_since'] if 'idle_since' in server else None,

                            server_info=server['server']['info'] if 'server' in server and 'info' in server['server'] else None,
                            server_uplink=server['server']['uplink'] if 'server' in server and 'uplink' in server['server'] else None,
                            server_num_users=server['server']['num_users'] if 'server' in server and 'num_users' in server['server'] else 0,
                            server_boot_time=server['server']['boot_time'] if 'server' in server and 'boot_time' in server['server'] else None,
                            server_synced=server['server']['synced'] if 'server' in server and 'synced' in server['server'] else False,
                            server_ulined=server['server']['ulined'] if 'server' in server and 'ulined' in server['server'] else False,

                            server_features_software=server['server']['features']['software'] if 'server' in server and 'features' in server['server'] and 'software' in server['server']['features'] else None,
                            server_features_protocol=server['server']['features']['protocol'] if 'server' in server and 'features' in server['server'] and 'protocol' in server['server']['features'] else 0,
                            server_features_usermodes=server['server']['features']['usermodes'] if 'server' in server and 'features' in server['server'] and 'usermodes' in server['server']['features'] else None,
                            server_features_chanmodes=server['server']['features']['chanmodes'] if 'server' in server and 'features' in server['server'] and 'chanmodes' in server['server']['features'] else [],
                            server_features_rpc_modules=server['server']['features']['rpc_modules'] if 'server' in server and 'features' in server['server'] and 'rpc_modules' in server['server']['features'] else [],

                            tls_cipher=server['tls']['cipher'] if 'tls' in server and 'cipher' in server['tls'] else None,
                            tls_certfp=server['tls']['certfp'] if 'tls' in server and 'certfp' in server['tls'] else None
                        )
                )

            return self.DB_SERVER

        except KeyError as ke:
            self.Logs.error(ke)
        except Exception as err:
            self.Logs.error(err)

    def get(self, _serverorsid: str = None) -> Union[ModelServer, None, bool]:
        """Retrieve all details of a single server.

        Args:
            _server (str, optional): the server name (or the SID). If not specified then the current server is assumed (the one you connect to via the JSON-RPC API). Defaults to None.

        Returns:
            Union[ModelServer, None, bool]: The ModelServer if success | None if nothing | False if error
        """
        try:

            response = self.Connection.query('server.get', {'server': _serverorsid})
            self.original_response = response

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            server = response['result']['server']

            serverObject = self.ModelServer(
                    name=server['name'] if 'name' in server else None,
                    id=server['id'] if 'id' in server else None,
                    hostname=server['hostname'] if 'hostname' in server else None,
                    ip=server['ip'] if 'ip' in server else None,
                    details=server['details'] if 'details' in server else None,
                    server_port=server['server_port'] if 'server_port' in server else 0,
                    client_port=server['client_port'] if 'client_port' in server else 0,
                    connected_since=server['connected_since'] if 'connected_since' in server else None,
                    idle_since=server['idle_since'] if 'idle_since' in server else None,

                    server_info=server['server']['info'] if 'server' in server and 'info' in server['server'] else None,
                    server_uplink=server['server']['uplink'] if 'server' in server and 'uplink' in server['server'] else None,
                    server_num_users=server['server']['num_users'] if 'server' in server and 'num_users' in server['server'] else None,
                    server_boot_time=server['server']['boot_time'] if 'server' in server and 'boot_time' in server['server'] else None,
                    server_synced=server['server']['synced'] if 'server' in server and 'synced' in server['server'] else None,
                    server_ulined=server['server']['ulined'] if 'server' in server and 'ulined' in server['server'] else None,

                    server_features_software=server['server']['features']['software'] if 'server' in server and 'features' in server['server'] and 'software' in server['server']['features'] else None,
                    server_features_protocol=server['server']['features']['protocol'] if 'server' in server and 'features' in server['server'] and 'protocol' in server['server']['features'] else None,
                    server_features_usermodes=server['server']['features']['usermodes'] if 'server' in server and 'features' in server['server'] and 'usermodes' in server['server']['features'] else None,
                    server_features_chanmodes=server['server']['features']['chanmodes'] if 'server' in server and 'features' in server['server'] and 'chanmodes' in server['server']['features'] else None,
                    server_features_rpc_modules=server['server']['features']['rpc_modules'] if 'server' in server and 'features' in server['server'] and 'rpc_modules' in server['server']['features'] else None,

                    tls_cipher=server['tls']['cipher'] if 'tls' in server and 'cipher' in server['tls'] else None,
                    tls_certfp=server['tls']['certfp'] if 'tls' in server and 'certfp' in server['tls'] else None
                )

            return serverObject

        except KeyError as ke:
            self.Logs.error(ke)
            return None
        except Exception as err:
            self.Logs.error(err)
            return None

    def rehash(self, _serverorsid: str = None) -> Union[ModelRehash, None, bool]:
        """Rehash the server.

        IMPORTANT: If all servers on your network have rpc.modules.default.conf included then this can return an object with full rehash details.
        Otherwise, for remote rehashes a simple boolean 'true' result is returned.

        Args:
            _serverorsid (str, optional): the server name (or SID). If not specified then the current server is assumed (the one you connect to via the JSON-RPC API). Defaults to None.

        Returns:
            bool: True if success or False if failed
        """
        try:
            response = self.Connection.query('server.rehash', {'server': _serverorsid})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            rehash = response['result']

            rehashObject = self.ModelRehash(
                        name=rehash['rehash_client']['name'] if 'rehash_client' in rehash and 'name' in rehash['rehash_client'] else None,
                        id=rehash['rehash_client']['id'] if 'rehash_client' in rehash and 'id' in rehash['rehash_client'] else None,
                        hostname=rehash['rehash_client']['hostname'] if 'rehash_client' in rehash and 'hostname' in rehash['rehash_client'] else None,
                        ip=rehash['rehash_client']['ip'] if 'rehash_client' in rehash and 'ip' in rehash['rehash_client'] else None,
                        server_port=rehash['rehash_client']['server_port'] if 'rehash_client' in rehash and 'server_port' in rehash['rehash_client'] else 0,
                        details=rehash['rehash_client']['details'] if 'rehash_client' in rehash and 'details' in rehash['rehash_client'] else None,
                        connected_since=rehash['rehash_client']['connected_since'] if 'rehash_client' in rehash and 'connected_since' in rehash['rehash_client'] else None,
                        idle_since=rehash['rehash_client']['idle_since'] if 'rehash_client' in rehash and 'idle_since' in rehash['rehash_client'] else None,
                        log=rehash['log'] if 'log' in rehash else [],
                        success=rehash['success'] if 'success' in rehash else False
                    )

            return rehashObject

        except TypeError as te:
            self.Logs.error(f'Type Error: {te}')
        except Exception as err:
            self.Logs.error(f'General Error: {err}')

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
            response = self.Connection.query('server.connect', {'link': link})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except Exception as err:
            self.Logs.error(f'General Error: {err}')

    def disconnect(self, link: str) -> bool:
        """Terminate a server link (disconnect).

        This works for both directly connected servers and remote servers further up the network.

        Args:
            link (str): the server name to unlink from

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query('server.disconnect', {'link': link})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except Exception as err:
            self.Logs.error(f'General Error: {err}')

    def module_list(self, _serverorsid: str = None) -> Union[list[ModelModules], None, bool]:
        """Get the module list (list of loaded modules) on a server.

        IMPORTANT: This only works with remote servers if all servers on your network have rpc.modules.default.conf included.
        This is because then the JSON-RPC request/response is forwarded over the IRC network.

        Args:
            _serverorsid (str): The server name (or the SID). If not specified then the current server is assumed (the one you connect to via the JSON-RPC API).. Defaults to None.

        Returns:
            ModelModules: if success you will find the object DB_MODULES
            bool: if False means that we have an error
        """
        try:
            response = self.Connection.query('server.module_list', {'server': _serverorsid})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            modules = response['result']['list']

            for module in modules:
                self.DB_MODULES.append(
                    self.ModelModules(
                        name=module['name'] if 'name' in module else None,
                        version=module['version'] if 'version' in module else None,
                        author=module['author'] if 'author' in module else None,
                        description=module['description'] if 'description' in module else None,
                        third_party=module['third_party'] if 'third_party' in module else None,
                        permanent=module['permanent'] if 'permanent' in module else None,
                        permanent_but_reloadable=module['permanent_but_reloadable'] if 'permanent_but_reloadable' in module else None
                    )
                )

            return self.DB_MODULES

        except Exception as err:
            self.Logs.error(f'General Error: {err}')
