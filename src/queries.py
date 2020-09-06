from psycopg2 import extras, connect
from uuid import UUID
from contextlib import contextmanager
import datetime

from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_DATABASE, POSTGRES_PASSWORD

from models import UserPayload, BaseTask, Task


# function call required to allow uuid type from postgres.
extras.register_uuid()

@contextmanager
def persistence():
    connection = None
    try:
        connection = connect(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DATABASE, user=POSTGRES_USER, password=POSTGRES_PASSWORD)
        yield connection
    finally:
        if connection is not None:
            connection.close()

def database_query(func: object):
    """ Decorator to present database connection via dependency injection """
    def wrapper(*args: tuple, **kwargs: dict): 
        with persistence() as connection:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            return func(connection, cursor, *args, **kwargs)
    return wrapper


@database_query
def get_task_by_id(connection: object, cursor: object, id: str):
    """ Retrieve a task given an ID from the database """
    cursor.execute("SELECT id, name, priority, duration FROM tasks WHERE id = %s", (id,))
    return cursor.fetchone()


@database_query
def get_tasks_by_user(connection: object, cursor: object, username: str, completed: bool = False):
    """ Retrieve the tasks of a given user, querying on their ID """
    if completed:
        query = ("SELECT id, name, username, description, priority, duration, due_date, completed_at FROM tasks WHERE username = %s AND completed_at IS NOT NULL")
    else:
        query = ("SELECT id, name, username, description, priority, duration, due_date, completed_at FROM tasks WHERE username = %s AND completed_at IS NULL")

    cursor.execute(query, (username,))
    return [Task(**row) for row in cursor.fetchall()]


@database_query
def get_user_by_username(connection: object, cursor: object, username: str):
    """ Get a user from the database by its username """
    cursor.execute("SELECT username, password, name FROM users WHERE username = %s", (username,))
    return cursor.fetchone()


@database_query
def create_user(connection: object, cursor: object, user: UserPayload):
    """ Create a user into the database """
    cursor.execute("INSERT INTO users (username, password, name) VALUES (%s, %s, %s) RETURNING username", (user.username, user.password, user.name,))
    connection.commit()
    return dict(cursor.fetchone()).get('username', None)


@database_query
def create_task(connection: object, cursor: object, task_body: BaseTask, username: str):
    """ Create a task with the given task information for a user. """
    args = (task_body.name, task_body.description,  username, task_body.priority, task_body.duration, task_body.due_date,)
    cursor.execute("INSERT INTO tasks (name, description, username, priority, duration, due_date) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", args)
    connection.commit()
    return dict(cursor.fetchone())

@database_query
def set_task_complete(connection: object, cursor: object, task_id: UUID):
    """ Mark a given task as completed """
    if get_task_by_id(id=task_id) is None:
        return None
    completion_time = datetime.datetime.utcnow().isoformat()
    cursor.execute("UPDATE tasks SET completed_at = %s WHERE id = %s;", (completion_time,task_id,))
    connection.commit()
    return True

@database_query
def set_task_incomplete(connection: object, cursor: object, task_id: UUID):
    """ Mark a given task as incomplete """
    if get_task_by_id(task_id) is None:
        return None
    cursor.execute("UPDATE tasks SET completed_at = NULL WHERE id = %s;", (task_id,))
    connection.commit()
    return True