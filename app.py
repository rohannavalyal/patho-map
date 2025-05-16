# PathoMap: Intermediate-Level Genomic Tracker for Outbreak Visualization

# Step 1: Flask App (app.py)
from flask import Flask, render_template, request, redirect, url_for
from utils.sequence_utils import load_sequences, count_mutations_per_sample
from utils.map_utils import load_metadata, generate_map, generate_timeline
import os
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

fasta_path = os.path.join(UPLOAD_FOLDER, 'samples.fasta')
csv_path = os.path.join(UPLOAD_FOLDER, 'metadata.csv')

@app.route('/')
def index():
    return redirect(url_for('upload'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        fasta_file = request.files['fasta']
        csv_file = request.files['metadata']

        if fasta_file:
            fasta_file.save(fasta_path)
        if csv_file:
            csv_file.save(csv_path)

        return redirect(url_for('map_view'))
    return render_template('upload.html')

@app.route('/map')
def map_view():
    sequences = load_sequences(fasta_path)
    mutations_df = count_mutations_per_sample(sequences)
    metadata_df = load_metadata(csv_path)
    merged_df = pd.merge(mutations_df, metadata_df, on='SampleID')
    map_html = generate_map(merged_df)
    return render_template('map.html', map_html=map_html)

@app.route('/mutations')
def mutations():
    sequences = load_sequences(fasta_path)
    mutations_df = count_mutations_per_sample(sequences)
    return render_template('mutations.html', tables=[mutations_df.to_html(classes='data', index=False)], titles=mutations_df.columns.values)

@app.route('/timeline')
def timeline():
    sequences = load_sequences(fasta_path)
    mutations_df = count_mutations_per_sample(sequences)
    metadata_df = load_metadata(csv_path)
    merged_df = pd.merge(mutations_df, metadata_df, on='SampleID')
    timeline_html = generate_timeline(merged_df)
    return render_template('timeline.html', timeline_html=timeline_html)

from flask import send_file

@app.route('/export')
def export_csv():
    # Check if required files exist
    if not os.path.exists(fasta_path) or not os.path.exists(csv_path):
        return "Error: Required files (FASTA and/or metadata CSV) are missing. Please upload the files first.", 400

    try:
        # Load and validate sequences
        sequences = load_sequences(fasta_path)
        if not sequences:
            return "Error: No sequences found in the FASTA file.", 400

        # Generate mutation data
        mutations_df = count_mutations_per_sample(sequences)
        
        # Load and validate metadata
        metadata_df = load_metadata(csv_path)
        if 'SampleID' not in metadata_df.columns:
            return "Error: 'SampleID' column is missing in the metadata file.", 400

        # Merge data with validation
        try:
            merged_df = pd.merge(mutations_df, metadata_df, on='SampleID', how='inner')
            if merged_df.empty:
                return "Error: No matching samples found between FASTA and metadata files.", 400
        except KeyError as e:
            return f"Error: {str(e)}. Please check the data format in both files.", 400

        # Create static directory if it doesn't exist
        os.makedirs('static', exist_ok=True)

        # Generate timestamp for unique filename
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f'mutation_report_{timestamp}.csv'
        export_path = os.path.join('static', export_filename)

        # Add metadata about the export
        export_info = pd.DataFrame({
            'Export_Info': [
                f'Generated on: {pd.Timestamp.now()}',
                f'Total samples: {len(merged_df)}',
                f'Reference sequence: {sequences[0].id}'
            ]
        })

        # Save the report
        with open(export_path, 'w') as f:
            export_info.to_csv(f, index=False)
            f.write('\n')  # Add a blank line between info and data
            merged_df.to_csv(f, index=False)

        return send_file(
            export_path,
            as_attachment=True,
            download_name=export_filename,
            mimetype='text/csv'
        )

    except Exception as e:
        return f"Error generating export: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
