
#!/usr/bin/env python3
# encoding: UTF-8

import os
import pkgutil
import sys
from xml.sax.saxutils import escape as xmlescape
import requests
import time

if sys.version_info.major == 3:
    import urllib.request as urllibreq
else:
    import urllib2 as urllibreq


def send_dlna_action(device, data, action):
    #print("templates/action-{0}.xml".format(action))
    # action_data = pkgutil.get_data(self, "templates/action-{0}.xml".format(action)).decode("UTF-8")
    action_data = open("app/TV/dnla/templates/action-{0}.xml".format(action), 'rb').read().decode("UTF-8")
    action_data = action_data.format(**data).encode("UTF-8")

    headers = {
        "Content-Type": "text/xml; charset=\"utf-8\"",
        "Content-Length": "{0}".format(len(action_data)),
        "Connection": "close",
        "SOAPACTION": "\"{0}#{1}\"".format(device["st"], action)
    }

    r = requests.post(device["action_url"], action_data, headers=headers)

    if r.status_code == 500:
        stop(device)
        time.sleep(5)
        r = requests.post(device["action_url"], action_data, headers=headers)

    # request = urllibreq.Request(device["action_url"], action_data, headers)
    # response = urllibreq.urlopen(request)
    # content =  response.read()
    # print(content)


def play(files_urls, device):

    video_data = {
        "uri_video": files_urls["file_video"],
        "type_video": os.path.splitext(files_urls["file_video"])[1][1:],
        "object_type": 'object.item.imageItem.photo' if (files_urls["file_video"].endswith('jpg') or files_urls["file_video"].endswith('png')) else "object.item.videoItem.movie"
    }

    if "file_subtitle" in files_urls and files_urls["file_subtitle"]:

        video_data.update({
            "uri_sub": files_urls["file_subtitle"],
            "type_sub": os.path.splitext(files_urls["file_subtitle"])[1][1:]
        })

        metadata = pkgutil.get_data(
            "nanodlna",
            "templates/metadata-video_subtitle.xml").decode("UTF-8")
        video_data["metadata"] = xmlescape(metadata.format(**video_data))

    else:
        video_data["metadata"] = ""

    send_dlna_action(device, video_data, "SetAVTransportURI")
    send_dlna_action(device, video_data, "Play")

def stop(device):
    send_dlna_action(device, {"":""}, "Stop")

def pause(device):
    send_dlna_action(device, {"":""}, "Pause")
