
from datetime import datetime
import boto3
import datetime
 
utctime = datetime.datetime.utcnow()
cutoffdate = utctime - datetime.timedelta(days=3)
mweek = utctime - datetime.timedelta(days=14)
monthly  = utctime.strftime('%Y-%m-01T%H:%M:%S.%fZ')


defalut_region = 'us-west-2'
DATEFORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
    
def lambda_handler(event, context):    
    client = boto3.client('ec2',defalut_region)
    response = client.describe_images(Filters=[{'Name': 'tag:Auto-Backup','Values': ['yes']}])
    #print(response)
    for i in response['Images']:
        print(i['ImageId'] + ' - ' + i['CreationDate'])    
        n = i['CreationDate']
        cdate = datetime.datetime.strptime(n, '%Y-%m-%dT%H:%M:%S.%fZ')
        weekday = cdate.strftime('%A') 
        
        if (n < cutoffdate.strftime(DATEFORMAT)) and (weekday!='Sunday') and (cdate != monthly) :
            print('amis can be deleted')
            print('Deregistering AMI with id '+  i['ImageId'])
            amis_delete = client.deregister_image(ImageId = i['ImageId'])
            print('ami with'+ i['ImageId'] + 'deleted')
            snap_id = i['BlockDeviceMappings'][0]['Ebs']['SnapshotId']   
            del_snap = client.delete_snapshot(SnapshotId= snap_id)
            print('snapshot with ' +snap_id+ 'deleted')
    
        elif (n <= mweek.strftime(DATEFORMAT)) and (weekday=='Sunday') and (cdate != monthly):  
            print('amis can be deleted')
            print('Deregistering AMI with id '+i['ImageId'])
            amis_delete = client.deregister_image(ImageId = i['ImageId'])
            print('ami with'+ i['ImageId'] + 'deleted')
            snap_id = i['BlockDeviceMappings'][0]['Ebs']['SnapshotId']   
            del_snap = client.delete_snapshot(SnapshotId= snap_id)
            print('snapshot with-'+snap_id+'deleted')
