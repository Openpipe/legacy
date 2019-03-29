"""
Description: Inserts an item into a SQLite database

- transport using sqlite:
    db_name: links.db
    sql: ISERT INTO table (field1, field2) VALUES (?)
    values: [ value1, value2 ]
"""
import sqlite3
import sys
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self._conn = sqlite3.connect(self.config['db_name'], timeout=30)
        self._conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))

    def on_input(self, item):
        sql = self.config['sql']
        values = self.config.get("values", [])
        if not isinstance(values, list):    # Convert single values to a list
            values = [values]
        cursor = self._conn.cursor()
        try:
            result = cursor.execute(sql, values)
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            print("SQL:", self.config['sql'], file=sys.stderr)
            print("VALUES:", values, file=sys.stderr)
            raise
        # print("SQL:", self.config['sql'], file=sys.stderr)
        # print("VALUES:", values, file=sys.stderr)
        # If delete was sucessfull, just pass the record
        command = sql.upper().strip().split()[0]
        if command == 'DELETE':
            if cursor.rowcount == 1:
                self.put(item)
        elif command != "SELECT":
            self.put(item)
        else:
            for item in result.fetchall():
                self.put(item)
        self._conn.commit()
        cursor.close()
