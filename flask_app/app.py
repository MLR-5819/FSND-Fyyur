#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config') #connects to local postgres with config.py
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    genres = db.Column(db.String(50))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  locations = db.session.query(Venue.id, Venue.city, Venue.state, Venue.name).distinct(Venue.city, Venue.state).all()
  data = [] 

  for venues in locations:
    shows = db.session.query(Show).filter(Show.venue_id==venues.id).all()
    num_upcoming = 0
    
    for time in shows:
      if time.start_time > datetime.now():
        num_upcoming += 1
    
    data.append({
      "city": venues.city,
      "state": venues.state,
      "venues": [{
        "id": venues.id,
        "name": venues.name,
        "num_upcoming_shows": num_upcoming,
      }]
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  user_search = request.form.get('search_term', '')
  venues_search = db.session.query(Venue).filter(Venue.name.ilike(f'%{user_search}%')).all()

  response = {}
  data = []
  tmp = {}

  for venue in venues_search:
    shows = db.session.query(Show).filter(Show.venue_id==venue.id).all()
    num_upcoming = 0
    for time in shows:
      if time.start_time > datetime.now():
        num_upcoming += 1

    tmp = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming,
    }
    data.append(tmp)

  response = {
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  venue = db.session.query(Venue).filter(Venue.id==venue_id).one()
  shows = db.session.query(Show).filter(Show.venue_id==venue_id).all()
  past_shows = []
  upcoming_shows = []
  
  num_upcoming = 0
  num_past = 0
  for time in shows:
    artist = db.session.query(Artist).filter(Artist.id==time.artist_id).all()
    tmp = {
      "artist_id": time.artist_id,
      "artist_name": time.artist.name,
      "artist_image_link": time.artist.image_link,
      "start_time": format_datetime(str(time.start_time)),
    }

    if time.start_time > datetime.now():
      upcoming_shows.append(tmp)
      num_upcoming += 1
    else:
      past_shows.append(tmp)
      num_past += 1
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": num_past,
    "upcoming_shows_count": num_upcoming,
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False
  success = False
  try:
    form = VenueForm()
    new_venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
    ) 

    db.session.add(new_venue)
    db.session.commit()
    success = True
  except:
    error = True
    if error:
      db.session.rollback()
      flash('ERROR: Venue ' + request.form['name'] + ' could not be listed! Please try again')
  finally:
    db.session.close()
    # on successful db insert, flash success
    if success:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  success = False
  
  try: 
    db.session.query(Venue).filter(Venue.id==venue_id).delete()
    db.session.commit()
    success = True
  except:
    error = True
    if error:
      db.session.rollback()
      flash('ERROR: Venue ' + request.form['name'] + ' could not be deleted! Please try again.')
  finally:
    db.session.close()
    if success:
      flash('Venue ' + request.form['name'] + ' was successfully deleted!')
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists = db.session.query(Artist).order_by(Artist.name).all()
  data = []

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  user_search = request.form.get('search_term', '')
  artists_search = db.session.query(Artist).filter(Artist.name.ilike(f'%{user_search}%')).all()

  response = {}
  data = []
  tmp = {}

  for artist in artists_search:
    shows = db.session.query(Show).filter(Show.artist_id==artist.id).all()
    num_upcoming = 0
    for time in shows:
      if time.start_time > datetime.now():
        num_upcoming += 1

    tmp = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming,
    }
    data.append(tmp)

  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  artist = db.session.query(Artist).filter(Artist.id==artist_id).one()
  shows = db.session.query(Show).filter(Show.artist_id==artist_id).all()
  past_shows = []
  upcoming_shows = []
  
  num_upcoming = 0
  num_past = 0
  for time in shows:
    venue = db.session.query(Venue).filter(Venue.id==time.venue_id).all()
    tmp = {
      "venue_id": time.venue_id,
      "venue_name": time.venue.name,
      "venue_image_link": time.venue.image_link,
      "start_time": format_datetime(str(time.start_time)),
    }

    if time.start_time > datetime.now():
      upcoming_shows.append(tmp)
      num_upcoming += 1
    else:
      past_shows.append(tmp)
      num_past += 1
  
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": num_past,
    "upcoming_shows_count": num_upcoming,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  edit_artist = db.session.query(Artist).filter(Artist.id==artist_id).one()
  
  artist={
    "id": edit_artist.id,
    "name": edit_artist.name,
    "genres": edit_artist.genres,
    "city": edit_artist.city,
    "state": edit_artist.state,
    "phone": edit_artist.phone,
    "facebook_link": edit_artist.facebook_link,
  }
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  success = False

  try:
    form = ArtistForm()
    edit_artist = {
      "name": form.name.data,
      "city": form.city.data,
      "state": form.state.data,
      "phone": form.phone.data,
      "genres": form.genres.data,
      "facebook_link": form.facebook_link.data,
    } 

    db.session.query(Artist).filter(Artist.id==artist_id).update(edit_artist)
    db.session.commit()
    success = True
  except:
    error = True
    if error:
      db.session.rollback()
      flash('ERROR: Artist ' + request.form['name'] + ' could not be updated! Please try again')
  finally:
    db.session.close()
    # on successful db insert, flash success
    if success:
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
 

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  edit_venue = db.session.query(Venue).filter(Venue.id==venue_id).one()
  
  venue={
    "id": edit_venue.id,
    "name": edit_venue.name,
    "genres": edit_venue.genres,
    "city": edit_venue.city,
    "state": edit_venue.state,
    "phone": edit_venue.phone,
    "facebook_link": edit_venue.facebook_link,
  }
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  error = False
  success = False
  try:
    form = VenueForm()
    edit_venue = {
      "name": form.name.data,
      "city": form.city.data,
      "state": form.state.data,
      "address": form.address.data,
      "phone": form.phone.data,
      "genres": form.genres.data,
      "facebook_link": form.facebook_link.data,
    } 

    db.session.query(Venue).filter(Venue.id==venue_id).update(edit_venue)
    db.session.commit()
    success = True
  except:
    error = True
    if error:
      db.session.rollback()
      flash('ERROR: Venue ' + request.form['name'] + ' could not be updated! Please try again')
  finally:
    db.session.close()
    # on successful db insert, flash success
    if success:
      flash('Venue ' + request.form['name'] + ' was successfully updated!') 
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False
  success = False
  try:
    form = ArtistForm()
    new_artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
    ) 

    db.session.add(new_artist)
    db.session.commit()
    success = True
  except:
    error = True
    if error:
      db.session.rollback()
      flash('ERROR: Artist ' + request.form['name'] + ' could not be listed! Please try again.')
  finally:
    db.session.close()
    # on successful db insert, flash success
    if success:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = db.session.query(Show).all()
  data=[]

  for show in shows:
    venue = db.session.query(Venue).filter(show.venue_id==Venue.id).all()
    artist = db.session.query(Artist).filter(show.artist_id==Artist.id).all()

    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time)),
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  error = False
  success = True
  try:
    form = ShowForm()
    new_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )

    db.session.add(new_show)
    db.session.commit()
    success = True
  except:
    error = True
    if error:
      db.session.rollback()
      flash('ERROR: Show could not be listed! Please try again')
  finally:
    db.session.close()
    # on successful db insert, flash success
    if success:
      flash('Show was successfully listed!')
  
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''