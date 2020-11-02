import aiosqlite
import os
import sys, traceback

database_path = os.path.join(f'{os.path.dirname(sys.argv[0])}/config', 'database.sqlite')

# Creates a connection to the database.
async def db_connect():
    database = await aiosqlite.connect(database_path)
    return database

# Creates the necessary tables if needed.
async def create_tables():
    database = await db_connect()
    cursor = await database.cursor()
    await cursor.executescript('''
        CREATE TABLE IF NOT EXISTS welcome(
        guild_id TEXT,
        welcome_msg TEXT,
        welcome_channel_id TEXT,
        welcome_channel_on INTEGER,
        welcome_role_id TEXT,
        welcome_role_on INTEGER
        );

        CREATE TABLE IF NOT EXISTS reaction(
        emoji TEXT,
        role TEXT,
        message_id TEXT,
        channel_id TEXT,
        guild_id TEXT
        );

        CREATE TABLE IF NOT EXISTS music(
        member_id TEXT,
        favourite1 TEXT,
        favourite2 TEXT,
        favourite3 TEXT,
        favourite4 TEXT,
        favourite5 TEXT,
        favourite6 TEXT,
        favourite7 TEXT,
        favourite8 TEXT,
        favourite9 TEXT,
        favourite10 TEXT
        );
    ''')
    return await commit_and_close(database, cursor)

# Executes a query and closes both the cursor and the database
async def execute_and_close(database, sql, val):
    cursor = await database.cursor()
    await cursor.execute(sql, val)
    return await commit_and_close(database, cursor)

# Commits the last change and closes both the cursor and the database
async def commit_and_close(database, cursor):
    await database.commit()
    await cursor.close()
    return await database.close()

# Close the cursor and the database
async def closeAll(database, cursor):
    await cursor.close()
    return await database.close()

# Add a guild to the database
async def add_guild(guildID):
    database = await db_connect()
    sql = ('INSERT INTO welcome(guild_id, welcome_channel_on, welcome_role_on) VALUES(?, ?, ?)')
    val = (guildID, 0, 0)
    return await execute_and_close(database, sql, val)

# Remove a guild from the database
async def remove_guild(guildID):
    database = await db_connect()
    sql = ('DELETE FROM welcome WHERE guild_id = ?')
    await cursor.execute(sql, (guildID, ))
    return await commit_and_close(database, cursor)

# Sets the welcome channel for a guild
async def set_welcome_channel(channelID, guildID):
    database = await db_connect()
    sql = ("UPDATE welcome SET welcome_channel_id = ? WHERE guild_id = ?")
    val = (channelID, guildID)
    return await execute_and_close(database, sql, val)
    

# Sets the welcome text for a guild
async def set_welcome_text(text, guildID):
    database = await db_connect()
    sql = ("UPDATE welcome SET welcome_msg = ? WHERE guild_id = ?")
    val = (text, guildID)
    return await execute_and_close(database, sql, val)

# Sets the welcome role for a guild
async def set_welcome_role(roleID, guildID):
    database = await db_connect()
    sql = ("UPDATE welcome SET welcome_role_id = ? WHERE guild_id = ?")
    val = (roleID, guildID)
    return await execute_and_close(database, sql, val)

# Activates or deactivates the welcome message for a guild
async def welcome_message_switch(value, guildID):
    database = await db_connect()
    sql = ("UPDATE welcome SET welcome_channel_on = ? WHERE guild_id = ?")
    val = (value, guildID)
    return await execute_and_close(database, sql, val)

# Activates or deactivates the welcome role for a guild
async def welcome_role_switch(value, guildID):
    database = await db_connect()
    sql = ("UPDATE welcome SET welcome_role_on = ? WHERE guild_id = ?")
    val = (value, guildID)
    return await execute_and_close(database, sql, val)

# Returns the ID of the welcome channel for a guild
async def get_welcome_channel_id(guildID):
    database = await db_connect()
    cursor = await database.cursor()
    await cursor.execute(f"SELECT welcome_channel_id FROM welcome WHERE guild_id = {guildID}")
    result = await cursor.fetchone()
    await closeAll(database, cursor)
    return result

# Returns the value of the welcome channel switch
async def get_welcome_channel_switch(guildID):
    database = await db_connect()
    cursor = await database.cursor()
    await cursor.execute(f"SELECT welcome_channel_on FROM welcome WHERE guild_id = {guildID}")
    result = await cursor.fetchone()
    await closeAll(database, cursor)
    return result

# Returns the text of the welcome message
async def get_welcome_message(guildID):
    database = await db_connect()
    cursor = await database.cursor()
    await cursor.execute(f"SELECT welcome_msg FROM welcome WHERE guild_id = {guildID}")
    result = await cursor.fetchone()
    await closeAll(database, cursor)
    return result

# Returns the value of the welcome role switch
async def get_welcome_role_switch(guildID):
    database = await db_connect()
    cursor = await database.cursor()
    await cursor.execute(f"SELECT welcome_role_on FROM welcome WHERE guild_id = {guildID}")
    result = await cursor.fetchone()
    await closeAll(database, cursor)
    return result

# Returns the value of the welcome role switch
async def get_welcome_role_id(guildID):
    database = await db_connect()
    cursor = await database.cursor()
    await cursor.execute(f"SELECT welcome_role_id FROM welcome WHERE guild_id = {guildID}")
    result = await cursor.fetchone()
    await closeAll(database, cursor)
    return result

# Returns all guild IDs in the database
async def get_guilds():
    database = await db_connect()
    cursor = await database.cursor()
    await cursor.execute("SELECT guild_id FROM welcome")
    fetched = await cursor.fetchall()
    print(fetched)
    await closeAll(database, cursor)
    guilds = []
    for guild in fetched:
        guilds.append(guild[0])
    return guilds