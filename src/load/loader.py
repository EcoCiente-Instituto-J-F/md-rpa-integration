class Loader:


    def __init__(self, database):

        self.database = database



    def load(
        self,
        table,
        dataframe
    ):


        dataframe.to_sql(

            table,

            self.database.engine,

            if_exists="append",

            index=False

        )