from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Spamfilter:

    DB_SPAMFILTERS: list[Dfn.Spamfilter] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self) -> list[Dfn.Spamfilter]:
        """List spamfilters.

        Returns:
            list[Spamfilter]: List of Spamfilter, None if nothing,
                see Error property if any error
        """
        try:
            self.DB_SPAMFILTERS = []

            response: dict[str, dict] = self.Connection.query(
                method='spamfilter.list')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_SPAMFILTERS.append(
                    Dfn.Spamfilter(error=response_model.error)
                )
                return self.DB_SPAMFILTERS

            spamfilters = response_model.result.get('list', [])

            for spamfilter in spamfilters:
                self.DB_SPAMFILTERS.append(Dfn.Spamfilter(**spamfilter))

            return self.DB_SPAMFILTERS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, name: str, match_type: str, ban_action: str,
            spamfilter_targets: str) -> Dfn.Spamfilter:
        """Retrieve all details of a single spamfilter.

        Mandatory arguments (see structure of a spamfilter
        for an explanation of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Spamfilter#Structure_of_a_spamfilter

        Args:
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.
            match_type (str): Only for spamfilters! The matching type.
                One of: simple, regex
            ban_action (str): Only for spamfilters! The action to take on
                spamfilter hit.
            spamfilter_targets (str): Only for spamfilters!
                Which targets the spamfilter must filter on.

        Returns:
            Spamfilter: The Object Spamfilter. Could be empty if error
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='spamfilter.get',
                param={"name": name, "match_type": match_type,
                       "ban_action": ban_action,
                       "spamfilter_targets": spamfilter_targets})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.Spamfilter(error=response_model.error)

            spamfilter = response_model.result.get('tkl', {})

            object_spamfilter = Dfn.Spamfilter(**spamfilter)

            return object_spamfilter

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.Spamfilter(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.Spamfilter(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def add(self, name: str, match_type: str, ban_action: str,
            ban_duration: int, spamfilter_targets: str,
            reason: str, set_by: str = None) -> Dfn.RPCResult:
        """Add a spamfilter.

        Mandatory arguments (see structure of a spamfilter for an explanation
        of the fields):

        {"name":"regex123","match_type": "regex","ban_action": "gline",
        "ban_duration": 30, "spamfilter_targets": "cpnNPq",
        "reason": "RPC test"}

        https://www.unrealircd.org/docs/JSON-RPC:Spamfilter#Structure_of_a_spamfilter

        Args:
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.
            match_type (str): Only for spamfilters!
                The matching type. One of: simple, regex
            ban_action (str): Only for spamfilters!
                The action to take on spamfilter hit.
            ban_duration (int): The duration of the ban
            spamfilter_targets (str): Only for spamfilters!
                Which targets the spamfilter must filter on.
            reason (str): The reason of the ban
            set_by (str, optional): Name of the person or server who set the
                ban. Default to None

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='spamfilter.add',
                param={"name": name, "match_type": match_type,
                       "ban_action": ban_action,
                       "ban_duration": ban_duration,
                       "spamfilter_targets": spamfilter_targets,
                       "reason": reason, "set_by": set_by}
                )
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def del_(self,  name: str, match_type: str, ban_action: str,
             spamfilter_targets: str, _set_by: str = None) -> Dfn.RPCResult:
        """Delete a spamfilter.

        Mandatory arguments (see structure of a spamfilter for an explanation
        of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Spamfilter#Structure_of_a_spamfilter

        Args:
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.
            match_type (str): Only for spamfilters! The matching type.
                One of: simple, regex
            ban_action (str): Only for spamfilters! The action to take on
                spamfilter hit.
            spamfilter_targets (str): Only for spamfilters! Which targets
                the spamfilter must filter on.
            _set_by (str, optional): Name of the person or server who set the
                ban. Default to None

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='spamfilter.del',
                param={"name": name, "match_type": match_type,
                       "ban_action": ban_action,
                       "spamfilter_targets": spamfilter_targets,
                       "set_by": _set_by}
                )
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))
