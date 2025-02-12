import uuid  # For generating UUIDs for associations
import json
from biolink_model.datamodel.pydanticmodel_v2 import Gene, OrganismTaxon, Association  # Replace * with any necessary data classes from the Biolink Model
from koza.cli_utils import get_koza_app

koza_app = get_koza_app("mo_gene_transform")

gene_rows = {}
taxon_rows = {}
cnt = 0
#while (row := koza_app.get_row()) is not None:
while (True):
    try: 
        row = koza_app.get_row()
    except StopIteration:
        break
    if(row==None): break
    cnt+=1
    #if(cnt%100000==0):print(cnt)
    #row = json.loads(row)
    if(row.get("in_taxon")!=None):
        gene_rows[row["id"]] = row
    if("NCBITaxon:" in row["id"]):
        taxon_rows[row["id"]]= row


from collections import defaultdict
taxon_cnt = defaultdict(int)
for gene_row in gene_rows.values():
    taxon = gene_row['in_taxon']
    gene_entity = Gene(
            id=gene_row["id"],
            name=gene_row["name"],
            category=["biolink:Gene"]
    )
    if(taxon not in taxon_rows): 
        raise ValueError(f"{taxon} was found in the row---{str(gene_row)}--- but does not have a corresponding taxon row.")
    taxon_row = taxon_rows[taxon]

    taxon_entity = OrganismTaxon(
            id=taxon_row["id"],
            name=taxon_row["name"],
            category=["biolink:OrganismTaxon"]
    )
    association = Association(
        id=str(uuid.uuid1()),
        subject=gene_row["id"],
        predicate="biolink:in_taxon",
        object=taxon_row["id"],
        subject_category="biolink:Gene",
        object_category="biolink:OrganismTaxon",
        category=["biolink:Association"],
        knowledge_level="not_provided",
        agent_type="not_provided",
    )
    koza_app.write(gene_entity, taxon_entity, association)

for taxon in sorted(taxon_cnt):
    print(taxon,taxon_cnt[taxon])


raise StopIteration