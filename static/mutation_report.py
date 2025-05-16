from flask import send_file
import pandas as pd

@app.route('/export')
def export_csv():
    if mutation_data:
        df = pd.DataFrame(mutation_data)
        file_path = 'static/mutation_report.csv'
        df.to_csv(file_path, index=False)
        return send_file(file_path, as_attachment=True)
    else:
        return "No mutation data to export."
