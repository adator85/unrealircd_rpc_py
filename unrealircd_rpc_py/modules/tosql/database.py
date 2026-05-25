import logging
import time
import traceback
import unrealircd_rpc_py.modules.tosql.models as model
import pathlib
from typing import TYPE_CHECKING, Any, Optional, Union
from sqlalchemy import (create_engine,
                        Connection, Result, event,
                        select, update, delete)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.sql import text
from sqlalchemy.exc import NoResultFound

if TYPE_CHECKING:
    from sqlalchemy import Delete, Select, Update, Sequence, RowMapping


class Database:

    def __init__(self, engine_name: str, *,
                 db_hostname: Optional[str] = None,
                 db_username: Optional[str] = None,
                 db_password: Optional[str] = None,
                 db_name: Optional[str] = None,
                 db_port: Optional[int] = 0,
                 db_debug: bool = False):
        """Init the database object

        Args:
            engine_name (str): The engine name (ex. sqlite, mysql, postgresql)
            db_hostname (str, optional): Hostname to connect the database.
                Defaults to None.
            db_port (int, optional): The Database port if set to 0 the default
                port of the selected engine name will be set. Defaults to 0.
            db_username (str, optional): The Database username.
                Defaults to None.
            db_password (str, optional): The password of the username.
                Defaults to None.
            db_name (str, optional): The database name. Defaults to None.
            db_debug (bool, optional): The debug flag. Defaults to False.
        """
        self.__engine: Optional[Engine] = None
        self.__scoped_session: Optional[scoped_session[Session]] = None
        self.logs: logging.Logger = logging.getLogger(
            'unrealircd-rpc-py-sql'
            )

        # Credentials setup
        self._engine_name: str = engine_name
        self._db_debug = db_debug
        self._db_hostname = db_hostname
        self._db_port = db_port
        self._db_username = db_username
        self._db_password = db_password
        self._db_name = db_name

        self._model = model
        self._base: Optional[Any] = self._model.Base
        self.delete = delete
        self.select = select
        self.update = update
        self.connected = False

    def __create_url_for_engine(self) -> str:
        _engine_name = (self._engine_name.strip().lower()
                        if self._engine_name is not None else None)

        _sql_engines = {'sqlite', 'mysql', 'postgresql'}

        if _engine_name is None:
            raise ValueError(
                f"Engine name not set must be "
                f"{', '.join([e for e in _sql_engines])}"
                )

        if _engine_name not in _sql_engines:
            raise ValueError(
                f"Engine name not set must be "
                f"{', '.join([e for e in _sql_engines])}"
                )

        match _engine_name:
            case 'sqlite':
                _fullpath = pathlib.Path('db')

                if not pathlib.Path(_fullpath).exists():
                    _fullpath.mkdir(parents=True)

                return f'sqlite:///{_fullpath.joinpath("data.db")}'

            case 'mysql':
                # mysql+pymysql://<username>:<password>@<host>:<port>/<database>
                _db_port = 3306 if self._db_port == 0 else self._db_port
                _chaine = (f'{self._db_username}:'
                           f'{self._db_password}@{self._db_hostname}:'
                           f'{_db_port}/{self._db_name}')
                return f'mysql+pymysql://{_chaine}'

            case 'postgresql':
                # postgresql://<username>:<password>@<host>:<port>/<database>
                _db_port = 5432 if self._db_port == 0 else self._db_port
                _chaine = (f'{self._db_username}:'
                           f'{self._db_password}@{self._db_hostname}:'
                           f'{_db_port}/{self._db_name}')
                return f'postgresql://{_chaine}'

            case _:
                ...

        return _sql_engines[_engine_name]

    def db_init(self) -> None:
        """Init the db connection.
        """
        try:
            # Get the connection chain string
            _url = self.__create_url_for_engine()

            # Create the engine.
            engine = create_engine(_url, echo=self._db_debug)

            # Set the engine
            self.set_engine(engine)

            # Create a session Factory
            session_factory = sessionmaker(
                autocommit=False, autoflush=False, bind=engine
                )

            # Local Session to use by Threads
            thread_session = scoped_session(session_factory)

            # Set The Scoped Session
            self.set_scoped_session(thread_session)

            if engine.dialect.name == 'sqlite':
                thread_session.execute(text('PRAGMA foreign_keys=ON'))

            # Setup events for sqlalchemy
            self._setup_events()

            # Create database and tables
            self.create_db()

            # Set connected to True to info that the connection is OK
            self.connected = True

            return None

        except Exception as err:
            self.logs.error(f'General Error: {err}', exc_info=True)

    def create_db(self):
        try:
            base = self._base
            base.metadata.drop_all(self.get_engine())
            base.metadata.create_all(self.get_engine())
            self.logs.debug("::> Database created using ORM <::")
        except Exception:
            raise

    def insert_multiple_objs_to_db(self, objs: list[object]) -> bool:
        """
        Insert multiple objects to the DB
        :param objs: List of objects to insert.
        :type objs: object
        :return: True if objects inserted
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:
                session.add_all(objs)
                session.commit()
                return True

            except Exception as err:
                self.logs.error(f'General Error: {err}')
                session.rollback()
                session.expunge_all()
                return False
            finally:
                session.expunge_all()
                __scoped_session.remove()

    def insert_obj_to_db(self, obj: object) -> bool:
        """Insert object to the Database

        Args:
            obj (object): ORM Object to instert

        Returns:
            bool: True if object inserted
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:
                session.add(obj)
                (session.flush()
                 if self.get_engine().dialect.name == 'sqlite' else None)
                session.commit()
                return True

            except Exception as err:
                self.logs.error(f'General Error: {err}')
                session.rollback()
                session.expunge_all()
                return False

            finally:
                session.expunge_all()
                __scoped_session.remove()

    def delete_obj_from_db(self, delete_statment: 'Delete') -> int:
        """
        Delete from the database using statments.
        :param delete_statment: The Delete SQLAlchemy statment.
        :type delete_statment: Delete
        :return: Number of rows deleted
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:
                result = session.execute(delete_statment)
                (session.flush()
                 if self.get_engine().dialect.name == 'sqlite' else None)
                session.commit()
                rowcount: int = (result.rowcount
                                 if isinstance(result.rowcount, int) else 0)
                return rowcount

            except Exception as err:
                self.logs.error(f'General Error: {err}')
                session.rollback()
                session.expunge_all()
                return 0

            finally:
                session.expunge_all()
                __scoped_session.remove()

    def update_obj_from_db(self, update_statment: 'Update') -> int:
        """
        Run the update statment
        :param update_statment: The Update SQLAlchemy statment.
        :return: The number of rows affected
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:
                result = session.execute(update_statment)
                (session.flush()
                 if self.get_engine().dialect.name == 'sqlite' else None)
                session.commit()
                rowcount: int = (result.rowcount
                                 if isinstance(result.rowcount, int) else 0)
                return rowcount

            except Exception as err:
                self.logs.error(f'General Error: {err}')
                session.rollback()
                session.expunge_all()
                return 0

            finally:
                session.expunge_all()
                __scoped_session.remove()

    def execute_select_all_stmt(self,
                                select_statment: 'Select'
                                ) -> Union['Sequence[RowMapping]', None]:
        """Run the Select statment object

        Example 1:
            >>> userobj = Mydbobj
            >>> stmt = Select(userobj.name, userobj.email, userobj.id
            ).where(userobj.email.like('%.com'))
            >>> users = execute_select_all_stmt(stmt)

            >>> for user in users:
                >>> print(user.get('id'), user.get('name'), user.get('email'))

        Example 2:
            >>> userobj = Mydbobj
            >>> stmt = Select(userobj).where(userobj.email.like('%.com'))
            >>> results = execute_select_all_stmt(stmt)

            >>> for result in results:
                >>> user = result.get('Mydbobj')
                >>> print(user.id, user.name, user.email)

        :param select_statment: The Select SQLAlchemy statment.
        :return: See the exemples.
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:
                result = session.execute(select_statment).mappings().all()
                return result

            except Exception as err:
                self.logs.error(f'General Error: {err}')
                session.rollback()
                traceback.print_exc()

            finally:
                session.expunge_all()
                __scoped_session.remove()

    def execute_select_first_stmt(self,
                                  select_statment: 'Select'
                                  ) -> Union['RowMapping', None]:
        """Run the Select statment object and get the first record

        Example 1:
            >>> userobj = Mydbobj
            >>> stmt = Select(userobj.name, userobj.email, userobj.id)
                        .where(userobj.id == 1)
            >>> user = execute_first_stmt(stmt)
            >>> print(user.id, user.name, user.email)

        Example 2:
            >>> userobj = Mydbobj
            >>> stmt = Select(func.max(userobj.id).label('max_id'))
                                    .where(userobj.email.like('%.com'))
            >>> myuser = execute_first_stmt(stmt)
            >>> print(myuser.max_id)

        :param select_statment: The Select SQLAlchemy statment.
        :return: See the exemples.
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:

                result = session.execute(select_statment).mappings().first()
                return result

            except Exception as err:
                self.logs.error(f'General Error: {err}')
                session.rollback()
                traceback.print_exc()

            finally:
                session.expunge_all()
                __scoped_session.remove()

    def execute_select_one_stmt(self,
                                select_statment: 'Select'
                                ) -> Union['RowMapping', None]:
        """Run the Select statment object and get one record.
        WARNINGS: You must return one record otherwise it will
                  trigger an error

        Example 1:
            >>> userobj = Mydbobj
            >>> stmt = Select(userobj.name, userobj.email, userobj.id)
                        .where(userobj.id == 1)
            >>> user = execute_select_one_stmt(stmt)
            >>> print(user.id, user.name, user.email)

        Example 2:
            >>> userobj = Mydbobj
            >>> stmt = Select(func.max(userobj.id).label('max_id'))
                    .where(userobj.email.like('%.com'))
            >>> myuser = execute_select_one_stmt(stmt)
            >>> print(myuser.max_id)

        :param select_statment: The Select SQLAlchemy statment.
        :return: See the exemples.
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:

                result = (session.execute(select_statment)
                          .mappings().one_or_none())
                return result

            except NoResultFound as noResult:
                self.logs.warning(f'NoResultFound Error: {noResult}')

            except Exception as err:
                self.logs.error(f'General Error: {err}')
                session.rollback()
                traceback.print_exc()

            finally:
                session.expunge_all()
                __scoped_session.remove()

    def execute_native_query(self,
                             query: str,
                             *,
                             params: Optional[dict] = None
                             ) -> Union[Result, None]:
        """Execute a query

        Args:
            query (str): The query to execute
            params (dict, optional): The parameters. Defaults to {}.
            is_thread (bool, optional): If you are using a thread.
                Defaults to False.

        Returns:
            CursorResult: The result of the query
        """
        __scoped_session: 'scoped_session[Session]' = (
            self.get_scoped_session()
            )
        with __scoped_session() as session:
            try:

                insert_query = text(query)
                if params is None:
                    response = session.execute(insert_query)
                else:
                    response = session.execute(insert_query, params)

                session.commit()

                return response

            except Exception as err:
                self.logs.error(f"General Error: {err}")
                session.rollback()
                return None

            finally:
                session.expunge_all()
                __scoped_session.remove()

    """
    BLOC DEDICATED TO SQLALCHEMY EVENTS
    """

    def _setup_events(self):
        """Sets up the event listeners to log query execution time."""
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn: Connection, cursor,
                                  statement, parameters, context, executemany
                                  ):
            """Capture the start time of the SQL query."""
            if self._db_debug:
                (conn.info.setdefault('query_start_time', [])
                 .append(time.time()))

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn: Connection, cursor,
                                 statement, parameters, context, executemany
                                 ):
            """Log the time taken for the SQL query execution."""
            if self._db_debug:
                if conn.info.get('query_start_time'):
                    if len(conn.info.get('query_start_time')) > 0:
                        total = time.time() - conn.info['query_start_time'][0]
                        self.logs.debug(
                            f"Query executed in {total:.4f} seconds:"
                            f"{statement}"
                            )
                        conn.info['query_start_time'].clear()
                else:
                    self.logs.debug("QueryStartTime empty!")

    #############################
    # GETTERS AND SETTERS METHODS
    #############################

    def set_engine(self, engine: Engine):
        self.__engine = engine

    def set_scoped_session(self, ss: scoped_session[Session]):
        self.__scoped_session = ss

    def get_engine(self) -> Engine:
        return self.__engine

    def get_scoped_session(self) -> scoped_session[Session]:
        return self.__scoped_session
