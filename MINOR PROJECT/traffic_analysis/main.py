import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import polyline  # For decoding polylines

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

# Page Config
st.set_page_config(page_title="Real-Time Traffic Analysis", layout="wide", initial_sidebar_state="expanded")

# Title
st.title("🚗 Real-Time Traffic Analysis & Route Optimization 🚶‍♂️")
st.markdown("Easily find the best routes with real-time traffic updates!")

# Sidebar
st.sidebar.header("Input Details")
username = st.sidebar.text_input("🧑‍💻 Your Name", "John Doe")
mode = st.sidebar.selectbox("🚲 Mode of Transport", ["Driving", "Walking", "Bicycling", "Transit"])
origin = st.sidebar.text_input("📍 Starting Point", "New York, NY")
destination = st.sidebar.text_input("🏁 Destination", "Boston, MA")
avoid_tolls = st.sidebar.checkbox("Avoid Tolls")
fastest_route = st.sidebar.checkbox("Fastest Route")
preferred_time = st.sidebar.slider("⏰ Travel Time", 0, 23, 12)
st.sidebar.write(f"Preferred time: {preferred_time}:00")

# Route Function
def get_route_data(origin, destination, mode, avoid_tolls, fastest_route):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode.lower(),
        "key": GOOGLE_MAPS_API_KEY,
        "avoid": "tolls" if avoid_tolls else "",
        "traffic_model": "best_guess" if fastest_route else "pessimistic"
    }
    response = requests.get(base_url, params=params)
    return response.json()

# Map Function
def plot_route_on_map(route_data, origin_coords, destination_coords):
    m = folium.Map(location=origin_coords, zoom_start=10, tiles="Stamen Toner")
    try:
        points = route_data['routes'][0]['overview_polyline']['points']
        decoded_points = polyline.decode(points)
        folium.PolyLine(decoded_points, color="blue", weight=5).add_to(m)
        # Markers for Origin and Destination
        folium.Marker(location=origin_coords, popup="Origin", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=destination_coords, popup="Destination", icon=folium.Icon(color="red")).add_to(m)
        return m
    except KeyError:
        return None

# Analyze Button
if st.sidebar.button("Analyze Route"):
    with st.spinner("Fetching route and traffic details..."):
        # Get route data directly using place names
        route_data = get_route_data(origin, destination, mode, avoid_tolls, fastest_route)
        if 'routes' in route_data and route_data['routes']:
            # Display Route Details
            st.subheader("📍 Route Details")
            distance = route_data['routes'][0]['legs'][0]['distance']['text']
            duration = route_data['routes'][0]['legs'][0]['duration']['text']
            start_location = route_data['routes'][0]['legs'][0]['start_location']
            end_location = route_data['routes'][0]['legs'][0]['end_location']
            st.write(f"**Distance**: {distance}")
            st.write(f"**ETA**: {duration}")

            # Display Route Map
            st.subheader("🗺️ Route Map")
            route_map = plot_route_on_map(route_data, 
                                          (start_location['lat'], start_location['lng']),
                                          (end_location['lat'], end_location['lng']))
            if route_map:
                folium_static(route_map)
            else:
                st.error("Could not plot the route.")
        else:
            st.error("Invalid addresses or no route data available. Please check the inputs.")

# Footer
st.markdown("""
    <style>
        footer {text-align: center; padding: 10px;}
        footer p {font-size: 14px; color: grey;}
    </style>
    <footer>
        <p>Powered by Streamlit 🌟 | Google Maps API 🌍</p>
    </footer>
""", unsafe_allow_html=True)