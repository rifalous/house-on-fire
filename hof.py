import RPi.GPIO as GPIO
import time
import SimpleCV
import datetime
import requests
import ftplib
import mq

camera = SimpleCV.Camera(0)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)
GPIO.setup(20, GPIO.IN)
GPIO.setup(16, GPIO.IN)
GPIO.setup(04, GPIO.OUT)

ftp = ftplib.FTP("ftp.rifalous.id")
ftp.login("root@rifalous.id","d033e22ae348aeb5660fc2140aec35850c4da997")

device_id = "ID001"
count = 01

mq2 = mq.MQ()

while True:
  mtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
  ftime = datetime.datetime.now().strftime("%d-%M-%Y-%H-%M-%S")
  capturename = device_id + str(count) + mtime
  filename = capturename + ".jpg"

  perc = mq2.MQPercentage()
  print "LPG: %g ppm, CO: %g ppm, Smoke: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"])
  flame = mq2.adc.read(1)
# sensor1 = GPIO.input(21)
# sensor3 = GPIO.input(20)
  sensor1 = GPIO.HIGH
  sensor3 = GPIO.HIGH
  if ((sensor1 == GPIO.LOW) or (sensor3 == GPIO.LOW) or ( perc["GAS_LPG"] > 10.0) or (flame < 2500) and ( perc["GAS_LPG"] > 10.0)) :
    if sensor1 == GPIO.LOW:
      print "Sensor1 melihat api %s" % ( ftime )
    if sensor3 == GPIO.LOW:
      print "Sensor3 melihat api %s" % ( ftime )
    if flame < 2500:
      print "Sensor2 melihat api %s" % ( ftime )
    if perc["GAS_LPG"] > 10.0:
      print "Sensor Gas mendeteksi asap %s" % ( perc["GAS_LPG"] )
    GPIO.output(04, True)
    time.sleep(1)
    img = camera.getImage()
    img.save( filename )
    file = filename
    ftp.storbinary("STOR " + file, open(file, "rb"), 1024)
    url = 'https://rifalous.id/project/add_actionSensorData.php?device_id=%s&value=%s&image=%s&time=%s&status=%s&skala=%s&submit=Submit' % ( device_id,'Ada Api',file,mtime,'0',flame )
    result = requests.get(url)
    print url
    print "Status: Ada Api"
    print result.status_code
    print flame
    count += 1
  else:
    url = 'https://rifalous.id/project/add_actionSensorData.php?device_id=%s&value=%s&image=&time=%s&status=%s&skala=%s&submit=Submit' % ( device_id,'Tidak Ada Api',mtime,'0',flame )
    result = requests.get(url)
    print url
    print "Status: Tidak Ada Api"
    print result.status_code
    print flame
  time.sleep(1)
  GPIO.output(04, False)
