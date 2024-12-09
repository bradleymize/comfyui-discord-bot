from collections import namedtuple
import sqlite3
import os
import logging
import json

log = logging.getLogger(__name__)

def namedtuple_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)

dbname = "database-dev.db"
if os.getenv("BOT_TYPE") == "PRODUCTION":
    dbname = "database-prod.db"

log.info(f"Connecting to {dbname}")

connection = sqlite3.connect(dbname)
connection.row_factory = namedtuple_factory
connection.autocommit = True

def initialize_database():
    cursor = connection.cursor()
    table_created = False

    for row in cursor.execute("SELECT name FROM sqlite_master"):
        if row.name == "comfyui":
            table_created = True

    if not table_created:
        log.info("Creating table 'comfyui'")
        cursor.execute("CREATE TABLE comfyui(discord_message_id, prompt_id, command_name, prompt_values)")
    else:
        log.info("Table 'comfyui' already exists")

def insert_prompt(message_id, command_name, prompt_data):
    data = (message_id, command_name, json.dumps(prompt_data, indent=2))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO comfyui (discord_message_id, command_name, prompt_values) VALUES (?, ?, ?)", data)
    cursor.close()


def get_prompt_information_for_message_id(message_id):
    cursor = connection.cursor()
    res = cursor.execute("SELECT command_name, prompt_values FROM comfyui WHERE discord_message_id = ?", (message_id,))
    response = res.fetchone()
    cursor.close()
    return response


def delete_prompt_information_for_message_id(message_id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM comfyui WHERE discord_message_id = ?", (message_id,))
    cursor.close()


def update_prompt_id_for_message_id(message_id, prompt_id):
    data = (prompt_id, message_id)
    cursor = connection.cursor()
    cursor.execute("UPDATE comfyui SET prompt_id = ? WHERE discord_message_id = ?", data)
    cursor.close()