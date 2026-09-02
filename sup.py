#!/usr/bin/env python

import datetime
from os.path import dirname, exists
from sys import argv
import yaml

from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, get_sun, get_body
from astropy.time import Time

import matplotlib.pyplot as plt
import numpy as np

known_observatories = {
    'SSO': {
        'lat': 37.419167*u.deg,
        'lon': -122.181667*u.deg,
        'height': 30*u.m
    }
}

known_timezones = {
    'UTC':  0*u.h,
    'PDT': -7*u.h,
    'PST': -8*u.h
}

settings = {
    'location': 'SSO',
    'time': None,
    'time_zone': 'PDT',
    'plot_plusminus': 12.,
    'show_twilight': True,
    'Nradar': 9,
    'min_alt': 30.,
    'objects': {'things': ['sun', 'moon']},
    'styles': {}
}


    


def sup(settings=settings, setfile=None, thispath=""):
    """
settings: dictionary; see example.yaml in this code's distribution
setfile: name of settings file to read (updates settings)
         OR an object catalog (no .yaml ending) with optional selection
         Either of these updates `settings`. See example.yaml again.
thispath: path to catalogs included with this distribution, if needed
    """

    if setfile is not None:
        if exists(setfile):
            with open(setfile, 'r') as f:
                up = yaml.safe_load(f.read())
            settings.update(up)
        else:
            print(setfile + " does not exist; interpreting as a catalog selection")
            settings['objects'] = {
                'targets': setfile,
                'avoid': ['sun', 'moon']
                }

    loc = settings['location']
    if loc.__class__ == str:
        loc = known_observatories[loc]
    loc = EarthLocation.from_geodetic(**loc)

    tzone = settings['time_zone']
    if tzone.__class__ == str:
        tzone = known_timezones[tzone]
    else:
        tzone *= u.h

    time = settings['time']
    if time is None:
        time = (Time.now() + tzone).datetime # NOW in UTC converted to local
    if time.__class__ == datetime.datetime:
        time = Time(time) - tzone # to UTC
        times = (time - 12*u.h) + np.linspace(0., 1., 36)*u.day
        sun = [get_sun(t).transform_to(AltAz(location=loc, obstime=t)) for t in times]
        sun_alt = np.array([s.alt.value for s in sun])
        time = times[np.argmin(sun_alt)]
        tstart = time - settings['plot_plusminus']*u.h
        tstop = time + settings['plot_plusminus']*u.h
    else:
        tstart = Time(time['begin']) - tzone # to UTC
        tstop = Time(time['end']) - tzone # to UTC

    objects = settings['objects']
    thing = {}
    for objtype in objects.keys():
        if objects[objtype].__class__ == str:
            words = objects[objtype].split()
            fname = words[0]+'.yaml'
            if not exists(fname):
                fname = thispath + '/' + fname
            if not exists(fname):
                raise Exception("Can't find " + words[0])
            with open(fname, 'r') as f:
                cat = yaml.safe_load(f.read())
            if len(words) == 1:
                objects[objtype] = cat
            else:
                objects[objtype] = [o for o in cat if o['name'] in words[1:]]
        thing[objtype] = []
        for o in objects[objtype]:
            if o.__class__ == dict:
                o['coords'] = SkyCoord(o['ra'], o['dec'], frame='icrs', unit=(u.deg, u.deg))
                thing[objtype].append(o)
            else:
                assert o.__class__ == str
                thing[objtype].append({'name': o})
    objects = thing

    styles = settings['styles']
    for i,objtype in enumerate(objects.keys()):
        if not objtype in styles.keys():
            styles[objtype] = {}
        if not 'color' in styles[objtype]:
            styles[objtype]['color'] = 'C'+str(i)



    def plottimes(ts, zone):
        return [(t+zone).datetime for t in ts]

    def tzonelab(tzone):
        s = str(tzone/u.h)
        if s[0] != '-':
            s = '+'+s
        return "Time (UTC" + s + ")"


    times = tstart + (tstop - tstart) * np.linspace(0., 1., 101)
    ptimes = plottimes(times, tzone)
    for objtype in objects.keys():
        for o in objects[objtype]:
            o['alt'] = np.empty(len(times))
    sun_alt = np.empty(len(times))
    for i,t in enumerate(times):
        altaz = AltAz(location=loc, obstime=t)
        sun_alt[i] = get_sun(t).transform_to(altaz).alt.value
        for objtype in objects.keys():
            for o in objects[objtype]:
                if 'coords' in o.keys():
                    o['alt'][i] = o['coords'].transform_to(altaz).alt.value
                else:
                    o['alt'][i] = get_body(o['name'], t, loc).transform_to(altaz).alt.value

    fig,ax = plt.subplots(1, 1, figsize=[10,5.5]);
    if settings['show_twilight']:
        ax.fill_between(ptimes, 0, 90, sun_alt>-18, color=(0.9,)*3);
        ax.fill_between(ptimes, 0, 90, sun_alt>-12, color=(0.8,)*3);
        ax.fill_between(ptimes, 0, 90, sun_alt>-6, color=(0.7,)*3);
        ax.fill_between(ptimes, 0, 90, sun_alt>0, color=(0.6,)*3);
    for objtype in objects.keys():
        for o in objects[objtype]:
            ax.plot(ptimes, o['alt'], **styles[objtype]);
            i = np.argmax(o['alt'])
            ax.text(ptimes[i], o['alt'][i], o['name'], ha='center', va='bottom', **styles[objtype]);
    fig.autofmt_xdate();
    ax.set_xlabel(tzonelab(tzone));
    ax.set_ylabel('Altitude (deg)');
    ax.set_ylim(0, 90);



    minalt = settings['min_alt']
    Nradar = settings['Nradar']
    times = tstart + (tstop - tstart) * np.linspace(0., 1., Nradar)
    ncol = 3
    nrow = int(np.ceil(Nradar/ncol))
    fig,axs = plt.subplots(nrow, ncol, figsize=[4*ncol,5*nrow], subplot_kw={'projection': 'polar'});
    for i,t in enumerate(times):
        ax = axs[np.unravel_index(i, (nrow,ncol))]
        ax.set_title(str(t+tzone));
        ax.set_rlim(90., minalt);
        ax.set_theta_zero_location('N');
        ax.set_theta_direction(-1);
        altaz = AltAz(location=loc, obstime=t)
        for objtype in objects.keys():
            for o in objects[objtype]:
                if 'coords' in o.keys():
                    c = o['coords'].transform_to(altaz)
                else:
                    c = get_body(o['name'], t, loc).transform_to(altaz)
                if c.alt.value > minalt:
                    ax.scatter(c.az/180.*np.pi, c.alt, **styles[objtype])
                    ax.text(c.az.value/180.*np.pi, c.alt.value, o['name'], ha='center', va='bottom')


    plt.show(block=True);



def main(argv):
    argc = len(argv)

    thispath = dirname(argv[0])

    setfile = None
    if argc > 1:
        if argv[1] == '-h':
            print("Usage: " + argv[0] )
            print("       " + argv[0] + " -h")
            print("       " + argv[0] + " <settings.yaml>")
            print("       " + argv[0] + " <catalog.yaml [ specific object(s) ]>")
            quit()
        setfile = ' '.join(argv[1:])

    sup(settings, setfile, thispath)


if __name__ == "__main__":
    main(argv)
