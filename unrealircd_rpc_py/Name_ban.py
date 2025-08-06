from types import SimpleNamespace
from typing import Union

from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as Dfn

class NameBan:

    DB_NAME_BANS: list[Dfn.NameBan] = []

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

    def list_(self) -> list[Dfn.NameBan]:
        """List name bans (qlines).

        Returns:
            ModelNameBan: List of ModelNameBan, None if nothing see Error property
        """
        try:
            self.DB_NAME_BANS = []
            self.Connection.EngineError.init_error()

            response: dict[str, dict] = self.Connection.query(method='name_ban.list')

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return []

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return []

            namebans: list[dict] = response.get('result', {}).get('list', []) # ['result']['list']

            for nameban in namebans:
                self.DB_NAME_BANS.append(
                        Dfn.NameBan(**nameban)
                )

            return self.DB_NAME_BANS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, name: str) -> Union[Dfn.NameBan, None]:
        """Retrieve all details of a single name ban (qline).

        Args:
            name (str): name of the ban, eg *C*h*a*n*s*e*r*v*

        Returns:
            Union[ModelNameBan, None, bool]: The Object ModelNameBan, None if nothing see Error property
        """
        try:
            self.Connection.EngineError.init_error()

            response: dict[str, dict] = self.Connection.query(method='name_ban.get', param={"name": name})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return None

            nameban = response['result']['tkl']

            obj = Dfn.NameBan(**nameban)

            return obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None

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

            response: dict[str, dict] = self.Connection.query(
                method='name_ban.add', 
                param={"name": name, "reason": reason, "set_by": set_by, "expire_at": expire_at, "duration_string": duration_string}
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

            response: dict[str, dict] = self.Connection.query(
                method='name_ban.del',
                param={"name": name, 'set_by': set_by}
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
