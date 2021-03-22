class User:
    IP = None
    id = None
    name = None
    password = None
    cost = None 
    money = None 
    gain=None
    active = True
    transactions = []
    def update_all(id=None, name=None, password=None, money=None, gain=None, cost=None):
        if id != None:
            User.id = id
        if name != None:
            User.name = name
        if password != None:
            User.password = password 
        if cost != None:
            User.cost=cost
        if money !=  None:
            User.money = money 
        if gain !=None:
            User.gain = gain
    def update(request):
        if User.IP != None and (User.name != None and User.password != None):
            exact_user = request.post(url='http://'+User.IP+':5000/exact_user', json={'username': User.name, 'password': User.password})
            if exact_user.json()['is_it_correct'] == True:
                data = exact_user.json()['data']
                User.update_all(id=data[0], name=data[1], password=data[2], money=data[3], 
                gain=data[4], cost=data[5])
