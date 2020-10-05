import pandas as pd
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

class LocationMapper:
    def __init__(self):
        self.locator = Nominatim(user_agent="openmapquest")
    def get_location_info (self, coordinates):
        location = self.locator.reverse(coordinates)
        address = location.raw["address"]
        district = address['state_district']
        state = address['state']
        country = address['country']
        return (district, state, country)

if __name__ == "__main__":
    lm = LocationMapper()
    lm.get_location_info("25.600258, 90.217247")