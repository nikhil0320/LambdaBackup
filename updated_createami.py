import boto3
import datetime
import sys
from datetime import date
from dateutil.tz import *
# variables
backup_tag = 'AMI_Backup_Policy'
table_name = 'Ami_Backup_Policy'
tagslist = []


now = datetime.datetime.now(gettz("US/Eastern")) 
dest_date=now.strftime("%Y-%m-%d")

todaydayest = now.strftime('%A')

todaydateest1  = now.strftime("%Y-%m-01")

current_dest_time=now.strftime("%H:%M")

client = boto3.client('ec2')
dynamodb = boto3.client('dynamodb')


def tags(amiid):
    if todaydayest == 'Sunday':
        client.create_tags(Resources=[amiid],Tags=[{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'W'}])
    elif dest_date == todaydateest1:
        client.create_tags(Resources=[amiid],Tags=[{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'M'}])
    else:
        client.create_tags(Resources=[amiid],Tags=[{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'D'}])

def lambda_handler(event, keys):
    response = client.describe_instances(Filters=[{'Name': 'tag-key', 'Values':[backup_tag]}])

    for reservation in response['Reservations']:
        for n in reservation['Instances']:
            tagslist = n['Tags']
            for k in tagslist:
                if k['Key'] == 'Name':
                    iname = k['Value']    
            for j in  n['Tags']:
                if j['Key'] == backup_tag:
                	bvalue =  j['Value']
                	x = bvalue.split('-')[0][0:bvalue.split('-')[0].find(':')]
                	timeValList = []
                	for i in range(0,6):
                            timeValList.append(x + ":0" + str(i))
                	if current_dest_time in timeValList:
                            amiresponse = client.create_image(InstanceId=n['InstanceId'], Name= iname+'-'+dest_date)
                            dynamodb.put_item(TableName = table_name,Item={'AMI_ID' :{'S': amiresponse['ImageId']} ,'Tag_Value' :{'S': bvalue  }})
                            amiid=amiresponse['ImageId']
                            for v in tagslist:
                                client.create_tags(Resources=[amiid],Tags=[{'Key': v['Key'],'Value': v['Value']}],)
                            tags(amiid);    
                                
	                        
