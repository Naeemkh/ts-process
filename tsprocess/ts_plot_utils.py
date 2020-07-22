"""
ts_plot_utils.py
====================================
The core module for timeseries plot helper functions.
"""
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties

from .ts_utils import check_opt_param_minmax, query_opt_params, list2message


def plot_displacement_helper(record, color_code, opt_params, list_inc,
 list_process, list_filters):
    """ Plots displacement timeseries and corresponding frequency spectra
     amplitude for 3 components. It is an internal function for
     plot_displacement_records methods in the Project class.
     should not be directly used by the end users.
    """
    
    with_details = False
    if query_opt_params(opt_params, 'save_figure'):  
        nrs = 7          
        fig, axarr = plt.subplots(nrows=nrs, ncols=3, figsize=(14, 9))
        counter = 2
        rspan = 2
        with_details = True
    else:
        nrs = 3
        fig, axarr = plt.subplots(nrows=nrs, ncols=3, figsize=(14, 9))
        counter = 1
        rspan = 1
    
    # h1, h2, UD
    for i in range(3):
        axarr[i][0] = plt.subplot2grid((nrs,3),(i*counter,0),
        rowspan=rspan, colspan=2)
        axarr[i][1] = plt.subplot2grid((nrs,3),(i*counter,2),
        rowspan=rspan, colspan=1)
        axarr[i][0].grid(True)
    
    if with_details:
        axarr[3][0] = plt.subplot2grid((7,3),(6,0),rowspan=1, colspan=3)
    
    x_lim_f = check_opt_param_minmax(opt_params, 'zoom_in_freq')
    x_lim_t = check_opt_param_minmax(opt_params, 'zoom_in_time')
    
    station_name = None
    epicentral_dist = None               
    for i,item in enumerate(record):
        if not item:
            continue
        axarr[0][0].plot(item.time_vec,item.disp_h1.value,
         color_code[i], label=list_inc[i])
        axarr[0][1].plot(item.freq_vec,abs(item.disp_h1.fft_value),
         color_code[i], label=list_inc[i])   
        axarr[1][0].plot(item.time_vec,item.disp_h2.value,
         color_code[i], label=list_inc[i])
        axarr[1][1].plot(item.freq_vec,abs(item.disp_h2.fft_value),
         color_code[i], label=list_inc[i])  
        axarr[2][0].plot(item.time_vec,item.disp_ver.value,
         color_code[i], label=list_inc[i])
        axarr[2][1].plot(item.freq_vec,abs(item.disp_ver.fft_value),
         color_code[i], label=list_inc[i])   
        # station name
        if not station_name:
            station_name = item.station.inc_st_name[list_inc[i]]
            temp_record = item
        
        # epicentral distance
        if not epicentral_dist:
            epicentral_dist = f"{item.epicentral_distance: 0.2f}"

    axarr[0][0].set_ylabel('h1')
    axarr[1][0].set_ylabel('h2')
    axarr[2][0].set_ylabel('ver')
    axarr[2][0].set_xlabel('Time (s)')
    axarr[2][1].set_xlabel('Frequency (Hz)')

    f_name_save = "f_disp_plot_" +\
         datetime.now().strftime("%Y%m%d_%H%M%S_%f" + ".pdf")
    details = [f_name_save, list_inc, list_process, list_filters,
     temp_record.station.inc_st_name]
    message = list2message(details)

    if with_details:
        footnote_font = FontProperties()
        footnote_font.set_size(6)
        max_height = 100 
        axarr[3][0].text(1,0.8 * max_height,message, va = 'top',
         fontproperties = footnote_font, wrap=True)
        
        axarr[3][0].set_xlim([0,50])
        axarr[3][0].set_ylim([0,max_height])
        axarr[3][0].get_xaxis().set_ticks([])
        axarr[3][0].get_yaxis().set_ticks([])
    
    for i in range(3):    
        axarr[i][0].set_xlim(x_lim_t)
        axarr[i][1].set_xlim(x_lim_f)
    
    axarr[0][0].legend()
    axarr[0][0].set_title(
        f'Station at incident {list_inc[0]}:'
        f'{station_name} - epicenteral dist:'
        f'{epicentral_dist} km'
        )    
    
    fig.tight_layout()  
    return fig, message, f_name_save

