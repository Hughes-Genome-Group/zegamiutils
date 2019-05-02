# zegamiutils
Utility methods for Zegami

### Requirements
requests (pip install requests)

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
