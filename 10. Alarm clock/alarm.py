import datetime  # Import the datetime module to work with dates and times
import time  # Import the time module for delays
import os

def play_alarm():
    alarm_time = datetime.datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
    # Get the current time and set the alarm time to 7:00 AM
    
    while True:
        current_time = datetime.datetime.now()
        # Get the current time
        
        if current_time >= alarm_time:
            os.system("arc https://youtu.be/g2j40WZ08Vw?list=RDCLAK5uy_nkcASjXWcg7Pu2wOP5G6VXGD34J0bmGkQ")
            #os.startfile("formula1.mp3")
            # Check if the current time is greater than or equal to the alarm time
            print("Wake up!")  # Print "Wake up!" to the console
            break  # Exit the loop if the alarm goes off
        
        else:
            time.sleep(1)  # Wait for 1 second before checking the time again

play_alarm()  # Call the play_alarm() function to start the alarm clock