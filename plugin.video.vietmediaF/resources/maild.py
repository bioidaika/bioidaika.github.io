import requests, re, time
from addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE
url = "https://api.maildrop.cc/graphql"
headers = {"authority": "api.maildrop.cc","content-type": "application/json","origin": "https://maildrop.cc","referer": "https://maildrop.cc/","user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.0.0"}

def deleteMail(email,email_id):
    data = {"operationName": "DeleteMessage","variables": {"mailbox":email ,"id": email_id},"query": "mutation DeleteMessage($mailbox: String!, $id: String!) {\n  delete(mailbox: $mailbox, id: $id)\n}"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        if response_data['data']['delete'] == True:
            print("deleted")
    else:
        print("Request failed with status code:", response.status_code)
def getMessage(email,email_id):
    data = {
        "operationName": "GetMessage",
        "variables": {
            "mailbox": email,
            "id": email_id
        },
        "query": "query GetMessage($mailbox: String!, $id: String!) {\n  message(mailbox: $mailbox, id: $id) {\n    id\n    subject\n    date\n    headerfrom\n    data\n    html\n    __typename\n  }\n}"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        data_text = response_data['data']['message']['html']
        regex = r"href=\"(https.*dlsession.*)\"\starget"
        match = re.search(regex,data_text)
        if match:
            session_delete_link = match.group(1)
            return(session_delete_link)

def deleteAllMail(email):
    alert('delete All')
    data = {
            "operationName": "GetInbox",
            "variables": {"mailbox": email},
            "query": "query GetInbox($mailbox: String!) {\n  ping(message: \"Test\")\n  inbox(mailbox: $mailbox) {\n    id\n    subject\n    date\n    headerfrom\n    __typename\n  }\n  altinbox(mailbox: $mailbox)\n}"
        }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        data_list = response_data['data']['inbox']
        for item in data_list:
            id_mail = item['id']
            subject = item['subject']
            deleteMail(email,id_mail)
            
    
def getlistMail(email):
    time.sleep(15)
    timeout=240
    start_time = time.time()
    i = 1
    while time.time() - start_time < timeout:
        alert("Check lần: "+i)
        data = {
            "operationName": "GetInbox",
            "variables": {"mailbox": email},
            "query": "query GetInbox($mailbox: String!) {\n  ping(message: \"Test\")\n  inbox(mailbox: $mailbox) {\n    id\n    subject\n    date\n    headerfrom\n    __typename\n  }\n  altinbox(mailbox: $mailbox)\n}"
        }
        print("Try again: "+str(i))
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            data_list = response_data['data']['inbox']
            
            for item in data_list:
                
                id_mail = item['id']
                subject = item['subject']
                
                if "Xác nhận xóa phiên tải" in subject or "Confirm delete download history" in subject:
                    session_link = getMessage(email,id_mail)
                    print("Reset link: "+session_link)
                    deleteMail(email,id_mail)
                    return (session_link)
        else:
            print("Request failed with status code:", response.status_code)
        time.sleep(15)
        i +=1

    return("No new mail arrived")


