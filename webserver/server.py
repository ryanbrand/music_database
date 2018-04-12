#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, current_app

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.227.79.146/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.227.79.146/proj1part2"
#
DATABASEURI = "postgresql://rmb2208:4410@35.227.79.146/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

# result = engine.execute("""SELECT * FROM users;""")
# for row in result:
#   print(type(row))

# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""") 


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM artists;")
  names = []
  for result in cursor:
    names.append(result['artist_name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/new_user')
def new_user():
  return render_template("new_user.html")

@app.route('/logout')
def logout():
  return render_template("index.html")

@app.route('/fail_new_user')
def fail_new_user():
  return render_template("fail_new_user.html")

@app.route('/login_fail')
def login_fail():
  return render_template("login_fail.html")

@app.route('/homepage')
def homepage():
  #artists_result = g.conn.execute("SELECT artist_name FROM artists  WHERE .userid=%s;", USERID)
  #artists = ''
  #for a in artists:
  #  artists = artists  + str(a['artist_name']) + '\n'
  #artists_result.close()

  albums_result = g.conn.execute("SELECT album_title, artist_name FROM album_saved_by a, artists t WHERE a.userid=%s AND a.artistid=t.artistid;", current_app.user_id)
  album_titles = ''
  for a in albums_result:
    album_titles = album_titles + str(a['album_title']) + ' by ' + str(a['artist_name']) + '\n'
  albums_result.close()

  songs_result = g.conn.execute("SELECT song_title, album_title, artist_name FROM song_saved_by s, artists t WHERE s.userid=%s AND s.artistid=t.artistid;", current_app.user_id)
  song_titles = ''
  for s in songs_result:
    song_titles = song_titles + str(s['song_title']) + ' from ' + str(s['album_title']) + ' by ' + str(s['artist_name']) + '\n'
  songs_result.close()
  
  priv_playlists_result = g.conn.execute("SELECT playlist_name FROM private_playlists p WHERE p.userid=%s;", current_app.user_id)
  priv_playlist_titles = ''
  for p in priv_playlists_result:
    priv_playlist_titles = priv_playlist_titles + str(p['playlist_name']) + '\n'
  priv_playlists_result.close()

  coll_playlists_result = g.conn.execute("SELECT playlist_name FROM collaborative_playlists p WHERE p.userid=%s;", current_app.user_id)
  coll_playlist_titles = ''
  for p in coll_playlists_result:
    coll_playlist_titles = coll_playlist_titles + str(p['playlist_name']) + '\n'
  coll_playlists_result.close()

  friend_playlists_result = g.conn.execute("SELECT playlist_name, user_name, userid FROM can_edit p, users u WHERE p.collaborator_userid=%s AND p.creator_userid=u.userid;", current_app.user_id)
  friend_playlist_titles = ''
  for p in friend_playlists_result:
    friend_playlist_titles = friend_playlist_titles + str(p['playlist_name']) + ' (Created by ' + str(p['user_name']) + ': ' + str(p['userid']) + ')\n'
  friend_playlists_result.close()

  friends_result = g.conn.execute("SELECT userid_2, user_name FROM users u, are_friends f WHERE f.userid_1=%s AND f.userid_2=u.userid", current_app.user_id)
  friend_names = ''
  for f in friends_result:
    friend_names = friend_names + str(f['user_name']) + ' (' + str(f['userid_2']) + ')' + '\n'
  friends_result.close()  

  context = dict(songs=song_titles, albums=album_titles, private_playlists=priv_playlist_titles, collaborative_playlists=coll_playlist_titles, friend_playlists=friend_playlist_titles, friends=friend_names)
  return render_template("homepage.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/add_new_user', methods=['POST'])
def add_new_user():
  name = request.form['name']
  userid = request.form['userid']
  password = request.form['password']
  try:
    g.conn.execute('INSERT INTO users VALUES (%s, %s, %s)', userid, name, password)
    return redirect('/')
  except Exception as e:
    return redirect('/fail_new_user')

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()

@app.route('/login2', methods=['POST'])
def login2():
  userid = request.form['userid']
  password = request.form['password']
  result = g.conn.execute("SELECT pwd FROM users WHERE users.userid=%s;", userid)

  for row in result:
    if password == row['pwd']:
      current_app.user_id = userid
      print('set USERID to ' + current_app.user_id)
      print('Successful login')
      return redirect('/homepage')
    else:
      return redirect('/login_fail')

@app.route('/search_artist', methods=['POST'])
def search_artist():
  artist_name = request.form['artist_name']
  result = g.conn.execute("SELECT * FROM artists a, albums b WHERE a.artist_name=%s AND a.artistid=b.artistid ORDER BY b.release_date DESC;", artist_name)
  album_titles = ''
  # if len(list(result)) == 0:
  #   current_app.artist_id = str(row['artistid'])
  #   return render_template("artist_fail.html")
  # else:
  for row in result:
    release_date = str(row['release_date'])
    album_title = str(row['album_title'])
    num_songs = str(row['num_songs'])
    album_titles = album_titles + '{}: released {}, {} tracks)\n'.format(album_title, release_date, num_songs)
    current_app.artist_id = str(row['artistid'])
  result.close()
    
  result2 = g.conn.execute("SELECT f.album_title, a.artist_name FROM features f, artists a WHERE f.featured_artistid=%s AND f.artistid=a.artistid", current_app.artist_id)
  album_titles2 = ''
  for row2 in result2:
    album_titles2 = album_titles2 + str(row2['album_title']) + ' by ' + str(row2['artist_name']) + '\n'
  result2.close()
      
  context = dict(artist_name=artist_name, albums=album_titles, albums_featured=album_titles2)
  return render_template("artist_results.html", **context)

@app.route('/search_album', methods=['POST'])
def search_album():
  album_title = request.form['album_title']
  result = g.conn.execute("SELECT * FROM songs s WHERE s.artistid=%s AND s.album_title=%s;", current_app.artist_id, album_title)
  song_titles = ''
  current_app.album_title = album_title
  # if len(list(result)) == 0:
  #   return render_template("album_fail.html")
  # else:
  for row in result:
    track_number = str(row['track_num'])
    song_title = str(row['song_title'])
    song_length = str(datetime.timedelta(minutes=row['song_length'])).split(".")[0]
    song_titles = song_titles + '{}: {} ({})\n'.format(track_number, song_title, song_length)
  result.close()
  context = dict(album_title=album_title, songs=song_titles)
  return render_template("album_results.html", **context)

@app.route('/add_album', methods=['POST'])
def add_album():
  album_title = request.form['album_title']
  try:
    g.conn.execute('INSERT INTO album_saved_by VALUES (%s, %s, %s)', current_app.user_id, album_title, current_app.artist_id)
    return redirect('/homepage')
  except Exception as e:
    return render_template('album_fail.html')

@app.route('/add_song', methods=['POST'])
def add_song():
  song_title = request.form['song_title']
  try:
    g.conn.execute('INSERT INTO song_saved_by VALUES (%s, %s, %s, %s)', current_app.user_id, song_title, current_app.album_title, current_app.artist_id)
    return redirect('/homepage')
  except Exception as e:
    return render_template('song_fail.html')

@app.route('/add_song_to_playlist', methods=['POST'])
def add_song_to_playlist():
  song_title = request.form['song_title']
  playlist_name = request.form['playlist_name']
  print('--------song_title=', song_title)
  print('--------playlist_name=', playlist_name)
  try:
    result = g.conn.execute('INSERT INTO in_playlist VALUES (%s, %s, %s, %s, %s)', song_title, current_app.album_title, current_app.artist_id, playlist_name, current_app.user_id)
    return redirect('/homepage')
  except Exception as e:
     return render_template('playlist_fail.html') 

@app.route('/show_playlist_songs', methods=['POST'])
def show_playlist_songs():
  playlist_name = request.form['playlist_name']
  result = g.conn.execute('SELECT artist_name, song_title, album_title FROM in_playlist p, artists a WHERE p.playlist_name=%s AND p.userid=%s AND a.artistid=p.artistid', playlist_name, current_app.user_id)
  song_titles = ''
  for row in result:
    song_title = str(row['song_title'])
    album_title = str(row['album_title'])
    artist_name = str(row['artist_name'])
    song_titles = song_title + " from " + album_title + " by " + artist_name + "\n"
  result.close()
   
  context = dict(songs=song_titles, playlist=playlist_name)
  return render_template('playlist_results.html', **context)

@app.route('/private_playlist_create', methods=['POST'])
def private_playlist_create():
  playlist_name = request.form['playlist_name']
  try:
    g.conn.execute('INSERT INTO playlists VALUES (%s, %s, %s)', playlist_name, str(datetime.date.today()), current_app.user_id)
    g.conn.execute('INSERT INTO private_playlists VALUES (%s, %s, %s)', True, playlist_name, current_app.user_id)
    return redirect('/homepage')
  except Exception as e:
    return render_template('playlist_fail.html')

@app.route('/collab_playlist_create', methods=['POST'])
def collab_playlist_create():
  playlist_name = request.form['playlist_name']
  try:
    g.conn.execute('INSERT INTO playlists VALUES (%s, %s, %s)', playlist_name, str(datetime.date.today()), current_app.user_id)
    g.conn.execute('INSERT INTO collaborative_playlists VALUES (%s, %s)', playlist_name, current_app.user_id)
    return redirect('/homepage')
  except Exception as e:
    return render_template('playlist_fail.html')

@app.route('/add_new_friend', methods=['POST'])
def add_new_friend():
  friend = request.form['friend_id']
  try:
    g.conn.execute('INSERT INTO are_friends VALUES (%s, %s, current_date)', current_app.user_id, friend)
    return redirect('/homepage')
  except Exception as e:
    return render_template('add_new_friend_fail.html') 

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
