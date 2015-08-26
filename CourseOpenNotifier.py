import json, requests, operator
import sys
from time import sleep
from twilio.rest import TwilioRestClient 
#Variables used for the request url
umdIoBaseUrl = "http://api.umd.io/v0/"
method="courses"
semester = 201508
dept_id = "CMSC"


def GetCoursesInSpecifiedDepartment(department_id):
	fullRequestUrl=umdIoBaseUrl+method+"?semester={}&dept_id={}".format(semester,dept_id)
	response = requests.get(fullRequestUrl)
	return response.json()

def CheckIf400LevelCourse(jsonOfCourse,dept_id):
	
	courseId= jsonOfCourse['course_id']
	IndexOfFirstDigitOfCourseNumber = courseId.index(dept_id)+len(dept_id)
	firstDigitOfCourseNumber=courseId[IndexOfFirstDigitOfCourseNumber]
	
	if(firstDigitOfCourseNumber=="4"):
		return courseId

def GetAvailableSections(course):
	if(course!=None):
		fullRequestUrl=umdIoBaseUrl+method+"?course_id={}".format(course)
		courseJson = requests.get(fullRequestUrl).json()[0]
		sections = courseJson['sections']

		return sections
	else:
		return
def CheckOpenSeats(section_id):
	coursesAndSections= method+"/sections"
	fullRequestUrl = umdIoBaseUrl+ coursesAndSections+"?section_id={}".format(section_id)
	sectionJson = requests.get(fullRequestUrl).json()[0]
	numOpenSeats = sectionJson['open_seats']
	if(int(numOpenSeats) >0):
		return section_id
def RemoveNoneEntries(array):
	newArray = []
	for element in array:
		if(element!= None):
			newArray.append(element)
	return newArray
def sendTextAlert(availableSection,fromNumber,toNumber,client):
	client.messages.create(
		body="A class has opened up in the section: "+availableSection,
		to=toNumber,
		from_=fromNumber
		
	)

def driver():

	jsonOfAllCoursesInDept = GetCoursesInSpecifiedDepartment("CMSC")
	listOf400LevelClasses=[CheckIf400LevelCourse(jsonOfIndividualCourse, dept_id) for jsonOfIndividualCourse in jsonOfAllCoursesInDept]

	listOfSections=RemoveNoneEntries([GetAvailableSections(course) for course in listOf400LevelClasses])
	listOfSections=reduce(operator.add, listOfSections)
	dictOfAvailableSections = {}
	ACCOUNT_SID = raw_input("Please enter your twilio ACCOUNT_SID value: \n")
	AUTH_TOKEN = raw_input("Please enter your twilio AUTH_TOKEN value \n")
	client = TwilioRestClient(ACCOUNT_SID,AUTH_TOKEN)
	fromNumber = raw_input("Enter the number associated with your twilio account(e.g. +11234567891): \n")
	toNumber= raw_input("Enter your phone number that you would like to be notified at(e.g. +11234567891): \n")
	while(True):
		for section in listOfSections:
			availableSection = CheckOpenSeats(section)
			if(availableSection !=None):
				print availableSection
				if ( availableSection not in dictOfAvailableSections):
					dictOfAvailableSections[availableSection] = True
					sendTextAlert(availableSection,fromNumber,toNumber,client)
		sleep(5)

	print listOfSections


driver()