def plot_velocity_helper(record, color_code, opt_params, list_inc, list_process,
 list_filters):
    """ Plots velocity timeseries and corresponding frequency spectra
     amplitude for 3 components. It is an internal function for
     plot_velocity_records methods in the Project class.
     should not be directly used by the end users.
    """
    
    with_details = False
    if query_opt_params(opt_params, 'save_figure'):  
        nrs = 7          
        fig, axarr = plt.subplots(nrows=nrs, ncols=3, figsize=(14, 9))
        counter = 2
        rspan = 2
        with_details = True
    else:
        nrs = 3
        fig, axarr = plt.subplots(nrows=nrs, ncols=3, figsize=(14, 9))
        counter = 1
        rspan = 1
    
    # h1, h2, UD
    for i in range(3):
        axarr[i][0] = plt.subplot2grid((nrs,3),(i*counter,0),
        rowspan=rspan, colspan=2)
        axarr[i][1] = plt.subplot2grid((nrs,3),(i*counter,2),
        rowspan=rspan, colspan=1)
        axarr[i][0].grid(True)
    
    if with_details:
        axarr[3][0] = plt.subplot2grid((7,3),(6,0),rowspan=1, colspan=3)
    
    x_lim_f = check_opt_param_minmax(opt_params, 'zoom_in_freq')
    x_lim_t = check_opt_param_minmax(opt_params, 'zoom_in_time')
    
    station_name = None
    epicentral_dist = None               
    for i,item in enumerate(record):
        if not item:
            continue
        axarr[0][0].plot(item.time_vec,item.vel_h1.value,
         color_code[i], label=list_inc[i])
        axarr[0][1].plot(item.freq_vec,abs(item.vel_h1.fft_value),
         color_code[i], label=list_inc[i])   
        axarr[1][0].plot(item.time_vec,item.vel_h2.value,
         color_code[i], label=list_inc[i])
        axarr[1][1].plot(item.freq_vec,abs(item.vel_h2.fft_value),
         color_code[i], label=list_inc[i])  
        axarr[2][0].plot(item.time_vec,item.vel_ver.value,
         color_code[i], label=list_inc[i])
        axarr[2][1].plot(item.freq_vec,abs(item.vel_ver.fft_value),
         color_code[i], label=list_inc[i])   
        # station name
        if not station_name:
            station_name = item.station.inc_st_name[list_inc[i]]
            temp_record = item
        
        # epicentral distance
        if not epicentral_dist:
            epicentral_dist = f"{item.epicentral_distance: 0.2f}"

    axarr[0][0].set_ylabel('h1')
    axarr[1][0].set_ylabel('h2')
    axarr[2][0].set_ylabel('ver')
    axarr[2][0].set_xlabel('Time (s)')
    axarr[2][1].set_xlabel('Frequency (Hz)')

    f_name_save = "f_velocity_plot_" +\
         datetime.now().strftime("%Y%m%d_%H%M%S_%f" + ".pdf")
    details = [f_name_save, list_inc, list_process, list_filters,
     temp_record.station.inc_st_name]
    message = list2message(details)

    if with_details:
        footnote_font = FontProperties()
        footnote_font.set_size(6)
        max_height = 100 
        axarr[3][0].text(1,0.8 * max_height,message, va = 'top',
         fontproperties = footnote_font, wrap=True)
        
        axarr[3][0].set_xlim([0,50])
        axarr[3][0].set_ylim([0,max_height])
        axarr[3][0].get_xaxis().set_ticks([])
        axarr[3][0].get_yaxis().set_ticks([])
    
    for i in range(3):    
        axarr[i][0].set_xlim(x_lim_t)
        axarr[i][1].set_xlim(x_lim_f)
    
    axarr[0][0].legend()
    axarr[0][0].set_title(
        f'Station at incident {list_inc[0]}:'
        f'{station_name} - epicenteral dist:'
        f'{epicentral_dist} km'
        )    
    
    fig.tight_layout()  
    return fig, message, f_name_save

