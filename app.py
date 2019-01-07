from autotrader.scraper import Scraper
from autotrader.vehiclerepository import VehicleRepository
import psycopg2


def main():
    # set up search parameters
    max_distance = 1500
    postcode = "rg315nr"
    berths = 6
    max_price = 27500
    keywords = "bunk"

    postgres_host = "localhost"
    postgres_port = 5432
    postgres_db = "postgres"
    try:
        postgres_connection = psycopg2.connect(
            host=postgres_host,
            port=postgres_port,
            dbname=postgres_db
        )
        scraper = Scraper()
        repo = VehicleRepository(postgres_connection)

        vans = scraper.get_vehicles(max_distance, postcode, berths, max_price, keywords)
        repo.store(vans)
    finally:
        postgres_connection.close()

main()
