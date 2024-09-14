from types import SimpleNamespace
from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Server_ban_exception:

    @dataclass
    class ModelServerBanException:
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
        exception_types: str

    DB_SERVERS_BANS_EXCEPTION: list[ModelServerBanException] = []

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

    def list_(self) -> Union[list[ModelServerBanException], None]:
        """List server ban exceptions (ELINEs).

        Returns:
            list[ModelServerBanException]: List of ModelServerBanException, None if nothing see the Error property
        """
        try:
            response = self.Connection.query(method='server_ban_exception.list')

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

            srvbansexceps = response['result']['list']

            for srvbansexcep in srvbansexceps:
                self.DB_SERVERS_BANS_EXCEPTION.append(
                        self.ModelServerBanException(
                            type=srvbansexcep['type'] if 'type' in srvbansexcep else None,
                            type_string=srvbansexcep['type_string'] if 'type_string' in srvbansexcep else None,
                            set_by=srvbansexcep['set_by'] if 'set_by' in srvbansexcep else None,
                            set_at=srvbansexcep['set_at'] if 'set_at' in srvbansexcep else None,
                            expire_at=srvbansexcep['expire_at'] if 'expire_at' in srvbansexcep else None,
                            set_at_string=srvbansexcep['set_at_string'] if 'set_at_string' in srvbansexcep else None,
                            expire_at_string=srvbansexcep['expire_at_string'] if 'expire_at_string' in srvbansexcep else None,
                            duration_string=srvbansexcep['duration_string'] if 'duration_string' in srvbansexcep else None,
                            set_at_delta=srvbansexcep['set_at_delta'] if 'set_at_delta' in srvbansexcep else 0,
                            set_in_config=srvbansexcep['set_in_config'] if 'set_in_config' in srvbansexcep else None,
                            name=srvbansexcep['name'] if 'name' in srvbansexcep else None,
                            reason=srvbansexcep['reason'] if 'reason' in srvbansexcep else None,
                            exception_types=srvbansexcep['exception_types'] if 'exception_types' in srvbansexcep else None
                        )
                )

            return self.DB_SERVERS_BANS_EXCEPTION

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def get(self, name: str) -> Union[ModelServerBanException, None]:
        """Retrieve all details of a single server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.

        Returns:
            ModelServerBanException (ModelServerBanException): The model ModelServerBanException Object | None if nothing see the Error property
        """
        try:
            response = self.Connection.query(method='server_ban_exception.get', param={'name': name})

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

            srvbanexcep = response['result']['tkl']

            objectServBanExcep = self.ModelServerBanException(
                            type=srvbanexcep['type'] if 'type' in srvbanexcep else None,
                            type_string=srvbanexcep['type_string'] if 'type_string' in srvbanexcep else None,
                            set_by=srvbanexcep['set_by'] if 'set_by' in srvbanexcep else None,
                            set_at=srvbanexcep['set_at'] if 'set_at' in srvbanexcep else None,
                            expire_at=srvbanexcep['expire_at'] if 'expire_at' in srvbanexcep else None,
                            set_at_string=srvbanexcep['set_at_string'] if 'set_at_string' in srvbanexcep else None,
                            expire_at_string=srvbanexcep['expire_at_string'] if 'expire_at_string' in srvbanexcep else None,
                            duration_string=srvbanexcep['duration_string'] if 'duration_string' in srvbanexcep else None,
                            set_at_delta=srvbanexcep['set_at_delta'] if 'set_at_delta' in srvbanexcep else 0,
                            set_in_config=srvbanexcep['set_in_config'] if 'set_in_config' in srvbanexcep else None,
                            name=srvbanexcep['name'] if 'name' in srvbanexcep else None,
                            reason=srvbanexcep['reason'] if 'reason' in srvbanexcep else None,
                            exception_types=srvbanexcep['exception_types'] if 'exception_types' in srvbanexcep else None
                        )

            return objectServBanExcep

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def add(self, name: str, exception_types: str, reason: str, _set_by: str = None, _expire_at: str = None, _duration_sting: str = None) -> bool:
        """Add a server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): user@host mask or extended server ban
            exception_types (str): eg k for a kline exception
            reason (str): The reason of the ban
            expire_at (str, optional): Date/Time when the server ban will expire. NULL means: never. Defaults to None.
            duration_sting (str, optional): How long the ban will last from this point in time (human printable). Uses "permanent" for forever. Defaults to None.
            _set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(method='server_ban_exception.add', param={"name": name, "exception_types": exception_types, "reason": reason, "expire_at": _expire_at, "duration_string": _duration_sting, 'set_by': _set_by})

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
        """Delete a server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            _set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(method='server_ban_exception.del', param={"name": name, 'set_by': _set_by})

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
