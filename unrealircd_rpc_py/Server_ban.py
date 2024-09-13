from types import SimpleNamespace
from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Server_ban:

    @dataclass
    class ModelServerBan:
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

    DB_SERVERS_BANS: list[ModelServerBan] = []

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

    def list_(self) -> Union[list[ModelServerBan], None, bool]:
        """List server bans (LINEs).

        Returns:
            Union[list[ModelServerBan], None, bool]: List of ModelServerBan, None if nothing or False if error
        """
        try:
            response = self.Connection.query(method='server_ban.list')

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            srvbans = response['result']['list']

            for srvban in srvbans:
                self.DB_SERVERS_BANS.append(
                        self.ModelServerBan(
                            type=srvban['type'] if 'type' in srvban else None,
                            type_string=srvban['type_string'] if 'type_string' in srvban else None,
                            set_by=srvban['set_by'] if 'set_by' in srvban else None,
                            set_at=srvban['set_at'] if 'set_at' in srvban else None,
                            expire_at=srvban['expire_at'] if 'expire_at' in srvban else None,
                            set_at_string=srvban['set_at_string'] if 'set_at_string' in srvban else None,
                            expire_at_string=srvban['expire_at_string'] if 'expire_at_string' in srvban else None,
                            duration_string=srvban['duration_string'] if 'duration_string' in srvban else None,
                            set_at_delta=srvban['set_at_delta'] if 'set_at_delta' in srvban else 0,
                            set_in_config=srvban['set_in_config'] if 'set_in_config' in srvban else None,
                            name=srvban['name'] if 'name' in srvban else None,
                            reason=srvban['reason'] if 'reason' in srvban else None
                        )
                )

            return self.DB_SERVERS_BANS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def get(self, type: str, name: str) -> Union[ModelServerBan, None, bool]:
        """Retrieve all details of a single server ban (LINE).

        Args:
            type (str): Type of the server ban. One of: gline, kline, gzline, zline, spamfilter, qline, except, shun, local-qline, local-exception, local-spamfilter.
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.

        Returns:
            Union[ModelServerBan, None, bool]: The model Object | None if nothing happen | False if an error
        """
        try:
            response = self.Connection.query(method='server_ban.get', param={'type': type, 'name': name})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            srvban = response['result']['tkl']

            objectChannel = self.ModelServerBan(
                            type=srvban['type'] if 'type' in srvban else None,
                            type_string=srvban['type_string'] if 'type_string' in srvban else None,
                            set_by=srvban['set_by'] if 'set_by' in srvban else None,
                            set_at=srvban['set_at'] if 'set_at' in srvban else None,
                            expire_at=srvban['expire_at'] if 'expire_at' in srvban else None,
                            set_at_string=srvban['set_at_string'] if 'set_at_string' in srvban else None,
                            expire_at_string=srvban['expire_at_string'] if 'expire_at_string' in srvban else None,
                            duration_string=srvban['duration_string'] if 'duration_string' in srvban else None,
                            set_at_delta=srvban['set_at_delta'] if 'set_at_delta' in srvban else 0,
                            set_in_config=srvban['set_in_config'] if 'set_in_config' in srvban else None,
                            name=srvban['name'] if 'name' in srvban else None,
                            reason=srvban['reason'] if 'reason' in srvban else None
                        )

            return objectChannel

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def add(self, type: str, name: str, reason: str, expire_at: str, duration_sting: str, _set_by: str = None) -> bool:
        """Add a server ban (LINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban#Structure_of_a_server_ban

        Args:
            type (str): Type of the server ban. One of: gline, kline, gzline, zline, spamfilter, qline, except, shun, local-qline, local-exception, local-spamfilter.
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            reason (str): The reason of the ban
            expire_at (str): Date/Time when the server ban will expire. NULL means: never.
            duration_sting (str): How long the ban will last from this point in time (human printable). Uses "permanent" for forever.
            _set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(method='server_ban.add', param={"type": type, "name": name, "reason": reason, "expire_at": expire_at, "duration_string": duration_sting, 'set_by': _set_by})

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

    def del_(self, type: str, name: str, _set_by: str = None) -> bool:
        """Delete a server ban (LINE).

        Mandatory arguments (see structure of a server ban for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban#Structure_of_a_server_ban

        Args:
            type (str): Type of the server ban. One of: gline, kline, gzline, zline, spamfilter, qline, except, shun, local-qline, local-exception, local-spamfilter.
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            _set_by (str, optional): Name of the person or server who set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(method='server_ban.del', param={"type": type, "name": name, 'set_by': _set_by})

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
