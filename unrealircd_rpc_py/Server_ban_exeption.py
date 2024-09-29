from types import SimpleNamespace
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Server_ban_exception:

    DB_SERVERS_BANS_EXCEPTION: list[dfn.ServerBanException] = []

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

    def list_(self) -> list[dfn.ServerBanException]:
        """List server ban exceptions (ELINEs).

        Returns:
            list[ModelServerBanException]: List of ModelServerBanException, None if nothing see the Error property
        """
        try:
            self.Connection.EngineError.init_error()

            self.DB_SERVERS_BANS_EXCEPTION = []
            response = self.Connection.query(method='server_ban_exception.list')

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

            srvbansexceps = response['result']['list']

            for srvbansexcep in srvbansexceps:
                self.DB_SERVERS_BANS_EXCEPTION.append(
                        dfn.ServerBanException(**srvbansexcep)
                )

            return self.DB_SERVERS_BANS_EXCEPTION

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def get(self, name: str) -> dfn.ServerBanException:
        """Retrieve all details of a single server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.

        Returns:
            ModelServerBanException (ModelServerBanException): The model ModelServerBanException Object | None if nothing see the Error property
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(method='server_ban_exception.get', param={'name': name})

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

            srvbanexcep = response['result']['tkl']

            objectServBanExcep = dfn.ServerBanException(**srvbanexcep)

            return objectServBanExcep

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def add(self, name: str, exception_types: str, reason: str, set_by: str = None, expire_at: str = None, duration_sting: str = None) -> bool:
        """Add a server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): user@host mask or extended server ban
            exception_types (str): eg k for a kline exception
            reason (str): The reason of the ban
            expire_at (str, optional): Date/Time when the server ban will expire. NULL means: never. Defaults to None.
            duration_sting (str, optional): How long the ban will last from this point in time (human printable). Uses "permanent" for forever. Defaults to None.
            set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(method='server_ban_exception.add', param={"name": name, "exception_types": exception_types, "reason": reason, "expire_at": expire_at, "duration_string": duration_sting, 'set_by': set_by})

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

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def del_(self, name: str, set_by: str = None) -> bool:
        """Delete a server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(method='server_ban_exception.del', param={"name": name, 'set_by': set_by})

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

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')
