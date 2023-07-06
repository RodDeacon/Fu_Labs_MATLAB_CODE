''' 
Rodney Deacon
7/6/2023
Fu Lab PLE code testground
system info from : https://github.com/ni/nidaqmx-python/blob/master/examples/system_properties.py
output voltage test from : https://github.com/ni/nidaqmx-python/blob/master/examples/ao_voltage_hw_timed.py
BUG: fix strange bug where BNC has constant voltage after program ends
    - set voltage to 3, then run program, after running once, change voltage to 2, both times, the voltage
        stays constant after program closes. After doing this, an attempt was made to change the voltage to 0,
        the BNC was not responsive to any further voltage changes so a reset of the device was needed.
TODO: remove redundancy of global _working_device variable as a function argument
'''
import nidaqmx
import traceback # temp for testing
 
# global for testing if a device found (currently depreciated keep true)
#devices_found = True
 
### GLOBALS ###
_working_device_name = "Dev1" # change this to the name of your device (Can be found using the get_system_info() method)
_working_device = nidaqmx.system.device.Device(_working_device_name)
 
_min_val= -3.0 # min value 
_max_val=  5.0
 
### FUNCTIONS ###
 
def get_system_info():
# test if there is successful communication with the DAQ, try and print system information
    local_system = nidaqmx.system.system.System.local() #create system object to get system info
    driver_version = local_system.driver_version # assign local_systems driver_version property to a driver_version variable
 
    # print the version of the driver using python's print format
    print(
        "DAQmx {0}.{1}.{2}".format(
            driver_version.major_version,
            driver_version.minor_version,
            driver_version.update_version, # might not need this comma
        )
    )
 
    # initilize a list to store devices
    #device_list = [] #TEST
 
    # attempt look through all devices and print 
    # TODO: if there are no devices to print, then we cannot get a test voltage. i.e. don't run the next function
    for device in local_system.devices:
        #device_list.append(device) # attempt to add device to device list #TEST
        print(
            #TODO: if device exists, add it to an array/list to be chosen from a list of devices
            "Device name: {0}, Product Category: {1}, Product type: {2}".format(
                device.name, device.product_category, device.product_type
            )
        )
    #if len(device_list) > 0: # if a device is found then the boolean will be made true
    #    devices_found = True
 
def test_out_voltage():
    ''' the following context manager is testing output voltage 
    '''
    print("\nattempting to create task\n")
    with nidaqmx.Task() as myTask:                              # instantiate a new task called "myTask"
        myTask.ao_channels.add_ao_voltage_chan("Dev1/ao1:1", min_val=_min_val, max_val=_max_val)      # add a new voltage channel to the task
 
 
        print(myTask.ao_channels.channel_names) #list available channels
 
        myTask.timing.cfg_samp_clk_timing(1000)                 # ASSUMED TO BE MILISECONDS
 
        print(myTask.write(3, auto_start=True))                 # "writes" 3 , to Dev1/ao3 for 1 clock timing "prints 1 to console to show it is working, 0 if not working"
 
        #myTask.wait_until_done()                                # waits for task is complete
        myTask.stop()                                           # stops task (didnt stop TRY CLOSE)
 
 
def available_terminals():
    '''loop through available terminals and print them out
    '''
    device = nidaqmx.system.device.Device("Dev1")
    for tr in device.terminals:
	    print(tr)
 
def ao_phys_channels():
    ''' attempt to view available ao_physical_channels
    '''
    for x in nidaqmx.system.physical_channel.ao_phys_channels:
        print(x)
    #print(nidaqmx.system.physical_channel.ao_physical_chans)
 
def available_accessories(d):
    ''' loop through available accessories
        param d = device to check
    '''
    print(
        "Accessory product number: {0}, product type {1}, serial number {2}".format(
            d.accessory_product_nums, d.accessory_product_types, d.accessory_product_nums
            )
        )
 


# def reset(d):
#     d.reset_device()


###### main program area ######
#print("\ndriver version:")                          # get driver info from system
#get_system_info()
 
#print("\nattemting to get accessory info")
#available_accessories(_working_device)
 
 
# print("\nattempting to reset device\n")             # reset device message to user
# _working_device.reset_device()                       # delimit the reset function of the device object
 
#print("\navailable terminals:\n")                  # show what terminals are available
#available_terminals()
 
#print("\nattempting to get all physical ao channels\n")
#ao_phys_channels()
 
#print("\nattempting to generate test volatage on \"Dev1\\ao3\"..")
#if devices_found: # if there are devices, try to run the function test_out_voltage() #TODO: device specific statements or menu    
#test_out_voltage()
#else: print("no devices found.") # will print message if no devices are found
print("\nprogram completed")