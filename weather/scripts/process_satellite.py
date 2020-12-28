# Made by Felix (Blobtoe)

import os
import json
from PIL import Image
from datetime import datetime, timedelta
import cv2
import numpy as np


#######################################
# records, demodulates, and decodes METEOR-M 2 given the json file for the pass and the output file name, then returns the image's file path
def METEOR(path, outfile, logfile):
    # set variables
    with open(path) as f:
        data = json.load(f)
        duration = data["duration"]
        frequency = data["frequency"]
        sun_elev = data["sun_elev"]

    # record pass baseband with rtl_fm
    print("recording pass...")
    os.system("timeout {} /usr/bin/rtl_fm -M raw -s 110k -f {} -E dc -g 49.6 -p 0 - | sox -t raw -r 110k -c 2 -b 16 -e s - -t wav {}.iq.wav rate 192k >> {}".format(duration, frequency, outfile, logfile))

    # demodulate the signal
    print("demodulating meteor signal...")
    os.system("/usr/bin/meteor_demod -B -r 72000 -m qpsk -o {}.qpsk {}.iq.wav >> {}".format(outfile, outfile, logfile))

    # decode the signal into an image
    print("decoding image...")
    os.system("/usr/local/bin/medet_arm {}.qpsk {}.rgb122 -q -cd -r 65 -g 65 -b 64 >> {}".format(outfile, outfile, logfile))
    os.system("/usr/local/bin/medet_arm {}.rgb122.dec {}.ir -d -q -r 68 -g 68 -b 68 >> {}".format(outfile, outfile, logfile))

    # convert bmp to jpg
    os.system("convert {}.rgb122.bmp {}.rgb122.jpg >> {}".format(outfile, outfile, logfile))
    os.system("convert {}.ir.bmp {}.ir.jpg >> {}".format(outfile, outfile, logfile))

    '''
    #get rid of the blue tint in the image (thanks to PotatoSalad for the code)
    img = Image.open(outfile + ".jpg")
    pix = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x, y][2] > 140 and pix[x, y][0] < pix[x, y][2]:
                pix[x, y] = (pix[x, y][2], pix[x, y][1], pix[x, y][2])
    img.save(outfile + ".equalized.jpg")
    '''

    # rectify images
    os.system("/usr/local/bin/rectify-jpg {}.rgb122.jpg >> {}".format(outfile, logfile))
    os.system("/usr/local/bin/rectify-jpg {}.ir.jpg >> {}".format(outfile, logfile))

    # rename file
    os.rename("{}.rgb122-rectified.jpg".format(outfile), "{}.rgb122.jpg".format(outfile))
    os.rename("{}.ir-rectified.jpg".format(outfile), "{}.ir.jpg".format(outfile))

    main_tag = "rgb122"
    if sun_elev <= 10:
        main_tag = "ir"

    # add precipitaion overlay to main image
    THRESHOLD = 25
    ir = cv2.imread("{}.ir.jpg".format(outfile), cv2.IMREAD_GRAYSCALE)
    image = cv2.imread("{}.{}.jpg".format(outfile, main_tag))
    clut = cv2.imread("/home/pi/website/weather/scripts/clut.png")

    _, mask = cv2.threshold(ir, THRESHOLD, 255, cv2.THRESH_BINARY_INV)
    image[np.where(mask == 255)] = [clut[0][int(value)] for value in ir[np.where(mask == 255)] * [255] / [THRESHOLD]]
    cv2.imwrite("{}.{}-precip.jpg".format(outfile, main_tag), image)

    # return the image's file path
    return [
        "{}.rgb122.jpg".format(outfile),
        "{}.ir.jpg".format(outfile),
        "{}.{}-precip.jpg".format(outfile, main_tag)
    ], "{}-precip".format(main_tag)


#######################################
# records and decodes NOAA APT satellites given the json file for the pass and the output file name, then returns the images' file paths
def NOAA(path, outfile, logfile):
    # set variables
    with open(path) as f:
        data = json.load(f)
        duration = data["duration"]
        frequency = data["frequency"]
        satellite = data["satellite"]
        aos = data["aos"]
        max_elevation = data["max_elevation"]
        sun_elev = data["sun_elev"]

    # record the pass with rtl_fm
    print("writing to file: {}.wav".format(outfile))
    os.system("timeout {} /usr/bin/rtl_fm -d 0 -f {} -g 49.6 -s 37000 -E deemp -F 9 - | sox -traw -esigned -c1 -b16 -r37000 - {}.wav rate 11025 >> {}".format(duration, frequency, outfile, logfile))

    # check if the wav file was properly created
    if os.path.isfile(outfile + ".wav") == True and os.stat(outfile + ".wav").st_size > 10:
        pass
    else:
        print("wav file was not created correctly. Aborting")
        exit()

    # create map overlay
    print("creating map")
    date = (datetime.utcfromtimestamp(aos)+timedelta(0, 90)).strftime("%d %b %Y %H:%M:%S")
    os.system("/usr/local/bin/wxmap -T \"{}\" -H /home/pi/website/weather/scripts/weather.tle -p 0 -l 0 -g 0 -o \"{}\" {}-map.png >> {}".format(satellite, date, outfile, logfile))

    # create images
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -a -e contrast {}.wav {}.a.jpg >> {}".format(outfile, outfile, outfile, logfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -b -e contrast {}.wav {}.b.jpg >> {}".format(outfile, outfile, outfile, logfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -e HVCT {}.wav {}.HVCT.jpg >> {}".format(outfile, outfile, outfile, logfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -e MSA {}.wav {}.MSA.jpg >> {}".format(outfile, outfile, outfile, logfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -e MSA-precip {}.wav {}.MSA-precip.jpg >> {}".format(outfile, outfile, outfile, logfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG {}.wav {}.raw.jpg >> {}".format(outfile, outfile, outfile, logfile))

    # change the main image depending on the sun elevation
    if sun_elev <= 10:
        main_tag = "b"
    elif sun_elev <= 30 or max_elevation <= 30:
        main_tag = "HVCT"
    else:
        main_tag = "MSA-precip"

    # return the images' file paths
    return [
        "{}.a.jpg".format(outfile),
        "{}.b.jpg".format(outfile),
        "{}.HVCT.jpg".format(outfile),
        "{}.MSA.jpg".format(outfile),
        "{}.MSA-precip.jpg".format(outfile),
        "{}.raw.jpg".format(outfile)], main_tag
