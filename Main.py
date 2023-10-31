from crypt import methods
from flask import Flask, g, request
import mysql.connector as connector
from config import db_config
import datetime
from flask_cors import CORS
from mysql.connector.errors import DatabaseError

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


@app.before_request
def connect_db():
    g.db = connector.connect(**db_config)
    g.db.cur = g.db.cursor()


@app.after_request
def after_callback(response):
    g.db.cur.close()
    g.db.close()
    return response


@app.route("/api/availableTrains", methods=["POST"])
def hello():
    body = request.json
    cur = g.db.cur
    cur.execute(
        f"""select distinct Train_No,Source_Station_Name, Source_Station_Code, Destination_Station_Code,Destination_Station_Name from train_info where Source_Station_Code='{body.get("from_station")}' AND Destination_Station_Code='{body.get("destination")}';"""
    )
    data = []
    data_list = cur.fetchall()
    for value in data_list:
        row = dict(zip(cur.column_names, value))
        data.append(row)
    return data


@app.route("/api/bookTicket", methods=["POST"])
def book_ticket():
    body = request.json
    cur = g.db.cur
    time = datetime.datetime.now()
    date = time.date().strftime("%d-%m-%Y")
    cur.execute(
        f"""INSERT INTO bookings(Train_No,Passenger_Name,Mobile_No,Passenger_Adhaar,Date_of_Booking,Class) VALUES('{body.get("train_no")}','{body.get("name")}','{body.get("phone_no")}','{body.get("adhaar_no")}','{date}','{body.get("coach_type")}');"""
    )
    g.db.commit()
    return {"message": "Success"}


@app.route("/api/myTickets", methods=["POST"])
def user_tickets():
    body = request.json
    cur = g.db.cur
    cur.execute(
        f"""select * from bookings where Passenger_Name='{body.get("name")}' AND Mobile_No='{body.get("phone_no")}'"""
    )
    data = []
    for value in cur.fetchall():
        row = dict(zip(cur.column_names, value))
        data.append(row)
    return data


@app.route("/api/cancelTicket", methods=["POST"])
def cancel_ticket():
    body = request.json
    cur = g.db.cur
    cur.execute(
        f"""delete from bookings where Booking_ID={body.get("ticket_id")} AND Mobile_No='{body.get("phone_no")}';"""
    )
    try:
        g.db.commit()
    except DatabaseError:
        return {"message": "Error"}
    return {"message": "Success"}


if __name__ == "__main__":
    app.run()
