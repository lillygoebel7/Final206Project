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
    cur.execute("CREATE TABLE IF NOT EXISTS bands_table (artist_id INTEGER PRIMARY KEY, date_time STRING, venue_name STRING, country STRING)")
    conn.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS venue_table (venue_id INTEGER PRIMARY KEY, venue_name STRING)")
    conn.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS country_table (country_id INTEGER PRIMARY KEY, country_name STRING)")
    conn.commit()

    bands_list = []
    venue_lst = []
    venue_dict = {}
    venue_count = 0
    country_dict={}
    country_count=0
    for i in billboard_data:
        artist_id = i[0]
        artist = i[1]
        data = requests.get(f'https://rest.bandsintown.com/artists/{artist}/events?app_id=7046cca7a6f82b8b0f8e50a15cc4ff9e')
        content = json.loads(data.text)
        if content == []:
            date_time = "Not on Tour"
            venue_name = "N/A"
            country = "N/A"
            my_tup = (artist_id, date_time, venue_name, country)
        elif content != []:
            inner_content = content[0]
            for d in inner_content:
                date_time = inner_content['datetime']
                venue_name = inner_content['venue']['name']
                if venue_name not in venue_dict:
                    venue_dict[venue_name] = venue_count
                    cur.execute('INSERT OR IGNORE INTO venue_table (venue_id, venue_name) VALUES (?,?)', (venue_count, venue_name))
                    conn.commit()
                    venue_name = venue_count
                    venue_count += 1

                country = inner_content['venue']['country']
                if country not in country_dict:
                    country_dict[country] = country_count    
                    cur.execute('INSERT OR IGNORE INTO country_table (country_id, country_name) VALUES (?,?)', (country_count, country))
                    conn.commit()
                    country = country_count
                    country_count += 1
            my_tup = (artist_id, date_time, venue_name, country)


            my_tup = (artist_id, date_time, venue_name, country)
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