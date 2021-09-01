# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
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

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os

account_sid = 'AC35e00c5a7c7f64129cc4001caecedbe5'#os.environ['TWILIO_ACCOUNT_SID']
auth_token ='5562567f47cd41a65a0bdc92e31b9b66' #os.environ['TWILIO_AUTH_TOKEN']
app = Flask(__name__)



@app.route("/")
def hello():
   return 

@app.route("/sms", methods=['POST'])
def sms_reply():
    number=request.form.get("From")
    number=number.replace("whatsapp:","")
    mobile_no=number
    greet="""Hello,
    
This is a bot service for tracking the availability of *Covid-19 Vaccination Slots* in India 🇮🇳 We can assist you by notifying slots available upto next 2 days.
    
_To request service, kindly enter your pincode and year of birth in the format as illustrated:_
    
*411001 1997*
 (PIN)    (YEAR) 
    
You'll be notified once slots are available!
    
Regards,
Akanksh """

    msg = request.form.get('Body')
    print("CONSOLE: "+msg)
    string=msg[:3]
    reg="^[0-9]{3}"
    p0=re.compile(reg);
    m0=re.match(p0,string)
    if m0 is None or string == '' :
        resp = MessagingResponse()
        resp.message(greet)
        return str(resp)
    else:
        pincode_year=msg
        regex="^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}\\s{1}(?:19|20)\d\d$"
        p=re.compile(regex);
        m=re.match(p, pincode_year)
        if m is None or pincode_year == '' :
            alert="""❗Invalid input
Please enter your *pincode* and *year of birth* in below format only:
*411001 1997*
   (PIN)  (YEAR)"""
            resp = MessagingResponse()
            resp.message(alert)
            return str(resp)
        else:
            pincode_year=pincode_year.split()
            pinCode=pincode_year[0]
            year=pincode_year[1]
            
            current_year=2021 #the worst
            age=current_year-int(year)
            if age > 101 or age <2:
                resp = MessagingResponse()
                resp.message(alert)
                return str(resp)
            #CHECK IN DB IF ALREADY EXIST
   
            mycursor = mydb.cursor()
            try:
                if_exists="SELECT IF( EXISTS( SELECT * FROM br0rnt7zaddut2deaqfi.regisrty \
                        WHERE MOBILE_NO='{}' and PINCODE={}), 1, 0)".format(mobile_no[3:],pinCode)
                # print("--------------")
                # print(if_exists)
                mycursor.execute(if_exists)
                result=mycursor.fetchall()
                found=(result[0][0])    
                
            except Exception as e:
                   print(e)
            if found==1:
                #YES:>>Send response already requested
                found_msg="""✅Your request has already been queued.
💬Wait to hear back from us."""
                resp = MessagingResponse()
                resp.message(found_msg)
                return str(resp)
            else:
                 #NO:>>Send response Queued 
                not_found_msg="""✅Your request is being queued. 
💬You'll be notified once vaccination slots for the Pin-code:"""+" *{}* ".format(pinCode)+""" and age group are available."""
                print("New entry for {} + {} added in coWin_slot_request_registry_db.registry ".format(mobile_no,pinCode))
                resp = MessagingResponse()
                resp.message(not_found_msg)
                ##Add to DB code
                mycursor = mydb.cursor()
                try:
                    insert_values="INSERT INTO regisrty values ({},{},{},{},'None')".format(mobile_no[3:],pinCode,age,0)
                    mycursor.execute(insert_values) 
                    mydb.commit()
                except Exception as e:
                   print(e)
                  
                return str(resp)
               
                
def send_availability_report(mobile_no):
        # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
   
    client = Client(account_sid, auth_token)
    
    message = client.messages \
        .create(
             media_url=['https://b589-129-110-241-33.ngrok.io/{}.pdf'.format(mobile_no)],
             from_='whatsapp:+14155238886',
             to='whatsapp:+91{}'.format(mobile_no)
         )
    print("here")
    print(message.sid)
    print("here1")



def generate_report(num,message):
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
    #frame3.addFromList(flow_obj3, pdf)
    
    
    # text6=message
    # t6=Paragraph(text6,style=styles["Normal"])
    # flow_obj3.append(t6)
    # frame3.addFromList(flow_obj3, pdf)
    
    # pdf.showPage()
        # pdf.showPage()
    message=message.split("**")

    
    print(message)
    n=len(message)
    print(len(message),n)
    content=""
    for i in range(0,5,5):
         try: 
           if(i<5):
               content+=message[i]
           if(i+1<5):
               content+=message[i+1]
           if(i+2<5):
               content+=message[i+2]
           if(i+3<5):
               content+=message[i+3]
           if(i+4<5):
               content+=message[i+4]
           if(i+5<5):    
               content+=message[i+5]
         except Exception as e:
             print(e)
   
    text6=content
    t6=Paragraph(text6,style=styles["Normal"])
    flow_obj3.append(t6)
    frame3.addFromList(flow_obj3, pdf)
    pdf.showPage()
 
    
    
    
    
    
    if n>5:
        for i in range(5,len(message),7):
          
            content=""
            frame3=Frame(40,20  ,540,740,showBoundary=1)
            flow_obj3=[]
            
            frame3.addFromList(flow_obj3, pdf)
            try: 
                if(i<n):
                    content+=message[i]
                if(i+1<n):
                    content+=message[i+1]
                if(i+2<n):
                    content+=message[i+2]
                if(i+3<n):
                    content+=message[i+3]
                if(i+4<n):
                    content+=message[i+4]
                if(i+5<n):    
                    content+=message[i+5]
                if(i+6<n):
                    content+=message[i+6]
            except Exception as e:
             print(e)
      
            # print(content)
            text6=content
            t6=Paragraph(text6,style=styles["Normal"])
            flow_obj3.append(t6)
            frame3.addFromList(flow_obj3, pdf)
            pdf.showPage()
           
       #  frame3.addFromList(flow_obj3, pdf)
       
       #  pdf.showPage()
       #  pdf.showPage()
       #  pdf.showPage()
       #  pdf.showPage()
    pdf.save()
            

    print("Report Generated !!!!! ")        
    

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
        
