from dataclasses import dataclass
from typing import Optional
from unrealircd_rpc_py.objects.Definition import MainModel
import unrealircd_rpc_py.utils.utils as utils
from datetime import datetime
from unrealircd_rpc_py.ConnectionFactory import ConnectionFactory
from unrealircd_rpc_py.connections.sync.IConnection import IConnection
from unrealircd_rpc_py.modules.tosql.database import Database
from unrealircd_rpc_py.modules.tosql.models import (
    Channel, ChannelMembers, Client, NameBan, User, Server, ClientServer
)


@dataclass
class RpcCredentialsHttp(MainModel):
    url: str = ''
    username: str = ''
    password: str = ''


class ToSql:
    """
    The ToSql class provides functionality to interact with an UnrealIRCd
    RPC server and transfer data from the RPC server into a SQL database.
    The class handles the connection to both the RPC server and the SQL
    database, and provides methods for transferring data related to clients,
    channels, name bans, and server-client relationships from the RPC server
    into the database.

    This class allows for seamless synchronization between UnrealIRCd's
    internal state (via JSON-RPC) and a relational database.

    Attributes:
        _date_format (str): The date format used for parsing datetime fields
            from the RPC server.
        _engine_name (str): The name of the database engine
            (e.g., 'sqlite', 'mysql', 'postgresql').
        logs (Logger): A logger instance for logging relevant information
            and errors.
        _db_debug (bool): Flag to enable/disable debug logging for the
            database connection.
        _db_hostname (Optional[str]): The hostname of the database server.
        _db_port (Optional[int]): The port number to connect to the database.
        _db_username (Optional[str]): The username to authenticate
            with the database.
        _db_password (Optional[str]): The password for the database username.
        _db_name (Optional[str]): The name of the database to connect to.
        _sql (Optional[Database]): The database connection instance.
        _rpc (Optional[IConnection]): The RPC connection instance for
            communicating with UnrealIRCd.
        __rpc_credentials (RpcCredentialsHttp): The credentials used to
            authenticate the RPC connection.
        _rpc_connected (bool): Flag indicating whether the RPC
            connection is established.
        _sql_connected (bool): Flag indicating whether the SQL
            connection is established.

    Methods:
        run() -> bool:
            Establishes connections to both the RPC server and the SQL
            database, and then transfers the data from the RPC server
            to the SQL database by calling other methods for different
            data types (e.g., channels, clients, name bans, etc.).

        channel_tosql() -> bool:
            Transfers channel and channel member data from the RPC server
            to the SQL database.

        client_tosql() -> bool:
            Transfers client and user data from the RPC server to the
            SQL database.

        nameban_tosql() -> bool:
            Transfers name ban data from the RPC server to the SQL database.

        client_server_tosql() -> bool:
            Transfers server and client-server relationship data from the
            RPC server to the SQL database.

        _rpc_connect() -> IConnection:
            Establishes the RPC connection and sets up the issuer
            for authentication.

        _sql_connect() -> Database:
            Establishes the SQL database connection and initializes it.

    Properties:
        rpc_credentials (RpcCredentialsHttp):
            Returns the current RPC credentials for connection.
    """

    def __init__(self, engine_name: str,
                 db_hostname: Optional[str] = None,
                 db_username: Optional[str] = None,
                 db_password: Optional[str] = None,
                 db_name: Optional[str] = None,
                 db_port: Optional[int] = 0,
                 db_debug: bool = False,
                 debug_level: int = 20):
        """The ToSql class provides functionality to interact with an
        UnrealIRCd RPC server and transfer data from the RPC server into a SQL
        database. The class handles the connection to both the RPC server
        and the SQL database, and provides methods for transferring data
        related to clients, channels, name bans, and server-client
        relationships from the RPC server into the database.

        This class allows for seamless synchronization between UnrealIRCd's
        internal state (via JSON-RPC) and a relational database.

        Args:
            engine_name (str): The engine name (ex. sqlite, mysql, postgresql)
            db_hostname (str, optional): Hostname to connect the database.
                                         Defaults to None.
            db_port (int, optional): The Database port
                    if set to 0 the default port of the selected engine name
                    will be set. Defaults to 0.
            db_username (str, optional): The Database username.
                    Defaults to None.
            db_password (str, optional): The password of the username.
                    Defaults to None.
            db_name (str, optional): The database name. Defaults to None.
            db_debug (bool, optional): The debug flag. Defaults to False.
        """
        self._date_format: str = '%Y-%m-%dT%H:%M:%S.%fZ'
        self._engine_name = engine_name
        self.logs = utils.start_log_system(
            'unrealircd-rpc-py-sql', debug_level
            )

        # Credentials setup
        self._db_debug = db_debug
        self._db_hostname = db_hostname
        self._db_port = db_port
        self._db_username = db_username
        self._db_password = db_password
        self._db_name = db_name

        # create sql object
        self._sql: Optional[Database] = None

        # Create Rpc object
        self._rpc: Optional[IConnection] = None
        self.__rpc_credentials: RpcCredentialsHttp = RpcCredentialsHttp()

        # Are servers connected
        self._rpc_connected = False

    def _rpc_connect(self) -> IConnection:
        try:
            # Init the rpc object
            rpc = ConnectionFactory().get('http')

            # Setup the rpc connection.
            rpc.setup(self.rpc_credentials.to_dict())

            # Set the issuer:
            rpc.Rpc.set_issuer('ircd_rpc_sql')

            # Connection established.
            self._rpc_connected = True

            return rpc
        except Exception as err:
            self.logs.error(f"API Error On JSONRPC Server: {err}")

    def _sql_connect(self) -> Database:
        _sql = Database(
            self._engine_name,
            db_hostname=self._db_hostname,
            db_port=self._db_port,
            db_username=self._db_username,
            db_password=self._db_password,
            db_name=self._db_name,
            db_debug=self._db_debug
        )
        _sql.db_init()
        return _sql

    def run(self) -> bool:
        self._rpc = self._rpc_connect()
        self._sql = self._sql_connect()

        if not self._rpc_connected:
            self.logs.critical("The JSON-RPC Server is down!")
            return False

        if not self._sql.connected:
            self.logs.critical("The SQL Connection is down!")
            return False

        if self._sql.connected and self._rpc_connected:
            self.client_tosql()
            self.channel_tosql()
            self.nameban_tosql()
            self.client_server_tosql()
            return True

        return False

    def channel_tosql(self) -> bool:

        rpc = self._rpc
        sql = self._sql

        dbmodels: list[Channel] = []
        db_chanmember_models: list[ChannelMembers] = []

        # Use User object
        rpc_channels = rpc.Channel.list_(4)

        # Empty
        sql.delete_obj_from_db(sql.delete(Channel))
        sql.delete_obj_from_db(sql.delete(ChannelMembers))

        for rpc_channel in rpc_channels:
            _c = rpc_channel.to_dict()
            c_id = utils.generate_ids()

            if not isinstance(_c['creation_time'], datetime):
                _c['creation_time'] = datetime.strptime(
                    _c['creation_time'],
                    self._date_format
                    ) if _c['creation_time'] is not None else None

            keys_pop = ['bans', 'ban_exemptions',
                        'invite_exceptions', 'members',
                        'error']
            channel_members = rpc_channel.members
            [_c.pop(keypop) for keypop in keys_pop]

            for chan_member in channel_members:
                _cm = chan_member.to_dict()
                [_cm.pop(keypop) for keypop in ['geoip', 'user', 'tls']]
                _cm['channel_id'] = c_id
                db_chanmember_models.append(ChannelMembers(**_cm))

            dbmodels.append(Channel(channel_id=c_id, **_c))

        # Extend the final list of objects
        dbmodels.extend(db_chanmember_models)

        if sql.insert_multiple_objs_to_db(dbmodels):
            sql.logs.debug(
                'Channels and Channel Members inserted into database!'
                )
            return True

        return False

    def client_tosql(self) -> bool:

        rpc = self._rpc
        sql = self._sql

        dbmodels: list[Client] = []
        db_user_models: list[User] = []

        # Use User object
        rpc_clients = rpc.User.list_(4)

        # Empty
        sql.delete_obj_from_db(sql.delete(Client))

        for rpc_client in rpc_clients:
            _c = rpc_client.to_dict()

            if not isinstance(_c['connected_since'], datetime):
                _c['connected_since'] = datetime.strptime(
                    _c['connected_since'], self._date_format
                    ) if _c['connected_since'] is not None else None
                _c['idle_since'] = datetime.strptime(
                    _c['idle_since'], self._date_format
                    ) if _c['idle_since'] is not None else None

            keys_pop = ['geoip', 'tls', 'user', 'error']
            _user = rpc_client.user
            _user.security_groups = '; '.join(_user.security_groups)
            _user.channels = '; '.join([c.name for c in _user.channels])
            [_c.pop(keypop) for keypop in keys_pop]

            _dict_user = _user.to_dict()
            if not isinstance(_dict_user['away_since'], datetime):
                _dict_user['away_since'] = datetime.strptime(
                    _dict_user['away_since'], self._date_format
                    ) if _dict_user['away_since'] is not None else None

            dbmodels.append(Client(**_c))
            db_user_models.append(User(id=rpc_client.id, **_dict_user))

        dbmodels.extend(db_user_models)

        if sql.insert_multiple_objs_to_db(dbmodels):
            sql.logs.debug('Client & Users have been inserted into database!')
            return True

        return False

    def nameban_tosql(self) -> bool:

        rpc = self._rpc
        sql = self._sql
        dbmodels: list[NameBan] = []

        # Use User object
        rpc_nbs = rpc.Name_ban.list_()

        # Empty
        sql.delete_obj_from_db(sql.delete(NameBan))

        for rpc_nb in rpc_nbs:
            _c = rpc_nb.to_dict()

            if not isinstance(_c['set_at'], datetime):
                _c['set_at'] = datetime.strptime(
                    _c['set_at'], self._date_format
                    ) if _c['set_at'] is not None else None
                _c['expire_at'] = datetime.strptime(
                    _c['expire_at'], self._date_format
                    ) if _c['expire_at'] is not None else None

            keys_pop = ['error']
            [_c.pop(keypop) for keypop in keys_pop]

            dbmodels.append(NameBan(**_c))

        if sql.insert_multiple_objs_to_db(dbmodels):
            sql.logs.debug('Name Bans have been inserted into database!')
            return True

        return False

    def client_server_tosql(self) -> bool:
        rpc = self._rpc
        sql = self._sql
        db_clientserver_models: list[ClientServer] = []
        db_server_models: list[Server] = []

        # Use User object
        rpc_servs = rpc.Server.list_()

        # Empty
        sql.delete_obj_from_db(sql.delete(ClientServer))
        sql.delete_obj_from_db(sql.delete(Server))

        for rpc_cserv in rpc_servs:
            _cs = rpc_cserv.to_dict()

            if not isinstance(_cs['connected_since'], datetime):
                _cs['connected_since'] = datetime.strptime(
                    _cs['connected_since'], self._date_format
                    ) if _cs['connected_since'] is not None else None
                _cs['idle_since'] = datetime.strptime(
                    _cs['idle_since'], self._date_format
                    ) if _cs['idle_since'] is not None else None

            _server = rpc_cserv.server.to_dict()
            if not isinstance(_server['boot_time'], datetime):
                _server['boot_time'] = datetime.strptime(
                    _server['boot_time'], self._date_format
                    ) if _server['boot_time'] is not None else None

            keys_pop = ['server', 'error', 'tls']
            [_cs.pop(keypop) for keypop in keys_pop]

            db_clientserver_models.append(ClientServer(**_cs))

            keys_pop = ['features']
            [_server.pop(keypop) for keypop in keys_pop]
            db_server_models.append(Server(id=rpc_cserv.id, **_server))

        db_clientserver_models.extend(db_server_models)
        if sql.insert_multiple_objs_to_db(db_clientserver_models):
            sql.logs.debug(
                'Client Server & Server have been inserted into database!'
                )
            return True

        return False

    @property
    def rpc_credentials(self) -> RpcCredentialsHttp:
        return self.__rpc_credentials
