"""
Message object for UnrealIRCd JSON-RPC
Minimum Unrealircd version: 6.2.2
"""
from typing import TYPE_CHECKING, Literal, Optional
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Message:

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def send_privmsg(self, nickoruid: str, message: str) -> Dfn.RPCResult:
        """This sends a PRIVMSG to a user.

        Args:
            nickoruid (str): User to send the message to (Nick or UID)
            message (str): The message to send

        Returns:
            RPCResult ([Dfn.RPCResult]): Returns RPCResult if the message
                was sent.
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'message.send_privmsg',
                {'nick': nickoruid, 'message': message}
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

    def send_notice(self, nickoruid: str, message: str) -> Dfn.RPCResult:
        """This sends a NOTICE to a user.

        Args:
            nickoruid (str): User to send the message to (Nick or UID)
            message (str): The message to send

        Returns:
            RPCResult ([Dfn.RPCResult]): Returns RPCResult if the message
                was sent.
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'message.send_notice',
                {'nick': nickoruid, 'message': message})
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

    def send_numeric(self, nickoruid: str, numeric: int, message: str
                     ) -> Dfn.RPCResult:
        """This sends an IRC numeric to a user.

        Args:
            nickoruid (str): User to send the message to (Nick or UID)
            numeric (int): Numeric to send (1-999)
            message (str): The message to send

        Returns:
            RPCResult ([Dfn.RPCResult]): Returns RPCResult if the message
                was sent.
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='message.send_numeric',
                param={'nick': nickoruid, 'numeric': numeric,
                       'message': message}
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

    def send_standard_reply(self, nickoruid: str,
                            type_: Literal['FAIL', 'WARN', 'NOTE'],
                            code: str,
                            description: str,
                            context: Optional[str] = None) -> Dfn.RPCResult:
        """This sends an IRC standard reply to a user

        Link to standard reply:
        https://ircv3.net/specs/extensions/standard-replies

        Args:
            nickoruid (str): User to send the message to (Nick or UID)
            type_ (str): FAIL, WARN or NOTE
            code (str): Machine-readable reply code representing the meaning
                of the message to client software
            description (str): Description of the reply which is shown to
                users.
            context (str, optional) : The context

        Returns:
            RPCResult ([Dfn.RPCResult]): Returns RPCResult if the message
                was sent.
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='message.send_standard_reply',
                param={'nick': nickoruid, 'type': type_, 'code': code,
                       'description': description, 'context': context})
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
