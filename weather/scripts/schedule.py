import requests
import json
import predict
import time
import os
from datetime import datetime
import sched
import sys

# local imports
import process


def run(hours):
    # get lat and lon from private file
    with open("/home/pi/website/weather/scripts/secrets.json") as f:
        data = json.load(f)
        lat = data["lat"]
        lon = data["lon"]

    # get the tle file form celestrak
    url = "https://www.celestrak.com/NORAD/elements/weather.txt"
    r = requests.get(url)
    tle = r.content.decode("utf-8").replace("\r\n", "newline").split("newline")

    # write tle to file for use with wxmap
    with open("/home/pi/website/weather/scripts/weather.tle", "w+") as f:
        f.write(r.text.replace("\r", ""))

    # find the satellites in the tle
    index = tle.index("NOAA 15                 ")
    NOAA15 = "\n".join(tle[index:index + 3])
    index = tle.index("NOAA 18                 ")
    NOAA18 = "\n".join(tle[index:index + 3])
    index = tle.index("NOAA 19                 ")
    NOAA19 = "\n".join(tle[index:index + 3])
    index = tle.index("METEOR-M 2              ")
    METEOR = "\n".join(tle[index:index + 3])

    # set the ground station location
    loc = (lat, lon * -1, 20)

    # get the next passes of NOAA 15 within the next 24 hours
    print("getting NOAA 15 passes")
    NOAA15_passes = predict.transits(NOAA15, loc,
                                     time.time() + 900,
                                     time.time() + (3600 * hours))

    # get the next passes of NOAA 18 within the next 24 hours
    print("getting NOAA 18 passes")
    NOAA18_passes = predict.transits(NOAA18, loc,
                                     time.time() + 900,
                                     time.time() + (3600 * hours))

    # get the next passes of NOAA 19 within the next 24 hours
    print("getting NOAA 19 passes")
    NOAA19_passes = predict.transits(NOAA19, loc,
                                     time.time() + 900,
                                     time.time() + (3600 * hours))

    # get the next passes of METEOR within the next 24 hours
    print("getting METEOR passes")
    METEOR_passes = predict.transits(METEOR, loc,
                                     time.time() + 900,
                                     time.time() + (3600 * hours))

    # create one big list of all the passes
    passes = []
    for p in NOAA15_passes:
        if p.peak()['elevation'] >= 20:
            passes.append(["NOAA 15", "NOAA", p])
    for p in NOAA18_passes:
        if p.peak()['elevation'] >= 20:
            passes.append(["NOAA 18", "NOAA", p])
    for p in NOAA19_passes:
        if p.peak()['elevation'] >= 20:
            passes.append(["NOAA 19", "NOAA", p])
    for p in METEOR_passes:
        if p.peak()['elevation'] >= 20:
            passes.append(["METEOR-M 2", "METEOR", p])

    # sort them by their date
    passes.sort(key=lambda x: x[2].start)

    freqs = {
        'NOAA 15': 137620000,
        'NOAA 18': 137912500,
        'NOAA 19': 137100000,
        'METEOR-M 2': 137100000,
    }

    # turn the info into json data
    data = []
    for p in passes:
        sat = p[0]
        sat_type = p[1]
        info = p[2]
        data.append({
            # ALL TIMES ARE IN SECONDS SINCE EPOCH (UTC)

            # name of the sat
            'satellite':
            sat,
            # the frequency in MHz the satellite transmits
            'frequency':
            freqs[sat],
            # time the sat rises above the horizon
            'aos':
            round(info.start),
            # time the sat reaches its max elevation
            'tca':
            round(info.peak()['epoch']),
            # time the sat passes below the horizon
            'los':
            round(info.end),
            # maximum degrees of elevation
            'max_elevation':
            round(info.peak()['elevation'], 1),
            # duration of the pass in seconds
            'duration':
            round(info.duration()),
            # status INCOMING, CURRENT or PASSED
            'status':
            "INCOMING",
            # type of satellite
            'type':
            sat_type,
            # azimuth at the aos
            'azimuth_aos':
            round(info.at(info.start)['azimuth'], 1),
            # azimuth at the los
            'azimuth_los':
            round(info.at(info.end)['azimuth'], 1),
            # either northbound or southbound
            'direction':
            "northbound"
            if 90 < info.at(info.start)['azimuth'] > 270 else "southbound"
        })

    # check if passes overlap and choose which one to prioritize
    i = 0
    while i < len(data) - 2:
        if data[i]['los'] > data[i + 1]['aos']:
            # prioritize higher elevation passes
            priority1 = data[i]['max_elevation']
            priority2 = data[i + 1]['max_elevation']

            # meteor gets more priority
            if data[i]['satellite'] == "METEOR-M 2":
                priority1 += 30
            elif data[i + 1]['satellite'] == "METEOR-M 2":
                priority2 += 30

            # keep the pass with higher priority
            if priority1 >= priority2:
                data.pop(i + 1)
            elif priority2 > priority1:
                data.pop(i)
        else:
            i += 1

    # write to the json file
    with open("/home/pi/website/weather/scripts/daily_passes.json",
              "w") as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

    # schedule the passes for the day
    s = sched.scheduler(time.time, time.sleep)
    i = 0
    for p in data:
        # create a job for every pass
        print("Scheduled a job for {} or {}".format(
            p['aos'],
            datetime.fromtimestamp(
                p['aos']).strftime("%B %-d, %Y at %-H:%M:%S %Z")))
        s.enterabs(p['aos'], 1, process.start, argument=(i, ))
        i += 1

    # commit changes to git repository
    #print("STATUS {} - ".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S")) + "Commiting changes to github")
    #os.system("/home/pi/website/weather/scripts/commit.sh 'Automatically scheduled satellite passes for the next 24 hours'")

    print("STATUS {} - ".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S")) +
          "Finished scheduling")

    next_pass = data[0]
    print(
        "STATUS: {} - ".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S")) +
        "Waiting until {} for {}° {} pass...".format(
            datetime.fromtimestamp(next_pass['aos']).strftime(
                "%B %-d, %Y at %-H:%M:%S"), next_pass['max_elevation'],
            next_pass['satellite']))

    s.run()

    run(hours)


if __name__ == "__main__":
    hours = int(sys.argv[1])
    run(hours)
