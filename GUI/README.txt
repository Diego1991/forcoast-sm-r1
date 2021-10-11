# This is the GUI version of the "FORCOAST-SM-R1: Retrieve Sources of
# Contaminants". Although OpenDrift is required to run the Python
# script SM-R1-GUI.py, it is not needed to display the Graphical 
# User Interface, which is based on Tkinter. Only when the "Start" is
# pressed, OpenDrift is required. 
#
# This GUI is just a suggestion of how the Service Module may look like
# in the final FORCOAST platform. Same options as in the CLI version are
# available to the user. 
#
# In order to run OpenDrift within this app, a few modifications of the
# OpenDrift code are needed to display the logging information into the
# app display. Copy the files in the OpenDrift folder into their 
# respective locations to replace the original ones in the local 
# OpenDrift installation (after OpenDrift has been installed following 
# the instructions in https://opendrift.github.io/):
#
# (1) \opendrift\opendrift\models\basemodel.py
#
# (2) \Miniconda3\envs\opendrift\Lib\logging\__init__.py
#
# Select the Pilot in the pilot.txt file.
