import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
#from datetime import date
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
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

###  * Home page.
###  * List all routes that are available.
@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Climate Information API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>start date/<end>end date 'YYYY-MM-DD/YYYY-MM-DD'<br/>"
        f"/api/v1.0/<start>start date 'YYYY-MM-DD'<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
# Create our session (link) from Python to the DB
    session = Session(engine)


###  * Convert the query results to a dictionary using `date` as the key and `prcp` # as the value.
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precip_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        precip_data.append(prcp_dict)

    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

###  * Return a JSON list of stations from the dataset.
    results = session.query(Station.station, Station.name).all()

    session.close()

    station_data = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_data.append(station_dict)

    return jsonify(station_data)


###  * Query the dates and temperature observations of the most active station for # the last year of data.
###  * Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    act_station = 'USC00519281'
    results_tobs = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= (year_ago)).filter(Measurement.station == act_station).\
    order_by(Measurement.date).all()

    session.close()

    temp_data = []
    for date, station, temp in results_tobs:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temp"] = temp
        temp_data.append(temp_dict)

    return jsonify(temp_data)


# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal #to the start date.
@app.route("/api/v1.0/<start>")
def S_dates(start):
# Create our session (link) from Python to the DB
    session = Session(engine)
    
    last_dt = dt.date(2017, 8, 23)
    s_dt = dt.date.fromisoformat(start) 
    e_dt = last_dt

    results_stats = session.query(func.max(Measurement.tobs),\
    func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= (s_dt)).filter(Measurement.date <= (e_dt)).all()                     
                                                                
    session.close()
           
    stat_data = []
    for max, min, avg in results_stats:
        stat_dict = {}
        stat_dict["Max"] = max
        stat_dict["Min"] = min
        stat_dict["AVG"] = avg                                      
        stat_data.append(stat_dict)
        if s_dt > last_dt:
            return jsonify({"error": f"Date selected is after the last day of the dataset {last_dt}."}), 404
  
    return jsonify(f'The following is the average, maximum and minimum \
    temperatures from all the stations between {s_dt} and {e_dt}.', stat_data)


#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between #the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def S_E_dates(start, end):
# Create our session (link) from Python to the DB
    session = Session(engine)
    
    last_dt = dt.date(2017, 8, 23)
    s_dt = dt.date.fromisoformat(start) 
    e_dt = dt.date.fromisoformat(end)
    
    results_stats = session.query(func.max(Measurement.tobs),\
    func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= (s_dt)).filter(Measurement.date <= (e_dt)).all()                     
                                                                
    session.close()
           
    stat_data = []
    for max, min, avg in results_stats:
        stat_dict = {}
        stat_dict["Max"] = max
        stat_dict["Min"] = min
        stat_dict["AVG"] = avg                                      
        stat_data.append(stat_dict)
        if s_dt > last_dt or e_dt > last_dt:
            return jsonify({"error": f"Date selected is after the last day of the dataset {last_dt}."}), 404
  
    return jsonify(f'The following is the average, maximum and minimum temperatures from all the stations between {s_dt} and {e_dt}.', stat_data)



if __name__ == "__main__":
    app.run(debug=True)
