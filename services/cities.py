import json

def get_data() -> list:
    with open("services/in.json", "r") as f:
        data = json.load(f)

    return data

data = get_data()

CITIES = [record['city'] for record in data]

def get_coords(city: str) -> tuple:
    record = list(filter(lambda record: record['city'] == city, data))
    if not record:
        return (0, 0,)

    return (float(record[0].get("lat")), float(record[0].get("lng")),)
