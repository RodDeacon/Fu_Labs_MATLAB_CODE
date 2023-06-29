''' 
Rodney Deacon
6/29/2023
Fu Lab PLE code testground

system info from : https://github.com/ni/nidaqmx-python/blob/master/examples/system_properties.py

output voltage test from : https://github.com/ni/nidaqmx-python/blob/master/examples/ao_voltage_hw_timed.py
'''
import nidaqmx
import traceback # temp for testing

devices_found = False

def get_system_info():
# test if there is successful communication with the DAQ, try and print system information
    local_system = nidaqmx.system.system.System.local() #create system object to get system info
    driver_version = local_system.driver_version # assign local_system's driver_version property to a driver_version variable

    # print the version of the driver using python's print format
    print(
        "DAQmx {0}.{1}.{2}".format(
            driver_version.major_version,
            driver_version.minor_version,
            driver_version.update_version, # might not need this comma
        )
    )

    # initilize a list to store devices
    device_list = [] #TEST

    # attempt look through all devices and print 
    # TODO: if there are no devices to print, then we cannot get a test voltage. i.e. don't run the next function
    for device in local_system.devices:
        device_list.append(device) # attempt to add device to device list #TEST
        print(
            #TODO: if device exists, add it to an array to be chosen from a list of devices
            "Device name: {0}, Product Category: {1}, Product type: {2}".format(
                device.name, device.product_category, device.product_type
            )
        )
    if len(device_list) > 0: # if a device is found then the boolean will be made true
        devices_found = True

# the following context manager is testing output voltage 
def test_out_voltage():
    with nidaqmx.Task() as myTask: # instantiate a new task called "myTask"
            myTask.ao_channels.add_ao_voltage_chan("Dev1/ao3") # add a new voltage channel to the task

            myTask.timing.cfg_samp_clk_timing(2000) # ASSUMED TO BE MILISECONDS

            print(myTask.write(3, auto_start=True)) # "writes" 3 , to Dev1/ao3 for 1 clock timing

            myTask.wait_until_done() # waits for task is complete
            myTask.stop()# stops task

print("\ndriver version:")
get_system_info()

print("\nattempting to generate test volatage on \"Dev1\\ao3\"..")
if devices_found: # if there are devices, try to run the function test_out_voltage() #TODO: device specific statements or menu    
    test_out_voltage()
else: print("no devices found.") # will print message if no devices are found
print("\nprogram completed")