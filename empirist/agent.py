import requests
import json
import datetime
import os.path

class Agent:
	def __init__(self, host, port):
		self.url="http://{}:{}".format(host, port)
		self.server=requests.get(self.url+"/server").text
		self.local_cache_folder=requests.get(self.url+"/local_cache").text

	def create_trial(self, params):
		self.trial_id=requests.post(self.server+"create_trial", data=json.dumps(params)).text
		return self.trial_id

	def set_success(self):
			requests.post(self.server+'set_success', {"trial_id": self.trial_id})

	def upload_data(self, streams_names):
		for stream in streams_names:
			datafile=self.local_cache_folder+"/{}-{}.csv".format(self.trial_id, stream)
			if os.path.isfile(datafile):
				files={"file": open(datafile,'r')}
				params={"data_stream": stream, "trial_id": self.trial_id}

				requests.post(self.server+"upload_datastream", params, files=files)


# a=Agent("localhost",5050)

# curtime=datetime.datetime.now()
# trial_id=a.create_trial({"__project":"Mess", "__experiment":"PythonExperiment", "__timestamp":str(curtime.strftime("%Y-%m-%d %H:%M:%S %z"))})
# f=open("/tmp/empirist-cache/{}-default.csv".format(trial_id), "w")
# f.write("asdadasd")
# f.close()
# a.upload_data(["default"])
# a.set_success()
