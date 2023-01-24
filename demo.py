import mysql.connector
from flask import Flask, request ,render_template
import random
import string
from math import radians, sin, cos, sqrt, atan2
import smtplib
from validate_email_address import validate_email
import requests,json

app = Flask(__name__,template_folder = 'template')


@app.route('/')
def home():
  return render_template('helperNewUi.html')

@app.route('/store_inputs', methods=['POST'])
def store_inputs():
  req = request.get_json()
  JobTitle = req['JobTitle']
  Address = req['Address']
  Contact = req['Contact']
  Email = req['Email']
  JobDescription = req['JobDescription']
  NumberVacancy = req['NumberVacancy']
  latitude = req['latitude']
  longitude = req['longitude']
  
  ShowData = 1

  conn = mysql.connector.connect(user='bdb28d22e39e92', password='3b5dcb81', host='us-cdbr-east-06.cleardb.net', database='heroku_f1be7c287b787df')
  cursor = conn.cursor()
  query = 'SELECT UniqueCode FROM jobslist'
  cursor.execute(query)
  AllUiqueCode = cursor.fetchall()
  cursor.close()
  conn.close()

  converted_list = [item[0] for item in AllUiqueCode]

  while True:
    UniqueCode = generate_code()
    if UniqueCode not in converted_list:
        break

    
  CheckIfMailSend = sendUniqueCode(Email,UniqueCode,JobTitle,Address,Contact,JobDescription,NumberVacancy)
  if CheckIfMailSend:
    conn = mysql.connector.connect(user='bdb28d22e39e92', password='3b5dcb81', host='us-cdbr-east-06.cleardb.net', database='heroku_f1be7c287b787df')
    cursor = conn.cursor()
    query = 'INSERT INTO jobslist (JobTitle, Address, Contact, Email, JobDescription, ''NumberofVacancy'',UniqueCode,ShowData,latitude,longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(query, (JobTitle, Address, Contact, Email, JobDescription, NumberVacancy,UniqueCode,ShowData,latitude,longitude))
    conn.commit()
    cursor.close()
    conn.close()
    returnMessage = True
    return {'returnMessage' : returnMessage}
  else:
    returnMessage = False
    return {'returnMessage' : returnMessage}
    

@app.route('/DeleteJob', methods=['POST'])
def DeleteJob():
  req = request.get_json()
  UniqueCode = str(req['UniqueCode'])
  
  conn = mysql.connector.connect(user='bdb28d22e39e92', password='3b5dcb81', host='us-cdbr-east-06.cleardb.net', database='heroku_f1be7c287b787df')
  cursor = conn.cursor()

  query = 'SELECT JobTitle,Address,Contact,JobDescription,NumberofVacancy from jobslist where UniqueCode = (%s) and ShowData = 1'
  cursor.execute(query,(UniqueCode,))
  DeleteJobEntry = cursor.fetchall()

  query = 'UPDATE jobslist SET ShowData = 0 WHERE UniqueCode = (%s)'
  cursor.execute(query,(UniqueCode,))
  conn.commit()
  queryToGetData = 'SELECT JobTitle,Address,Contact, DATE_FORMAT(PostedDate, "%Y-%m-%d"),JobDescription,NumberofVacancy,latitude,longitude FROM jobslist WHERE ShowData = 1'
  cursor.execute(queryToGetData)
  rows = cursor.fetchall()

  query = 'SELECT COUNT(*) FROM jobslist WHERE ShowData = 1'
  cursor.execute(query)
  count = cursor.fetchone()[0]

  cursor.close()
  conn.close()
  if len(DeleteJobEntry)!=0:
    StrdeletedJobEntryAlert = 'Job Title :' + str(DeleteJobEntry[0][0]) + ', Address :' +str(DeleteJobEntry[0][1])+', Contact :'+str(DeleteJobEntry[0][2])+', Job Description :'+str(DeleteJobEntry[0][3])+', Number of Vacancy :'+str(DeleteJobEntry[0][4])+' ; Is deleted Successfully.'
  else:
    StrdeletedJobEntryAlert = 'There is no job record found for this '+UniqueCode+' code.'  
  
  return {'rows': rows,'StrdeletedJobEntryAlert': StrdeletedJobEntryAlert, 'count': count}


@app.route('/get_jobs', methods=['POST'])
def get_jobs():
  req = request.get_json()

  conn = mysql.connector.connect(user='bdb28d22e39e92', password='3b5dcb81', host='us-cdbr-east-06.cleardb.net', database='heroku_f1be7c287b787df')
  cursor = conn.cursor()
  query = 'SELECT JobTitle,Address,Contact, DATE_FORMAT(PostedDate, "%Y-%m-%d"),JobDescription,NumberofVacancy,latitude,longitude FROM jobslist WHERE ShowData = 1'
  cursor.execute(query)
  rows = cursor.fetchall()

  query = 'SELECT COUNT(*) FROM jobslist WHERE ShowData = 1'

  cursor.execute(query)
  count = cursor.fetchone()[0]

  cursor.close()
  conn.close()


  if(req['jobtype']=='allJobs'):
    return {'rows': rows , 'count': count}
  else:
    lat = float(req['latitude'])
    lon = float(req['longitude'])
    rows = sorted(rows, key=lambda x: get_distance(lat, lon, x[6], x[7]))
    return {'rows': rows , 'count': count}  
    

def get_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    # Calculate the differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Use the Haversine formula to calculate the distance
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Return the distance in kilometers
    return 6371 * c


def sendUniqueCode(Email,UniqueCode,JobTitle,Address,Contact,JobDescription,NumberVacancy):


  url = "https://api.zerobounce.net/v2/validate"
  api_key = "537d0106aead4110a6a9b0eb5073036d"
  ip_address = "" #ip_address can be blank
    
  params = {"email": Email, "api_key": api_key, "ip_address":ip_address}
    
  response = requests.get(url, params=params)
    
   # Print the returned json
  validEmailCheck = json.loads(response.content)['status']

  if validEmailCheck =='valid':
    server = smtplib.SMTP('smtp.gmail.com',587)

    # Connect to the server
    server.connect("smtp.gmail.com",587)

    # Start TLS encryption
    server.starttls()  
    
    # Login to the email account
    server.login("helperjob86@gmail.com","pbnetypyocpxnxvs")

    # Send the email
    to = Email
    subject = "Unique Helper Code"
    body = "This is your Unique Helper Code " + UniqueCode + " . For Job :" +JobTitle+ ", Address :" +Address+ ", Contact :" +Contact+ ", Job Description :" +JobDescription+", Number of Vacancy :" +NumberVacancy+". Only Use when you want to delete your job posting"
    msg = f"Subject: {subject}\n\n{body}"

    send_status = server.sendmail("helperJob86@gmail.com",to,msg)
    server.quit()
    return True
  else:
    return False
      

def generate_code():
  code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
  return code  

if __name__ == '__main__':
  app.run(debug=True,threaded=True)
