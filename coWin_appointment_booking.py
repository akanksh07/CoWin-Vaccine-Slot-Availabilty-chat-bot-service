# -*- coding: utf-8 -*-
"""
Created on Sun May  2 00:52:50 2021

@author: akanksh.belchada
"""

import mysql.connector
import re
import threading
import time
import requests
import datetime


from reportlab.pdfgen import canvas
from reportlab.platypus import Frame,Paragraph,Spacer
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


#Base class for other exceptions
class Error(Exception):
   pass

class invalidPinCodeError(Error):
    pass

class invalidAgeError(Error):
    pass

class invalidMobileError(Error):
    pass

def user_input():
    while True:
        try:
            mobile_no=input("Enter Mobile Number:")
            if len(mobile_no)!=10:
                raise invalidMobileError
        except invalidMobileError:
            print("Invalid Mobile number!")
            continue
         
        try:
            year_of_birth=input("Enter year of birth:")
            age=current_year-int(year_of_birth)
            if age > 101 or age <2:
                raise invalidAgeError
        except invalidAgeError:
            print("Invalid Age")    
            continue
                     
        try:   
            pincode=input("Enter PIN-CODE:")
            regex="^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$"
            p=re.compile(regex);
            if (pincode == ''):
                raise invalidPinCodeError
            m=re.match(p, pincode)
            if m is None:
                raise invalidPinCodeError
        except invalidAgeError:
            print("Invalid PIN-CODE!")  
            continue
          
        try:
            insert_values="INSERT INTO regisrty values ({},{},{},{},'None')".format(mobile_no,pincode,age,flag)
            mycursor.execute(insert_values) 
            mydb.commit()
        except Exception as e:
           print(e)

       
def generate_report(num,msg_body):
    pdf=canvas.Canvas(num+".pdf",pagesize=letter)
    flow_obj1=[]
    flow_obj2=[]
    flow_obj3=[]
    pdf.translate(cm,cm)

    frame1=Frame(10,660,540,80,showBoundary=1)
    frame2=Frame(10,590,540,60,showBoundary=1)
    frame3=Frame(10,0,540,580,showBoundary=1)
    
    styles=getSampleStyleSheet()
    text1="""<b><font size=26>  VACCINE SLOT AVAILABILITY REPORT</font></b><br></br><br></br> <br></br>"""
    t1=Paragraph(text1,style=styles["Normal"])
    flow_obj1.append(t1)
    flow_obj1.append(Spacer(6,6))
    text2="""<b>Generated on:</b>""" +" "+str(datetime.datetime.now())
    t2=Paragraph(text2,style=styles["Normal"])
    flow_obj1.append(t2)
    text3="""<b>Requested by:</b>""" +" "+num
    t3=Paragraph(text3,style=styles["Normal"])
    flow_obj1.append(t3) 
    frame1.addFromList(flow_obj1, pdf)


    text4="""<b>Disclaimer:</b><br></br> This service is developed using  <u>https://apisetu.gov.in/public/api/cowin</u>  to find appointment availabilty. These APIs are available for use by all third party applications. The appointment availability data is cached and may be upto 30 minutes old. 
             Book vaccination slots using  <u>https://selfregistration.cowin.gov.in/</u>."""
    t4=Paragraph(text4,style=styles["Normal"])
    flow_obj2.append(t4)
    frame2.addFromList(flow_obj2, pdf)
    
    text5="""<b><font >Vaccination Slots:</font></b><br></br>"""
    t5=Paragraph(text5,style=styles["Normal"])
    flow_obj3.append(t5)
    text6=msg_body
    t6=Paragraph(text6,style=styles["Normal"])
    flow_obj3.append(t6)
    frame3.addFromList(flow_obj3, pdf)
    
    pdf.showPage()
    pdf.save()
    print("Report Generated for ")        
    

def load_records():
        global pincode_list
        global age_list
        global flag_list
        global mobile_no_list
        
        mycursor = mydb.cursor()
        mycursor.execute(age_query)
        age_list=mycursor.fetchall()
        
        mycursor = mydb.cursor()
        mycursor.execute(pincode_query)
        pincode_list=mycursor.fetchall()

        mycursor = mydb.cursor()
        mycursor.execute(mobile_no_query)
        mobile_no_list=mycursor.fetchall()
        
        mycursor = mydb.cursor()
        mycursor.execute(flag_query)
        flag_list=mycursor.fetchall()
        
def update_response_msg(message,mobile_no):
    mycursor = mydb.cursor()
    update_response_msg="UPDATE regisrty SET FLAG=1, RESPONSE_MSG='{}' where MOBILE_NO='{}'".format(message,mobile_no)
    try:
        mycursor.execute(update_response_msg)
        mydb.commit()
    except Exception as e:
        print(e)
    
def drop_record(mobile_no):
     mycursor = mydb.cursor()
     drop_record_query="DELETE FROM regisrty WHERE MOBILE_NO='{}'".format(mobile_no)
     try:
        mycursor.execute(drop_record_query)
        mydb.commit()
        print("RECORD DROPPED!")   
     except Exception as e:
        print(e)
        
        
        
