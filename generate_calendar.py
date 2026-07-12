import ephem
from ics import Calendar, Event
from datetime import datetime, timedelta
import math

def get_zodiac_sign(longitude_rad):
    """Converts ecliptic longitude radians to a Zodiac sign."""
    deg = math.degrees(longitude_rad)
    signs = [
        "Aries ♈️", "Taurus ♉️", "Gemini ♊️", "Cancer ♋️", 
        "Leo ♌️", "Virgo ♍️", "Libra ♎️", "Scorpio ♏️", 
        "Sagittarius ♐️", "Capricorn ♑️", "Aquarius ♒️", "Pisces ♓️"
    ]
    idx = int(deg / 30) % 12
    return signs[idx]

def get_closest_aspect_dist(ephem_date):
    """Calculates the minimum distance to any major Ptolemaic aspect (0, 60, 90, 120, 180) 
    between the Moon and the Sun, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto."""
    planets = [
        ephem.Sun(), ephem.Mercury(), ephem.Venus(), ephem.Mars(), 
        ephem.Jupiter(), ephem.Saturn(), ephem.Uranus(), ephem.Neptune(), ephem.Pluto()
    ]
    moon = ephem.Moon()
    moon.compute(ephem_date)
    m_lon = math.degrees(ephem.Ecliptic(moon).lon)
    
    min_dist = 999
    for p in planets:
        p.compute(ephem_date)
        p_lon = math.degrees(ephem.Ecliptic(p).lon)
        
        # Calculate angular separation along the ecliptic
        diff = abs(m_lon - p_lon) % 360
        if diff > 180:
            diff = 360 - diff
            
        # Check against major Ptolemaic aspects
        for aspect in [0, 60, 90, 120, 180]:
            dist = abs(diff - aspect)
            if dist < min_dist:
                min_dist = dist
                
    return min_dist

def find_last_aspect_time(ingress, egress):
    """Scans backwards from egress to ingress to find when the last aspect perfected."""
    step = timedelta(minutes=30)
    current_time = egress
    points = []
    
    while current_time >= ingress:
        points.append((current_time, get_closest_aspect_dist(ephem.Date(current_time))))
        current_time -= step
        
    # Look for the first local minimum going backwards (latest chronologically)
    for i in range(1, len(points) - 1):
        time_i, dist_i = points[i]
        if dist_i < points[i-1][1] and dist_i < points[i+1][1] and dist_i < 0.35:
            return time_i
            
    # Fallback to absolute minimum if a clean local minimum wasn't captured
    if points:
        best_time, best_dist = min(points, key=lambda x: x[1])
        if best_dist < 0.35:
            return best_time
            
    return ingress

def generate_astrology_calendar():
    cal = Calendar()
    moon = ephem.Moon()
    
    start_time = datetime.utcnow() - timedelta(days=30)
    end_time = datetime.utcnow() + timedelta(days=1800)
    
    # ----------------------------------------------------
    # 1. GENERATE MOON PHASES
    # ----------------------------------------------------
    phases = [
        (ephem.next_new_moon, "🌑 New Moon"),
        (ephem.next_first_quarter_moon, "🌓 First Quarter Moon"),
        (ephem.next_full_moon, "🌕 Full Moon"),
        (ephem.next_last_quarter_moon, "🌗 Last Quarter Moon")
    ]
    
    for finder, name in phases:
        d = start_time
        while d < end_time:
            try:
                res = finder(d)
                dt = res.datetime()
                if dt > end_time: 
                    break
                e = Event()
                e.name = name
                e.begin = dt.strftime('%Y-%m-%d %H:%M:%S')
                e.end = (dt + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                cal.events.add(e)
                d = dt + timedelta(days=1)
            except:
                break

    # ----------------------------------------------------
    # 2. GENERATE MOON SIGN TRANSITS & VOID OF COURSE (VoC)
    # ----------------------------------------------------
    current_time = start_time
    time_step = timedelta(hours=1)
    
    last_sign = None
    event_start = None
    transits = []

    # First pass: Collect all the sign boundaries
    while current_time <= end_time:
        ephem_date = ephem.Date(current_time)
        moon.compute(ephem_date)
        ecliptic_lon = ephem.Ecliptic(moon).lon
        current_sign = get_zodiac_sign(ecliptic_lon)
        
        if current_sign != last_sign:
            if last_sign is not None:
                transits.append({
                    'sign': last_sign,
                    'start': event_start,
                    'end': current_time
                })
            last_sign = current_sign
            event_start = current_time
            
        current_time += time_step

    # Second pass: Process transits and calculate VoC windows
    for transit in transits:
        # Add the main sign transit event
        e_transit = Event()
        e_transit.name = f"Moon in {transit['sign']}"
        e_transit.begin = transit['start'].strftime('%Y-%m-%d %H:%M:%S')
        e_transit.end = transit['end'].strftime('%Y-%m-%d %H:%M:%S')
        cal.events.add(e_transit)
        
        # Calculate Void of Course (VoC)
        last_aspect = find_last_aspect_time(transit['start'], transit['end'])
        
        # If the last aspect happened before the moon left the sign, it's Void of Course from that moment until ingress
        if transit['end'] - last_aspect > timedelta(minutes=15):
            e_voc = Event()
            e_voc.name = f"❌ Void of Course Moon ({transit['sign'].split()[0]})"
            e_voc.begin = last_aspect.strftime('%Y-%m-%d %H:%M:%S')
            e_voc.end = transit['end'].strftime('%Y-%m-%d %H:%M:%S')
            cal.events.add(e_voc)

    with open("astrology.ics", "w") as f:
        f.writelines(cal.serialize())
    print("Successfully generated full 1800-day Astrology Calendar with Phases and VoC!")

if __name__ == "__main__":
    generate_astrology_calendar()
