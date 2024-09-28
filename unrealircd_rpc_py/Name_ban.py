from types import SimpleNamespace
from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Name_ban:

    @dataclass
    class ModelNameBan:
        type: str
        type_string: str
        set_by: str
        set_at: str
        expire_at: str
        set_at_string: str
        expire_at_string: str
        duration_string: str
        set_at_delta: int
        set_in_config: bool
        name: str
        reason: str

    DB_NAME_BANS: list[ModelNameBan] = []

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

    def list_(self) -> Union[list[ModelNameBan], None]:
        """List name bans (qlines).

        Returns:
            ModelNameBan: List of ModelNameBan, None if nothing see Error property
        """
        try:
            self.DB_NAME_BANS = []
            response = self.Connection.query(method='name_ban.list')

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                error = {"error": {"code": -1, "message": "Empty response"}}
                self.Connection.set_error(error)
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return None

            namebans = response['result']['list']

            for nameban in namebans:
                self.DB_NAME_BANS.append(
                        self.ModelNameBan(
                            type=nameban['type'] if 'type' in nameban else None,
                            type_string=nameban['type_string'] if 'type_string' in nameban else None,
                            set_by=nameban['set_by'] if 'set_by' in nameban else None,
                            set_at=nameban['set_at'] if 'set_at' in nameban else None,
                            expire_at=nameban['expier_at'] if 'expier_at' in nameban else None,
                            set_at_string=nameban['set_at_string'] if 'set_at_string' in nameban else None,
                            expire_at_string=nameban['expier_at_string'] if 'expier_at_string' in nameban else None,
                            duration_string=nameban['duration_string'] if 'duration_string' in nameban else None,
                            set_at_delta=nameban['set_at_delta'] if 'set_at_delta' in nameban else 0,
                            set_in_config=nameban['set_in_config'] if 'set_in_config' in nameban else False,
                            name=nameban['name'] if 'name' in nameban else None,
                            reason=nameban['reason'] if 'reason' in nameban else None
                            )
                )

            return self.DB_NAME_BANS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def get(self, name: str) -> Union[ModelNameBan, None]:
        """Retrieve all details of a single name ban (qline).

        Args:
            name (str): name of the ban, eg *C*h*a*n*s*e*r*v*

        Returns:
            Union[ModelNameBan, None, bool]: The Object ModelNameBan, None if nothing see Error property
        """
        try:
            response = self.Connection.query(method='name_ban.get', param={"name": name})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                error = {"error": {"code": -1, "message": "Empty response"}}
                self.Connection.set_error(error)
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return None

            nameban = response['result']['tkl']

            objectNameBan = self.ModelNameBan(
                            type=nameban['type'] if 'type' in nameban else None,
                            type_string=nameban['type_string'] if 'type_string' in nameban else None,
                            set_by=nameban['set_by'] if 'set_by' in nameban else None,
                            set_at=nameban['set_at'] if 'set_at' in nameban else None,
                            expire_at=nameban['expier_at'] if 'expier_at' in nameban else None,
                            set_at_string=nameban['set_at_string'] if 'set_at_string' in nameban else None,
                            expire_at_string=nameban['expier_at_string'] if 'expier_at_string' in nameban else None,
                            duration_string=nameban['duration_string'] if 'duration_string' in nameban else None,
                            set_at_delta=nameban['set_at_delta'] if 'set_at_delta' in nameban else 0,
                            set_in_config=nameban['set_in_config'] if 'set_in_config' in nameban else False,
                            name=nameban['name'] if 'name' in nameban else None,
                            reason=nameban['reason'] if 'reason' in nameban else None
                            )

            return objectNameBan

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def add(self, name: str, reason: str, _set_by: str = None, _expire_at: str = None, _duration_string: str = None) -> bool:
        """Add a name ban (qline).

        Mandatory arguments (see structure of a name ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Name_ban#Structure_of_a_name_ban

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            reason (str): The reason of the ban
            _set_by (str, optional): Name of the person or server who set the ban. Default to None
            _expire_at (str, optional): Date/Time when the server ban will expire. NULL means: never. Default to None
            _duration_string (str, optional): How long the ban will last from this point in time (human printable). Uses "permanent" for forever. Default to None

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(
                method='name_ban.add', 
                param={"name": name, "reason": reason, "set_by": _set_by, "expire_at": _expire_at, "duration_string": _duration_string}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
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

    def del_(self, name: str, _set_by: str = None) -> bool:
        """Delete a name ban (LINE).

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            _set_by (str, optional): Name of the person or server who set the ban. Default to None

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(
                method='name_ban.del',
                param={"name": name, 'set_by': _set_by}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
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
