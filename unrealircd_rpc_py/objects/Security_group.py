from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class SecurityGroup:

    DB_SECURITY_GROUPS: list[Dfn.SecurityGroup] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self) -> list[Dfn.SecurityGroup]:
        """The list of all security groups

        Returns:
            list[SecurityGroup]: List of SecurityGroup objects
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'security_group.list'
                )
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_SECURITY_GROUPS.append(
                    Dfn.SecurityGroup(error=response_model.error)
                    )
                return self.DB_SECURITY_GROUPS

            _sgs = response_model.result.get('list', [])
            for _sg in _sgs:
                self.DB_SECURITY_GROUPS.append(Dfn.SecurityGroup(**_sg))

            return self.DB_SECURITY_GROUPS

        except KeyError as ke:
            self.Logs.error(f'Key error: {ke}')
            return self.DB_SECURITY_GROUPS

        except Exception as err:
            self.Logs.error(f'General error: {err}', exc_info=True)
            return self.DB_SECURITY_GROUPS

    def get(self, name: str) -> Dfn.SecurityGroup:
        """Retrieve a security group by name

        Args:
            name (str): The name of the SG you want to retrieve.
        Returns:
            SecurityGroup: The SG Object
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'security_group.get', {'name': name})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.SecurityGroup(error=response_model.error)

            _sg = Dfn.SecurityGroup(**response_model.result)
            return _sg

        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.SecurityGroup(
                error=Dfn.RPCErrorModel(-1, err.__str__())
                )
