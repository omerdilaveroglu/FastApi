import sqlite3
import json
import pandas as pd
import uuid
from pydantic import BaseModel
from functions import get_password_hash
from functions import user_register

import datetime

conn = sqlite3.connect("db.sqlite3")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS USERS (
          id TEXT PRIMARY KEY,
          first_name TEXT KEY NOT NULL, 
          last_name TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          sex TEXT NOT NULL,
          hashed_password TEXT NOT NULL,
          disabled INTEGER NOT NULL,
          creation_date DATETIME NOT NULL,
          closing_date DATETIME
)""")
conn.commit()

user_register('ali','deniz','ali.deniz@hotmail.com','Male','ali.123')