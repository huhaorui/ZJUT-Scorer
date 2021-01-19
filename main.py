import socket

import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def sendmail(msg, config):
    mail_host = config[4]
    mail_user = config[5]
    mail_pass = config[6]
    sender = config[5]
    receivers = config[7]
    message = getHTML(msg)
    message['From'] = Header('S-Server<score@zjut.edu.cn>', 'utf-8')
    message['To'] = Header(config[7] + '<' + config[7] + '>', 'utf-8')
    message['Subject'] = Header('出成绩了！', 'utf-8')
    try:
        SMTPObj = smtplib.SMTP_SSL(mail_host, 465)
        SMTPObj.ehlo()
        SMTPObj.login(mail_user, mail_pass)
        SMTPObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPAuthenticationError:
        print("邮箱账号或密码错误")
    except socket.gaierror:
        print("网络连接错误，请检查SMTP服务器配置")


def getHTML(msg):
    msg = msg.replace('\n', '</td>\n</tr>\n<tr>\n<td>')
    msg = msg.replace('\t', '</td>\n<td>')
    html = """
<html lang="zh-cn">
<head>
    <style>
        tr, td, th, table {
            border: 1px solid black;
        }
    </style>
</head>
<body>
<table>
    <tr>
        <th>
            课程名称
        </th>
        <th>
            成绩
        </th>
    </tr>
    <tr>
        <td>
    """ + msg + """
           </td>
    </tr>
</table>
</body>
</html>
    """
    print(html)
    text_html = MIMEText(html, 'html', 'utf-8')
    text_html["Content-Disposition"] = 'attachment; filename="scores.html"'
    return text_html


if __name__ == '__main__':
    configFile = open('config.ini', mode='r', encoding='utf-8')
    config = configFile.read().split('\n')
    headers = {
        "Host": "api.jh.zjut.edu.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/79.0.3945.88 Safari/537.36 Edg/79.0.309.54 "
    }
    url = "http://api.jh.zjut.edu.cn/student/scoresZf.php?ip=164&username=" + config[0] + "&password=" + config[
        1] + "&year=" + config[2] + "&term=" + config[3]
    size = 0  # 现在已经出成绩的科目数量
    flag = 0  # 标记有没有成功查到过成绩
    while True:
        try:
            times = 0
            content = requests.get(url, headers=headers).content.decode().encode("GBK")
            decodedJSON = json.loads(content)
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
                credit = 0
                GP = 0
                msg = ''
                for each in decodedJSON["msg"]:
                    if each['kcxzmc'] != '任选课':
                        credit = credit + eval(each['xf'])
                        GP = GP + eval(each['xf']) * eval(each['jd'])
                    msg = msg + each['kcmc'] + '\t' + each['classscore'] + '\n'
                GPA = GP / credit
                msg = msg + "当前GPA：\t" + str(GPA)
                sendmail(msg, config)
                size = len(decodedJSON["msg"])
        except requests.exceptions.ConnectionError as e:
            print('Network Error')
        except KeyError as e:
            print('KeyError')
        except json.decoder.JSONDecodeError as e:
            print('JsonDecodeError')
        except Exception as e:
            print('error')
        finally:
            time.sleep(60)
