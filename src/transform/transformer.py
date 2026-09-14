from src.transform.id_mapper import IDMapper



class Transformer:


    def __init__(self):

        self.mapper = IDMapper()



    def process(
        self,
        table,
        dataframe
    ):


        dataframe.columns = [
            c.lower()
            for c in dataframe.columns
        ]


        dataframe = dataframe.fillna(
            None
        )


        return dataframe