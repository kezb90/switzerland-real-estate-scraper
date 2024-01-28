from peewee import PostgresqlDatabase, OperationalError


class DatabaseManager:
    def __init__(self, database_name, user, password, host, port):
        self.database_name = database_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.db = self.connect_to_database()

    def connect_to_database(self):
        database_connection = PostgresqlDatabase(
            self.database_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        try:
            database_connection.connect()
        except OperationalError as e:
            print("Please check your connection to database such as username, password, host or port!")
            print(e.args)
            exit()
        return database_connection

    def close_connection(self):
        self.db.close()

    def create_tables(self, models):
        self.db.create_tables(models)
