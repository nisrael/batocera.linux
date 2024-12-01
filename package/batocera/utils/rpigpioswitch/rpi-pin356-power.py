#!/usr/bin/python3

import os
import gpiod
import subprocess
import time

# Pin Configuration
POWER_CHIP = "/dev/gpiochip0"
POWER_PIN = 3  # pin 5
RESET_PIN = 2  # pin 3
LED_PIN = 4   # pin 7

def init_gpio():
    try:
        chip = gpiod.Chip(POWER_CHIP)
        
        power_button = chip.get_line(POWER_PIN)
        reset_button = chip.get_line(RESET_PIN)
        led = chip.get_line(LED_PIN)

        power_button.request(
            consumer='power', 
            type=gpiod.LINE_REQ_EV_FALLING_EDGE, 
            flags=gpiod.LINE_REQ_FLAG_PULL_UP
        )
        reset_button.request(
            consumer='reset', 
            type=gpiod.LINE_REQ_EV_FALLING_EDGE, 
            flags=gpiod.LINE_REQ_FLAG_PULL_UP
        )
        led.request(consumer='led', type=gpiod.LINE_REQ_DIR_OUT)
        
        led.set_value(1)  # Turn on LED
        
        return chip, power_button, reset_button, led
    
    except Exception as e:
        print(f"Failed to initialize GPIO: {e}")
        exit(1)

def blinkLED(led):
    while True:
        led.set_value(0)
        time.sleep(0.5)
        led.set_value(1)
        time.sleep(0.5)

def handle_shutdown():
    print('Shutting down Batocera')
    subprocess.run('(sleep 2; shutdown -h now) &', shell=True)

def handle_emulator_exit():
    print('Exiting all Batocera emulators')
    subprocess.run('batocera-es-swissknife --emukill', shell=True)

def watch_gpio_events():
    try:
        chip, power_button, reset_button, led = init_gpio()
        
        print("GPIO event monitoring started")
        
        while True:
            reset_event = reset_button.event_wait(sec=1)
            power_event = power_button.event_wait(sec=1)
            
            if reset_event:
                reset_button.event_read()
                handle_emulator_exit()
            
            if power_event:
                power_button.event_read()
                handle_shutdown()
                blinkLED(led)
            
    
    except Exception as e:
        print(f"Error watching GPIO events: {e}")
        exit(1)

def main():
    watch_gpio_events()

if __name__ == "__main__":
    main()
