import time



class Timer:


    def start(self):

        self.begin=time.time()



    def stop(self):

        self.end=time.time()



    def report(self):

        total=self.end-self.begin

        return (

        f"""
        MIGRAÇÃO FINALIZADA

        Tempo:
        {total:.2f} segundos

        """

        )