def plot_acceleration_helper(record, color_code, opt_params, list_inc,
 list_process, list_filters):
    """ Plots acceleration timeseries and corresponding response spectra
     amplitude for 3 components. It is an internal function for
     plot_acceleration_records methods in the Project class.
     should not be directly used by the end users.
    """
    
    with_details = False
    if query_opt_params(opt_params, 'save_figure'):  
        nrs = 7          
        fig, axarr = plt.subplots(nrows=nrs, ncols=3, figsize=(14, 9))
        counter = 2
        rspan = 2
        with_details = True
    else:
        nrs = 3
        fig, axarr = plt.subplots(nrows=nrs, ncols=3, figsize=(14, 9))
        counter = 1
        rspan = 1
    
    # h1, h2, UD
    for i in range(3):
        axarr[i][0] = plt.subplot2grid((nrs,3),(i*counter,0),
        rowspan=rspan, colspan=2)
        axarr[i][1] = plt.subplot2grid((nrs,3),(i*counter,2),
        rowspan=rspan, colspan=1)
        axarr[i][0].grid(True)
    
    if with_details:
        axarr[3][0] = plt.subplot2grid((7,3),(6,0),rowspan=1, colspan=3)
    
    x_lim_rsp = check_opt_param_minmax(opt_params, 'zoom_in_rsp')
    x_lim_t = check_opt_param_minmax(opt_params, 'zoom_in_time')
    
    station_name = None
    epicentral_dist = None               
    for i,item in enumerate(record):
        if not item:
            continue
        axarr[0][0].plot(item.time_vec,item.acc_h1.value,
         color_code[i], label=list_inc[i])
        axarr[0][1].plot(item.acc_h1.response_spectra[0],
         item.acc_h1.response_spectra[1], color_code[i], label=list_inc[i])   
        axarr[1][0].plot(item.time_vec,item.acc_h2.value,
         color_code[i], label=list_inc[i])
        axarr[1][1].plot(item.acc_h2.response_spectra[0],
         item.acc_h2.response_spectra[1], color_code[i], label=list_inc[i])  
        axarr[2][0].plot(item.time_vec,item.acc_ver.value,
         color_code[i], label=list_inc[i])
        axarr[2][1].plot(item.acc_ver.response_spectra[0],
         item.acc_ver.response_spectra[1], color_code[i], label=list_inc[i])   

        # station name
        if not station_name:
            station_name = item.station.inc_st_name[list_inc[i]]
            temp_record = item
        
        # epicentral distance
        if not epicentral_dist:
            epicentral_dist = f"{item.epicentral_distance: 0.2f}"

    axarr[0][0].set_ylabel('h1')
    axarr[1][0].set_ylabel('h2')
    axarr[2][0].set_ylabel('ver')
    axarr[2][0].set_xlabel('Time (s)')
    axarr[2][1].set_xlabel('Period (s)')
    axarr[0][1].set_title('Response Spectra')

    f_name_save = "f_acceleration_plot_" +\
         datetime.now().strftime("%Y%m%d_%H%M%S_%f" + ".pdf")
    details = [f_name_save, list_inc, list_process, list_filters,
     temp_record.station.inc_st_name]
    message = list2message(details)

    if with_details:
        footnote_font = FontProperties()
        footnote_font.set_size(6)
        max_height = 100 
        axarr[3][0].text(1,0.8 * max_height,message, va = 'top',
         fontproperties = footnote_font, wrap=True)
        
        axarr[3][0].set_xlim([0,50])
        axarr[3][0].set_ylim([0,max_height])
        axarr[3][0].get_xaxis().set_ticks([])
        axarr[3][0].get_yaxis().set_ticks([])
    
    for i in range(3):    
        axarr[i][0].set_xlim(x_lim_t)
        axarr[i][1].set_xlim(x_lim_rsp)
    
    axarr[0][0].legend()
    axarr[0][0].set_title(
        f'Station at incident {list_inc[0]}:'
        f'{station_name} - epicenteral dist:'
        f'{epicentral_dist} km'
        )    
    
    fig.tight_layout()  
    return fig, message, f_name_save



