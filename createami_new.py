import boto3
import datetime
import sys
import os
from datetime import date
from dateutil.tz import *
# variables
client = boto3.client('ec2','us-east-1')
dynamodb = boto3.client('dynamodb','us-east-1')
sesclient = boto3.client('ses','us-east-1')

def tags(amiid,todaydayest,dest_date,todaydateest1,client):
    if todaydayest == 'Sunday':
        client.create_tags(Resources=[amiid],Tags=[{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'W'}])
    elif dest_date == todaydateest1:
        client.create_tags(Resources=[amiid],Tags=[{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'M'}])
    else:
        client.create_tags(Resources=[amiid],Tags=[{'Key': 'Auto-Backup','Value': 'yes'},{'Key': 'backup_type' ,'Value':'D'}])


def lambda_handler(event, keys):
    backup_tag = 'AMI_Backup_Policy'
    table_name = 'Ami_Backup_Policy'
    tagslist = []
    AMIList = []
    AMIDet = []
    finalemail = ''
    From_Email_Address = 'ms@reancloud.com'
    To_Email_Address = ['nikhil.linga@reancloud.com']
    subject = 'AMI_Creation_Summary'
    result = ''
    result2= ''
    
    lambdanow = datetime.datetime.now()
    now = datetime.datetime.now(gettz("US/Eastern"))
    dest_date=now.strftime("%Y-%m-%d")
    
    todaydayest = now.strftime('%A')

    todaydateest1  = now.strftime("%Y-%m-01")

    current_dest_time = now.strftime("%H:%M")
    #print(type(current_dest_time))
    #current_dest_time = '02:00'


   # print(lambdanow)
    print(current_dest_time)
    #current_dest_time = now.strftime("%H:%M")
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
                    y= bvalue.split('-')[0]
                    x = bvalue.split('-')[0][0:bvalue.split('-')[0].find(':')]
                    if current_dest_time == y:
                        print('creating ami')
                        amiresponse = client.create_image(InstanceId=n['InstanceId'], Name= iname+'-'+n['InstanceId']+'-'+dest_date)
                        dynamodb.put_item(TableName = table_name,Item={'AMI_ID' :{'S': amiresponse['ImageId']} ,'Tag_Value' :{'S': bvalue  }})
                        amiid = amiresponse['ImageId']
                        for v in tagslist:
                            if v['Key'].startswith('aws:'):
                                continue
                            client.create_tags(Resources=[amiid],Tags=[{'Key': v['Key'],'Value': v['Value']}],)
                        tags(amiid,todaydayest,dest_date,todaydateest1,client);
                        AMIList.append(amiid)
   
    if len(AMIList) != 0:
        for ami in AMIList:
            desami = client.describe_images(ImageIds=[ami])
            aminame=desami['Images'][0]['Name']
            result2 = '<tr><td style ="border:1px solid; padding : 5px;">'+aminame+'</td><td style ="border:1px solid; padding : 5px;">'+ami+'</td><tr>'
            AMIDet.append(result2)
        
        for j in AMIDet:
            result+= j
            
        finalemail = '<table style ="border:1px solid; padding : 5px;"><tr><th style="border:1px solid; padding : 5px;">AMI_Name</th><th style="border:1px solid; padding : 5px;">AMI_ID</th></tr>'+result+'</table>'  
        
        mail = sesclient.send_email(Source=From_Email_Address,Destination={'ToAddresses': To_Email_Address},Message={'Subject': {'Data': subject}, 'Body': {'Html': {'Data':'<b>List of AMI Created AT '+current_dest_time+'</b><br><br>'+finalemail}}}, ReplyToAddresses=[From_Email_Address])
        
