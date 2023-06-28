# Description
The ple gui will be a simple gui to run the PLE code.
It will allow the user to:
1. Define the parameters of the scan.
2. Read the collected data in real time.

# Design
1. There will be a main area where a single plot of the currently running, or most recently run scan will be presented.
2. There will be a button menu, where it will have options to start and stop the scan. (maybe even pause?)
3. There will be a dropdown menu to chose what type of scan is wanted (Stationary or Continuous).
    1. Clicking on one of the two options, a setup menu will pop up.
    2. The setup menu can be modified during a scan, but the changes will be applied until after the scan is finished.
    3. The setup parameters can be save/uploaded as json files.