def plot_recordsection_helper(records, color_code, opt_params,list_inc,list_process,list_filters):
    """ Plots seismic record section. It is an internal function for
     plot_record_section methods in the Project class.
     should not be directly used by the end users.
    """
    # Check number of input incidents
    if len(records[0]) > len(color_code):
        LOGGER.error(f"Number of timeseries are more than dedicated" 
        "colors.")
        return

    with_details = False
    if query_opt_params(opt_params, 'save_figure'):  
        nrs = 7          
        fig, axarr = plt.subplots(nrows=nrs, ncols=1, figsize=(14, 9))
        rspan = 6
        with_details = True
    else:
        nrs = 1
        fig, axarr = plt.subplots(nrows=nrs, ncols=1, figsize=(14, 9))
        rspan = 1
    
    axarr[0] = plt.subplot2grid((nrs,1),(0,0),rowspan=rspan, colspan=1)

    if with_details:
        axarr[1] = plt.subplot2grid((nrs,1),(6,0),rowspan=1, colspan=1)

    x_lim_t = check_opt_param_minmax(opt_params, 'zoom_in_time')

    comp = opt_params.get('comp',None)
    if not comp or (comp not in ["h1","h2","ver"]):
        if comp:
            LOGGER.warning(f"The component: {comp} is not supported. "
              "h1 is used.")
        comp = "h1"
    
    for k,record in enumerate(records):
        for i,item in enumerate(record):
            if not item:
                continue
                                           
            if comp == "h1":
                tmp_data = (0.8*item.vel_h1.value/item.vel_h1.peak_vv)+\
                    item.epicentral_distance
            elif comp == "h2":
                tmp_data = (0.8*item.vel_h2.value/item.vel_h2.peak_vv)+\
                    item.epicentral_distance
            elif comp == "ver":
                tmp_data = (0.8*item.vel_ver.value/item.vel_ver.peak_vv)+\
                    item.epicentral_distance
            else: 
                LOGGER.error("Should never get here. Double check.")
                                
            if k == 0: 
                legend_label=list_inc[i]    
            else:
                legend_label=None
            axarr[0].plot(item.time_vec, tmp_data, color_code[i], 
            label=legend_label, linewidth=0.2)
        
    axarr[0].set_xlabel('Time (s)')
    axarr[0].set_ylabel('Epicentral Distance (km)')        
    axarr[0].set_xlim(x_lim_t)
    axarr[0].legend()
    axarr[0].set_title(
     f"Normalized Seismic Record Section -"
     f"Number of stations/incident: {k+1}"
     f"- Component: {comp}"
    )    

    f_name_save = "f_recordsection_plot_" +\
    datetime.now().strftime("%Y%m%d_%H%M%S_%f" + ".pdf")
    details = [f_name_save, list_inc, list_process, list_filters,{}]
    message = list2message(details)

    if with_details:
        footnote_font = FontProperties()
        footnote_font.set_size(6)
        max_height = 100 
        axarr[1].text(1,0.8 * max_height,message, va = 'top',
         fontproperties = footnote_font, wrap=True)
        
        axarr[1].set_xlim([0,50])
        axarr[1].set_ylim([0,max_height])
        axarr[1].get_xaxis().set_ticks([])
        axarr[1].get_yaxis().set_ticks([])
    
    fig.tight_layout() 

    return fig, message, f_name_save        