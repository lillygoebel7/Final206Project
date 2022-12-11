# Names: Lilly Goebel, Saira Rathod, & Alina Parr
# Student id: 5814 4413, 0262 6614, & 9577 5805
# Email: goebelli@umich.edu, rathods@umich.edu, & amparr@umich.edu

import unittest
import sqlite3
import json
import os
import csv
import requests
from bs4 import BeautifulSoup
import re
import math
import matplotlib.pyplot as plt
import numpy as np
import statistics
from scipy.stats import norm
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


def get_country_data(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()

    cur.execute('''
    SELECT COUNT(country_table.country_name), country_table.country_name 
    FROM bands_table 
    JOIN country_table 
    ON bands_table.country_id = country_table.country_id 
    GROUP BY country_table.country_name''')

    country_data = cur.fetchall()
    return country_data


def get_tour_data(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()

    cur.execute('''
    SELECT COUNT(bands_table.date_time), bands_table.date_time
    FROM bands_table 
    WHERE date_time = '0'
    ''')

    tour_data = cur.fetchall()
    on_tour = 100 - tour_data[0][0]
    list_on_tour = (on_tour, "On Tour") 
    tour_data.append(list_on_tour)
    return tour_data


def get_avg_song_length(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor() 

    cur.execute('''
    SELECT AVG(itunes_songs.track_time), itunes_songs.track_time 
    FROM itunes_songs 
    ''')

    song_length_data = cur.fetchall()
    song_length_data = song_length_data[0][0]/ 60000


    cur.execute('''
    SELECT itunes_songs.track_time 
    FROM itunes_songs''')

    times = cur.fetchall()
    my_lst = []
    for time in times:
        my_lst.append(int(time[0]))
    sd = statistics.stdev(my_lst) / 60000

    song_data =(song_length_data,sd)
   
    return song_data


def write_csv(explicit_data, genre_data, tour_data, country_data, song_data, filename):
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

        writer.writerow([' '])
        writer.writerow(["On Tour or Not on Tour", "Number of Artisit on Tour"])
        for item in tour_data:
            t_list = []
            t_list.append(item[1])
            t_list.append(item[0])
            writer.writerow(t_list)

        writer.writerow([' '])
        writer.writerow(["Country", "Number of Events in Each Country"])
        for item in country_data:
            c_list = []
            c_list.append(item[1])
            c_list.append(item[0])
            writer.writerow(c_list)

        writer.writerow([' '])
        writer.writerow(["Average Song Length for 100 songs", "Standard Deviation"])
        s_list = []
        song_avg_data = ("%.2f" % song_data[0])
        song_sd_data = ("%.2f" % song_data[1])
        s_list.append(song_avg_data)
        s_list.append(song_sd_data)
        writer.writerow(s_list)
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
    
    plt.barh(num_genre, genre, color = 'plum')
    plt.ylabel("Genre Categories")
    plt.xlabel("Quantity")
    plt.title("Number of Aritist Top Songs per Genre")
    plt.show()

    pass


def tour_chart(tour_data):

    not_tour = tour_data[0][0]
    on_tour = tour_data[1][0]

    labels = 'Not on Tour', 'On Tour'
    colors = ['pink', 'purple']
    sizes = [not_tour, on_tour]

    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title("Artisits Not on Tour vs on Tour")
    plt.show()

    pass


def country_chart(country_data):

    country_dict = {}
    for item in country_data:
        count = item[0]
        country = item[1]
        country_dict[country] = count
        
    num_country = []
    country = []
    for x in country_dict:
        country.append(x)
        num_country.append(country_dict[x])

    plt.bar(country, num_country, color = 'powderblue')
    plt.xlabel("Countries")
    plt.ylabel("Quantity")
    plt.xticks(rotation = 40)
    plt.title("Performing Events By Countries")

    plt.show()

    pass

def avg_length_chart(song_data):

    x = np.arange(-1, 8, 0.01)
    plt.plot(x, norm.pdf(x, song_data[0], song_data[1]))
   
    plt.xlabel('Song Length in Minutes')
    plt.ylabel("Frequency")
    plt.title('Normal Distribution of Song Length in Minutes', fontsize=14)
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
    get_country_data('music_information2.db')
    get_tour_data('music_information2.db')
    get_avg_song_length('music_information2.db')


    explicit_data = get_explicit_data('music_information2.db')
    genre_data = get_genre_data('music_information2.db')
    tour_data = get_tour_data('music_information2.db')
    country_data = get_country_data('music_information2.db')
    song_data = get_avg_song_length('music_information2.db')
    write_csv(explicit_data, genre_data, tour_data, country_data, song_data, 'music_data.csv')

    # explicit_data = get_explicit_data('music_information2.db')
    explicit_chart(explicit_data)

    # genre_data = get_genre_data('music_information2.db')
    genre_chart(genre_data)

    tour_chart(tour_data)

    # country_data = get_country_data('music_information2.db')
    country_chart(country_data)

    avg_length_chart(song_data)

    
    pass

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)