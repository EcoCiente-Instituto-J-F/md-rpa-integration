class Extractor:


    def __init__(self, database):

        self.database = database



    def extract(self, table):

        sql = (
            f"SELECT * FROM {table}"
        )

        return self.database.query(sql)