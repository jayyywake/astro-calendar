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
    
    # NEW: Start tracking from 30 days AGO so your recent past calendar history is preserved
    start_time = datetime.utcnow() - timedelta(days=30)
    
    # NEW: Look 365 days into the future (plus the 30 days of past history)
    end_time = datetime.utcnow() + timedelta(days=1800)
    
    current_time = start_time
    time_step = timedelta(hours=1)
    
    last_sign = None
    event_start = None

    while current_time <= end_time:
        ephem_date = ephem.Date(current_time)
        moon.compute(ephem_date)
        ecliptic_lon = ephem.Ecliptic(moon).lon
        
        current_sign = get_zodiac_sign(ecliptic_lon)
        
        if current_sign != last_sign:
            if last_sign is not None:
                e = Event()
                e.name = f"Moon in {last_sign}"
                e.begin = event_start.strftime('%Y-%m-%d %H:%M:%S')
                e.end = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cal.events.add(e)
            
            last_sign = current_sign
            event_start = current_time
            
        current_time += time_step

    with open("astrology.ics", "w") as f:
        f.writelines(cal.serialize())
    print("Successfully generated expanded 1-year astrology.ics!")

if __name__ == "__main__":
    generate_moon_calendar()
