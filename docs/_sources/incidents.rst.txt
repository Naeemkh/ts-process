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




