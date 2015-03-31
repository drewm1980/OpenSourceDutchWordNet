from lxml import etree
from collections import defaultdict
import cPickle
import argparse

#parse user input
parser = argparse.ArgumentParser(description='Create synonym dict odwn')
parser.add_argument('-i', 
                    dest='input_path',   
                    help='full path to odwn_1.0.xml (synset file). On 31-3-2015, it could be found here: http://kyoto.let.vu.nl/~postma/odwn/Data/odwn_1.0.xml.gz',
                    required=True)
args = parser.parse_args().__dict__    

#parse odwn
doc = etree.parse(args['input_path'])

#set synonyms_dict
synonyms_dict = defaultdict(set)

#loop through all synonyms elements
for synonyms_el in doc.iterfind("cdb_synset/synonyms"):
    
    #obtain non-english synonyms of this synset
    synonyms = [syn_el.get("c_lu_id-previewtext").split(":")[0]
                for syn_el in synonyms_el.iterfind("synonym")
                if syn_el.get("c_lu_id-previewtext").startswith("eng_") == False]
    
    #if length of synonyms if 2 or more, add each synonym in the list
    #to the synonym list of each entry in the list
    if len(synonyms) >= 2:
        for lemma in synonyms:
            for synonym in synonyms:
                synonyms_dict[lemma].update([synonym])
                
#save dict to file
#output is mapping from synonym to list of synonyms
with open("synonyms_dict_odwn1.0.bin","w") as outfile:
    cPickle.dump(synonyms_dict, outfile)

print
print "the output can be found here:"
print "synonyms_dict_odwn1.0.bin"
print "this is a cPickle file (https://wiki.python.org/moin/UsingPickle)"
print "it contains a mapping from a synonym to a list of synonyms of this synonym"
