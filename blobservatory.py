import picamera
import time
import RPi.GPIO as GPIO
from fractions import Fraction
import os
import argparse
import datetime
import logging
import Adafruit_DHT
import csv
import os.path

logging.basicConfig(level=logging.INFO,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
logger = logging.getLogger("blobservatory")

EVENT_FILE="evenements.csv"
PREVIEW_TIME=2

LED_PIN=17
DHT_PIN = 4

def init_GPIO():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    # Configure PIN for LED
    GPIO.setup(LED_PIN,GPIO.OUT)

def add_event(event_name="picture",file_name="evenements.csv"):
    pass

def play_sound(sound="camera.wav"):
    # This function could rely on Python libs instead
    os.system('aplay camera.wav')

def take_capture(capture_name, manual=True, preview_time=PREVIEW_TIME, iso=200, resolution=(2592,1944), with_sound=False, awb_mode="sunlight", shutter_speed=1000000):
    try:
        cam = picamera.PiCamera()
        cam.resolution = resolution
        cam.led=False
        if manual:
            #cam.framerate = Fraction(1, framerate)
            cam.sensor_mode = 3
            cam.framerate = 1
            cam.exposure_mode = "off"
            cam.shutter_speed = shutter_speed
            # modes:verylong, spotlight, off,...
            cam.iso = iso
            cam.led = 0
            # awsmodes:sunlight cloudy, tungsten, flusorescent
            cam.awb_mode=awb_mode
        light_on()
        if preview_time != 0:
            logger.info("Wait before taking picture")
            time.sleep(preview_time)
        if with_sound:
            play_sound()
        logger.debug("AWB: " + str(cam.awb_mode) + " | gains: " + str(cam.awb_gains))
        logger.debug("Exposure Speed: " + str(cam.exposure_speed))
        logger.info("Camera Capture in " + str(capture_name))
        cam.capture(capture_name)
        light_off()
        cam.close()
        logger.debug("Camera closed")
    except Exception as e:
        logger.error("Error: " + str(e.args))
        light_off()

def test_configurations(directory="pictures", preview_time=2, iso=200, awb_mode="auto"):

    for ss in range(500000,1000000,50000):
        logger.info("---------- ShutterSpeed: " + str(ss) + " ----------")
        take_capture(directory+"/test_" + str(ss) + ".jpg", manual=True, iso=200, preview_time=preview_time, \
                with_sound=True, awb_mode=awb_mode, shutter_speed=ss) 


def light_on():
    logger.debug("Turning lights ON")
    GPIO.output(LED_PIN, GPIO.HIGH)

def light_off():
    logger.debug("Turning lights OFF")
    GPIO.output(LED_PIN, GPIO.LOW)


def wait_for_capture(delay=30, capture_name="pictures/coucou.jpg"):
    GPIO.output(ALIM_PIN, GPIO.HIGH)
    start_time = int(time.time())
    print("Press button to take a picture")
    while True:
        channel = GPIO.wait_for_edge(BUTTON_PIN,GPIO.RISING,timeout=1000)
        print(capture_continuouchannel)
        if channel and channel == BUTTON_PIN:
            take_capture(capture_name)    
        if start_time + delay < int(time.time()):
                break

def timelapse(duration=3600, base_name="pictures/blob_", interval=300, preview_time=PREVIEW_TIME, minute=0):
    logger.info("Starting timelapse")
    start_time = int(time.time())
    i = 0
    current_time = int(time.time())
    while(start_time + duration > current_time):
        current_time = int(time.time())
        print("Taking capture " + str(i))
        take_capture(base_name+str(i)+".jpg")
        if start_time + duration < current_time:
            break
        i+=1
        time.sleep(interval-preview_time)


def read_dht(max_loops=10, temperature_file="", capture_time=""):
    logger.debug("Reading temperature")
    DHT_SENSOR=Adafruit_DHT.DHT11
    for i in range(1,max_loops):
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        if humidity and temperature:
            logger.info("Temperature: " + str(temperature) + " | Humidity: " + str(humidity) )
            break
        else:
            logger.debug("Doing another loop...")
            time.sleep(1)
    if humidity and temperature and temperature_file != "":
        file_exists = os.path.isfile(temperature_file)
        with open(temperature_file, "a", newline='') as csv_file:
            fn = ["Timestamp", "Temperature", "Humidity"]
            csv_writer = csv.DictWriter(csv_file, fieldnames=fn, delimiter=";")
            if not file_exists:
                csv_writer.writeheader()
            tmp_dict = {"Timestamp": capture_time, "Temperature": temperature, "Humidity": humidity}
            logger.debug("Writing Row in " + str(temperature_file) + " | " + str(tmp_dict))
            csv_writer.writerow(tmp_dict)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Pass arguments")
    parser.add_argument('-m', "--mode", choices=["photo", "timelapse", "test", "led", "cron", "temperature"], default="photo")
    parser.add_argument('-f', "--file_name", default="blob")
    parser.add_argument('-d', "--directory", default="pictures")
    parser.add_argument("--awb-mode", choices=["auto", "sunlight", "cloudy", "shade", "tungsten", "fluorescent", "incandescent"], default="auto")
    parser.add_argument("--sound", action="store_true")
    parser.add_argument('-p', "--preview", type=int, default=0)
    parser.add_argument("--duration", default=86400)
    parser.add_argument("--interval", default=600)
    parser.add_argument("--minute", default=10)
    parser.add_argument('-v', "--verbosity", choices=[10,20,30,40,50], default=20, type=int)
    args = parser.parse_args()
    logger.setLevel(args.verbosity)
    if args.mode == "photo":
        init_GPIO()
        light_off()
        take_capture(args.directory + "/" + args.file_name + ".jpg")

    if args.mode == "test":
        init_GPIO()
        light_off()
        test_configurations(directory=args.directory, preview_time=args.preview ,awb_mode=args.awb_mode)

    if args.mode == "timelapse":
        init_GPIO()
        light_off()
        timelapse()

    if args.mode == "led":
        init_GPIO()
        light_on()
        time.sleep(30)
        light_off()

    if args.mode == "cron":
        init_GPIO()
        light_off()
        timestamp = str(datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))
        file_name = args.file_name + "_" +  str(timestamp)
        take_capture(args.directory + "/" + file_name + ".jpg", iso=800, preview_time=args.preview, \
                awb_mode=args.awb_mode, with_sound=True, shutter_speed=1000000)
        read_dht(capture_time=timestamp, temperature_file=args.directory+"/temprature.csv")

    if args.mode == "temperature":
        init_GPIO()
        light_off()
        read_dht(capture_time="test", temperature_file="/mnt/key/temperatures.csv")
        pass
        
