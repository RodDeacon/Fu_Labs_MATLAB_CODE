''' 
Rodney Deacon
6/29/2023
Fu Lab PLE code testground

output voltage test from : https://github.com/ni/nidaqmx-python/blob/master/examples/ao_voltage_hw_timed.py
'''
import nidaqmx

# the following context manager is testing output voltage 
with nidaqmx.Task() as myTask: # instantiate a new task called "myTask"
    myTask.ao_channels.add_ao_voltage_chan("Dev1/ao3") # add a new voltage channel to the task

    myTask.timing.cfg_samp_clk_timing(2000) # ASSUMED TO BE MILISECONDS

    print(myTask.write(3, auto_start=True)) # "writes" 3 , to Dev1/ao3 for 1 clock timing

    myTask.wait_until_done() # waits for task is complete
    myTask.stop()# stops task

