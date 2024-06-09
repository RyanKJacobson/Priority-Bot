"""
Provides an interface for storing which channels
to post the priority lists in each server using the bot
"""
import sqlite3
from typing import List, Tuple


def connect_db() -> sqlite3.dbapi2:
    """Get a connection object representing the database"""
    return sqlite3.connect("database.sqlite")


def init_db():
    """Ensure the database contains the required tables"""
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Lists (Id INTEGER PRIMARY KEY, Guild INTEGER NOT NULL, Channel INTEGER, MessageId INTEGER , Name VARCHAR);")
    cursor.execute("CREATE TABLE IF NOT EXISTS Tasks (Id INTEGER PRIMARY KEY, List INTEGER NOT NULL, Priority INTEGER NOT NULL, Name VARCHAR, Description VARCHAR);")
    cursor.close()
    db.commit()

def create_list(name: str, guild_id: int) -> int:
    """
    Create a new list, which only the specified server can view/modify.

    :param name: The name of the list. Used by subsequent commands to select which list to operate on
    :param guild_id: The server the list belongs to
    :return: The unique ID of the new list.
    """
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Lists (Name, Guild)", (name, guild_id))
    new_list_id = cursor.lastrowid()
    cursor.close()
    db.commit()

    return new_list_id


def create_task(list_id: int, task_name: str, priority: int, description: str):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Tasks (List, Priority, Name, Description) VALUES(?, ?, ?, ?)", (list_id, priority, task_name, description))
    cursor.close()
    db.commit()

def get_tasks(list_id: int) -> List[dict]:
    """
    Return every task under the given list
    """
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT Name, Priority, Description FROM Tasks WHERE List = ?", (list_id, ))
    all_tasks = cursor.fetchall()
    cursor.close()
    db.commit()
    return [{"name": name, "priority": priority, "description": description} for name, priority, description in all_tasks]


def set_channel(list_id: int, channel_id: int):
    """
    Persistently store which channel in the guild the priority list
    will be in.

    If a channel has already been set for the guild it will
    be overwritten.

    :param list_id: The list to display
    :param channel_id: The channel to display the list in. Must be in the same server as the list
    """
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE Lists Set Channel = ? WHERE Id = ?",
                   (channel_id, list_id))
    cursor.close()
    db.commit()


def forget_channel(list_id: int):
    """
    Stop displaying updates to this list
    """
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE Lists Set Channel = NULL, MessageId = NULL WHERE Id = ?", (list_id, ))
    cursor.close()
    db.commit()


def get_channel(list_id: int) -> Tuple[int | None, int | None]:
    """
    Gets the channel id (if any) that the list should be displayed in,
    as well as the most recent message id
    """
    db = connect_db()
    cursor = db.cursor()
    # Get the channel id for this guild from the database
    cursor.execute("SELECT Channel, MessageId FROM Lists WHERE Id = (?)", (list_id, ))
    data = cursor.fetchone()
    cursor.close()
    db.commit()

    return data
