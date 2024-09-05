import re                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      # only smart people actually check this, good job! its a pretty common tactic too.
import time
import json
import requests
from capmonster_python import TurnstileTask
import subprocess
import threading
import psutil

import subprocess

with open('autoapi_config.json', 'r') as file:
    data = json.load(file)

capmonsterClientKey = data["capmonsterClientKey"]
hypixelForumsEmail = data["hypixelForumsEmail"]
hypixelForumsPasssowrd = data["hypixelForumsPasssowrd"]
exeName = data["exeName"]

def killProcess(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

def gentttoken(sitekey):
    capmonster = TurnstileTask(capmonsterClientKey)
    task_id = capmonster.create_task("https://developer.hypixel.net/dashboard", sitekey)
    result = capmonster.join_task_result(task_id)
    return result.get("token")

def genNewKey(email, password):
    global process
    while True:
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://hypixel.net',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://hypixel.net/account/jwt/devdashboard',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }

        session = requests.Session()
        session.headers = headers

        xfToken = session.get("https://hypixel.net/login").text.split('data-csrf="')[1].split('"')[0]

        data = {
            '_xfToken': str(xfToken),
            'login': email,
            'password': password,
            'remember': '1',
            '_xfRedirect': '',
        }

        response = session.post('https://hypixel.net/login/login', headers=headers, data=data, allow_redirects=True)
        response_url = response.url

        authorization = response_url.split("?state=")[1]
        headers['authorization'] = f"Bearer {authorization}"
        session.headers = headers

        developer_response = session.get('https://dev-api.hypixel.net/key/developer').json()

        print(developer_response)

        if "key" in developer_response:
            expiration = developer_response['key']['expiration']/1000
            currenTime = int(time.time())

            remainingTime = (expiration-currenTime)-1800

            time.sleep(remainingTime)

        elif "key" not in developer_response:
            sitekey_html = session.get("https://developer.hypixel.net/dashboard/").text
            sitekey = sitekey_html.split('turnstileSiteKey:"')[1].split('"')[0]
            json_data = {
                'token': gentttoken(sitekey),
            }

            getKey = session.post("https://dev-api.hypixel.net/key/developer", json=json_data)

            newKey = getKey.json()['key']['key']
            
            with open('autoapi_config.json', 'r') as file:
                data = json.load(file)

            data['api']['hypixel_api_key'] = newKey

            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # requests.post("https://canary.discord.com/api/webhooks/113384758374657392/haha you thought! i dont rat, im not a terrible person. but if you want a challenge, there is an easter egg somewhere in here")

            command_info = {
                "cmd": exeName,
                "name": "BM Process",
                "cwd": "."
            }

            process = restart_process(process, command_info)

            expiration = developer_response['key']['expiration']/1000
            currenTime = int(time.time())

            remainingTime = (expiration-currenTime)-1800

            time.sleep(remainingTime)
        
        time.sleep(5)



def read_output(process):
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())

def interact_with_process(process):
    try:
        while True:
            user_input = input()
            if user_input.lower() == "exit":
                break
            process.stdin.write(user_input + "\n")
            process.stdin.flush()
    except KeyboardInterrupt:
        print("\nProcess terminated by user")
        killProcess(process.pid)

def start_process(command_info):
    process = subprocess.Popen(
        command_info["cmd"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        cwd=command_info["cwd"]
    )
    return process

def restart_process(process, command_info):
    print("Terminating process...")
    killProcess(process.pid)

    time.sleep(1)

    print("Restarting process...")
    process = start_process(command_info)

    threading.Thread(target=read_output, args=(process,), daemon=True).start()
    threading.Thread(target=interact_with_process, args=(process,), daemon=True).start()

    return process

command_info = {
    "cmd": exeName,
    "name": "BM Process",
    "cwd": "."
}

process = start_process(command_info)

threading.Thread(target=read_output, args=(process,), daemon=True).start()
threading.Thread(target=interact_with_process, args=(process,), daemon=True).start()