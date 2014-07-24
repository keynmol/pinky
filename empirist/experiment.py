import argparse
import reporting
import datetime
import agent

#distinguish between experiment and observation! E.g. experiment name depends on the number of runs, and observation includes the number of current run!
 
class Experiment:
	def __init__(self, agent_str="localhost:5050", parse=True):
		self.parser=argparse.ArgumentParser(prog=self.__class__.__name__+".py")
		self.add_run=True
		self.runs=1
		self.options={}
		self.experiment_class=self.__class__.__name__
		self.report=reporting.Report()
		self.hashing=False
		self.streams={}
		self.project="Mess"
		self.trial_name=None

		host,port=agent_str.split(":")
		self.agent=agent.Agent(host,port)
		self.data_folder=self.agent.local_cache_folder



		self.configure()

		
		if parse:
			self.parse_options()

	def parse_options(self):
		if self.add_run:
			self.parser.add_argument("--runs", type=int, default=self.runs)
			self.report.addParameter(reporting.Param("Run",1))

		self.options=self.parser.parse_args()


		self.report.addWriter(reporting.CSVWriter(self.data_folder+"/"+self.get_trial_name()+"-{stream}.csv"))

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
		self.agent.set_success() 
		self.agent.upload_data(self.report.streamsNames())    
 
	def get_trial_name(self):
		if self.trial_name==None:
			options=vars(self.options)
			options['__timestamp']=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z"))
			options['__project']=self.project
			options['__experiment']=self.experiment_class


			self.trial_id=self.agent.create_trial(options)
			self.trial_name=str(self.trial_id)
		return self.trial_name

	# @classmethod
	# def get_trials(cls, project, experiment, params):
	# 	s={'__project':project, '__experiment':experiment, '__successful':1}
	# 	s.update(params)
	# 	return Experiment.trials.find_one(s)


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
