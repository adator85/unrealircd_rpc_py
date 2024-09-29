from types import SimpleNamespace
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Name_ban:

    DB_NAME_BANS: list[dfn.NameBan] = []

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

    def list_(self) -> list[dfn.NameBan]:
        """List name bans (qlines).

        Returns:
            ModelNameBan: List of ModelNameBan, None if nothing see Error property
        """
        try:
            self.DB_NAME_BANS = []
            self.Connection.EngineError.init_error()

            response = self.Connection.query(method='name_ban.list')

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

            namebans = response['result']['list']

            for nameban in namebans:
                self.DB_NAME_BANS.append(
                        dfn.NameBan(**nameban)
                )

            return self.DB_NAME_BANS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def get(self, name: str) -> dfn.NameBan:
        """Retrieve all details of a single name ban (qline).

        Args:
            name (str): name of the ban, eg *C*h*a*n*s*e*r*v*

        Returns:
            Union[ModelNameBan, None, bool]: The Object ModelNameBan, None if nothing see Error property
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(method='name_ban.get', param={"name": name})

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

            nameban = response['result']['tkl']

            objectNameBan = dfn.NameBan(**nameban)

            return objectNameBan

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def add(self, name: str, reason: str, set_by: str = None, expire_at: str = None, duration_string: str = None) -> bool:
        """Add a name ban (qline).

        Mandatory arguments (see structure of a name ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Name_ban#Structure_of_a_name_ban

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            reason (str): The reason of the ban
            set_by (str, optional): Name of the person or server who set the ban. Default to None
            expire_at (str, optional): Date/Time when the server ban will expire. NULL means: never. Default to None
            duration_string (str, optional): How long the ban will last from this point in time (human printable). Uses "permanent" for forever. Default to None

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                method='name_ban.add', 
                param={"name": name, "reason": reason, "set_by": set_by, "expire_at": expire_at, "duration_string": duration_string}
                )

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
        """Delete a name ban (LINE).

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            set_by (str, optional): Name of the person or server who set the ban. Default to None

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                method='name_ban.del',
                param={"name": name, 'set_by': set_by}
                )

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
