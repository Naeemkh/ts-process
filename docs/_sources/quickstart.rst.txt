Quickstart
==========

`Set up <setup_env.rst>`_ the environment and import the package. Working with 
Jupyter Notebook is strongly recommended.

.. code-block:: console

    $ from tsprocess import project as pr
    $ p1 = pr.Project('myproject1')

Create an `incident folder <incidents.rst>`_ and add the incident to the project.

.. code-block:: console

    $ # assuming incident is located at incident_folder
    $ # and incident name is inc_1  
    $ p1.add_incident(incident_folder)
   
Define a taper processing label.

.. code-block:: console
 
    $ # example for tapering 100 sample points at the beggining and end of the 
    $ # timeseries.
    $ p1.add_processing_label('taper1','taper',{"flag":"all", "m":100})

Define a filter for selecting stations at an epicentral distance less than 10 km.

.. code-block:: console

    $ p1.add_station_filter("lesst10", "epi_dist_lt", {"distance":10})

Plot velocity records based on the defined processing labels and stations
selection filter.

.. code-block:: console

    $ p1.plot_velocity_records(['inc_1'],[['taper1']],['lesst10'],{})

It should return tapered plots of stations at an epicentral distance less than 
10 km. 

See `API Reference <api_ref.rst>`_ and `Examples <examples.rst>`_ for more details. 