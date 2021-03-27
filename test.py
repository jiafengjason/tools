from functools import lru_cache

def getUserId(id):
    return id+1
    
def getDevId(id):
    return id+2

@lru_cache()
def commonGet(getFunc,id):
    print(str(getFunc))
    return getFunc(id)
    
    
print(commonGet(getUserId,1))
print(commonGet(getUserId,2))
print(commonGet(getUserId,1))
print(commonGet(getDevId,1))
print(commonGet(getDevId,2))
print(commonGet(getDevId,1))