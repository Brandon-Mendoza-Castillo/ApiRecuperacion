
from flask import Flask, render_template, redirect, url_for, abort
import os
from nbconvert import HTMLExporter
import nbformat
import papermill as pm

app = Flask(__name__)

# Carpetas de trabajo
BASE_DIR = os.path.dirname(__file__)
NOTEBOOK_DIR = os.path.join(BASE_DIR, 'notebooks')
EXECUTED_DIR = os.path.join(NOTEBOOK_DIR, 'executed')
DATASET_DIR = os.path.join(BASE_DIR, 'datasets')

# Asegurar que la carpeta 'executed' exista
os.makedirs(EXECUTED_DIR, exist_ok=True)

@app.route('/')
def index():
    """Página principal que lista los notebooks."""
    notebooks = [f for f in os.listdir(NOTEBOOK_DIR) if f.endswith('.ipynb') and not f.startswith('executed')]
    return render_template('index.html', notebooks=notebooks)

@app.route('/execute/<filename>')
def execute_notebook(filename):
    """Ejecuta un notebook usando papermill."""
    notebook_path = os.path.join(NOTEBOOK_DIR, filename)
    executed_path = os.path.join(EXECUTED_DIR, f"{os.path.splitext(filename)[0]}_executed.ipynb")

    if not os.path.exists(notebook_path):
        abort(404)

    try:
        # Ejecutar el notebook con papermill
        pm.execute_notebook(
            notebook_path,
            executed_path,
            parameters={"DATASET_DIR": DATASET_DIR}  # Pasar la ruta del dataset como parámetro
        )
    except Exception as e:
        return f"Error al ejecutar el notebook: {e}", 500

    return redirect(url_for('view_notebook', filename=f"executed/{os.path.basename(executed_path)}"))

@app.route('/notebook/<path:filename>')
def view_notebook(filename):
    """Muestra un notebook convertido a HTML."""
    notebook_path = os.path.join(NOTEBOOK_DIR, filename)
    if not os.path.exists(notebook_path):
        abort(404)

    html_exporter = HTMLExporter()
    html_exporter.template_name = 'lab'
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_node = nbformat.read(f, as_version=4)
        (body, _) = html_exporter.from_notebook_node(notebook_node)

    return render_template('notebook.html', notebook_html=body)

if __name__ == '__main__':
    app.run(debug=True)
