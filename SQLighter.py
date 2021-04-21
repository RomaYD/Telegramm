import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()


    def select_single(self, rownum):
        with self.connection:
            return self.cursor.execute('SELECT * FROM music WHERE id = ?', (rownum,)).fetchall()[0]

    def count_rows(self):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM music').fetchall()
            return len(result)


    def select_all(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM music').fetchall()

    def close(self):
        # Закрытие соединения с базой данных
        self.connection.close()
