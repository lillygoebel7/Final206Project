import unittest
import sqlite3
import json
import os
import requests
from bs4 import BeautifulSoup
import re
from billboard import read_billboard_data

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def bandsintown(billboard_data, conn, cur):
    cur.execute("CREATE TABLE IF NOT EXISTS genre_table (genre_id INTEGER PRIMARY KEY, genre_name STRING)")
    conn.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS bands_table (artist_id INTEGER PRIMARY KEY, date_time STRING, location STRING, venue_name STRING, country STRING)")
    conn.commit()

    bands_list = []

    for i in billboard_data:
        artist_id = i[0]
        artist = i[1]
        data = requests.get(f'https://rest.bandsintown.com/artists/{artist}/events?app_id=7046cca7a6f82b8b0f8e50a15cc4ff9e')
        content = json.loads(data.text)
        if content == []:
            date_time = "Not on Tour"
            location = "Not on Tour"
            venue_name = "Not on Tour"
            country = "Not on Tour"
        elif content != []:
            inner_content = content[0]
            for d in inner_content:
                date_time = inner_content['datetime']
                location = inner_content['venue']["location"]
                venue_name = inner_content['venue']['name']
                country = inner_content['venue']['country']
            my_tup = (artist_id, date_time, location, venue_name, country)
        bands_list.append(my_tup)
    print(bands_list)
    return bands_list

def main():
    url = "https://www.billboard.com/charts/artist-100/"
    cur, conn = open_database('music_information2.db')
    billboard_data = read_billboard_data(url, cur, conn)
    bandsintown(billboard_data, conn, cur)
    pass


if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)