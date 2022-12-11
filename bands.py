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
    cur.execute("CREATE TABLE IF NOT EXISTS bands_table (artist_id INTEGER PRIMARY KEY, date_time STRING, country_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS country_table (country_id INTEGER PRIMARY KEY, country_name STRING)")
    cur.execute("CREATE TABLE IF NOT EXISTS Not_On_Tour (tour_id INTEGER PRIMARY KEY, tour_name STRING)")
    conn.commit()
    cur.execute('INSERT OR IGNORE INTO Not_On_Tour (tour_id, tour_name) VALUES (?,?)', (0, "Not On Tour"))


    bands_list = []
    for i in billboard_data:
        artist_id = i[0]
        artist = i[1]
        data = requests.get(f'https://rest.bandsintown.com/artists/{artist}/events?app_id=7046cca7a6f82b8b0f8e50a15cc4ff9e')
        content = json.loads(data.text)
        if content == []:
            my_tup = (artist_id, 0, 0)
            cur.execute('INSERT OR IGNORE INTO country_table (country_id, country_name) VALUES (?,?)', (0, "Not on Tour"))
            conn.commit()
        elif content != []:
            inner_content = content[0]
            date_time = inner_content['datetime']
            
            country = inner_content['venue']['country']
            country_list = ["Not on Tour", "United States", "New Zealand", "Australia", "United Kingdom", "Portugal", "Canada", "Qatar", "Mexico"]
            country_dict = {}
            count = 0
            for country_name in country_list:
                country_dict[country_name] = count
                count += 1
            for i in country_dict:
                if country == i:
                    country = country_dict[i]
                    cur.execute('INSERT OR IGNORE INTO country_table (country_id, country_name) VALUES (?,?)', (country, i))
                    conn.commit()
            my_tup = (artist_id, date_time, country)
        bands_list.append(my_tup)
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