# SUMOBot
Mechatronics SUMO Bot Student Competition

This project uses a MicroPython board

You can get started right away by writing your Python code in 'main.py'.

For a serial prompt:
 - Windows: you need to go to 'Device manager', right click on the unknown device,
   then update the driver software, using the 'pybcdc.inf' file found on this drive.
   Then use a terminal program like Hyperterminal or putty.
 - Mac OS X: use the command: screen /dev/tty.usbmodem*
 - Linux: use the command: screen /dev/ttyACM0

Please visit http://micropython.org/help/ for further help.

To run the program, flash files onto Microcontroller and start up the boot sequence.

| Files | Description |
-----------------------
| boot | Initiate boot sequence |
| controller | A class for a motor controller that enables a user to ser a proportional control gain kp and a setPoint for the duty cycle |
| cotask | A class that runs cooperatively scheduled tasks. A scheduling algorithm is chosen by the user |
| encoder_timer | A class that reads or zeroes an encoder value used for motor control |
| main | A driver that defines movement controls and sensor readings for the bot. Admittedly should be broken into more modular components |
| motor | A class that actually integrates the motor with the Microcontroller. Allow the user to set a duty cycle |
| print_task | A  class for queueing characters to be printed to the screen. Avoids blocking cooperative multitasking when using print statement |
| task_share | A class that contains a system-level list of queues and shared variables to enable safe sharing of data |
