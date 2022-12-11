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
import csv
import matplotlib.pyplot as plt
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
    try:
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
            country = bands_data[x][2]
            cur.execute('INSERT OR IGNORE INTO bands_table (artist_id, date_time, country_id) VALUES (?,?,?)', (artist_id, date_time, country))
        conn.commit()
    except:
        print("All Data Has Been Loaded")
    pass


def get_explicit_data(db_filename):
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
    explicit_data = cur.fetchall()
    return explicit_data


def get_genre_data(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()
    cur.execute('''
    SELECT COUNT(genre_table.genre_name), genre_table.genre_name 
    FROM itunes_songs 
    JOIN genre_table 
    ON itunes_songs.genre = genre_table.genre_id 
    GROUP BY genre''')
    genre_data = cur.fetchall()
    return genre_data

def write_csv(explicit_data, genre_data, filename):
    with open(filename, 'w', newline="") as fileout:
        writer = csv.writer(fileout)
        header = ['Explict or Not Explicit','Number of Explicit Songs']
        writer.writerow(header)
        for item in explicit_data:
            e_list = []
            if item[1] == 1:
                e_list.append("Explicit")
            elif item[1] == 0:
                e_list.append("Not Explicit")
            e_list.append(item[0])
            writer.writerow(e_list)
        writer.writerow([' '])
        writer.writerow(["Genre", "Number of songs in Genre"])
        for item in genre_data:
            g_list = []
            g_list.append(item[1])
            g_list.append(item[0])
            writer.writerow(g_list)
    pass

def explicit_chart(explicit_data):
    explict = explicit_data[0][0]
    nonexplicit = explicit_data[1][0]
    labels = 'Explicit', 'Non-Explicit'
    colors = ['gold', 'yellowgreen']
    sizes = [explict, nonexplicit]
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title("Explicit vs Non-Explicit Songs")
    plt.show()
    pass

def genre_chart(genre_data):
    dict = {}
    for item in genre_data:
        count = item[0]
        genre = item[1]
        dict[genre] = count
    num_genre = []
    genre = []
    for x in dict:
        num_genre.append(x)
        genre.append(dict[x])
    plt.barh(num_genre, genre, color = 'yellowgreen')
    plt.ylabel("Genre Categories")
    plt.xlabel("Quantity")
    plt.title("Number of Aritist Top Songs per Genre")
    plt.show()
    pass

def main():
    url = "https://www.billboard.com/charts/artist-100/"
    cur, conn = open_database('music_information2.db')
    billboard_data = read_billboard_data(url, cur, conn)
    iTunes_list = iTunesSearch(billboard_data, conn, cur)
    bands_data = bandsintown(billboard_data, conn, cur)
    enter_data(billboard_data, iTunes_list, bands_data, conn, cur)
    explicit_table(conn, cur)
    get_explicit_data('music_information2.db')
    get_genre_data('music_information2.db')
    explicit_data = get_explicit_data('music_information2.db')
    genre_data = get_genre_data('music_information2.db')
    write_csv(explicit_data, genre_data, 'music_data.csv')
    explicit_data = get_explicit_data('music_information2.db')
    explicit_chart(explicit_data)
    genre_data = get_genre_data('music_information2.db')
    genre_chart(genre_data)
    pass

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)