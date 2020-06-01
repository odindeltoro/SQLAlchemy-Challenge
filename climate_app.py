#################################################
# Import dependencies
#################################################
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Hyperlinks
#################################################
# Welcome page: http://127.0.0.1:5000/
# Precipitation page: http://127.0.0.1:5000/api/v1.0/precipitation
# Station page: http://127.0.0.1:5000/api/v1.0/stations
# Temperature observations page: http://127.0.0.1:5000/api/v1.0/tobs
# Start date page: http://127.0.0.1:5000/api/v1.0/2016-08-23
# Start-end date page: http://127.0.0.1:5000/api/v1.0/2016-08-23/2017-08-23

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Weather Data, before planning your trip you should review it"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Set a start date between 2016-08-23/2017-08-22: /api/v1.0/2016-08-23<YYYY-MM-DD><br/>"
        f"Set a start date between 2016-08-23/2017-08-22 and end date between 2016-08-24/2017-08-23: /api/v1.0/2016-08-23/2017-08-23<YYYY-MM-D/YYYY-MM-DD><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert query results to a dictionary using date as the key and prcp as the value and return the JSON representation of your dictionary."""
    # Query precipitation, filter las year and set DataFrame
    df = pd.DataFrame(session.query(Measurement.date, Measurement.prcp).filter((Measurement.date >= '2016-08-23') & (Measurement.date <= '2017-08-23')).order_by(Measurement.date).all())
    # Convert to a dictionary
    precipitation_dictionary = df.to_dict()
    return jsonify(precipitation_dictionary)

@app.route("/api/v1.0/stations")
def station():
    """Return a JSON list of stations from the dataset."""
    # List of all unique stations
    station_list = session.query(Measurement.station).distinct().all()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data and return a JSON list of temperature observations (TOBS) for the previous year."""
    # Filter by most active station
    highest_station_active = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    # List of all temperature observations
    temperatures = session.query(Measurement.station,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.station == highest_station_active.station).group_by(Measurement.station).all()
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>")
def start(start):
    """ Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start."""
    """ Calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    # Set a start date and calculate minimum, maximum and average temperatures
    start_temperatures = session.query(Measurement.date,func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<='2017-08-23').all()
    tmin = start_temperatures[0][0]
    tavg = start_temperatures[0][1]
    tmax = start_temperatures[0][2]
    
    # Convert to a dictionary
    start_temperatures_dict = {}
    start_temperatures_dict["TMIN"] = tmin
    start_temperatures_dict["TAVG"] = tavg
    start_temperatures_dict["TMAX"] = tmax
    return jsonify(start_temperatures_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a start-end range."""
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    # Set a range of dates and calculate minimum, maximum and average temperatures
    range_temperatures = session.query(Measurement.date,func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    tmin = range_temperatures[0][0]
    tavg = range_temperatures[0][1]
    tmax = range_temperatures[0][2]
    
    # Convert to a dictionary
    range_temperatures_dict = {}
    range_temperatures_dict["TMIN"] = tmin
    range_temperatures_dict["TAVG"] = tavg
    range_temperatures_dict["TMAX"] = tmax
    return jsonify(range_temperatures_dict)

if __name__ == '__main__':
    app.run(debug=True)
