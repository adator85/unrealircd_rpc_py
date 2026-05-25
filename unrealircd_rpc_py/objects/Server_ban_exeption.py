from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class ServerBanException:

    DB_SERVERS_BANS_EXCEPTION: list[Dfn.ServerBanException] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self) -> list[Dfn.ServerBanException]:
        """List server ban exceptions (ELINEs).

        Returns:
            list[ModelServerBanException]: List of ModelServerBanException,
                None if nothing see the Error property
        """
        try:
            self.DB_SERVERS_BANS_EXCEPTION = []
            response: dict[str, dict] = self.Connection.query(
                method='server_ban_exception.list')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_SERVERS_BANS_EXCEPTION.append(
                    Dfn.ServerBanException(error=response_model.error)
                )
                return self.DB_SERVERS_BANS_EXCEPTION

            srvbansexceps = response_model.result.get('list', {})

            for srvbansexcep in srvbansexceps:
                self.DB_SERVERS_BANS_EXCEPTION.append(
                        Dfn.ServerBanException(**srvbansexcep)
                )

            return self.DB_SERVERS_BANS_EXCEPTION

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, name: str) -> Dfn.ServerBanException:
        """Retrieve all details of a single server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation
        of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.

        Returns:
            ModelServerBanException (ModelServerBanException):
                The model ModelServerBanException Object
                | None if nothing see the Error property
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='server_ban_exception.get', param={'name': name})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.ServerBanException(error=response_model.error)

            srvbanexcep = response_model.result.get('tkl')

            obj = Dfn.ServerBanException(**srvbanexcep)

            return obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.ServerBanException(
                error=Dfn.RPCErrorModel(-1, ke.__str__())
            )
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.ServerBanException(
                error=Dfn.RPCErrorModel(-1, err.__str__())
            )

    def add(self, name: str, exception_types: str, reason: str,
            set_by: str = None, expire_at: str = None,
            duration_sting: str = None
            ) -> Dfn.RPCResult:
        """Add a server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation
        of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): user@host mask or extended server ban
            exception_types (str): eg k for a kline exception
            reason (str): The reason of the ban
            expire_at (str, optional): Date/Time when the server ban will
                expire. NULL means: never. Defaults to None.
            duration_sting (str, optional): How long the ban will last from
                this point in time (human printable).
                Uses "permanent" for forever. Defaults to None.
            set_by (str, optional): Name of the person or server who
                set the ban. Defaults to None.

        Returns:
            RPCResult: The RPCResult.
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='server_ban_exception.add',
                param={"name": name, "exception_types": exception_types,
                       "reason": reason, "expire_at": expire_at,
                       "duration_string": duration_sting, 'set_by': set_by})
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
        """Delete a server ban exception (ELINE).

        Mandatory arguments (see structure of a server ban for an explanation
        of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban_exception#Structure_of_a_server_ban_exception

        Args:
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.
            set_by (str, optional): Name of the person or server who
                set the ban. Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='server_ban_exception.del',
                param={"name": name, "set_by": set_by})
            response_model = utils.construct_rpc_response(response)
            print(response_model)

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
