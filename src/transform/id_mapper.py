import json
class IdMapper:
    def __init__(self): self.maps={}
    def add(self,table,old,new): self.maps.setdefault(table,{})[str(old)]=new
    def get(self,table,old): return self.maps.get(table,{}).get(str(old))
    def save(self,path): json.dump(self.maps,open(path,'w'),indent=2)
