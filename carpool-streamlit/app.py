import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Nanded City Carpool", layout="centered")

pickup_points = [
    "Sarang", "Asawari", "Madhuvanti",
    "Shubh-Kalyan", "Pancham", "Sargam", "Sur"
]
pickup_index = {name: i for i, name in enumerate(pickup_points)}

# ---------------- DATABASE ----------------
conn = sqlite3.connect("carpool.db", check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute("""
CREATE TABLE IF NOT EXISTS rides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_name TEXT,
    driver_whatsapp TEXT,
    start_pickup_index INTEGER,
    ride_date TEXT,
    ride_time TEXT,
    total_seats INTEGER,
    available_seats INTEGER,
    created_at TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS ride_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ride_id INTEGER,
    passenger_name TEXT,
    passenger_whatsapp TEXT,
    pickup_index INTEGER,
    status TEXT,
    requested_at TEXT
)
""")

conn.commit()

# ---------------- UI ----------------
st.title("🚗 Nanded City → Infosys Phase 2 Carpool")

role = st.sidebar.selectbox("Select Role", ["Driver", "Passenger", "History"])

# ==================================================
# DRIVER
# ==================================================
if role == "Driver":
    st.subheader("🚘 Offer a Ride")

    driver_name = st.text_input("Driver Name")
    driver_whatsapp = st.text_input("Driver WhatsApp Number")

    start_pickup = st.selectbox("Starting Pickup Point", pickup_points)
    start_index = pickup_index[start_pickup]

    ride_date = st.date_input("Ride Date")
    ride_time = st.time_input("Ride Time")

    seats = st.selectbox("Available Seats", [1, 2, 3, 4])

    if st.button("Offer Ride"):
        if driver_name and driver_whatsapp:
            c.execute("""
                INSERT INTO rides (
                    driver_name, driver_whatsapp, start_pickup_index,
                    ride_date, ride_time, total_seats, available_seats, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                driver_name,
                driver_whatsapp,
                start_index,
                str(ride_date),
                str(ride_time),
                seats,
                seats,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))
            conn.commit()
            st.success("Ride offered successfully!")
        else:
            st.error("Please fill all fields")

# ==================================================
# PASSENGER
# ==================================================
elif role == "Passenger":
    st.subheader("🧍 Find a Ride")

    passenger_name = st.text_input("Passenger Name")
    passenger_whatsapp = st.text_input("Passenger WhatsApp Number")

    pickup = st.selectbox("Your Pickup Point", pickup_points)
    pickup_idx = pickup_index[pickup]

    c.execute("""
        SELECT * FROM rides
        WHERE start_pickup_index <= ?
        AND available_seats > 0
        ORDER BY ride_date, ride_time
    """, (pickup_idx,))
    rides = c.fetchall()

    if rides:
        ride_map = {}
        for r in rides:
            label = f"Driver: {r[1]} | Date: {r[4]} | Time: {r[5]} | Seats: {r[7]}"
            ride_map[label] = r

        selected = st.selectbox("Available Rides", ride_map.keys())

        if st.button("Book Seat"):
            if passenger_name and passenger_whatsapp:
                ride = ride_map[selected]
                ride_id = ride[0]

                c.execute("""
                    INSERT INTO ride_requests (
                        ride_id, passenger_name, passenger_whatsapp,
                        pickup_index, status, requested_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    ride_id,
                    passenger_name,
                    passenger_whatsapp,
                    pickup_idx,
                    "Booked",
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ))

                c.execute("""
                    UPDATE rides
                    SET available_seats = available_seats - 1
                    WHERE id = ?
                """, (ride_id,))

                conn.commit()

                # WhatsApp sample messages
                passenger_msg = f"""
✅ Ride Confirmed

📅 Date: {ride[4]}
⏰ Time: {ride[5]}
📍 Pickup: {pickup}
🏁 Drop: Infosys Phase 2

🚗 Driver: {ride[1]}
📞 Contact: {ride[2]}
"""

                driver_msg = f"""
🚗 New Passenger Joined

👤 Name: {passenger_name}
📍 Pickup: {pickup}
📅 Date: {ride[4]}
⏰ Time: {ride[5]}
"""

                st.success("Seat booked successfully!")

                st.subheader("📩 WhatsApp Message Preview (Passenger)")
                st.text_area("", passenger_msg, height=180)

                st.subheader("📩 WhatsApp Message Preview (Driver)")
                st.text_area("", driver_msg, height=160)

            else:
                st.error("Enter passenger details")
    else:
        st.warning("No rides available")

# ==================================================
# HISTORY
# ==================================================
else:
    st.subheader("📜 Ride History")

    c.execute("""
        SELECT r.driver_name, rr.passenger_name,
               r.ride_date, r.ride_time,
               rr.pickup_index, rr.status
        FROM ride_requests rr
        JOIN rides r ON rr.ride_id = r.id
        ORDER BY rr.requested_at DESC
    """)

    rows = c.fetchall()

    if rows:
        data = []
        for row in rows:
            data.append({
                "Driver": row[0],
                "Passenger": row[1],
                "Date": row[2],
                "Time": row[3],
                "Pickup": pickup_points[row[4]],
                "Status": row[5]
            })
        st.dataframe(pd.DataFrame(data))
    else:
        st.info("No ride history yet")

st.markdown("---")
st.caption("Route: Nanded City → Infosys Phase 2, Hinjewadi")
