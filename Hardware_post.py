from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi import HTTPException

app = FastAPI()

DATABASE_URL = "dbname=dementia_guardian_db user=dementia_guardian_user password=kfczNoAgGcoeXRkWntJ2JimdzoEerlnv host=dpg-cqeagspu0jms7397k2hg-a.oregon-postgres.render.com port=5432"





# Allow CORS for all origins during development (replace "*" with your actual frontend URL in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class Sensor(BaseModel):
    location_long: float
    location_lat: float
    source: str


class User(BaseModel):
    home_long: float
    home_lat: float


@app.post("/sensor")
async def create_sensor_data(sensor: Sensor):
    conn = None
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(DATABASE_URL)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Get current datetime
        now = datetime.now()

        # Insert sensor data and current datetime into the table
        cur.execute(
            """
            INSERT INTO alert_history (time_stamp, location_long, location_lat, source)
            VALUES (%s, %s, %s, %s)
            """,
            (now, sensor.location_long, sensor.location_lat, sensor.source)
        )

        # Commit the changes
        conn.commit()

        return {"status": "success"}

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        # Close communication with the database
        if conn:
            cur.close()
            conn.close()


@app.post("/user")
async def create_user(user: User):
    conn = None
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(DATABASE_URL)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Insert user data into the table with correct table name casing
        cur.execute(
            """
            INSERT INTO user_iot (home_long, home_lat)
            VALUES (%s, %s)
            """,
            (user.home_long, user.home_lat)
        )

        # Commit the changes
        conn.commit()

        return {"status": "success"}

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        # Close communication with the database
        if conn:
            cur.close()
            conn.close()


@app.get("/home_location")
async def get_home_location():
    conn = None
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Execute a query to fetch the home location
        # replace with your actual SQL query
        cur.execute("SELECT home_lat, home_long FROM home_location_table")
        home_lat, home_long = cur.fetchone()

        return {"home_lat": home_lat, "home_long": home_long}

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        # Close communication with the database
        if conn:
            cur.close()
            conn.close()


class MedicineAlert(BaseModel):
    time: int
    medicine_name: str


@app.get("/medicine_alerts", response_model=MedicineAlert)
async def get_medicine_alerts():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""SELECT "time", "medicine_name" FROM "Medicine_Alert" """)
        time, medicinename = cur.fetchone()
        return {"time": time, "medicine_name": medicinename}
    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}
    finally:
        if conn:
            cur.close()
            conn.close()
