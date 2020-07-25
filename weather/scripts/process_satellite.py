#Made by Felix (Blobtoe)

import os
import json
from PIL import Image
from datetime import datetime, timedelta


#######################################
#records, demodulates, and decodes METEOR-M 2 given the json file for the pass and the output file name, then returns the image's file path
def METEOR(path, outfile):
    #set variables
    with open(path) as f:
        data = json.load(f)
        duration = data["duration"]
        frequency = data["frequency"]

    #record pass baseband with rtl_fm
    print("recording pass...")
    os.system("timeout {} /usr/bin/rtl_fm -M raw -s 140k -f {} -E dc -g 49.6 -p 0 - | sox -t raw -r 140k -c 2 -b 16 -e s - -t wav {}.iq.wav rate 192k".format(duration, frequency, outfile))

    #demodulate the signal
    print("demodulating meteor signal...")
    os.system("/usr/bin/meteor_demod -B -r 72000 -m qpsk -o {}.qpsk {}.iq.wav".format(outfile, outfile))

    #decode the signal into an image
    print("decoding image...")
    os.system("/usr/local/bin/medet_arm {}.qpsk {} -q -cd".format(outfile, outfile))
    
    #convert bmp to jpg
    bmp = Image.open("{}.bmp".format(outfile))
    bmp = bmp.rotate(180)
    bmp.save("{}.jpg".format(outfile))

    #get rid of the blue tint in the image (thanks to PotatoSalad for the code)
    img = Image.open(outfile + ".jpg")
    pix = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x, y][2] > 140 and pix[x, y][0] < pix[x, y][2]:
                pix[x, y] = (pix[x, y][2], pix[x, y][1], pix[x, y][2])
    img.save(outfile + ".equalized.jpg")

    #rectify images
    os.system("/usr/local/bin/rectify-jpg {}.equalized.jpg".format(outfile))

    #rename file
    os.rename("{}.equalized-rectified.jpg".format(outfile), "{}.rgb123.jpg".format(outfile))

    #return the image's file path
    return ["{}.equalized-rectified.jpg".format(outfile)]


#######################################
#records and decodes NOAA APT satellites given the json file for the pass and the output file name, then returns the images' file paths
def NOAA(path, outfile):
    #set variables
    with open(path) as f:
        data = json.load(f)
        duration = data["duration"]
        frequency = data["frequency"]
        satellite = data["satellite"]
        aos = data["aos"]

    #record the pass with rtl_fm
    print("writing to file: {}.wav".format(outfile))
    os.system("timeout {} /usr/bin/rtl_fm -d 0 -f {} -g 49.6 -s 37000 -E deemp -F 9 - | sox -traw -esigned -c1 -b16 -r37000 - {}.wav rate 11025".format(duration, frequency, outfile))

    #check if the wav file was properly created
    if os.path.isfile(outfile + ".wav") == True and os.stat(outfile + ".wav").st_size > 10:
        pass
    else:
        print("wav file was not created correctly. Aborting")
        exit()

    #create map overlay
    print("creating map")
    date = (datetime.strptime(aos, "%Y-%m-%d %H:%M:%S.%f %Z")+timedelta(0, 90)).strftime("%d %b %Y %H:%M:%S")
    os.system("/usr/local/bin/wxmap -T \"{}\" -H /home/pi/website/weather/scripts/weather.tle -p 0 -l 0 -g 0 -o \"{}\" {}-map.png".format(satellite, date, outfile))

    #create images
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -a -e contrast {}.wav {}.a.png".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -b -e contrast {}.wav {}.b.png".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -e HVCT {}.wav {}.HVCT.png".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -e MSA {}.wav {}.MSA.png".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -e MSA-precip {}.wav {}.MSA-precip.png".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A {}.wav {}.raw.png".format(outfile, outfile, outfile))

    #return the images' file paths
    return [
        "{}.a.png".format(outfile),
        "{}.b.png".format(outfile),
        "{}.HVCT.png".format(outfile),
        "{}.MSA.png".format(outfile),
        "{}.MSA-precip.png".format(outfile),
        "{}.raw.png".format(outfile)]