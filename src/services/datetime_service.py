from datetime import datetime, timedelta 
def getNow(): 
    return datetime.now() 
def addTime(datetime , hour = 0 , minute = 0 , day = 0 , second = 0):
    delta = timedelta(hours=hour , minutes=minute , days=day , seconds=second)
    return datetime + delta 
def toStr(datetime): 
    return str(datetime) 