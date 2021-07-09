from math import pi,sin,cos,tan,asin,atan2,acos
from datetime import datetime
import time

PI   = pi
atan = atan2
rad  = PI / 180.0
class Earth(object):
    def __init__(self):
        self.dayMs = 86400000
        self.J1970 = 2440588
        self.J2000 = 2451545
        self.J0 = 0.0009;

        self.times  = (
            (-0.833, 'sunrise',       'sunset'      ),
            (  -0.3, 'sunriseEnd',    'sunsetStart' ),
            (    -6, 'dawn',          'dusk'        ),
            (   -12, 'nauticalDawn',  'nauticalDusk'),
            (   -18, 'nightEnd',      'night'       ),
            (     6, 'goldenHourEnd', 'goldenHour'  )
        )
        self.e = 0.40909994067971484 # obliquity of the Earth
    def solarMeanAnomaly(self,d):
        return rad * (357.5291 + 0.98560028 * d)
    
    def fromJulian(self,j):
    	return datetime.fromtimestamp(((j + 0.5 - self.J1970) * self.dayMs)/1000.0) 
    
    def julianCycle(self,d, lw):
        return round(d - self.J0 - lw / (2 * PI))

    def approxTransit(self,Ht, lw, n):
    	return self.J0 + (Ht + lw) / (2 * PI) + n
    
    def solarTransitJ(self,ds, M, L):
    	return self.J2000 + ds + 0.0053 * sin(M) - 0.0069 * sin(2 * L)
    
    def getSetJ(self,h, lw, phi, dec, n, M, L):
        w = self.hourAngle(h, phi, dec)
        a = self.approxTransit(w, lw, n)
        return self.solarTransitJ(a, M, L)
    
    def eclipticLongitude(self,M):
        C = rad * (1.9148 * sin(M) + 0.02 * sin(2 * M) + 0.0003 * sin(3 * M)) # equation of center
        P = rad * 102.9372 # perihelion of the Earth
        return M + C + P + PI

    def toJulian(self,date):
        return (time.mktime(date.timetuple()) * 1000) / self.dayMs - 0.5 + self.J1970
    
    def toDays(self,date):   
        return self.toJulian(date) - self.J2000 
    
    def rightAscension(self,l, b): 
        return atan(sin(l) * cos(self.e) - tan(b) * sin(self.e), cos(l))
   
    def siderealTime(self,d, lw):
        return rad * (280.16 + 360.9856235 * d) - lw
   
    def declination(self,l, b):    
        return asin(sin(b) * cos(self.e) + cos(b) * sin(self.e) * sin(l))
    
    def sunCoords(self,d):
        M = self.solarMeanAnomaly(d)
        L = self.eclipticLongitude(M)
        return dict(dec= self.declination(L, 0),ra= self.rightAscension(L, 0))
   
    def hourAngle(self,h, phi, d):
    	try:
    		ret = acos((sin(h) - sin(phi) * sin(d)) / (cos(phi) * cos(d)))
    		return ret
    	except ValueError as e:
    		print(h, phi, d)
    		print(e)

    def azimuth(self,H, phi, dec):  
        return PI+atan(sin(H), cos(H) * sin(phi) - tan(dec) * cos(phi))
    
    def altitude(self,H, phi, dec):
        return asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(H))

    def getTimes(self,date, lat, lng):
        lw = rad * -lng
        phi = rad * lat
    
        d = self.toDays(date)
        n = self.julianCycle(d, lw)
        ds = self.approxTransit(0, lw, n)
    
        M = self.solarMeanAnomaly(ds)
        L = self.eclipticLongitude(M)
        dec = self.declination(L, 0)
    
        Jnoon = self.solarTransitJ(ds, M, L)
    
        result = dict()

        for i in range(len(self.times)):
            time = self.times[i]
            Jset = self.getSetJ(time[0] * rad, lw, phi, dec, n, M, L);
            Jrise = Jnoon - (Jset - Jnoon);
            result[time[1]] = self.fromJulian(Jrise).strftime('%Y-%m-%d %H:%M:%S');
            result[time[2]] = self.fromJulian(Jset).strftime('%Y-%m-%d %H:%M:%S');
    
        return result
   
    def getPosition(self,date, lat, lng):
        lw  = rad * -lng
        phi = rad * lat
        d   = self.toDays(date)
        c  = self.sunCoords(d)
        H  = self.siderealTime(d, lw) - c["ra"]
        return dict(azimuth=self.azimuth(H, phi, c["dec"]), altitude=self.altitude(H, phi, c["dec"]))
    @staticmethod
    def fetch(date,lat,long):
        return "https://suncalc.org/#/"+str(lat)+","+str(long)+",17/"+str(date.year)+"."+str(date.month)+"."+str(date.day)+"/"+str(date.hour)+":"+str(date.minute)+"/1/0"
