> Great repository names are short and memorable. How about musical-giggle?

How about no.

# sup
#### Find out what's up.

Simple script for plotting altitude and azimuth vs time of various celestial things from a given location. Sure, there are probably prettier and more complete tools out there. Who cares.

**Requires:** astropy, matplotlib, numpy

### Settings

See [example.yaml](example.yaml).

### Command-line interface
```bash
usage: sup [-h] [--location LOCATION] [--time TIME] [--time_zone TIME_ZONE]
           [--plot_plusminus PLOT_PLUSMINUS] [--show_twilight SHOW_TWILIGHT]
           [--invert_twilight INVERT_TWILIGHT] [--Nradar NRADAR]
           [--min_alt MIN_ALT] [--outprefix OUTPREFIX]
           [setfile ...]

Find out what's up.

positional arguments:
  setfile               E.g. <settings.yaml> or <catalog.yaml [ specific
                        object(s) ]> (default: [])

options:
  -h, --help            show this help message and exit
  --location LOCATION   # (default: SSO)
  --time TIME           # (default: now)
  --time_zone TIME_ZONE
                        # (default: PDT)
  --plot_plusminus PLOT_PLUSMINUS
                        # (default: 12.0)
  --show_twilight SHOW_TWILIGHT
                        # (default: True)
  --invert_twilight INVERT_TWILIGHT
                        # (default: False)
  --Nradar NRADAR       # (default: 9)
  --min_alt MIN_ALT     # (default: 30.0)
  --outprefix OUTPREFIX
                        # (default: None)

See example settings file for details about each option. Settings files take
precedence over command line options.
```

### Python interface

See [example.ipynb](example.ipynb).

### Acknowledgements

The Messier subcatalogs packaged here are derived from data maintained by [seds.org](http://www.messier.seds.org/) ([usage](http://www.messier.seds.org/usage.html)).
