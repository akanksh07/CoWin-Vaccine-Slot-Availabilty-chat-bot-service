# What am I trying to build?
<p align="justify">       Nationwide vaccination for COVID-19 for age group 18-45 years in India has started from 1st May 2021. However, the number of people seeking vaccination slots at nearby hospitals far exceeds the availablity. Today (as of 9th May), the existing system relies on individual users to log  into https://www.cowin.gov.in/ and hunt for free slots the odds of landing up on one of the convinient slots is very unlikely (2% chance :/). As a result, an individual has to intermittently  keep checking for slots all day which is a painstaking exercise. This pull based mechanism will delay our country's ability to get all it's citizens vaccinated. I am instead going to pivot this to a push based model where users get notified when a vaccination slot opens up at a prefered zipcode and thus ensuring that no available vaccination slots are left unclaimed.

# Why is this necessary?
  As of 1st May 2021 only 1.8M users<\p> [[1]](http://mohfw.gov.in/pdf/CumulativeCOVIDVaccinationCoverageReport1stMay2021.pdf) have been vaccinated as against the 2.7M users [[2]]( http://mohfw.gov.in/pdf/CumulativeCOVIDVaccinationCoverageReport30thApril2021.pdf) that got vaccinated as of April 30th. This shows that  we are either running out of vaccine doses or users are unable to find timely vaccination slots  at preferred locations and they are waiting it out. The former is getting fixed but the later will not, since it is limited by human tendancy. The intent of this effort is to change that behavior by notifying users as soon as a slot is available near them

[1] http://mohfw.gov.in/pdf/CumulativeCOVIDVaccinationCoverageReport1stMay2021.pdf 
<br>[2] http://mohfw.gov.in/pdf/CumulativeCOVIDVaccinationCoverageReport30thApril2021.pdf



# CoWin-Vaccine-Slot-Availabilty-Chat-Bot-service
![Chatbot - fast (1)](https://user-images.githubusercontent.com/36961513/131516236-e377bebd-46c3-413e-b3a6-1ae06a7fd4b1.gif)


# Cowin Public API Endpoint:
https://apisetu.gov.in/public/marketplace/api/cowin#/Appointment%20Availability%20APIs/findByPin

