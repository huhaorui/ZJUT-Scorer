import sys

import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def sendmail(msg):
    mail_host = "smtp.qq.com"
    mail_user = "XX@XX.XX"
    mail_pass = "XXXX"
    sender = 'XX@XX.XX'
    receivers = ['XX@XX.XX']
    message = MIMEText(msg)
    message['From'] = Header('S-Server<score@zjut.edu.cn>', 'utf-8')
    message['To'] = Header('XX@XX.XX<XX@XX.XX>', 'utf-8')
    message['Subject'] = Header('出成绩了！', 'utf-8')
    try:
        SMTPObj = smtplib.SMTP_SSL(mail_host, 465)
        SMTPObj.ehlo()
        SMTPObj.login(mail_user, mail_pass)
        SMTPObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


if __name__ == '__main__':
    headers = {
        "Host": "api.jh.zjut.edu.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/79.0.3945.88 Safari/537.36 Edg/79.0.309.54 "
    }
    # TODO
    url = "http://api.jh.zjut.edu.cn/student/scoresZf.php?username=XXXXXXXXXXXX&password=XXXXXX&year=2019&term=3"
    size = 0  # 现在已经出成绩的科目数量
    flag = 0  # 标记有没有成功查到过成绩
    while True:
        try:
            times = 0
            content = requests.get(url, headers=headers).content.decode().encode("GBK")
            decodedJSON = json.loads(content)
            # print(decodedJSON)
            while decodedJSON["status"] != "success":
                print('查询错误')
                content = requests.get(url, headers=headers).content.decode().encode("GBK")
                decodedJSON = json.loads(content)
                # print(decodedJSON)
                times = times + 1
                if times == 5 and flag == 0:
                    exit(0)
                if times == 10:
                    continue
            flag = 1
            if len(decodedJSON["msg"]) != size:
                msg = ''
                for each in decodedJSON["msg"]:
                    msg = msg + each['kcmc'] + '\t' + each['classscore'] + '\n'
                sendmail(msg)
                size = len(decodedJSON["msg"])
            # print(len(decodedJSON["msg"]))
            time.sleep(60)
        except requests.exceptions.ConnectionError as e:
            print('Network Error')
        except KeyError as e:
            print('KeyError')
        except json.decoder.JSONDecodeError as e:
            print('JsonDecodeError')
