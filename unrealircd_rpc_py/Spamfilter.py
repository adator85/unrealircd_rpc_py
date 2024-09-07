from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Spamfilter:

    @dataclass
    class ModelSpamfilter:
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
        match_type: str
        ban_action: str
        ban_duration: int
        ban_duration_string: str
        spamfilter_targets: str
        reason: str
        hits: int
        hits_except: int

    DB_SPAMFILTERS: list[ModelSpamfilter] = []


    def __init__(self, Connection: Connection) -> None:

        # Record the original response
        self.original_response: str = ''

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def list_(self) -> Union[list[ModelSpamfilter], None, bool]:
        """List spamfilters.

        Returns:
            Union[list[ModelSpamfilter], None, bool]: List of ModelSpamfilter, None if nothing or False if error
        """
        try:
            response = self.Connection.query(method='spamfilter.list')
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            spamfilters = response['result']['list']

            for spamfilter in spamfilters:
                self.DB_SPAMFILTERS.append(
                        self.ModelSpamfilter(
                            type=spamfilter['type'] if 'type' in spamfilter else None,
                            type_string=spamfilter['type_string'] if 'type_string' in spamfilter else None,
                            set_by=spamfilter['set_by'] if 'set_by' in spamfilter else None,
                            set_at=spamfilter['set_at'] if 'set_at' in spamfilter else None,
                            expire_at=spamfilter['expier_at'] if 'expier_at' in spamfilter else None,
                            set_at_string=spamfilter['set_at_string'] if 'set_at_string' in spamfilter else None,
                            expire_at_string=spamfilter['expier_at_string'] if 'expier_at_string' in spamfilter else None,
                            duration_string=spamfilter['duration_string'] if 'duration_string' in spamfilter else None,
                            set_at_delta=spamfilter['set_at_delta'] if 'set_at_delta' in spamfilter else 0,
                            set_in_config=spamfilter['set_in_config'] if 'set_in_config' in spamfilter else False,
                            name=spamfilter['name'] if 'name' in spamfilter else None,
                            match_type=spamfilter['match_type'] if 'match_type' in spamfilter else None,
                            ban_action=spamfilter['ban_action'] if 'ban_action' in spamfilter else None,
                            ban_duration=spamfilter['ban_duration'] if 'ban_duration' in spamfilter else 0,
                            ban_duration_string=spamfilter['ban_duration_string'] if 'ban_duration_string' in spamfilter else None,
                            spamfilter_targets=spamfilter['spamfilter_targets'] if 'spamfilter_targets' in spamfilter else None,
                            reason=spamfilter['reason'] if 'reason' in spamfilter else None,
                            hits=spamfilter['hits'] if 'hits' in spamfilter else 0,
                            hits_except=spamfilter['hits_except'] if 'hits_except' in spamfilter else 0
                            )
                )

            return self.DB_SPAMFILTERS

        except KeyError as ke:
            self.Logs.error(ke)
        except Exception as err:
            self.Logs.error(err)

    def get(self, name: str, match_type: str, ban_action: str, spamfilter_targets: str) -> Union[ModelSpamfilter, None, bool]:
        """Retrieve all details of a single spamfilter.

        Mandatory arguments (see structure of a spamfilter for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Spamfilter#Structure_of_a_spamfilter

        Args:
            name (str): The target of the ban or except. For Spamfilter this is the regex/matcher.
            match_type (str): Only for spamfilters! The matching type. One of: simple, regex
            ban_action (str): Only for spamfilters! The action to take on spamfilter hit.
            spamfilter_targets (str): Only for spamfilters! Which targets the spamfilter must filter on.

        Returns:
            Union[ModelSpamfilter, None, bool]: The Object ModelSpamfilter, None if nothing or False if error
        """
        try:
            response = self.Connection.query(method='spamfilter.get', param={"name": name, "match_type": match_type, "ban_action": ban_action, "spamfilter_targets": spamfilter_targets})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            spamfilter = response['result']['tkl']

            objectSpamfilter = self.ModelSpamfilter(
                            type=spamfilter['type'] if 'type' in spamfilter else None,
                            type_string=spamfilter['type_string'] if 'type_string' in spamfilter else None,
                            set_by=spamfilter['set_by'] if 'set_by' in spamfilter else None,
                            set_at=spamfilter['set_at'] if 'set_at' in spamfilter else None,
                            expire_at=spamfilter['expier_at'] if 'expier_at' in spamfilter else None,
                            set_at_string=spamfilter['set_at_string'] if 'set_at_string' in spamfilter else None,
                            expire_at_string=spamfilter['expier_at_string'] if 'expier_at_string' in spamfilter else None,
                            duration_string=spamfilter['duration_string'] if 'duration_string' in spamfilter else None,
                            set_at_delta=spamfilter['set_at_delta'] if 'set_at_delta' in spamfilter else 0,
                            set_in_config=spamfilter['set_in_config'] if 'set_in_config' in spamfilter else False,
                            name=spamfilter['name'] if 'name' in spamfilter else None,
                            match_type=spamfilter['match_type'] if 'match_type' in spamfilter else None,
                            ban_action=spamfilter['ban_action'] if 'ban_action' in spamfilter else None,
                            ban_duration=spamfilter['ban_duration'] if 'ban_duration' in spamfilter else 0,
                            ban_duration_string=spamfilter['ban_duration_string'] if 'ban_duration_string' in spamfilter else None,
                            spamfilter_targets=spamfilter['spamfilter_targets'] if 'spamfilter_targets' in spamfilter else None,
                            reason=spamfilter['reason'] if 'reason' in spamfilter else None,
                            hits=spamfilter['hits'] if 'hits' in spamfilter else 0,
                            hits_except=spamfilter['hits_except'] if 'hits_except' in spamfilter else 0
                        )

            return objectSpamfilter

        except KeyError as ke:
            self.Logs.error(ke)
        except Exception as err:
            self.Logs.error(err)

    def add(self, name: str, match_type: str, ban_action: str, ban_duration: int, spamfilter_targets: str, reason: str, _set_by: str = None) -> bool:
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
        response = self.Connection.query(
            method='spamfilter.add', 
            param={"name": name, "match_type": match_type, "ban_action": ban_action, "ban_duration": ban_duration, "spamfilter_targets": spamfilter_targets, 'reason': reason, 'set_by': _set_by}
            )

        self.original_response = response

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
        response = self.Connection.query(
            method='spamfilter.del',
            param={"name": name, "match_type": match_type, "ban_action": ban_action, "spamfilter_targets": spamfilter_targets, 'set_by': _set_by}
            )

        self.original_response = response

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
