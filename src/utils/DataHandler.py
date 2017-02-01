# from config import config
import pyodbc
import json
from config import config
import base64

class DataHandler:
	def __init__(self):
		self.server = config["database"]["hostname"] 
		self.database = config["database"]["database"]
		self.username = config["database"]["username"]
		self.password = config["database"]["password"]
		# self.driver = '/usr/lib/x86_64-linux-gnu/libodbc.so'
		self.driver = '{ODBC Driver 13 for SQL Server}'
		self.connstr = 'DRIVER='+self.driver+';PORT=1433;SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+self.password
		#print "Try to connect with string: " + self.connstr
		self.conn = pyodbc.connect(self.connstr)
		#print "Connecting to server ..."
		self.jobtablename = "jobs-%s" %  config["clusterId"]

		self.CreateTable()

	def CreateTable(self):
		
		sql = """
		if not exists (select * from sysobjects where name='%s' and xtype='U')
			CREATE TABLE [dbo].[%s]
			(
			    [id]        INT          IDENTITY (1, 1) NOT NULL,
			    [jobId] NTEXT   NOT NULL,
			    [jobName]         NTEXT NOT NULL,
			    [userName]         NTEXT NOT NULL,
				[jobStatus]         NTEXT NOT NULL DEFAULT 'queued',
				[jobType]         NTEXT NOT NULL,
			    [jobDescriptionPath]  NTEXT NULL,
				[jobDescription]  NTEXT NULL,
				[jobTime] DATETIME     DEFAULT (getdate()) NOT NULL,
			    [endpoints] NTEXT NULL, 
			    [errorMsg] NTEXT NULL, 
			    [jobParams] NTEXT NOT NULL, 
			    [jobMeta] NTEXT NULL, 
			    [jobLog] NTEXT NULL, 
			    PRIMARY KEY CLUSTERED ([id] ASC)
			)
			""" % (self.jobtablename,self.jobtablename)

		cursor = self.conn.cursor()
		cursor.execute(sql)
		self.conn.commit()
		cursor.close()



	def AddJob(self, jobParams):
		try:
			sql = """INSERT INTO [%s] (jobId, jobName, userName, jobType,jobParams ) VALUES (?,?,?,?,?)""" % self.jobtablename
			cursor = self.conn.cursor()
			jobParam = base64.b64encode(json.dumps(jobParams))
			cursor.execute(sql, jobParams["jobId"], jobParams["jobName"], jobParams["userName"], jobParams["jobType"],jobParam)
			self.conn.commit()
			cursor.close()
			return True
		except:
			return False

    


	def GetJobList(self, userName):
		cursor = self.conn.cursor()
		query = "SELECT [jobId],[jobName],[userName], [jobStatus], [jobType], [jobDescriptionPath], [jobDescription], [jobTime], [endpoints], [jobParams],[errorMsg] ,[jobMeta] FROM [%s] " % self.jobtablename
		if userName != "all":
			query += " where cast([userName] as nvarchar(max)) = N'%s'" % userName
		cursor.execute(query)
		ret = []
		for (jobId,jobName,userName, jobStatus, jobType, jobDescriptionPath, jobDescription, jobTime, endpoints, jobParams,errorMsg, jobMeta) in cursor:
			record = {}
			record["jobId"] = jobId
			record["jobName"] = jobName
			record["userName"] = userName
			record["jobStatus"] = jobStatus
			record["jobType"] = jobType
			record["jobDescriptionPath"] = jobDescriptionPath
			record["jobDescription"] = jobDescription
			record["jobTime"] = jobTime
			record["endpoints"] = endpoints
			record["jobParams"] = jobParams
			record["errorMsg"] = errorMsg
			record["jobMeta"] = jobMeta
		  	ret.append(record)
		cursor.close()

		return ret


	def GetJob(self,jobId):
		cursor = self.conn.cursor()
		query = "SELECT [jobId],[jobName],[userName], [jobStatus], [jobType], [jobDescriptionPath], [jobDescription], [jobTime], [endpoints], [jobParams],[errorMsg] ,[jobMeta]  FROM [%s] where cast([jobId] as nvarchar(max)) = N'%s' " % (self.jobtablename,jobId)
		cursor.execute(query)
		ret = []
		for (jobId,jobName,userName, jobStatus, jobType, jobDescriptionPath, jobDescription, jobTime, endpoints, jobParams,errorMsg, jobMeta) in cursor:
			record = {}
			record["jobId"] = jobId
			record["jobName"] = jobName
			record["userName"] = userName
			record["jobStatus"] = jobStatus
			record["jobType"] = jobType
			record["jobDescriptionPath"] = jobDescriptionPath
			record["jobDescription"] = jobDescription
			record["jobTime"] = jobTime
			record["endpoints"] = endpoints
			record["jobParams"] = jobParams
			record["errorMsg"] = errorMsg
			record["jobMeta"] = jobMeta
		  	ret.append(record)
		cursor.close()

		return ret


	def KillJob(self,jobId):
		try:
			sql = """update [%s] set jobStatus = 'killing' where cast([jobId] as nvarchar(max)) = N'%s' """ % (self.jobtablename,jobId)
			cursor = self.conn.cursor()
			cursor.execute(sql)
			self.conn.commit()
			cursor.close()
			return True
		except:
			return False


	def GetPendingJobs(self):
		cursor = self.conn.cursor()
		query = "SELECT [jobId],[jobName],[userName], [jobStatus], [jobType], [jobDescriptionPath], [jobDescription], [jobTime], [endpoints], [jobParams],[errorMsg] ,[jobMeta] FROM [%s] where cast([jobStatus] as nvarchar(max)) <> N'error' and cast([jobStatus] as nvarchar(max)) <> N'failed' and cast([jobStatus] as nvarchar(max)) <> N'finished' and cast([jobStatus] as nvarchar(max)) <> N'killed' " % (self.jobtablename)
		cursor.execute(query)
		ret = []
		for (jobId,jobName,userName, jobStatus, jobType, jobDescriptionPath, jobDescription, jobTime, endpoints, jobParams,errorMsg, jobMeta) in cursor:
			record = {}
			record["jobId"] = jobId
			record["jobName"] = jobName
			record["userName"] = userName
			record["jobStatus"] = jobStatus
			record["jobType"] = jobType
			record["jobDescriptionPath"] = jobDescriptionPath
			record["jobDescription"] = jobDescription
			record["jobTime"] = jobTime
			record["endpoints"] = endpoints
			record["jobParams"] = jobParams
			record["errorMsg"] = errorMsg
			record["jobMeta"] = jobMeta
		  	ret.append(record)
		cursor.close()

		return ret		


	def SetJobError(self,jobId,errorMsg):
		try:
			sql = """update [%s] set jobStatus = 'error', [errorMsg] = ? where cast([jobId] as nvarchar(max)) = N'%s' """ % (self.jobtablename,jobId)
			cursor = self.conn.cursor()
			cursor.execute(sql,errorMsg)
			self.conn.commit()
			cursor.close()
			return True
		except:
			return False		


	def UpdateJobTextField(self,jobId,field,value):
		try:
			sql = """update [%s] set [%s] = ? where cast([jobId] as nvarchar(max)) = N'%s' """ % (self.jobtablename,field, jobId)
			cursor = self.conn.cursor()
			cursor.execute(sql,value)
			self.conn.commit()
			cursor.close()
			return True
		except:
			return False


	def GetJobTextField(self,jobId,field):
		cursor = self.conn.cursor()
		query = "SELECT [jobId], [%s] FROM [%s] where cast([jobId] as nvarchar(max)) = N'%s' " % (field, self.jobtablename,jobId)
		cursor.execute(query)
		ret = None

		for (jobId, value) in cursor:
			ret = value
		cursor.close()

		return ret

####################################################################################################################			


	def GetVersion(self):
		cursor = self.conn.cursor()
		query = ("select @@VERSION")
		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		return row; 


	def ChangeStatus(self,jobId, newStatus):
		pass
	def Close(self):
		self.conn.close()

if __name__ == '__main__':
	TEST_INSERT_JOB = False
	TEST_QUERY_JOB_LIST = False
	CREATE_TABLE = True
	dataHandler = DataHandler()
	
	if TEST_INSERT_JOB:
		jobParams = {}
		jobParams["id"] = "dist-tf-00001"
		jobParams["job-name"] = "dist-tf"
		jobParams["user-id"] = "hongzl"
		jobParams["job-meta-path"] = "/dlws/jobfiles/***"
		jobParams["job-meta"] = "ADSCASDcAE!EDASCASDFD"
		
		dataHandler.AddJob(jobParams)
	
	if TEST_QUERY_JOB_LIST:
		print dataHandler.GetVersion()

	if CREATE_TABLE:
		dataHandler.CreateTable()

