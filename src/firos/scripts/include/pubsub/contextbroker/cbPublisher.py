import json
import time
import rospy
import urllib2

from include.constants import CONTEXTBROKER
from include.pubsub.iPubSub import Ipublisher

class CbPublisher(Ipublisher):
    def createContent(self, topic, datatype, data):
        data["firosstamp"] = time.time()
        return {
            "name": topic,
            "type": datatype,
            "value": json.dumps(data).replace('"', "'")
        }

    def publish(self, contex_id, datatype, attributes=[]):
        commands = []
        for attribute in attributes:
            commands.append(attribute["name"])
        attributes.insert(0, {
            "name": "COMMAND",
            "type": "COMMAND",
            "value": commands
        })
        data = {
            "contextElements": [
                {
                    "id": contex_id,
                    "type": datatype,
                    "isPattern": "false",
                    "attributes": attributes
                }
            ],
            "updateAction": "APPEND"
        }

        url = "http://{}:{}/{}/updateContext".format(CONTEXTBROKER["ADDRESS"], CONTEXTBROKER["PORT"], CONTEXTBROKER["PROTOCOL"])
        data_json = json.dumps(data)
        request = urllib2.Request(url, data_json, {'Content-Type': 'application/json', 'Accept': 'application/json'})
        response = urllib2.urlopen(request)
        response_body = json.loads(response.read())
        response.close()

        if "errorCode" in response_body:
            rospy.logerr("Error sending data to Context Broker:")
            rospy.logerr(response_body["errorCode"]["details"])
        else:
            print "Success sending"