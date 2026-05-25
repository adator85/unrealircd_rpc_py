from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class NameBan:

    DB_NAME_BANS: list[Dfn.NameBan] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self) -> list[Dfn.NameBan]:
        """List name bans (qlines).

        Returns:
            ModelNameBan: List of ModelNameBan, None if nothing see Error
                property
        """
        try:
            self.DB_NAME_BANS = []
            response: dict[str, dict] = self.Connection.query('name_ban.list')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_NAME_BANS.append(
                    Dfn.NameBan(error=response_model.error)
                )
                return self.DB_NAME_BANS

            namebans: list[dict] = response.get('result', {}).get('list', [])

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

    def get(self, name: str) -> Dfn.NameBan:
        """Retrieve all details of a single name ban (qline).

        Args:
            name (str): name of the ban, eg *C*h*a*n*s*e*r*v*

        Returns:
            Union[ModelNameBan, None, bool]: The Object ModelNameBan, None if
                nothing see Error property
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='name_ban.get', param={"name": name}
            )
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.NameBan(error=response_model.error)

            nameban = response_model.result.get('tkl', {})

            obj = Dfn.NameBan(**nameban)

            return obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.NameBan(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.NameBan(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def add(self, name: str, reason: str, set_by: str = None,
            expire_at: str = None, duration_string: str = None
            ) -> Dfn.RPCResult:
        """Add a name ban (qline).

        Mandatory arguments (see structure of a name ban for an explanation
        of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Name_ban#Structure_of_a_name_ban

        Args:
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.
            reason (str): The reason of the ban
            set_by (str, optional): Name of the person or server who
                set the ban. Default to None
            expire_at (str, optional): Date/Time when the server ban will
                expire. NULL means: never. Default to None
            duration_string (str, optional): How long the ban will last from
                this point in time (human printable). Uses "permanent"
                for forever. Default to None

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='name_ban.add',
                param={"name": name, "reason": reason, "set_by": set_by,
                       "expire_at": expire_at,
                       "duration_string": duration_string}
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

    def del_(self, name: str, set_by: str = None) -> Dfn.RPCResult:
        """Delete a name ban (LINE).

        Args:
            name (str): The target of the ban or except. For Spamfilter this
                is the regex/matcher.
            set_by (str, optional): Name of the person or server who set
                the ban. Default to None

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='name_ban.del',
                param={"name": name, 'set_by': set_by}
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
