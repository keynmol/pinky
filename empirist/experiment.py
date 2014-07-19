import md5
import argparse
import reporting

from pymongo import MongoClient
import datetime

#distinguish between experiment and observation! E.g. experiment name depends on the number of runs, and observation includes the number of current run!
 
class Experiment:
	client = MongoClient('mongodb://localhost:27017/')
	db=client.empirist
	trials=db.trials

	def __init__(self, description="", parse=True):
		self.parser=argparse.ArgumentParser(prog=self.__class__.__name__+".py", description=description)
		self.add_run=True
		self.runs=1
		self.options={}
		self.experiment_class=self.__class__.__name__
		self.report=reporting.Report()
		self.hashing=False
		self.streams={}
		self.data_folder="./data"
		self.namespace="Mess"
		self.trial_name=None


		self.configure()

		
		if parse:
			self.parse_options()

	def parse_options(self):
		if self.add_run:
			self.parser.add_argument("--runs", type=int, default=self.runs)
			self.report.addParameter(reporting.Param("Run",1))

		self.options=self.parser.parse_args()

		if len(self.streams)>1:
			self.report.addWriter(reporting.CSVWriter(self.data_folder+"/"+self.get_trial_name()+"-{stream}.csv"))
		else:
			self.report.addWriter(reporting.CSVWriter(self.data_folder+"/"+self.get_trial_name()+".csv"))

		for k in self.streams:
			self.report.addStream(k, self.streams[k])


	def set_state(self, param, new_value):
		self.report.parameters[param].setValue(new_value)

	def get_state(self,param):
		return self.report.parameters[param].value

	def add_state(self, param, value):
		self.report.addParameter(reporting.Param(param, value))

	def reset_state(self, param):
		self.report.parameters[param].reset()

	def change_state(self, param, increase=1):
		self.report.parameters[param].setValue(self.report.parameters[param]+increase)	 	

	# TODO: only one default stream!
	def data_stream(self, params, name="default"):
		self.streams[name]=reporting.DataStream(params)

	def observation(self, data, stream="default"):
		self.report.observation(stream, data)

  
	 
	def execute(self):		
		for self.run_num in range(self.options.runs):
			if self.add_run:
				self.set_state("Run", self.run_num)
				print "Run #"+str(self.run_num)
			self.pre_experiment() 
			self.experiment()
			self.post_experiment() 

		self.report.finish()
		self.set_success() 

	def set_success(self):
		Experiment.trials.update({"_id":self.trial_id},{"$set":{"__successful":1}})

	def get_trial_name(self):
		if self.trial_name==None:
			# optstring=[]
			# hs=vars(self.options)
			# for k in hs:
			# 	optstring.append(k+str(hs[k]))
			# return self.namespae+"-"+self.experiment_class+"_"+"_".join(optstring)
			options=vars(self.options)
			options['__timestamp']=datetime.datetime.utcnow()
			options['__namespace']=self.namespace
			options['__experiment']=self.experiment_class


			self.trial_id=Experiment.trials.insert(options)
			self.trial_name=self.namespace+"-"+self.experiment_class+"-"+str(self.trial_id)
		return self.trial_name

	@classmethod
	def get_trials(cls, namespace, experiment, params):
		s={'__namespace':namespace, '__experiment':experiment, '__successful':1}
		s.update(params)
		return Experiment.trials.find_one(s)


	def add_parameters(self, params):
		for p in params:
			self.add_parameter(p)

	def add_parameter(self,param, param_default=None):
		if param_default==None:
			self.parser.add_argument("--"+param, type=int)
		else:
			self.parser.add_argument("--"+param, type=type(param_default), default=param_default)

	def pre_experiment(self):
		pass

	def post_experiment(self):
		pass
