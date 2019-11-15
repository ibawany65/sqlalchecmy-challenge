import datetime as dt
import numpy as np
import pandas as pd
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Setup The Database ################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect database and tables
Base = automap_base()
Base.prepare(engine, reflect=True)

#Save reference for tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session to DB
session = Session(engine)

# Use Flask to serve
app = Flask(__name__)
@app.route("/")
def welcome():
    return (
        f"Aloha and Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Show precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()

    # Create dictionary with date as key and prcp as value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Show list of stations."""
    results = session.query(Station.station).all()

    # Create list from results with numpy ravel
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Show temperature observations for last year."""
    # Calculate the date 1 year ago from last date in database
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query all tobs from primary stations from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()

    # create list for temps using numpy ravel
    temps = list(np.ravel(results))

    # show the results as json
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Show TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # convert to a list with numpy ravel
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # convert to a list with numpy ravel
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()
