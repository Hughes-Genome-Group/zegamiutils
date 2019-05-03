import argparse
import io
import os
import re
import sys
import json



from .lib import (
    api,
    auth
)

API_URL="https://zegami.com/api/"
OAUTH_URL="https://zegami.com/oauth/token/"



def count_dir(dir):
# counts number of files in a directory
    count = 0
    for filename in os.listdir(dir):
        full_path = dir + "/" + filename
        if os.path.isfile(full_path):
            count = count + 1
    return count

   
def get_client(username,password,project):
    '''Returns the client'''
    auth_client = auth.AuthClient(OAUTH_URL)
    auth_client.set_name_pass(username,password)
    token = auth_client.get_user_token()
    client = api.Client(API_URL, project, token)
    return client


def create_collection(name,tsv_file,image_column,client,desc=""):
    '''Creates a zegami collection
    Args:
        name(str): The name of the collection
        tsv_file(str): The absolute path of the tsv file
        image_column(str): The header of the image column in the tsv file
        desc(str): The description of the collection
        
    Returns:
        The url of the newly created collection and the collection id
    '''
   
   
    
    # create a collection with above name and description
   
    collection = client.create_collection(name, desc,
                                          dynamic=False)
   

    # get id of our collection's imageset and fill it with images
    imageset_id = collection["imageset_id"]
        
    dataset_id = collection["dataset_id"]
    with open(tsv_file) as f:
        client.upload_data(dataset_id, tsv_file, f)
        
    join_ds = client.create_join(
        "Join for " + name, imageset_id, dataset_id, join_field=image_column)
    collection['join_dataset_id'] = join_ds['id']

    # send our complete collection to zegami
    client.update_collection(collection['id'], collection)

  
    url = "https://zegami.com/collections/{}-{}".format(client.project,collection['id'])
    return url,collection["id"]
    

def upload_images(image_dir,collection_id,client,from_count=0):
    '''Uploads images to an exisitng collection
    Args:
        image_dir(str): The full path of the directory containing the images
        collection_id(str): The id of the collection
        tsv_file(str): The absolute path of the tsv file
        job (object): optional If supplied the the job will be updated with the number of uploaded images
        project (object) optional - if supplied the project data will be updated with the number 
            of images uploaded.
        from_count (int): optional (default is 0) - The index (zero based) to start uploading 
            the images from. Used if image uploading was previously disrupted.
    Returns:
        The url of the newly created collection
    '''
    count = 0
    collection =client.get_collection(collection_id)
    collection=collection["collection"]
    imageset_id = collection["imageset_id"]
    
    total=count_dir(image_dir)
    try:
        for filename in os.listdir(image_dir):
            if count<from_count:
                count+=1
                continue
            full_path = image_dir + "/" + filename
            if os.path.isfile(full_path):
                with open(os.path.join(image_dir, filename), 'rb') as f:
                    client.upload_png(imageset_id, filename, f)
                count = count + 1
                if count%200 ==0:
                    print ("uploaded {}/{}".format(count,total))
    except:
        print ("only uploaded {}/{} images".format(count,total))
        print(traceback.format_exc())
        return False,count
    
    return True,total
              
                    
                    

def update_collection(collection_id,upload_file,client):
    '''Updates the collection with the supplied file
    Args:
        collection_id(str): The id of the collection
        upload_file(str): The full path of the file containing the new information
    '''
    collection =client.get_collection(collection_id)
    dataset_id =collection['collection']['dataset_id']
    
    with open(upload_file) as f:
        client.upload_data(dataset_id, upload_file, f)
        

           
def create_new_set(collection_id,upload_file,name):
    '''Creates a new subset specified by the the supplied file
    Args:
        collection_id(str): The id of the original collection collection
        upload_file(str): The full path of the file containing a subset of the
            original collection
    Returns:
        The url of the newly created subset
    '''
    info = app.config['ZEGAMI_SETTINGS']
    
    desc="test"
    client = get_client()
    
    collection =client.get_collection(collection_id)
    
    imageset_id=collection['collection']["imageset_id"]
    new_collection = client.create_collection(name, desc,
                                          dynamic=False)
    
    new_collection['imageset_id'] = imageset_id
    client.update_collection(new_collection['id'], new_collection)
    
    dataset_id = new_collection["dataset_id"]
    with open(upload_file) as f:
        client.upload_data(dataset_id, upload_file, f)

    # join the imageset and the dataset together using the dataset join column
    join_ds = client.create_join(
        "Join for " + name, imageset_id, dataset_id, join_field="Image Name")

    # tell our collection where the join data lives
  
    new_collection['join_dataset_id'] = join_ds['id']

    # send our complete collection to zegami
    client.update_collection(new_collection['id'], new_collection)
    
    url = "https://zegami.com/collections/{}-{}".format(info['PROJECT'],new_collection['id'])
    return url

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="specify action:- create_collection")
    args = parser.parse_args()
    params=json.loads(open(args.config).read())

    
    client =  get_client(params["username"],params["password"],params["project"])
    description = params.get("collection_description","")
    
    if params["action"] == "create_and_upload":
        url,collection_id = create_collection(params["collection_name"],params["tsvfile"],params["imagecol"],client,description)
        print("created collection - id:{}".format(collection_id))
        success,num_uploaded = upload_images(params["imagedir"], collection_id, client)
        if success:
            print("successfully created collection and uploaded all images")
        else:
            print ("only uploaded {} images".format(num_uploaded))
        print("url:{}".format(url))
        print("collection id:{}".format(collection_id))
        
    if params["action"] == "create":
        url,collection_id = create_collection(params["collection_name"],params["tsvfile"],params["imagecol"],client,description)
        print("Sucessfully created collection")
        print("url:{}".format(url))
        print("collection id:{}".format(collection_id))
        
    if params["action"] == "upload":
        from_count=params.get("from_count",0)
        success,num_uploaded = upload_images(params["imagedir"], params["collection_id"], client,from_count)
        if success:
            print("successfully created collection and uploaded all images")
        else:
            print ("only uploaded {} images".format(num_uploaded))
            
    if params["action"] == "delete":
        from_count=params.get("from_count",0)
        success = delete_colloection(params["collection_id"], client)
        if success:
            print("successfully deleted collection {}".format(params["collection_id"]))
        else:
            print("unable to delete collection {}".format(params["collection_id"]))
            
    if params["action"]== "update":
        update_collection(params["collection_id"],params["tsvfile"],client)
        print("sucessfully updated collection")
      
             
    
def delete_collection(collection_id,client):
    resp = client.delete_collection(collection_id)
    return resp.status_code==204
    
        
def get_tags(collection_id,client):
    return client.get_tags(collection_id)


if __name__ == "__main__":
    main()


w