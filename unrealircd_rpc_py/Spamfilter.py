from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Spamfilter:

    DB_SPAMFILTERS: list[dfn.Spamfilter] = []

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

    def list_(self) -> list[dfn.Spamfilter]:
        """List spamfilters.

        Returns:
            list[Spamfilter]: List of Spamfilter, None if nothing, see Error property if any error
        """
        try:
            self.Connection.EngineError.init_error()
            self.DB_SPAMFILTERS = []

            response = self.Connection.query(method='spamfilter.list')

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return self.DB_SPAMFILTERS

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return self.DB_SPAMFILTERS

            spamfilters = response['result']['list']

            for spamfilter in spamfilters:
                self.DB_SPAMFILTERS.append(dfn.Spamfilter(**spamfilter))

            return self.DB_SPAMFILTERS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return self.DB_SPAMFILTERS
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return self.DB_SPAMFILTERS

    def get(self, name: str, match_type: str, ban_action: str, spamfilter_targets: str) -> Union[dfn.Spamfilter, None]:
        """Retrieve all details of a single spamfilter.

        Mandatory arguments (see structure of a spamfilter for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Spamfilter#Structure_of_a_spamfilter

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            match_type (str): Only for spamfilters! The matching type. One of: simple, regex
            ban_action (str): Only for spamfilters! The action to take on spamfilter hit.
            spamfilter_targets (str): Only for spamfilters! Which targets the spamfilter must filter on.

        Returns:
            Spamfilter: The Object Spamfilter. Could be empty if error
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(method='spamfilter.get', param={"name": name, "match_type": match_type, "ban_action": ban_action, "spamfilter_targets": spamfilter_targets})

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

            spamfilter = response['result']['tkl']

            objectSpamfilter = dfn.Spamfilter(**spamfilter)

            return objectSpamfilter

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None

    def add(self, name: str, match_type: str, ban_action: str, ban_duration: int, spamfilter_targets: str, reason: str, set_by: str = None) -> bool:
        """Add a spamfilter.

        Mandatory arguments (see structure of a spamfilter for an explanation of the fields):

        {"name":"regex123","match_type": "regex","ban_action": "gline","ban_duration": 30,"spamfilter_targets": "cpnNPq","reason": "RPC test"}

        https://www.unrealircd.org/docs/JSON-RPC:Spamfilter#Structure_of_a_spamfilter

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            match_type (str): Only for spamfilters! The matching type. One of: simple, regex
            ban_action (str): Only for spamfilters! The action to take on spamfilter hit.
            ban_duration (int): The duration of the ban
            spamfilter_targets (str): Only for spamfilters! Which targets the spamfilter must filter on.
            reason (str): The reason of the ban
            _set_by (str, optional): Name of the person or server who set the ban. Default to None

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                method='spamfilter.add', 
                param={"name": name, "match_type": match_type, "ban_action": ban_action, "ban_duration": ban_duration, "spamfilter_targets": spamfilter_targets, 'reason': reason, 'set_by': set_by}
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

    def del_(self,  name: str, match_type: str, ban_action: str, spamfilter_targets: str, _set_by: str = None) -> bool:
        """Delete a spamfilter.

        Mandatory arguments (see structure of a spamfilter for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Spamfilter#Structure_of_a_spamfilter

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            match_type (str): Only for spamfilters! The matching type. One of: simple, regex
            ban_action (str): Only for spamfilters! The action to take on spamfilter hit.
            spamfilter_targets (str): Only for spamfilters! Which targets the spamfilter must filter on.
            _set_by (str, optional): Name of the person or server who set the ban. Default to None

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                method='spamfilter.del',
                param={"name": name, "match_type": match_type, "ban_action": ban_action, "spamfilter_targets": spamfilter_targets, 'set_by': _set_by}
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