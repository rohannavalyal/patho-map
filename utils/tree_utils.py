# utils/tree_utils.py
from Bio import AlignIO, Phylo
from Bio.Align.Applications import ClustalwCommandline
import os

def generate_tree_html(fasta_path, output_dir='data'):
    aln_path = os.path.join(output_dir, 'aligned.aln')
    dnd_path = os.path.join(output_dir, 'tree.dnd')
    
    # Save temp fasta and run ClustalW
    with open(fasta_path, 'r') as f:
        input_fasta = f.read()
    
    with open(os.path.join(output_dir, 'temp.fasta'), 'w') as f:
        f.write(input_fasta)

    clustalw_cline = ClustalwCommandline("clustalw2", infile=os.path.join(output_dir, 'temp.fasta'))
    stdout, stderr = clustalw_cline()

    tree = Phylo.read(dnd_path, "newick")
    Phylo.draw_ascii(tree)

    return tree
