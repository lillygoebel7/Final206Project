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

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def read_billboard_data(url, cur, conn):
    '''
    this function takes in the BillBoard Top 100 Artists Url. The URL is then used to create a Soup object, which is parsed through to return a list of tuples containing the artist_id and artist name
    '''
    #Database Entries
    cur.execute("CREATE TABLE IF NOT EXISTS artists (artist_id INTEGER PRIMARY KEY, artist_name STRING)")
    conn.commit()

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    lst = []
    top_artist_data = soup.find_all('div', class_="lrv-u-flex u-align-items-center@mobile-max")
    for i in top_artist_data:
        top = re.findall('>(\w+\s\w+)<', str(i))
        top_artist = top[0]
        lst.append(top_artist)
    this = soup.find_all('li', class_ = "o-chart-results-list__item // lrv-u-flex-grow-1 lrv-u-flex lrv-u-flex-direction-column lrv-u-justify-content-center lrv-u-border-b-1 u-border-b-0@mobile-max lrv-u-border-color-grey-light lrv-u-padding-l-050 lrv-u-padding-l-1@mobile-max")
    for i in this:
        for x in i:
            for n in x:
                t = n.strip()
                if t != '':
                    if t == "Bruce Sprinsteen":
                        t = "Bruce Springsteen"
                    lst.append(t)
    count = 1
    my_list = []
    for i in lst:
        my_tup = (count, i)
        my_list.append(my_tup)
        count += 1
    return(my_list)

def main():
    url = "https://www.billboard.com/charts/artist-100/"
    cur, conn = open_database('music_information2.db')
    this_val = read_billboard_data(url, cur, conn)
    pass

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)