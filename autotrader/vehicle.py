class Vehicle:
    uid = None
    thumbnail = None
    link = None
    title = None
    price = 0
    town = None
    distance = 0
    year = 1970
    berth = 0
    miles = 0
    transmission = None
    seats = None
    engine = None
    extras = None

    def __init__(self, uid):
        super(Vehicle, self).__init__()
        self.uid = uid
