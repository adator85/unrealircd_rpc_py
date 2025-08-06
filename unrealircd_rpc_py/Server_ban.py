from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as Dfn

class ServerBan:

    DB_SERVERS_BANS: list[Dfn.ServerBan] = []

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

    def list_(self) -> list[Dfn.ServerBan]:
        """List server bans (LINEs).

        Returns:
            list[ServerBan]: List of ServerBan, if empty see Error Object
        """
        try:
            self.Connection.EngineError.init_error()
            self.DB_SERVERS_BANS = []

            response:dict[str, dict] = self.Connection.query(method='server_ban.list')

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return self.DB_SERVERS_BANS

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return self.DB_SERVERS_BANS

            srvbans:list[dict] = response.get('result', {}).get('list', [])

            for srvban in srvbans:
                self.DB_SERVERS_BANS.append(Dfn.ServerBan(**srvban))

            return self.DB_SERVERS_BANS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, query_type: str, name: str) -> Union[Dfn.ServerBan, None]:
        """Retrieve all details of a single server ban (LINE).

        Args:
            query_type (str): Type of the server ban. One of: gline, kline, gzline, zline, spamfilter, qline, except, shun, local-qline, local-exception, local-spamfilter.
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.

        Returns:
            ServerBan (ServerBan): The model Object | If None see the Error Attribut
        """
        try:
            self.Connection.EngineError.init_error()

            response:dict[str, dict] = self.Connection.query(method='server_ban.get', param={'type': query_type, 'name': name})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return None

            srvban: dict = response.get('result', {}).get('tkl', {})

            obj = Dfn.ServerBan(**srvban)

            return obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None

    def add(self, query_type: str, name: str, reason: str, expire_at: str,
            duration_sting: str, set_by: str = None) -> bool:
        """Add a server ban (LINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban#Structure_of_a_server_ban

        Args:
            query_type (str): Type of the server ban. One of: gline, kline, gzline, zline, spamfilter, qline, except, shun, local-qline, local-exception, local-spamfilter.
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            reason (str): The reason of the ban
            expire_at (str): Date/Time when the server ban will expire. NULL means: never.
            duration_sting (str): How long the ban will last from this point in time (human printable). Uses "permanent" for forever.
            set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response: dict[str, dict] = self.Connection.query(method='server_ban.add',
                                             param={"type": query_type, "name": name, "reason": reason,
                                                    "expire_at": expire_at, "duration_string": duration_sting,
                                                    'set_by': set_by}
                                             )

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return False
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return False

    def del_(self, query_type: str, name: str, set_by: str = None) -> bool:
        """Delete a server ban (LINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban#Structure_of_a_server_ban

        Args:
            query_type (str): Type of the server ban. One of: gline, kline, gzline, zline, spamfilter, qline, except, shun, local-qline, local-exception, local-spamfilter.
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response: dict[str, dict] = self.Connection.query(method='server_ban.del',
                                             param={"type": query_type, "name": name, 'set_by': set_by})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return False
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return False
