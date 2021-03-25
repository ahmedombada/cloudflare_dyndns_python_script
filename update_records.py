from pathlib import Path
import subprocess
import logging
import json
import requests
import tldextract
import sys
import os.path

def update_records(records):
    #clean up the record name
    for record in records:
        zones.append(tldextract.extract(record).registered_domain)

    logging.info('getting zone ids ...')
    # get zone ids
    for zone in zones:
        url = 'https://api.cloudflare.com/client/v4/zones?name={}'.format(zone)
        headers = {'User-Agent':'curl/7.47.1','X-Auth-Email':'%s'%email,'X-Auth-Key':'%s'%api_key, 'Content-Type': 'application/json'}
        request = requests.request("GET",url, headers=headers)
        zone_ids_request.append(request.json())
    #clean up zone ids
    for i in range(len(zone_ids_request)):
        zone_ids_final.append(zone_ids_request[i]['result'][0]['id'])

    #saving zone ids to a file for reference 
    zone_ids_file = open("zone_ids.txt", "a+")
    for zone_id in zone_ids_final:
        zone_ids_file.write("%s\n"%zone_id)
    zone_ids_file.close()

    logging.info('got zone ids ...')


    logging.info('getting record ids ...')
    #get record ids
    for zone,record in zip(zone_ids_final, records):
        url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records?name={}'.format(zone,record)
        headers = {'User-Agent':'curl/7.47.1','X-Auth-Email':'%s'%email,'X-Auth-Key':'%s'%api_key, 'Content-Type': 'application/json'}
        request = requests.request("GET",url, headers=headers)
        record_ids_request.append(request.json())

    #clean up recod_ids
    for i in range(len(record_ids_request)):
        record_ids_final.append(record_ids_request[i]['result'][0]['id'])

    #saving record ids to a file for reference
    record_ids_file = open("record_ids.txt", "a+")
    for record_id in record_ids_final:
        record_ids_file.write("%s\n"%record_id)
    record_ids_file.close()

    logging.info('got record ids ...')

    logging.info('getting record type ...')
    #get record types
    for j in range(len(record_ids_request)):
        records_type.append(record_ids_request[i]['result'][0]['type'])
    
    #saving record type to a file for reference
    records_type_file = open("records_type.txt", "a+")
    for record_type in records_type:
        records_type_file.write("%s\n"%record_type)
    records_type_file.close()

    logging.info('got record type ...')

    if 'A' not in records_type and 'AAAA' not in records_type:
        logging.info('this only works for A and AAAA records')
        sys.exit()
    else:
        pass


    logging.info('checking types ...')
    
    logging.info('updating records ...')

    #Actually update the records
    for (z_id, r_id, r_t, r) in zip(zone_ids_final, record_ids_final, records_type, records):
        url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(z_id,r_id)
        headers = {'User-Agent':'curl/7.47.1','X-Auth-Email':'%s'%email,'X-Auth-Key':'%s'%api_key, 'Content-Type': 'application/json'}
        data = json.dumps({'id':'%s'%z_id, 'type':'%s'%r_t, 'name':'%s'%r, 'content':'%s'%ip})
        request = requests.request("PUT",url, headers=headers, data=data)
        final.append(request.json())

    logging.info('record updated successfully ...')


ip = subprocess.getoutput("curl -s http://ipv4.icanhazip.com").strip()
records = ["subdomain1.example.com", "subdomain2.example.com", "subdomain3.example.com"] #Enter the records that you want to update here
zone_ids_request = []
zone_ids_final = []
record_ids_request = []
record_ids_final = []
zones = []
final = []
records_type = []
email = "" #Enter your email here
api_key = "" #Enter your API key here
logging.basicConfig(filename='cloudflare.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logging.info('checking for changes ...')


if os.path.isfile("ip.txt"):
    old_ip = open('ip.txt', 'r').read().strip("\n")
else:
    old_ip = open("ip.txt","a+")
    old_ip.write(ip)
    old_ip.close()

if old_ip == ip:
    logging.info("IP didnt change")
    sys.exit()
else:
    update_records(records)