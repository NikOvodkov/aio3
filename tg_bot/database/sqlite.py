import sqlite3


class SQLiteDatabase:
    def __init__(self, path_to_db='sqlite160124.db'):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def create_table_users(self):
        sql = '''
        CREATE TABLE Users (
        user_id int NOT NULL,
        Name varchar(255) NOT NULL,
        email varchar(255),
        time_zone varchar(10),
        birth_date varchar(10),
        life_date varchar(10),
        life_calendar varchar(255),
        latitude varchar(255),
        longitude varchar(255),
        PRIMARY KEY (user_id)
        );
        '''
        self.execute(sql, commit=True)

    def execute_through_sql(self, sql):
        self.execute(sql, commit=True)

    def add_user(self, user_id: int, name: str, email: str = None, time_zone: str = None, birth_date: str = None,
                 life_date: str = None, life_calendar: str = None, latitude=None, longitude=None):
        sql = 'INSERT INTO Users(user_id, Name, email, time_zone, birth_date, life_date, life_calendar, latitude, longitude) ' \
              'VALUES(?,?,?,?,?,?,?,?,?)'
        parameters = (user_id, name, email, time_zone, birth_date, life_date, life_calendar, latitude, longitude)
        self.execute(sql, parameters=parameters, commit=True)

    def select_all_users(self):
        sql = 'SELECT * FROM Users'
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += ' AND '.join([
            f'{item} = ?' for item in parameters
        ])
        return sql, tuple(parameters.values())

    def select_user(self, **kwargs):
        sql = 'SELECT * FROM Users WHERE '
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)

    def count_users(self):
        return self.execute('SELECT COUNT(*) FROM Users;', fetchone=True)

    def update_email(self, email, user_id):
        sql = 'UPDATE Users SET email=? WHERE user_id=?'
        return self.execute(sql, parameters=(email, user_id), commit=True)

    def update_time_zone(self, time_zone, user_id):
        sql = 'UPDATE Users SET time_zone=? WHERE user_id=?'
        return self.execute(sql, parameters=(time_zone, user_id), commit=True)

    def update_birth_date(self, birth_date, user_id):
        sql = 'UPDATE Users SET birth_date=? WHERE user_id=?'
        return self.execute(sql, parameters=(birth_date, user_id), commit=True)

    def update_life_date(self, life_date, user_id):
        sql = 'UPDATE Users SET life_date=? WHERE user_id=?'
        return self.execute(sql, parameters=(life_date, user_id), commit=True)

    def update_life_calendar(self, life_calendar, user_id):
        sql = 'UPDATE Users SET life_calendar=? WHERE user_id=?'
        return self.execute(sql, parameters=(life_calendar, user_id), commit=True)

    def update_latitude(self, latitude, user_id):
        sql = 'UPDATE Users SET latitude=? WHERE user_id=?'
        return self.execute(sql, parameters=(latitude, user_id), commit=True)

    def update_longitude(self, longitude, user_id):
        sql = 'UPDATE Users SET longitude=? WHERE user_id=?'
        return self.execute(sql, parameters=(longitude, user_id), commit=True)

    def delete_users(self):
        self.execute('DELETE FROM Users WHERE True')


def logger(statement):
    print(f'''
    ______________________________________
    Executing:
    {statement}
    ______________________________________
''')
