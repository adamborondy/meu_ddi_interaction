from flask import Flask, render_template, request, redirect, url_for
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('ddi.db')
    conn.row_factory = sqlite3.Row
    return conn

def check_drug_interaction(new_drug_id, medications):

    # List of existing drugs assigned to a patient
    existing_drug_ids = set()
    for drug in medications:
        existing_drug_ids.add(drug['drug_id'])

    sparql = SPARQLWrapper("https://bio2rdf.org/sparql")

    # Query to get the list of drugs with an interaction with new one about to be assigned
    query = f"""
    PREFIX dv: <http://bio2rdf.org/drugbank_vocabulary:>
    PREFIX brv: <http://bio2rdf.org/bio2rdf_vocabulary:>
    PREFIX dct: <http://purl.org/dc/terms/>

    SELECT DISTINCT ?object
    WHERE {{
    ?escitalopram a dv:Drug .
    ?escitalopram brv:identifier ?id .
    ?escitalopram dv:ddi-interactor-in ?drug_interaction .
    ?drug_interaction brv:identifier ?object .
    FILTER(STR(?id) = "{new_drug_id}") .
    }}
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    ddi_df = sparql.query().convert()

    data = []

    for r in ddi_df["results"]["bindings"]:
        drug_ids = r["object"]["value"]
        data.append(drug_ids)

    ddi_res = pd.DataFrame(data, columns=['ddi'])
    # Make a list out of the unique drug id-s
    ddi_res = ddi_res['ddi'].str.split('_').explode().unique()

    # Return whether there is any overlap between 1) the ones incompatible with the new one and 2) the ones already assigned
    return not existing_drug_ids.isdisjoint(ddi_res)

@app.route('/', methods=['GET', 'POST'])
def index():

    selected_patient = None
    interaction_warning = None
    medications = []
    all_drugs = []

    if request.method == 'POST':

        patient_id = request.form['patient_id']
        conn = get_db_connection()
        # List of all available drugs
        all_drugs = conn.execute('SELECT distinct id, drug_name FROM drugs').fetchall()
        # All information about a given patient
        patient_query = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()

        if patient_query:
            selected_patient = dict(patient_query)
            # Medications prescribed for a patient of interest
            medication_query = conn.execute('''
                SELECT p.drug_id, d.drug_name
                FROM prescriptions p
                INNER JOIN drugs d ON p.drug_id = d.id
                WHERE p.patient_id = ?
            ''', (patient_id,))
            medications = [dict(med) for med in medication_query.fetchall()]

        if 'prescribe_drug' in request.form and 'drug_id' in request.form:
            new_drug_id = request.form['drug_id']
            # Give warning if overlap is found by check_drug_interaction()
            if check_drug_interaction(new_drug_id, medications):
                interaction_warning = "Warning: Potential drug-drug-interaction detected!"
            # Otherwise write prescription into db
            else:
                conn.execute('INSERT INTO prescriptions (patient_id, drug_id) VALUES (?, ?)', (patient_id, new_drug_id))
                conn.commit()

        elif 'confirm_prescription' in request.form:
            new_drug_id = request.form['drug_id']
            conn.execute('INSERT INTO prescriptions (patient_id, drug_id) VALUES (?, ?)', (patient_id, new_drug_id))
            conn.commit()
            return redirect(url_for('index'))

        elif 'cancel_prescription' in request.form:
            return redirect(url_for('index'))

        conn.close()
    return render_template('index.html', selected_patient=selected_patient, medications=medications, all_drugs=all_drugs, interaction_warning=interaction_warning)

if __name__ == '__main__':
    app.run(debug=True)