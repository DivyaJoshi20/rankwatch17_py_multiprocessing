import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process, Lock, Queue, Value
import random, time
import sys


class EmailSender:
    """ Process to send email """
    def __init__(self):
        self.msg = None

    def mailsend(self, lock, queue,status, mailfrom, password):
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
                        print ("Email sent")
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

    def csv_dict_reader(self, lock, queue,status, mailfrom):
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


def initialize_username_password():
    """
    This function is used to set mailfrom and password from csv file name user_info.csv.
    Incase there is multiple entries it will take the last one
    """

    user_info_dict = {}
    with open("user_info.csv") as user_info:
        reader = csv.DictReader(user_info, delimiter = ',')
        for line in reader:
            user_info_dict['mailfrom'] = line['username']
            user_info_dict['password'] = line['password']

    return user_info_dict


if __name__ == "__main__":
    user_info_dict = initialize_username_password()
    lock = Lock()
    queue = Queue()
    status = Value('d')

    process_pool = []
    csvReader = CsvReader()
    emailSender = EmailSender()
    readerProcess = Process(target=csvReader.csv_dict_reader, args=(lock, queue,status, user_info_dict['mailfrom']))
    emailSender = Process(target=emailSender.mailsend, args=(lock, queue,status,
                                                             user_info_dict['mailfrom'], user_info_dict['password']))
    readerProcess.start()
    emailSender.start()
