# tsprocess

Ground motion time series processing tools

tsprocess is a Python3-based software program that facilitates processing 3D ground-motion simulation results. It provides a convenient interface for conducting different analyses on a series of simulated and observed earthquakes time series requiring the least effort from the researchers. By generating a unique hash value for data and actions on the data, it guarantees that each process is carried out once and stored once. As a result, it eliminates redundant processes and also redundant versions of processed data. Processed data are stored in a NoSQL key-value database, and an in-memory dictionary is used to reduce the amount of query to the database. The tsprocess library also provides codes for calculating ROTD50 so that a common implementation is used to process both 3D simulation seismograms and 1D broadband platform seismograms.

These codes have been developed as part of earthquake ground motion research performed by the Southern California Earthquake Center (SCEC) www.scec.org.

## Documentation

Documentation is hosted at https://naeemkh.github.io/tsprocess/

## Primary Developers of tsprocess library:

* Naeem Khoshnevis - University of Memphis
* Fabio Silva - Southern California Earthquake Center
* Ricardo Taborda - Universidad EAFIT Medellín Colombia
* Christine Goulet - University of Southern California

## Software support:
* software @ scec.org 
