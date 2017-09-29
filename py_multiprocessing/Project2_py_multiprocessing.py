import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process, Lock, Queue, Value
import random, time
import sys

# mailfrom = str(raw_input('Enter your email: ')).lower().strip()
mailfrom = "divyapracticemail@gmail.com"
password = "Divya@123"

class EmailSender:
    """ Process to send email """
    def __init__(self):
        self.msg = None

    def mailsend(self, lock, queue,status):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            print("connection to gmail server successful")
            # password = str(raw_input('Enter password: ')).strip()
            server.login(mailfrom, password)
            print("login success")
            while (1):
                try:
                    lock.acquire()
                    if queue.qsize()!= 0:
                        msg = queue.get()
                        server.sendmail(msg['From'], msg['To'], msg.as_string())
                        print ("sent")
                        print(queue.qsize())
                        lock.release()
                        time.sleep(random.randrange(5, 10))
                    elif queue.qsize() == 0 and int(status.value) == 1:
                        print ("Queue looks empty")
                        sys.exit(0)
                except Exception as e:
                    print ("not sent" + str(e))
                    lock.release()

        except Exception as e:
            print ("connection error" + str(e))


class CsvReader:

    """ Process to read the csv file "maildoc.csv" """
    def __init__(self):
        self.msg = None

    def csv_dict_reader(self, lock, queue,status):
        with open("maildoc.csv") as mail_doc:
           reader = csv.DictReader(mail_doc, delimiter=',')
           for line in reader:
                mail_id = line["email"]
                mail_sub = line["subject"]
                mail_msg = line["message"]
                msg = MIMEMultipart()
                msg['From'] = mailfrom
                msg['To'] = mail_id
                msg['Subject'] = mail_sub
                msg.attach(MIMEText(mail_msg))
                lock.acquire()
                queue.put(msg)
                lock.release()
                time.sleep(random.randrange(5, 10))
           status.value = 1
           print "Reading part finished !!"


if __name__ == "__main__":
    lock = Lock()
    queue = Queue()
    status = Value('d')

    process_pool = []
    csvReader = CsvReader()
    emailSender = EmailSender()
    readerProcess = Process(target=csvReader.csv_dict_reader, args=(lock, queue,status))
    emailSender = Process(target=emailSender.mailsend, args=(lock, queue,status))
    readerProcess.start()
    emailSender.start()