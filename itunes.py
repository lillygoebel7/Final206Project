# Names: Lilly Goebel, Saira Rathod, & Alina Parr
# Student id: 5814 4413, 0262 6614, & 9577 5805
# Email: goebelli@umich.edu, rathods@umich.edu, & amparr@umich.edu

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

def iTunesSearch(billboard_data, conn, cur):
    cur.execute("CREATE TABLE IF NOT EXISTS itunes_songs (artist_id INTEGER PRIMARY KEY, trackName STRING, genre STRING, release_date STRING, track_time INTEGER, trackExplicitness STRING)")
    conn.commit()

    itunes_lst = []
    for artist in billboard_data:
        artist_id = artist[0]
        artist_name = artist[1]
        try:
            data = requests.get(f"https://itunes.apple.com/search?term={artist_name}&entity=song&media=music&limit=1")
            content = json.loads(data.text)
            track_name = content['results'][0]['trackName']
            release_date = content["results"][0]["releaseDate"]
            track_time = content["results"][0]["trackTimeMillis"]

            cur.execute("CREATE TABLE IF NOT EXISTS genre_table (genre_id INTEGER PRIMARY KEY, genre_name STRING)")
            conn.commit()

            genre = content['results'][0]['primaryGenreName']
            genre_list = ["Pop", "Soundtrack", "Country", "Hip-Hop/Rap", "Holiday", "Christmas", "Jazz", "R&B/Soul", "Vocal Pop", "Alternative", "Metal", "Musicals", "Dance", "Singer/Songwriter", "Rock", "Hip-Hop"]
            genre_dict = {}
            count = 0
            for genre_name in genre_list:
                genre_dict[genre_name] = count
                count += 1
            for i in genre_dict:
                if genre == i:
                    genre = genre_dict[i]
                    cur.execute('INSERT OR IGNORE INTO genre_table (genre_id, genre_name) VALUES (?,?)', (genre, i))
        
            trackExplicitness = content['results'][0]['trackExplicitness']
            if trackExplicitness == "notExplicit":
                trackExplicitness = 0
            else:
                trackExplicitness = 1
            itunes_tup = (artist_id, track_name, genre, release_date, track_time, trackExplicitness)
            itunes_lst.append(itunes_tup)
        except:
            not_avail = "N/A"
            itunes_tup = (artist_id, not_avail, not_avail, not_avail, not_avail, not_avail)
            itunes_lst.append(itunes_tup)
    return itunes_lst

def explicit_table(conn, cur):
    cur.execute("CREATE TABLE IF NOT EXISTS explicit_table (explicit_id INTEGER PRIMARY KEY, explicit STRING)")
    conn.commit()
    cur.execute('INSERT OR IGNORE INTO explicit_table (explicit_id, explicit) VALUES (?,?)', (0, "not explicit"))
    cur.execute('INSERT OR IGNORE INTO explicit_table (explicit_id, explicit) VALUES (?,?)', (1, "explicit"))
    cur.execute("DROP TABLE IF EXISTS new_songs")
    conn.commit()


def main():
    url = "https://www.billboard.com/charts/artist-100/"
    cur, conn = open_database('music_information2.db')
    billboard_data = read_billboard_data(url, cur, conn)
    iTunesSearch(billboard_data, conn, cur)
    explicit_table(conn, cur)
    pass

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)