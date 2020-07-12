Concepts
========

In this section, we explain the concepts and logic behind each design. The concepts are explained with details:

- to help the researchers and developers to understand the current workflow, and 
- to be open about the methods and hopefully receive some feedback for fixing potential bugs or improving the methods. 


Overview
--------
In **tsprocess** package, we target the following goals:

- Each record will be load or processed if it is required.
- Each record will be load or processed, once.
- The user does not need to store any inter-processing results. 
- All results should be reproducible
 

Access to Data
--------------
A record of a ground motion simulation can go through different processing paths (e.g., filtering, rotation, zero-padding, ...). In a specific study, we may never use some of those records. As a result, we want to make sure that, we only load those data that we need and if we process them once we do not want to repeat that processing again.

Adding an instance to the project does not load any data, it registers the incident folder location, incident type, and their stations location. The smallest unit of data that is saved into database is a Record instance (through a pickle object). Each record has a time vector, 9 seismic vectors, which they are also different classes, and a station object. 

Original records are reside inside incident folders. We use **(incident_name + station_name)** hash value to put and retrieve that record from the database. We use a NoSQL key-value database. Keys are hash values that are generated at different steps. Since incident name is unique, and station name inside one incident is also unique, the resultant hash value will be a unique value. If we cannot find that hash value inside the database, we load it from the incident folder, and store it in the database with the same hash value. Through these steps, if we need that record for the second time, we will retrieve it from the database rather than loading from the incident folder. 

The processed records are dependent to the original records. We use processing label idea to track the processed records. Through this implementation, the users are not allowed to directly process any time series, however, they can define processing labels. Processing label name is unique, therefore, a combination of the processing label and the record itself will generate a unique hash value. The processed record will be stored in the database with the generated hash value as a key. The hash value, will be stored in the *processed* attribute of the record. Before, any processing, we generate the hash value, if that value is in the *processed* attribute, we retrieve that record from the database. Following these steps, we never repeat the same processing again, also we never store one processed record in different folders. Users can define as much as processing labels they want. Here is an example:

.. code-block:: console

     $ pr = Project('example_project')
     $ pr.add_processing_label('lpf2','lowpass_filter', {"N" : 4, "Wn" : 2.0})

*lpf2* is a unique name and *lowpass_filter* is the process label type, then we provide a dictionary of hyper-parameters. Once a label is defined, it is not immutable. However, the user always can define another label if needed. 


Stations
--------
Each station is defined through a geographical point *(latitude, longitude, depth)*. We keep track of generated stations, and we only generate station if there is not any station defined for that geographical location. We keep track of available stations through *list_of_stations* class attribute. Each station has an incident station name (*inc_st_name*) dictionary attribute. We join records from different simulation based on this attribute. Because of different location accuracy in different runs, we also use vicinity estimation (*vicinity_estimation*) class variable. The default value is 10 meters. The distance between geographical points are computed based on Haversine formula.  As a result, if a new geographical point is less than a 10 meters from an available station, it will be added to that station. Here is an example for a geographical point (33.84, -117.957, 0). This location in *hercules_1* incident is `station.10` and in `observation_1` incident is `CE16850`. As a result, the inc_st_name attribute of this instance will be:

.. code-block:: console
 
    $station.inc_st_name
    > {'hercules_1':'station.10', 'observation_1':'CE16850'}

All processing are based on a loop on stations. Therefore, if I need to extract data for the mentioned location, for `hercules_1` incident, I need to load `station.10` data from the incident folder. 


 