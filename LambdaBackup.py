import boto3
import datetime
import sys
from datetime import date
from dateutil.tz import *
# variables
backup_tag = 'AMI_Backup_Policy'
table_name = 'Ami_Backup_Policy'


now = datetime.datetime.now(gettz("US/Eastern")) 
dest_date=now.strftime("%Y-%m-%d")

todaydayest = now.strftime('%A')

todaydateest1  = now.strftime("%Y-%m-01")

current_dest_time=now.strftime("%H:%M")

#current_dest_time = '02:00'

client = boto3.client('ec2')
dynamodb = boto3.client('dynamodb')
def create_ami(inst,tagtime):
    amiresponse = client.create_image(InstanceId=inst, Name= inst+'-'+dest_date) 
    if todaydayest == 'Sunday':
        client.create_tags(Resources = [amiresponse['ImageId']],Tags=[{'Key': 'Name','Value': inst+'-'+dest_date },{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'W'  }],)
    elif dest_date == todaydateest1:
        client.create_tags(Resources = [amiresponse['ImageId']],Tags=[{'Key': 'Name','Value': inst+'-'+dest_date },{'Key': 'Auto-Backup','Value': 'yes'},{'Key':'backup_type' ,'Value':'M'  }],)
    else:
        client.create_tags(Resources = [amiresponse['ImageId']],Tags=[{'Key': 'Name','Value': inst+'-'+dest_date },{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'D'  }],)
    print('ami with id'+amiresponse['ImageId']+'created successfully')        
    #dynamodb.put_item(TableName = 'ami_backup_policy',Item={'ami_ids' :{'S': amiresponse['ImageId'],}})
    dynamodb.put_item(TableName = table_name,Item={'AMI_ID' :{'S': amiresponse['ImageId']} ,'Tag_Value' :{'S': tagtime  }})
    print('Copied AMI_id to Dynamodb table')
def lambda_handler(event, keys):
    
   
    response = client.describe_instances(Filters=[{'Name': 'tag-key', 'Values':[backup_tag]}])
# print response
    for reservation in response['Reservations']:
        for n in reservation['Instances']:
            for j in  n['Tags']:
                if j['Key'] == backup_tag:
                	bvalue =  j['Value']
                	tagtime = bvalue.split('-')[0]
                	x = bvalue.split('-')[0][0:bvalue.split('-')[0].find(':')]
                	timeValList = []
                	for i in range(0,6):
                            timeValList.append(x + ":0" + str(i))
                	if current_dest_time in timeValList:
                            create_ami(n['InstanceId'],tagtime);
