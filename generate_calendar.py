import ephem
from ics import Calendar, Event
from datetime import datetime, timedelta

def get_zodiac_sign(longitude_rad):
    """Converts ecliptic longitude radians to a Zodiac sign."""
    import math
    deg = math.degrees(longitude_rad)
    signs = [
        "Aries ♈️", "Taurus ♉️", "Gemini ♊️", "Cancer ♋️", 
        "Leo ♌️", "Virgo ♍️", "Libra ♎️", "Scorpio ♏️", 
        "Sagittarius ♐️", "Capricorn ♑️", "Aquarius ♒️", "Pisces ♓️"
    ]
    idx = int(deg / 30) % 12
    return signs[idx]

def generate_moon_calendar():
    cal = Calendar()
    moon = ephem.Moon()
    
    # Start tracking from today
    start_time = datetime.utcnow()
    # Check positions for the next 30 days
    end_time = start_time + timedelta(days=30)
    
    current_time = start_time
    time_step = timedelta(hours=1)
    
    last_sign = None
    event_start = None

    while current_time <= end_time:
        # Convert datetime to ephem date format
        ephem_date = ephem.Date(current_time)
        
        # Calculate Moon position relative to the Earth's orbit (Ecliptic)
        moon.compute(ephem_date)
        ecliptic_lon = ephem.Ecliptic(moon).lon
        
        current_sign = get_zodiac_sign(ecliptic_lon)
        
        # If the sign changes, close out the previous event and start a new one
        if current_sign != last_sign:
            if last_sign is not None:
                # Create the calendar event for the completed transit
                e = Event()
                e.name = f"Moon in {last_sign}"
                e.begin = event_start.strftime('%Y-%m-%d %H:%M:%S')
                e.end = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cal.events.add(e)
            
            # Reset trackers for the new sign
            last_sign = current_sign
            event_start = current_time
            
        current_time += time_step

    # Save the finalized calendar to a file
    with open("astrology.ics", "w") as f:
        f.writelines(cal.serialize())
    print("Successfully generated astrology.ics!")

if __name__ == "__main__":
    generate_moon_calendar()