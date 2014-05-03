from ws4py.client.threadedclient import WebSocketClient
from datetime import datetime
import json
import time

registrationRequest = json.dumps({'type': 'REGISTRATION_REQUEST', 'data': 'null'})
workInitRequest = json.dumps({'type': 'WORK_INIT_REQUEST', 'data': 'null'})

class BioworkerPython(WebSocketClient):
    startTime = datetime.now()
    count = 0
    distances = []
    
    def opened(self):
        print("connected, now registering")
        self.send(registrationRequest)

    def closed(self, code, reason):
        print("Closed")

    def received_message(self, message):
        response = json.loads(str(message))
        
        if (response['type'] == 'REGISTRATION_RESPONSE'):
            print("registered")
            self.send(workInitRequest)
            
        if (response['type'] == 'WORK_INIT_RESPONSE'):
            print("initialized")
            BioworkerPython.distances = response['data'][0]
            task = response['data'][1]
            computation = self.computeResult(task)
            resultMessage = self.getWorkRequest(task, computation)
            self.send(resultMessage)
            BioworkerPython.count += 1
            
        if (response['type'] == 'WORK_RESPONSE'):
            task = response['data']
            computation = self.computeResult(task)
            resultMessage = self.getWorkRequest(task, computation)
            self.send(resultMessage)
            BioworkerPython.count += 1
            if BioworkerPython.count % 1000 == 0:
                endTime = datetime.now()
                print("{0}ms for last 1000 computations".format(endTime - BioworkerPython.startTime, 1000))
                BioworkerPython.startTime = endTime
            
    def getWorkRequest(self, task, data):
        message = {"type": "WORK_REQUEST", "data": {"id": task["id"], "slot": task["slot"], "result": data}}
        #print(message)
        return json.dumps(message);
    
    def computeResult(self, task):
        return self.computeFitness(task['genome'])

    def computeFitness(self, data):
        pathLength = 0.0;
    
        for i in xrange(0, len(data) - 1):
            pathLength += BioworkerPython.distances[data[i]][data[i + 1]]
    
        pathLength += BioworkerPython.distances[data[len(data) - 1]][data[0]]
        return pathLength
            
try:
    ws = BioworkerPython('ws://kleintroppl:30000/websocket/ga')
#     ws = BioworkerPython('ws://master:30000/websocket/ga')
    ws.connect()
    ws.run_forever()
except KeyboardInterrupt:
    ws.close()
