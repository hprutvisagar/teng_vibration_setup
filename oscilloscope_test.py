"""
# GitHub examples repository path: Oscilloscopes/Python/RsInstrument

This Python example shows how to transfer waveform data (ASCII and binary format)
+ screenshot from MXO oscilloscope to the controller PC. The MXO probe compensation
signal can be used for a simple test.

Preconditions:
- Installed RsInstrument Python module from pypi.org
- Installed VISA e.g. R&S Visa 5.12.x or newer

Tested with:
- MXO, FW: v1.3.2.0
- Python 3.9
- RsInstrument 1.53.0

Author: R&S Customer Support /  Changes to MXO PJ
Updated on 04.05.2023
Version: v1.0

Technical support -> https://www.rohde-schwarz.com/support

Before running, please always check this script for unsuitable setting !
This example does not claim to be complete. All information have been
compiled with care. However, errors can’t be ruled out.

"""

from RsInstrument import *  # The RsInstrument package is hosted on pypi.org, see Readme.txt for more details
import matplotlib.pyplot as plt
from time import time


def main():
    import RsInstrument
    import numpy as np
    import csv
    import matplotlib.pyplot as plt
    import pandas as pd

    # Connect to the oscilloscope
    rtb = RsInstrument.RsInstrument('USB0::0x0AAD::0x01D6::111986::INSTR', True, True)

    # -----------------------------------------------------------
    # Basic Settings:
    # ---------------------------- -------------------------------
    rtb.write_str("TIM:ACQT 120e-3")  # Horizontal range---1.2ms Acquisition time
    rtb.write_str("CHAN1:RANG 8")  # vertical range 0.6V (0.5V/div)
    rtb.write_str("CHAN1:OFFS 0.0")  # Offset 0
    rtb.write_str("CHAN1:COUP ACL")  # Coupling AC 1MOhm
    rtb.write_str("CHAN1:STAT ON")  # Switch Channel 1 ON

    # -----------------------------------------------------------
    # Trigger Settings:
    # -----------------------------------------------------------
    rtb.write_str("TRIG:A:MODE AUTO")  # Trigger Auto mode in case of no signal is applied
    rtb.write_str("TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")  # Trigger type Edge Positive
    rtb.write_str("TRIG:A:SOUR CH1")  # Trigger source CH1
    rtb.write_str("TRIG:A:LEV1 0.0")  # Trigger level 0.05V
    rtb.query_opc()  # Using *OPC? query waits until all the instrument settings are finished

    # Initiate a single acquisition and wait for it to finish
    rtb.write_str_with_opc("SINGle", 3000)

    # Query array of floats in ASCII format
    waveform = rtb.query_bin_or_ascii_float_list('FORM ASC;:CHAN1:DATA?')

    # Fetch timebase settings
    x_increment = float(rtb.query('CHAN1:DATA:XINC?'))  # Horizontal scale
    x_origin = float(rtb.query('CHAN1:DATA:XOR?'))  # Horizontal position

    # Calculate time data
    time_data = np.arange(0, len(waveform)) * x_increment + x_origin


    rtb.close()

    # data plotting
    data = pd.DataFrame({
        'time_data': time_data,
        'waveform': waveform
    })

    data.plot(x='time_data', 
              y='waveform', 
              xlabel='Time', 
              ylabel='Voltage (V)', 
              title='Oscilloscope Waveform', 
              figsize=(16,8),
              grid=True
              )
    plt.show()

    # Save waveform data to CSV file
    csv_file_path = 'waveform_data.csv'
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Time (s)', 'Voltage (V)'])  # Write the header
        csv_writer.writerows(zip(time_data, waveform))  # Write the time and voltage data

        print(f"Waveform data saved to '{csv_file_path}'")


if __name__ == "__main__":
    main()
