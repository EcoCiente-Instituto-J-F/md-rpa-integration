import pandas as pd

from src.config.database import create_source_engine



class SourceDatabase:


    def __init__(self):

        self.engine = create_source_engine()



    def query(self, sql):

        return pd.read_sql(
            sql,
            self.engine
        )