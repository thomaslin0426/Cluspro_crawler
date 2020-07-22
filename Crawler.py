#!/usr/bin/env python3
# coding: utf-8
#auther: Lam Yuk Shing

import datetime
import re
import requests
import time

stop_id = input(">>please key in the latest id:")
user = input(">>please key in the latest id:")
pwd = input(">>please key in the latest id:")
from bs4 import BeautifulSoup as bs
starttime = datetime.datetime.now()
login_url = "https://cluspro.bu.edu/login.php?redir=/home.php"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
header ={"user-agent": UA, "Referer":"https://cluspro.bu.edu/login.php?redir=/home.php"}
session_requests = requests.session()
fget = session_requests.get(login_url, headers = header).text
soup = bs(fget, "html.parser")

postData = {"username":user, "password":pwd, "redir":"/home.php", "action":"Login" }
session_requests.post(login_url, data = postData, headers = header)

result_url = "https://cluspro.bu.edu/results.php?offset="
id_value = re.compile(r"(?<=\.php\?job=)(\d+)")
name_value = re.compile(r"(?<=</a></td><td>)(.{1,20})(?=\</td><td>)")
stauts_value = re.compile(r"(?<=</a></td><td>).{1,20}\</td><td>([0-9a-zA-Z_ ]+)(?=</td></tr>)")

data_all = {}
now_counts = 0
stop_sign = False
for i in range(0,420):
    if stop_sign == False:
        result_url_tmp = result_url + str(i)
        result_tmp = session_requests.get(result_url_tmp, headers = header)
        table_html = str(result_tmp.content.decode())
        find_id_value = id_value.findall(table_html)
        find_name_value = name_value.findall(table_html)
        find_stauts_value = stauts_value.findall(table_html)
        if find_id_value and find_name_value and find_stauts_value != []:
            for j in range(0,10): 
                if find_id_value[j] != stop_id:
                    data_all[str((j + now_counts + 1))] = {"ID":find_id_value[j], 
                                                           "Name":find_name_value[j], 
                                                           "Status":find_stauts_value[j]}
                else:    
                    stop_sign = True
                    data_all[str((j + now_counts + 1))] = {"ID":find_id_value[j], 
                                                           "Name":find_name_value[j], 
                                                           "Status":find_stauts_value[j]}
                    break
            now_counts = 10 * (i + 1)
        else:
            print("Getting id table error")
    else:
        print("Target Id data is found")
        break

score_url = "https://cluspro.bu.edu/scores.php?job="
score_url_end = "&coeffi=0" 

cluster_value = re.compile(r"(?<=\<tr><th rowspan=\"2\" scope=\"rowgroup\">)(\d{1,2})")
members_value = re.compile(r"(?<=\</th><td rowspan\=\"2\">)(\d+)")
center_value = re.compile(r"(?<=\<td>)(\w{6})\</td><td>(.{6})")
lower_energy_value = re.compile(r"(?<=\<tr><td>)(.{13})\</td><td>(.{6})")

for i in range (1,len(data_all) + 1):
    if data_all[str(i)]["Status"] == "finished":
        page_id = str(data_all[str(i)]["ID"])
        score_url_tmp = score_url + page_id + score_url_end
        score_tmp = session_requests.get(score_url_tmp, headers = header)
        score_table_html = str(score_tmp.content.decode())
        find_cluster_value = cluster_value.findall(score_table_html)
        find_members_value = members_value.findall(score_table_html)
        find_center_value = center_value.findall(score_table_html)
        find_lower_energy_value = lower_energy_value.findall(score_table_html)
        Cluster = {}
        if find_id_value and find_name_value and find_stauts_value != []:
            for j in range (0, len(find_cluster_value)):
                Cluster[find_cluster_value[j]] = {"Members":find_members_value[j], 
                                                          find_center_value[j][0]:find_center_value[j][1],
                                                          find_lower_energy_value[j][0]:find_lower_energy_value[j][1]}
        
                print("Have been catch all data of this page")
        else:
                print("Get data error")
    
        data_all[str(i)]["Cluster"] = Cluster
    else:
        continue

 
localtime = time.asctime( time.localtime(time.time()) )
localtime
filename = user + " " + localtime + ".csv"

with open(str(filename), "w") as outfile:
    outfile.write("{}, {}, {}, {}, {}, {}\n".format("ID",
                                                  "Name",
                                                  "Cluster",
                                                  "Members",
                                                  "Center_Score",
                                                  "Lowest_Energy_Score"))
    for i in range(1,len(data_all)+1):
        if data_all[str(i)]["Status"] == "finished":
            store_id = data_all[str(i)]['ID']
            store_name = data_all[str(i)]['Name']
            for key in data_all[str(i)]['Cluster']:
                member = data_all[str(i)]['Cluster'][key]['Members']
                center = data_all[str(i)]['Cluster'][key]['Center']
                low_ene = data_all[str(i)]['Cluster'][key]['Lowest Energy']
                outfile.write("{}, {}, {}, {}, {}, {}\n".format(store_id, store_name, key, member, center, low_ene))
        else:
            continue

endtime = datetime.datetime.now()
print (endtime - starttime)

