
import requests
from bs4 import BeautifulSoup
import string
import urlparse 
import re
import locale
import pickle
from dateutil import parser
import dateutil.parser

# The create_dict function creates a dictionary of movies and their url id from The-numbers.com.  
# You fil the function with the value for the year you want to start pulling movies and it will create the urls 
# for the top grossing movies from that year through 2015.  
# This function then call the get_movieid fucntion for each url and scrape that site of the movie title and movie id
# and put it in to the predefined movies_dict.  This function will grab the top 200 grossing movies for that year.

def create_dict(year):
	while year < 2015:
		url = 'http://www.the-numbers.com/market/%d/top-grossing-movies' % (year)
		get_movieid(url)
		year += 1



def get_movieid(url):
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page)
    rows = soup.find('table').find_all('tr')[1:201]
    for row in rows:
        try:
            title = filter(lambda x: x in string.printable, row.a.text)
            title = str(title)
            movies_dict[title]= {}
            movie_id = row.a['href']
            par = urlparse.urlparse(movie_id).path.lstrip("/movie")
            movies_dict[title]['id']= par
        except:
            print row


# Now that you have created a dictionary of all the movies you want information on, 
# the get_details() function will us the gnerated url to grab the summary details of the film.
# I was not interested int he total gross domestic or international numbers so this funciton 
# does not grab that data. It places the information about each movie into a dictionary inside
# the movies dict.

def get_details(url, movie):
    print movie 
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page) 
    
    try:
        rt_score = soup.find(id="movie_ratings").find_all('a')[2].br.next_sibling
        rt_score = str(rt_score)
        match = re.search(r'\d+', rt_score)
        critic_score = int(match.group())
    except:
        critic_score = ""
    
    rows = soup.find_all('table')[2].find_all('tr')
    for row in rows:
        if row.find_all('td')[0].text == u'Production\xa0Budget:':
            budget = row.find_all('td')[1].text
            locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
            prod_budget = locale.atoi(budget.strip("$"))
        if row.find_all('td')[0].text =='Domestic Releases:':
            wide = '(Wide)' in row.find_all('td')[1].text
            release =  row.find_all('td')[1]
            release = str(release.text).split(" (")
            release_dt = parser.parse(release[0])
            company = str(row.find_all('td')[1].find('a').text)
        if row.find_all('td')[0].text == u'MPAA\xa0Rating:':
            rating = str(row.find_all('td')[1].find('a').text)
        if row.find_all('td')[0].text == u'Production\xa0Method:':
            prod_method = str(row.find_all('td')[1].find('a').text)
        if row.find_all('td')[0].text =='Running Time:':
            runtime = row.find_all('td')[1].text
            runtime = runtime.replace(' minutes','')
            run_time = int(runtime)
        if row.find_all('td')[0].text =='Source:':
            source = str(row.find_all('td')[1].find('a').text)
        if row.find_all('td')[0].text =='Genre:':
            genre = str(row.find_all('td')[1].find('a').text)

    try:
    	movies_dict[movie]['release']= wide
    except: 
    	movies_dict[movie]['release']= ""
    try:
        movies_dict[movie]['rating']= rating
    except: 
        movies_dict[movie]['rating']= ""
    try:
        movies_dict[movie]['budget']= prod_budget
    except: 
        movies_dict[movie]['budget']= ""
    try:
        movies_dict[movie]['budget']= prod_budget
    except:
        movies_dict[movie]['budget']= ""
    try:
        movies_dict[movie]['method']= prod_method
    except:
        movies_dict[movie]['method']= ""
    try:
        movies_dict[movie]['source']= source
    except:
        movies_dict[movie]['source']= ""
    try:    
        movies_dict[movie]['genre']= genre
    except:
        movies_dict[movie]['genre']= ""
    try:
        movies_dict[movie]['distribution']= company
    except:
        movies_dict[movie]['distribution']= ""
    try:
        movies_dict[movie]['runtime']= run_time
    except: 
        movies_dict[movie]['runtime']= ""
    try:
        movies_dict[movie]['critic_rating']= critic_score
    except:
        movies_dict[movie]['critic_rating']= ""
   
# The get_weeklys() function works the same as the get_details function, but
# for the box office data by week.

def get_weeklys(url, movie):
    def to_date(datestring):
        date = dateutil.parser.parse(datestring)
        return date

    def money_to_int(moneystring):
        moneystring = moneystring.replace('$', '').replace(',', '')
        return int(moneystring)

    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page) 
    rows = soup.find(text = 'Weekend Box Office Performance').next_element.next_element
    rowset = rows.find_all('tr')[1:6]
    week_count = 0
    for row in rowset:
        datestring = row.find_all('td')[0].text
        date = to_date(datestring)

        rank = int(row.find_all('td')[1].text)

        earn = row.find_all('td')[2].text
        gross = money_to_int(earn)

        count = row.find_all('td')[4].text
        theaters = int(count.replace(',', ''))

        per = row.find_all('td')[5].text
        per_theater = money_to_int(per)
        week_count += 1

        movies_weekly[movie]['weekend%d_date'% week_count]= date
        movies_weekly[movie]['weekend%d_rank'% week_count]= rank
        movies_weekly[movie]['weekend%d_gross'% week_count] = gross
        movies_weekly[movie]['weekend%d_theaters'% week_count] = theaters
        movies_weekly[movie]['weekend%d_pertheater'% week_count] = per_theater

# 
# This is the main functio that calls all of the previous functions.  After running this,
# you should have a dictionary for all of the top 200 grossing movies for each year and
# all of their corresponding information in an inner dictionary.

def scrape(movies_dict):
    for movie in movies_dict: 
        print movie
        summary_url = 'http://www.the-numbers.com/movie/%s#tab=summary' % (str(movies_dict[movie]['id']))
        try:
            get_details(summary_url, movie)
        except:
            print "------Could not get details for " + movie
        boxoffice_url = 'http://www.the-numbers.com/movie/%s#tab=box-office' % (str(movies_dict[movie]['id']))
        try:
            get_weeklys(boxoffice_url, movie)
        except: 
            print "-----Could not get weekly for " + movie



movies_dict= {}


create_dict(2003)

movies_weekly = movies_dict

scrape(movies_dict)



with open('movie_info_dicts.pkl', 'w') as picklefile:
    pickle.dump(movies_dict, picklefile)


with open('movie_weekly_dicts.pkl', 'w') as picklefile:
    pickle.dump(movies_weekly, picklefile)