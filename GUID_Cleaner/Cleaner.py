"""
@author: AndresF-DLR

"""

import os
import pandas as pd

def renameTif(image_list, data):
    """
    (list, dataFrame) --> None
    
    Function receives a list of image file titled with their source's GUIDs
    and a dataframe matching source identifiers to the destination's GUIDs. The script parses
    through each image, cross-checks identifiers, and renames the file with the destination's GUID. 
    
    If the image represents a record with a companion file (identified by a "-v"), its old filename must be sliced
    by its hyphen and its new filename must follow a slightly different naming scheme. 
    """
    extra_listings = []
    
    for i in image_list:
        
        #Ignore files with destination GUIDs titles - ("D...")
        if not i.startswith("D"):
        
            #Filename follows verso-image naming scheme
            try:
                source_number = i[:i.index("-")]
                
                new_name = data[data["Source Number"] == source_number]["Object number"].item() + ".v.tif"
                
                print(i + ": " + new_name)
            
            #Filename follows standard naming scheme
            except ValueError:
                source_number = i[:i.index(".")]
                
                new_name = data[data["Source Number"] == source_number]["Object number"].item() + ".tif"
                
                print(i + ": "  + new_name)
                
            os.rename(i, new_name)
        
        #Track files that did not go through any alterations
        else: 
            extra_listings.append(i)
    
    if extra_listings:
        
        print(extra_listings)

if __name__ == "__main__":
    
    #Initialize DataFrame from Records in CSV File 
    records = pd.read_csv("GUIDConversion.csv")

    path = os.getcwd() + "/GUID_Records"
    
    os.chdir(path)
    
    #Filter files within directory without a valid file extension
    images = [i for i in os.listdir(path) if os.path.splitext(i)[1] == ".tif"]
    
    renameTif(images, records)
    
    
