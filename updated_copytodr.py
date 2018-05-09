from datetime import datetime
import boto3
import datetime
from dateutil.tz import * 


#variable
tablename = 'Ami_Backup_Policy'
dest_region = 'us-east-1'
src_region = 'us-west-2'


datenowest = datetime.datetime.now(gettz("US/Eastern")) 
todaydayest = datenowest.strftime('%A')
todaydateest = datenowest.strftime("%Y-%m-%d")
todaydateest1  = datenowest.strftime("%Y-%m-01")

dynamodb=boto3.client('dynamodb',src_region)
cpyami=boto3.client('ec2',dest_region)
souceami=boto3.client('ec2',src_region) 

def copy_tags(dest_ami,j):
    camidesc = souceami.describe_images(ImageIds=[j])
    for a in camidesc['Images']:
        for val in a['Tags']:
            cpyami.create_tags(Resources=[dest_ami],Tags=[{'Key': val['Key'],'Value': val['Value']}],)

def lambda_handler(event, context):
    
    
    response=dynamodb.scan(TableName = tablename)
    
    amis=response['Items']
    
    #print "for loop started"
    for i in response['Items']:
        j = i['AMI_ID']['S']
    #    print(j)
    #    print "for loop ended"
        resp = cpyami.copy_image(
            Name='copy of '+j+' from us-west-2',
            SourceImageId = j,
            SourceRegion = src_region
         )
        print('adding tags')
        dest_ami=resp['ImageId']
        
        copy_tags(dest_ami,j);

        print('copied ami with id = '+resp['ImageId']+' successfully') 
        print('Deleting the source ami_id from dynamodb ')
        
        delete_entry = dynamodb.delete_item(
        TableName = tablename,
        Key = {
            'AMI_ID' :{
                'S': j
            }    
        }  
        )
        print('deleted ami id '+j+' from dynamodb table')
