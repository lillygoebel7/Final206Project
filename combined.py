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
from itunes import iTunesSearch
from itunes import explicit_table
from bands import bandsintown

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def enter_data(billboard_data, iTunes_list, bands_data, conn, cur):
    cur.execute("SELECT max(artist_id) FROM artists")
    count = cur.fetchone()[0]

    if count == None:
        count = 0

    for x in range(count,count+25):
        artist_id = billboard_data[x][0]
        artist_name = billboard_data[x][1]
        cur.execute('INSERT OR IGNORE INTO artists (artist_id, artist_name) VALUES (?,?)', (artist_id, artist_name))

        artist_id = iTunes_list[x][0]
        trackname = iTunes_list[x][1]
        genre = iTunes_list[x][2]
        release_date = iTunes_list[x][3]
        track_time = iTunes_list[x][4]
        trackExplicitness = iTunes_list[x][5]
        cur.execute('INSERT OR IGNORE INTO itunes_songs (artist_id, trackName, genre, release_date, track_time, trackExplicitness) VALUES (?,?,?,?,?,?)', (artist_id, trackname, genre, release_date, track_time, trackExplicitness))

        artist_id = bands_data[x][0]
        date_time = bands_data[x][1]
        venue_name = bands_data[x][2]
        country = bands_data[x][3]
        cur.execute('INSERT OR IGNORE INTO bands_table (artist_id, date_time, venue_name, country) VALUES (?,?,?,?)', (artist_id, date_time, venue_name, country))
    conn.commit()
    pass


def get_explicit_chart(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*), trackExplicitness
    FROM itunes_songs
    JOIN  explicit_table
    ON explicit_table.explicit_id= itunes_songs.trackExplicitness
    GROUP BY explicit_table.explicit
    """)
    data = cur.fetchall()
    explict_data = data[0][0]
    nonexplicit_data = data[1][0]

    labels = 'Explicit', 'Non-Explicit'
    colors = ['gold', 'yellowgreen']
    sizes = [explict_data, nonexplicit_data]

    # plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    # plt.title("Explicit vs Non-Explicit Songs")
    # plt.show()
    pass


def get_avg_lyrics_chart(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*), trackExplicitness
    FROM itunes_songs
    JOIN  explicit_table
    ON explicit_table.explicit_id= itunes_songs.trackExplicitness
    GROUP BY explicit_table.explicit
    """)



def main():
    url = "https://www.billboard.com/charts/artist-100/"
    cur, conn = open_database('music_information2.db')
    billboard_data = read_billboard_data(url, cur, conn)
    iTunes_list = iTunesSearch(billboard_data, conn, cur)
    bands_data = bandsintown(billboard_data, conn, cur)
    enter_data(billboard_data, iTunes_list, bands_data, conn, cur)
    explicit_table(conn, cur)
    pass

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)