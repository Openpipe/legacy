from mdatapipe.core import PipelinePlugin
import cx_Oracle

"""
Requires: cx_Oracle

Example:
    - collect datasource oracledb:
        host: localhost
        port: 2110
        sid: MYDB
        user: scott
        passwd: tiger

"""


class Plugin(PipelinePlugin):

    def on_start(self):
        host = self.config['host']
        port = str(self.config['port'])
        sid = self.config['sid']
        user = self.config['user']
        passwd = self.config['passwd']

        db_connect = user+'/'+passwd
        db_connect += '@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST='+host+')(PORT='+port+')))'
        db_connect += '(CONNECT_DATA=(SID='+sid+')))'
        self.con = cx_Oracle.connect(db_connect)
        self.cur = self.con.cursor()

    def on_input(self, item):
        # Execute sql
        self.query = self.config['query']
        self.cur.execute(self.query)
        result = self.cur.fetchall()

        for line in result:
            new_item = {}
            field_names = [row[0] for row in self.cur.description]
            for i, name in enumerate(field_names):
                new_item[name] = line[i]
            self.put(new_item)

    def on_exit(self):
        self.cur.close()
        self.con.close()
