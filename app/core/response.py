def success(data=None, message=None):
    r={"success":True,"data":data}
    if message: r["message"]=message
    return r