def update_response_msg(message,mobile_no,pinCode):
    mycursor = mydb.cursor()
    update_response_msg="UPDATE regisrty SET FLAG=1, RESPONSE_MSG='{}' where MOBILE_NO='{}' AND PINCODE={}".format(message,mobile_no,pinCode)
    try:
        mycursor.execute(update_response_msg)
        mydb.commit()
    except Exception as e:
        print(e)
    
def drop_record(mobile_no,pinCode):
     mycursor = mydb.cursor()
     drop_record_query="DELETE FROM regisrty WHERE MOBILE_NO='{}' AND PINCODE={}".format(mobile_no,pinCode)
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
            time.sleep(25)   
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
                    print(URL)
                    response = requests.get(URL,headers=headers)
                    print(response)
                    if response.ok:
                        resp_json = response.json()
                        # print(json.dumps(resp_json, indent = 1))
                        
                        flag = False
                        if resp_json["centers"]:    
                                for center in resp_json["centers"]:
                                    for session in center["sessions"]:
                                        if ( session["min_age_limit"] <= age and session["available_capacity"]>0 ) :
                                            
                                            message+="<br></br><b>Pin-code</b>: "
                                         
                                            message+=str(pinCode)+"<br></br>"
                                  
                                            message+="<b>Available on</b>: {}<br></br>".format(INP_DATE)
                              
                                            message+="<b>Centre</b>: {}<br></br>".format( center["name"])
                                      
                                            message+="<b>Block</b>: {}<br></br>".format(center["block_name"])
                                    
                                            message+="<b>Price</b>: {}<br></br>".format( center["fee_type"])
                                   
                                            message+="<b>Available Capacity</b>:<b>{}</b><br></br>".format(session["available_capacity"])
                                            print(message)
                                            if(session["vaccine"] != ''):
                                                message+="<b>Vaccine</b>: {}<br></br>".format(session["vaccine"])
                                            message+="**"
                                            
                                            count +=1
                                            print(message)
                                            
                    else:
                        message="BAD Response for {} on {}".format(pinCode,INP_DATE)
                        print(message)
                        update_response_msg(message,mobile_no)
                        
                if(count == 0):
                    
                    message="‼️ No Vaccination centers avaliable for the given Pin-code: *{}* and age group. Please try another Pin-code!".format(pinCode)
                    client = Client(account_sid, auth_token)
                    
                    message = client.messages \
                        .create(
                             body="‼️ No Vaccination centers avaliable for the given Pin-code: *{}* and age group. Please try another Pin-code!".format(pinCode),
                             from_='whatsapp:+14155238886',
                             to='whatsapp:+91{}'.format(mobile_no)
                         )
                   
                    print(message.sid +"for No Vaccination Message!!")
                    update_response_msg(message,mobile_no,pinCode)
                    drop_record(mobile_no,pinCode)
                    
                    
                else:
                    print("Vaccination Center available")
                    # update_response_msg(message,mobile_no,pinCode)
                   
                    
                
                    update_requests_served_table(mobile_no,pinCode,age,message)
                    drop_record(mobile_no,pinCode)
                    generate_report(mobile_no,message)
                    send_availability_report(mobile_no)
                    
            print("Completed...")
   except Exception as e:
        print(e)
            
       


if __name__=="__main__":
        #Connecting to MySQL Server
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        mydb = mysql.connector.connect(
             host="br0rnt7zaddut2deaqfi-mysql.services.clever-cloud.com",
          user='uytzwjcmm7jaxjr8',
          password='ldbHuvOHqhf0OJ4S9sne'
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
          host="br0rnt7zaddut2deaqfi-mysql.services.clever-cloud.com",
          user='uytzwjcmm7jaxjr8',
          password='ldbHuvOHqhf0OJ4S9sne',
          database="br0rnt7zaddut2deaqfi"
        )
        
        mycursor = mydb.cursor()
        try:
            mycursor.execute("CREATE TABLE IF NOT EXISTS regisrty \
                             (MOBILE_NO VARCHAR(10),\
                             PINCODE INTEGER,\
                             AGE INTEGER,\
                             FLAG INTEGER,\
                             RESPONSE_MSG VARCHAR(5000),\
                             PRIMARY KEY (MOBILE_NO,PINCODE))")
        except Exception as e:
            print(e)
        
        mycursor = mydb.cursor()
        try:
            mycursor.execute("CREATE TABLE IF NOT EXISTS requests_served \
                             (MOBILE_NO VARCHAR(10) , \
                              PINCODE INTEGER,\
                              AGE INTEGER,\
                              MESSAGE VARCHAR(5000))")
                                 
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


       
        check_appointments_api_process= threading.Thread(target = check_appointments_api, daemon = True)
        # process2_process = threading.Thread(target = process2, daemon = True)
       
        check_appointments_api_process.start()
        app.run(debug=True)
        check_appointments_api_process.join()
        




#   SELECT table_schema "br0rnt7zaddut2deaqfi",
#       ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) 'Size in MiB'
# FROM information_schema.tables
# GROUP BY table_schema;











