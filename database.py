"""
Provides an interface for storing which channels
to post the priority lists in each server using the bot
"""
import sqlite3


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


def set_channel(guild_id: int, channel_id: int):
    """
    Persistently store which channel in the guild the priority list
    will be in.

    If a channel has already been set for the guild it will
    be overwritten.

    :param guild_id: The server containing the channel
    :param channel_id: The channel to receive daily menus in
    """
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("INSERT OR REPLACE INTO Channels (Guild, Channel) VALUES(?, ?);",
                   (guild_id, channel_id))
    cursor.close()
    db.commit()


def forget_channel(guild_id: int):
    """
    Stop receiving daily menus in the channel

    :param guild_id:
    :return:
    """
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Channels WHERE Guild = (?)", (guild_id, ))
    cursor.close()
    db.commit()


def get_channel(guild_id: int) -> (int, None):
    """Gets the channel id for this server's daily menus,
    or None if one has not been set

    :param guild_id: The id of the guild to query, or none if one was not set
    """
    db = connect_db()
    cursor = db.cursor()
    # Get the channel id for this guild from the database
    cursor.execute("SELECT Channel FROM Channels WHERE Guild = (?)", (guild_id, ))
    channel_id = cursor.fetchone()
    cursor.close()
    db.commit()
    # Database returns none if no channel is found, pass it through to the caller
    if channel_id is None:
        return None
    # The database returns the id as a single element tuple, just want the int
    return channel_id[0]


def get_channels() -> list:
    """Returns a list of every channel registered to receive daily menus"""
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT Channel FROM Channels")  # Get all the registered channel IDs
    channel_ids = cursor.fetchall()
    cursor.close()
    db.commit()

    # cursor.fetchall() provides a list of single element tuples
    # Unpack those tuples into a list of integers
    channel_ids = [id_tuple[0] for id_tuple in channel_ids]
    return channel_ids