def update_requests_served_table(mobile_no,pinCode,age,message):
    mycursor = mydb.cursor()

    try:
        insert_record="INSERT INTO requests_served VALUES ('{}','{}','{}','{}')".format(mobile_no,pinCode,age,message)
        print(insert_record)
        mycursor.execute(insert_record) 
        mydb.commit()
        print("SERVED REQUEST TABLE UPDATED!")
    except Exception as e:
        print(e)
    
        
 
def check_appointments_api():
   try: 
       while True:
            time.sleep(20)   
            load_records()
            for pinCode,age,flag,mobile_no in zip(pincode_list,age_list,flag_list,mobile_no_list):    
                pinCode=pinCode[0]
                age=age[0]
                flag=flag[0]
                mobile_no=mobile_no[0]
                print(pinCode,age,flag,mobile_no)
                count = 0
                message=""
                for INP_DATE in date_str:
                    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}".format(pinCode, INP_DATE)
                    # print(URL)
                    response = requests.get(URL,headers=headers)
                    print(response)
                    if response.ok:
                        resp_json = response.json()
                        # print(json.dumps(resp_json, indent = 1))
                        
                        flag = False
                        if resp_json["centers"]:    
                                for center in resp_json["centers"]:
                                    for session in center["sessions"]:
                                        if ( session["min_age_limit"] <= age and session["available_capacity"]>=0 ) :
                                            
                                            message+="<br></br><b>Pin-code</b>: "
                                            message+=str(pinCode)+"<br></br>"
                                            message+="<b>Available on</b>: {}<br></br><b>Centre</b>: {},{}<br></br>".format(INP_DATE, center["name"],center["block_name"])
                                            message+="<b>Price</b>: {}<br></br>".format( center["fee_type"])
                                            message+="<b>Available Capacity</b>: <br></br>".format(session["available_capacity"])
                                            if(session["vaccine"] != ''):
                                                message+="<b>Vaccine</b>: {}<br></br>".format(session["vaccine"])
                                            
                                            count = count + 1
                                            print(message)
                                            
                    else:
                        message="BAD Response for {} on {}".format(pinCode,INP_DATE)
                        print(message)
                        update_response_msg(message,mobile_no)
                        
                if(count == 0):
                    
                    message="No Vaccination center avaliable for the given PIN-CODE!"
                    update_response_msg(message,mobile_no)
                else:
                    print("Vaccination Center available")
                    # update_response_msg(message,mobile_no)
                   
                    
                
                    update_requests_served_table(mobile_no,pinCode,age,message)
                    drop_record(mobile_no)
                    generate_report(mobile_no,message)
                    
            print("Completed...")
   except Exception as e:
        print(e)
            
       


if __name__=="__main__":
        #Connecting to MySQL Server
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        mydb = mysql.connector.connect(
          host="localhost",
          user='root',
          password='GaTech340/340',
        )
        
        mycursor = mydb.cursor()
        try:
            mycursor.execute("CREATE DATABASE IF NOT EXISTS  coWin_slot_request_registry_db")
        except Exception as e:
            print(e)
            
        show_db_query = "SHOW DATABASES"
        mycursor.execute(show_db_query)
        for db in mycursor:
            print(db)
               
        mydb = mysql.connector.connect(
          host="localhost",
          user='root',
          password='GaTech340/340',
          database="coWin_slot_request_registry_db"
        )
        
        mycursor = mydb.cursor()
        try:
            mycursor.execute("CREATE TABLE IF NOT EXISTS regisrty \
                             (MOBILE_NO VARCHAR(10),\
                             PINCODE INTEGER,\
                             AGE INTEGER,\
                             FLAG INTEGER,\
                             RESPONSE_MSG VARCHAR(1000),\
                             PRIMARY KEY (MOBILE_NO,PINCODE))")
        except Exception as e:
            print(e)
        
        mycursor = mydb.cursor()
        try:
            mycursor.execute("CREATE TABLE IF NOT EXISTS requests_served \
                             (MOBILE_NO VARCHAR(10) PRIMARY KEY, \
                              PINCODE INTEGER,\
                              AGE INTEGER,\
                              MESSAGE VARCHAR(1000))")
                                 
        except Exception as e:
            print(e)
        
        print(type(mycursor.execute("SHOW TABLES")))
        for x in mycursor:
          print(x)
        
     
        flag=0
        current_year=2021
        pincode_query="SELECT PINCODE FROM regisrty"
        age_query="SELECT AGE FROM regisrty"
        mobile_no_query="SELECT MOBILE_NO FROM regisrty"
        flag_query="SELECT FLAG FROM regisrty"
        
        
        pincode_list=[]
        age_list=[]
        mobile_no_list=[]
        flag_list=[]
        
        numdays = 7
        
        base = datetime.datetime.today()
        date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]
        date_str = [x.strftime("%d-%m-%Y") for x in date_list]


        user_input_process = threading.Thread(target  = user_input)
        check_appointments_api_process= threading.Thread(target = check_appointments_api, daemon = True)
        # process2_process = threading.Thread(target = process2, daemon = True)
        user_input_process.start()
        check_appointments_api_process.start()
       
        user_input_process.join()
        check_appointments_api_process.join()
        












#  SELECT table_schema "cowin_slot_request_registry_db",
#       ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) 'Size in MiB'
# FROM information_schema.tables
# GROUP BY table_schema;










