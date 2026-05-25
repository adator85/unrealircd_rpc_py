from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.inspection import inspect


class ToDict:
    def to_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }


Base = declarative_base(cls=ToDict)
_prefix = 'unrealircd_'


class Channel(Base):
    __tablename__ = f'{_prefix}channels'
    channel_id: str = Column(String(32), unique=True, primary_key=True)
    name: str = Column(String(32), nullable=False)
    creation_time: datetime = Column(DateTime, nullable=False)
    num_users: int = Column(Integer, nullable=False)
    topic: str = Column(String(255))
    topic_set_by: str = Column(String(255))
    topic_set_at: str = Column(String(255))
    modes: str = Column(String(32))


class ChannelMembers(Base):
    __tablename__ = f'{_prefix}channel_members'
    cm_id: str = Column(
        Integer, autoincrement=True, unique=True, primary_key=True
        )
    channel_id: str = Column(
        String(32), ForeignKey(
            f'{_prefix}channels', name='fk_channel_id', ondelete='CASCADE'
            )
        )
    id: str = Column(
        String(9), ForeignKey(f'{_prefix}clients', name='fk_client_2_id')
        )
    name: str = Column(String(32), nullable=False)
    hostname: str = Column(String(32))
    level: str = Column(String(32))
    ip: str = Column(String(64))
    details: str = Column(String(255))
    connected_since: datetime = Column(DateTime)
    idle_since: datetime = Column(DateTime)
    server_port: int = Column(Integer)
    client_port: int = Column(Integer)

    # Establish relationship from the Nickname side to the Account
    channel = relationship("Channel")
    client = relationship("Client")


class Client(Base):
    __tablename__ = f'{_prefix}clients'
    id: str = Column(String(9), primary_key=True, unique=True)
    name: str = Column(String(32), nullable=False)
    hostname: str = Column(String(32), nullable=False)
    ip: str = Column(String(32), nullable=False)
    details: str = Column(String(255))
    server_port: int = Column(Integer)
    client_port: int = Column(Integer)
    connected_since: str = Column(DateTime)
    idle_since: str = Column(DateTime)
    country_code: str = Column(String(2))


class User(Base):
    __tablename__ = f'{_prefix}users'
    sys_id: str = Column(
        Integer, autoincrement=True, unique=True, primary_key=True
        )
    id: str = Column(
        String(9), ForeignKey(
            f'{_prefix}clients', name='fk_client_id', ondelete='CASCADE'
            )
        )
    username: str = Column(String(32), nullable=False)
    realname: str = Column(String(32), nullable=False)
    vhost: str = Column(String(100))
    cloakedhost: str = Column(String(100))
    servername: str = Column(String(100))
    account: str = Column(String(100))
    reputation: int = Column(Integer)
    security_groups: str = Column(String(255))
    away_reason: str = Column(String(255))
    away_since: datetime = Column(DateTime)
    modes: str = Column(String(100))
    snomasks: str = Column(String(100))
    operlogin: str = Column(String(100))
    operclass: str = Column(String(100))
    channels: str = Column(String(255))

    # Establish relationship from the Nickname side to the Account
    client = relationship("Client")


class NameBan(Base):
    __tablename__ = f'{_prefix}namebans'
    sys_id: str = Column(
        Integer, autoincrement=True, unique=True, primary_key=True
        )
    type: str = Column(String(100))
    type_string: str = Column(String(100))
    set_by: str = Column(String(100))
    set_at: datetime = Column(DateTime)
    expire_at: datetime = Column(DateTime)
    set_at_string: str = Column(String(100))
    expire_at_string: str = Column(String(100))
    duration_string: str = Column(String(100))
    set_at_delta: int = Column(Integer)
    set_in_config: bool = Column(Boolean)
    name: str = Column(String(100))
    reason: str = Column(String(100))


class Server(Base):
    __tablename__ = f'{_prefix}servers'
    sys_id: str = Column(
        Integer, autoincrement=True, unique=True, primary_key=True
        )
    id: str = Column(
        String(9),
        ForeignKey(f'{_prefix}clientservers',
                   name='fk_clientserver_id',
                   ondelete='CASCADE')
        )
    info: str = Column(String(255))
    uplink: str = Column(String(100))
    num_users: int = Column(Integer)
    boot_time: datetime = Column(DateTime)
    synced: bool = Column(Boolean)
    ulined: bool = Column(Boolean)

    # Establish relationship from the Nickname side to the Account
    clientserver = relationship("ClientServer")


class ClientServer(Base):
    __tablename__ = f'{_prefix}clientservers'
    id: str = Column(String(32), unique=True, primary_key=True)
    name: str = Column(String(100))
    hostname: str = Column(String(100))
    ip: str = Column(String(100))
    details: str = Column(String(100))
    server_port: int = Column(Integer)
    client_port: int = Column(Integer)
    connected_since: datetime = Column(DateTime)
    idle_since: datetime = Column(DateTime)
