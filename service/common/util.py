
import boto3
import base64
import re

# Instance for s3 digitaloceanspaces
#!! NOTE: I am using harcode keys becouse it is just to test. The idea is use SECRETS for kubernetes or something else
session = boto3.session.Session()
CLIENT = session.client("s3",
            endpoint_url='https://evaluacion-ksp.sfo3.digitaloceanspaces.com', # Find your endpoint in the control panel, under Settings. Prepend "https://".
            region_name='sfo3', # Use the region in your endpoint.
            aws_access_key_id='DO00NH3W77NKD94LR9J3', # Access key pair. You can create access key pairs using the control panel or API.
            aws_secret_access_key='2ALvqRtVqN/cxGW/srCh3TpxmCx4sbB6indXWfOVeS8' # Secret access key defined through an environment variable.
)


def upload_img(img, name):
    typee = re.search("image/[a-z]*", img)
    #img = re.sub(r"^data:image/.*,","",img)
    image_base64=base64.b64encode(bytes(img,"utf-8"))
    name = name+"."+typee.group().split("/")[1]
    #image_base64 = base64.decode(img)
    res = CLIENT.put_object(Bucket="evaluacion-ksp",
                  Key=name, # Object key, referenced whenever you want to access this file later.
                  Body=base64.b64decode(image_base64), # The object's contents.
                  ACL='public-read', # Defines Access-control List (ACL) permissions, such as private or public.
                  ContentType=typee.group()
                )
    return "https://evaluacion-ksp.sfo3.digitaloceanspaces.com/evaluacion-ksp/"+name