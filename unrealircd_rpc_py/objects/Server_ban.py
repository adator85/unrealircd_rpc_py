from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class ServerBan:

    DB_SERVERS_BANS: list[Dfn.ServerBan] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self) -> list[Dfn.ServerBan]:
        """List server bans (LINEs).

        Returns:
            list[ServerBan]: List of ServerBan, if empty see Error Object
        """
        try:
            self.DB_SERVERS_BANS = []
            response: dict[str, dict] = self.Connection.query(
                method='server_ban.list')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_SERVERS_BANS.append(
                    Dfn.ServerBan(error=response_model.error)
                )
                return self.DB_SERVERS_BANS

            srvbans: list[dict] = response_model.result.get('list', [])

            for srvban in srvbans:
                self.DB_SERVERS_BANS.append(Dfn.ServerBan(**srvban))

            return self.DB_SERVERS_BANS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, query_type: str, name: str) -> Dfn.ServerBan:
        """Retrieve all details of a single server ban (LINE).

        Args:
            query_type (str): Type of the server ban. One of: gline, kline,
                gzline, zline, spamfilter, qline, except, shun, local-qline,
                local-exception, local-spamfilter.
            name (str): The target of the ban or except. For Spamfilter this
                is the regex/matcher.

        Returns:
            ServerBan (ServerBan): The ServerBan model Object
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='server_ban.get',
                param={'type': query_type, 'name': name})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.ServerBan(error=response_model.error)

            srvban: dict = response_model.result.get('tkl', {})

            obj = Dfn.ServerBan(**srvban)

            return obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.ServerBan(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.ServerBan(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def add(self, query_type: str, name: str, reason: str, expire_at: str,
            duration_sting: str, set_by: str = None) -> Dfn.RPCResult:
        """Add a server ban (LINE).

        Mandatory arguments (see structure of a server ban for an explanation
        of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban#Structure_of_a_server_ban

        Args:
            query_type (str): Type of the server ban. One of: gline, kline,
                gzline, zline, spamfilter, qline, except, shun, local-qline,
                local-exception, local-spamfilter.
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.
            reason (str): The reason of the ban
            expire_at (str): Date/Time when the server ban will expire.
                NULL means: never.
            duration_sting (str): How long the ban will last from this point
                in time (human printable). Uses "permanent" for forever.
            set_by (str, optional): Name of the person or server who set the
                ban. Defaults to None.

        Returns:
            RPCResult: The RPCResult Model
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='server_ban.add',
                param={"type": query_type, "name": name, "reason": reason,
                       "expire_at": expire_at,
                       "duration_string": duration_sting,
                       "set_by": set_by}
            )
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.ServerBan(error=response_model.error)

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.ServerBan(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.ServerBan(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def del_(self, query_type: str, name: str, set_by: str = None
             ) -> Dfn.RPCResult:
        """Delete a server ban (LINE).

        Mandatory arguments (see structure of a server ban for an explanation
        of the fields):

        https://www.unrealircd.org/docs/JSON-RPC:Server_ban#Structure_of_a_server_ban

        Args:
            query_type (str): Type of the server ban. One of: gline, kline,
                gzline, zline, spamfilter, qline, except, shun, local-qline,
                local-exception, local-spamfilter.
            name (str): The target of the ban or except.
                For Spamfilter this is the regex/matcher.
            set_by (str, optional): Name of the person or server who
                set the ban. Defaults to None.

        Returns:
            RPCResult: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='server_ban.del',
                param={"type": query_type, "name": name, "set_by": set_by})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.ServerBan(error=response_model.error)

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.ServerBan(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.ServerBan(error=Dfn.RPCErrorModel(-1, err.__str__()))
