import pickle

class a:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def __pickle__(self):
        print('dd')

Time = a('Teo', 17)

class b(a):
    def __init__(self, uff):
        print(self.name)
        self.uff = uff

Time2 = b('lop')

with open('Data/classe.pickle', 'wb') as f:
    pickle.dump(Time, f)

with open('Data/classe.pickle', 'rb') as f:
    LOL = pickle.load(f)

    print(LOL.age)