#!/usr/bin/python
"""
Description: Insers an item into a MariaDB database

Requires: mysql-connector

- transport into mariadb:
    username: root
    password: passwd
    host: localhost
    db_name: test
    sql: ISERT INTO table (field1, field2) VALUES (?)
    values: [ value1, value2 ]
"""
from mdatapipe.core import PipelinePlugin
import sys
import mysql.connector


class Plugin(PipelinePlugin):

    def on_start(self):
        user = self.config.get("user", "root")
        password = self.config.get("password", None)
        host = self.config.get("host", "localhost")
        database = self.config.get('database', "test")

        self._conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database,
        )

    def on_input(self, item):  # NOQA: C901
        sql = self.config['sql']
        command = sql.upper().strip().split()[0]
        values = self.config.get("values", [])
        if not isinstance(values, list):    # Convert single values to a list
            values = [values]
        #  print("SQL:", self.config['sql'], file=sys.stderr)
        #  for v in values:
        #   print("VAL:", type(v), v, file=sys.stderr)
        cursor = self._conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, values)
        except (mysql.connector.OperationalError, mysql.connector.ProgrammingError):
            print("SQL:", self.config['sql'], file=sys.stderr)
            print("VALUES:", values, file=sys.stderr)
            raise
        except (mysql.connector.IntegrityError):
            if not self.config.get("ignore_integrity_errors", False):
                raise
        if command == "SELECT":
            result_set = cursor.fetchall()
            for result in result_set:
                self.put(result)
        # If delete was sucessfull, just pass the record
        if command in ['INSERT', 'DELETE', "UPDATE"]:
            if cursor.rowcount == 1:
                self.put(item)
        elif command != "SELECT":
            self.put(item)
        self._conn.commit()
        cursor.close()
