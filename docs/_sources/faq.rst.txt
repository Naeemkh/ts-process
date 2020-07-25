Frequently Asked Questions
==========================

**Q.** I set ``save_figure = True`` in the optional parameters, however, I am
not sure how to pass a name to the saved figures. 

    **A.** A figure that is generated in "tsprocess" can be generated based on 
    records of different incidents, where each incidet went through different 
    processing steps. As a result, a file name based on incidents and 
    their processing labels will be a very long name. On ther other hand, it
    will be tedious for users to choose name for numerous stations (e.g., 300
    stations.)
    In tsprocess, we store figures inside ``tsprocess_output`` folder. All
    figures are suffixed with datetime signature, as a result they are unique. 
    In ``tsprocess_output`` folder, there is another file named
    ``output_item_description.txt`` that includes file names and their details.
    Users can refer to this file and findout the processing path that each 
    record went through. These details are also added to the bottom of each 
    figure. 



