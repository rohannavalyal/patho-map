# utils/sequence_utils.py
from Bio import SeqIO
import pandas as pd

def load_sequences(fasta_path):
    return list(SeqIO.parse(fasta_path, "fasta"))

def count_mutations_per_sample(sequences):
    reference_seq = str(sequences[0].seq)
    reference_id = sequences[0].id.split('|')[0]
    
    data = []
    for record in sequences:
        sample_id = record.id.split('|')[0]
        sample_seq = str(record.seq)
        mutation_count = sum(1 for a, b in zip(reference_seq, sample_seq) if a != b)
        data.append({'SampleID': sample_id, 'MutationCount': mutation_count})
    
    return pd.DataFrame(data)
