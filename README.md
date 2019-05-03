# zegamiutils
Utility methods for Zegami

## Requirements
requests (pip install requests)

## Using in a Script
Make sure the zegami module is in your syspath.Import zegamutils, then create a client supplying username,password and project then you can call methods (see below for examples)

**N.B.** The project is the identifier which is the url of your collections. It is the first part (before the hyphon) in the last segment of the url. For example if the url is  https://zegami.com/collections/**ztrbzvw2**-5ccbf819f64c130001eb2cb2, then the project would be ztrbzvw2

### Example  
```
from zegami import zegamiutils
#get client giving username, password and project id
client = zegamiutils.get_client("me@somewhere.com","password","ztrbzvw2")

#create the collection giving collection name, tsv file, the name of the image column in the tsv file and the client
url,collection_id = zegamiutils.create_collection("My Collection","c:\\zeg_data\\images\data.tsv","Image Name",client)

#upload the images giving the image folder, collection id and client
zegamiutils.upload_images("c:\\zeg_data\\images",collection_id,client)
```

## Using at the Command Line
To save typing lots of parameters and exposing your password on the command line - parameters are stored in a config file and this is given at the command line e.g
```
python -m zegami.zegamiutils config.json
```

The config is a json file (see example_configs)  with the following parameters

* *username* required - your zegami username (usually your email address)
* *password* required  - your password
* *project* required - the unique identifier which is the first part of the last section of the a collection url (see above)
* *action* required - can be create_and_upload,create,upload,delete,update 
* *collection_name* required for create and create_and_upload actions - the name you want to give to the collection
* *collection_description optional for create and create_and_upload actions - the description you want to give to the collection
* *tsvfile* required for create,create_and_upload and update actions - the tab delimited file (with column headings) that will be used to update/create the collection
* *imagecol* required for create and create_and_uplaod actions - the name of the column in the tsv file which specifies the name of the image linked to the data row
* *from_count* optional for the update action - the number of the image to start uploading from. This may be required if previously uplaoading images was interrupted and you should have got information about how many images were uploaded 


