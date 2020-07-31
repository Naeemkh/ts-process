Incidents
=========
An earthquake incident (or incident for short) is a folder that includes observed or simulated earthquakes with their source and stations details. **tsporcess** parses all files inside the incident folder and extract the required data. In the following, we explain the incident folders' details for major ground motion simulation platforms. Please let `us <contact.rst>`_ know if you need to add your research group incident format into **tsporcess**.


Hercules
--------

`Hercules <https://github.com/CMU-Quake/hercules/wiki/Hercules>`_ is a simulation software for anelastic wave propagation in highly heterogeneous media due to kinematic faulting. The following figure shows the required files and folders and their arrangements.

.. image:: images/png/hercules_folder_arrangment.png 
   :alt: hercules folder arrangement
   :width: 600px
   :align: center 

The only extra file is **description.txt** that has several mandatory keys and
values. These keys are shown below. The incident name should be a unique name.
Incident type is one of the supported incidents, which in this case, is
*hercules*.  Horizontal orientations should be perpendecular, and vertical
orientation shows the direction that records are considered positive. 

.. code-block:: console
     
    # description.txt
    incident_name         =  hercules_1
    incident_type         =  hercules
    inputfiles_parameters =  inputfiles/parameters.in
    source_hypocenter     =  lat, lon, depth(km)
    hr_comp_orientation_1 =  degree
    hr_comp_orientation_2 =  degree
    ver_comp_orientation  =  up or down



RWG
---
TBD


AWP
---
TBD

CESMD
-----

Center for Engineering Strong Motion Data (CESMD) is a cooperative center
established by the US Geological Survey and the California Geological Survey
(CGS) to monitor earthquake strong-motion data. Read more
`here <https://strongmotioncenter.org>`_. CESMD provides data in different
formats. In this section, we explain Consortium of Organizations for
Strong-Motion Observation Systems (`COSMOS <https://www.strongmotion.org>`_ )
format. COSMOS has 3 different volumes including V1, V2, V3. V1 is raw
, unprocessed acceleration data. V2 is processed and corrected acceleration,
velocity and displacement records. V3 includes spectra files. 

Vol1
++++

TBD

Vol2
++++

As mentioned earlier, Vol2 format is the corrected and processed version. So we
do not need to deal with normal proprocessing (e.g., removing instrument
response and baseline correction.) One can download strong-motion data from 
`strongmotioncenter.org <https://strongmotioncenter.org>`_ . 

The following figure shows the required files and folders and their arrangements.

.. image:: images/png/CESMDV2.png 
   :alt: CESMDV2 folder arrangement
   :width: 400px
   :align: center 

``stations_list.txt`` includes station name, lat, lon, depth of stations that
are located in ``seismic_records`` folder. Here is an example of
``stations_list.txt``:

.. code-block:: console
     
    # stations_list.txt
    CIOLI	       33.945	-117.924	0
    CE13873	       33.933	-117.896	0
    CE13880	       33.909	-117.931	0
    CE13881	       33.931	-117.956	0

**description.txt** file requires several mandatory keys and
values. These keys are shown below. The incident name should be a unique name.
It can be any name, however, we would suggest a very short name, because, you
will use the name frequently during the processing, and also it will appear as 
legends in the figures. Incident type should be one of the supported incidents, 
which in this case, is *cesmdv2*. Orientations of different components are read
from each seismic record file. 

.. code-block:: console
     
    # description.txt
    incident_name         =  cesmdv2_1
    incident_type         =  cesmdv2

You can add any key-value metadata to this file. They will be accessible in the 
incident metadata attribute.