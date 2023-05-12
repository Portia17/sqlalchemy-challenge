# Import the dependencies.
import numpy as np

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
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement= Base.classes.measurement
Stations= Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"For precipitation data from the last 12 months of data: /api/v1.0/precipitation<br/>"
        f"For station list: /api/v1.0/stations<br/>"
        f"For temperature data from the last 12 months of data at the most active station:\
              /api/v1.0/tobs<br/>"
        f"For min, max and avg temp data from a specified start date, format(yyyy-mm-dd): /api/v1.0/start<br/>/"
        f"For min, max and avg temp data from a specified start and end date, format(yyyy-mm-dd): /api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=(dt.date(2016, 8, 23))).all()
    session.close()
    
    prcp_list=[]
    for date, prcp in results:
        prcp_dict={}
        prcp_dict['date']= date
        prcp_dict['prcp']= prcp
        prcp_list.append(prcp_dict)
    
    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Stations.station).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results= session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=(dt.date(2016, 8, 23)))\
            .filter(Measurement.station=='USC00519281').all()
    session.close()

    tobs_list=[]
    for date, tobs in results:
        tobs_dict={}
        tobs_dict['date']= date
        tobs_dict['tobs']= tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>/")
def start(start):
    results=session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date>=start).all()
    session.close()

    start_list=[]
    for tmax, tmin, tavg in results:
        start_dict={}
        start_dict['max']= tmax
        start_dict['min']= tmin
        start_dict['avg']= tavg
        start_list.append(start_dict)

    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>/")
def time(start,end):
    session= Session(engine)
    results=session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    session.close()

    time_list=[]
    for tmax, tmin, tavg in results:
        time_dict={}
        time_dict['max']= tmax
        time_dict['min']= tmin
        time_dict['avg']= tavg
        time_list.append(time_dict)

    return jsonify(time_list)



if __name__ == '__main__':
    app.run(debug=True)

