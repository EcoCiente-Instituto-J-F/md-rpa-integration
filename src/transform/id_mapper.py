
class IDMapper:


    def __init__(self):

        self.maps={}



    def save(
        self,
        table,
        old,
        new
    ):

        if table not in self.maps:

            self.maps[table]={}


        self.maps[table][old]=new



    def get(
        self,
        table,
        old
    ):

        return self.maps.get(
            table,
            {}
        ).get(old)