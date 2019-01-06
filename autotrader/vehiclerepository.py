import datetime


class VehicleRepository:
    def __init__(self, postgres_connection):
        super(VehicleRepository, self).__init__()
        self.conn = postgres_connection

    def exists(self, uid):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                            SELECT COUNT(*) FROM search.results where uid = %s
                        """, (uid,))
            answer = cur.fetchone()
            if answer[0] > 0:
                return True
            else:
                return False
        finally:
            cur.close()



    def create(self, vehicle):
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO
                    search.results
                    (
                        uid,
                        thumbnail,
                        link,
                        title,
                        price,
                        town,
                        distance,
                        year,
                        berth,
                        miles,
                        transmission,
                        seats,
                        engine,
                        extras,
                        first_seen,
                        last_seen
                    )
                VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """,
                (vehicle.uid,
                 vehicle.thumbnail,
                 vehicle.link,
                 vehicle.title,
                 vehicle.price,
                 vehicle.town,
                 vehicle.distance,
                 vehicle.year,
                 vehicle.berth,
                 vehicle.miles,
                 vehicle.transmission,
                 vehicle.seats,
                 vehicle.engine,
                 vehicle.extras,
                 datetime.datetime.utcnow(),
                 datetime.datetime.utcnow()))
            self.conn.commit()
            print(f"CREATED {vehicle.uid}")
        finally:
            cur.close()

    def update_vehicle(self, vehicle):
        try:
            cur = self.conn.cursor()
            # get current record for this uid
            cur.execute("""
                SELECT * FROM search.results WHERE uid = %s
                """, (vehicle.uid,))
            row = cur.fetchone()

            # log any differences
            differences = {}
            if row[1] != vehicle.thumbnail:
                differences['thumbnail-new'] = vehicle.thumbnail
                differences['thumbnail-old'] = row[1]
            if row[2] != vehicle.link:
                differences['link-new'] = vehicle.link
                differences['link-old'] = row[2]
            if row[3] != vehicle.title:
                differences['title-new'] = vehicle.title
                differences['title-old'] = row[3]
            if row[4] != vehicle.price:
                differences['price-new'] = vehicle.price
                differences['price-old'] = row[4]
            if row[5] != vehicle.town:
                differences['town-new'] = vehicle.town
                differences['town-old'] = row[5]
            if row[6] != vehicle.distance:
                differences['distance-new'] = vehicle.distance
                differences['distance-old'] = row[6]
            if row[7] != vehicle.year:
                differences['year-new'] = vehicle.year
                differences['year-old'] = row[7]
            if row[8] != vehicle.berth:
                differences['berth-new'] = vehicle.berth
                differences['berth-old'] = row[8]
            if row[9] != vehicle.miles:
                differences['mileage-new'] = vehicle.miles
                differences['mileage-old'] = row[9]
            if row[10] != vehicle.transmission:
                differences['transmission-new'] = vehicle.transmission
                differences['transmission-old'] = row[10]
            if row[11] != vehicle.seats:
                differences['seats-new'] = vehicle.seats
                differences['seats-old'] = row[11]
            if row[12] != vehicle.engine:
                differences['engine-new'] = vehicle.engine
                differences['engine-old'] = row[12]
            if row[13] != vehicle.extras:
                differences['extras-new'] = vehicle.extras
                differences['extras-old'] = row[13]

            # update the vehicle with this uid
            cur.execute(
                """
                UPDATE
                    search.results
                SET
                    thumbnail = %s,
                    link = %s,
                    title = %s,
                    price = %s,
                    town = %s,
                    distance = %s,
                    year = %s,
                    berth = %s,
                    miles = %s,
                    transmission = %s,
                    seats = %s,
                    engine = %s,
                    extras = %s,
                    last_seen = %s
                WHERE
                    uid = %s
                """,
                (vehicle.thumbnail,
                 vehicle.link,
                 vehicle.title,
                 vehicle.price,
                 vehicle.town,
                 vehicle.distance,
                 vehicle.year,
                 vehicle.berth,
                 vehicle.miles,
                 vehicle.transmission,
                 vehicle.seats,
                 vehicle.engine,
                 vehicle.extras,
                 datetime.datetime.utcnow(),
                 vehicle.uid,))
            self.conn.commit()

            #FIXME move to a summary message below to replace "updated"
            if len(differences.keys()) > 0:
                print(f"UPDATED {vehicle.uid} with {differences}")
        finally:
            cur.close()

    def store(self, vans):
        for vehicle in vans:
            if self.exists(vehicle.uid):
                self.update_vehicle(vehicle)
            else:
                self.create(vehicle)
