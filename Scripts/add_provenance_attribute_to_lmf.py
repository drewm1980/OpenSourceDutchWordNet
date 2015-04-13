#import built-in modules
import os 
import subprocess
import cPickle
import argparse

#import installed modules
from lxml import etree
 
#parse user input
parser = argparse.ArgumentParser(description='Update LMF with provenance attribute')
parser.add_argument('-d', 
                    dest='data_folder',   
                    help='full path to Data folder of this Github repository',
                    required=True)
args = parser.parse_args()    

rerun_odwn = True # only used for debugging

#paths and settings
odwn = os.path.join(args.data_folder,"odwn_1.0.xml")
lmf  = os.path.join(args.data_folder,"odwn_orbn-LMF.xml")

#gunzip if needed
for path in [odwn,lmf]:
    
    #check if exists, else gunzip the file
    if os.path.isfile(path) == False:
        subprocess.call("gunzip {path}.gz".format(**locals()),
                        shell=True)
        
#create mapping from (synset_id1,synset_id2) -> provenance (pwd or odwn)
relations_provenance = {}

#parse odwn

if rerun_odwn:
    doc           = etree.parse(odwn)
    relation_path = "wn_internal_relations/relation"
    
    for synset_el in doc.iterfind("cdb_synset"):
        
        #obtain identifier
        synset_identifier = synset_el.get("c_sy_id")
        
        #loop through relations
        for relation in synset_el.iterfind(relation_path):
            
            #get source and provenance
            source = relation.get("source")
            target = relation.get('target')
            
            #add relation to dict
            first,second = sorted([synset_identifier,target])
            
            relations_provenance[(first,second)] = source
    
    with open('relations_provenance.bin','w') as outfile:
        cPickle.dump(relations_provenance,outfile)
        
else:
    relations_provenance = cPickle.load(open('relations_provenance.bin'))
    
#parse lmf
doc                  = etree.parse(lmf,
                                   etree.XMLParser(remove_blank_text=True))
path_synset_relation = "Lexicon/Synset"

for synset_el in doc.iterfind(path_synset_relation):
     
    one_identifier = synset_el.get("id")
    
    for synset_relation_el in synset_el.iterfind("SynsetRelations/SynsetRelation"):
        target = synset_relation_el.get('target')
        
        first,second = sorted([one_identifier,target])
        
        if (first,second) in relations_provenance:
            source = relations_provenance[(first,second)]
            
            #update elements
            synset_relation_el.attrib['source'] = source
            
        else:
            print (first,second),'not found'

#overwrite lmf to file
with open(lmf,"w") as outfile:
        doc.write(outfile,
        pretty_print=True,
        xml_declaration=True,
        encoding='utf-8')