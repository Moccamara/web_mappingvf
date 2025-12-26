import json
from qgis.core import QgsProject, QgsFeatureRequest

# --- Chemins vers le projet QGIS et le JSON de sélection ---
QGIS_PROJECT = r"qgis_project/project.qgz"
SE_FILE = r"qgis_project/se_selected/selected_se.json"

# --- Charger le projet QGIS ---
project = QgsProject.instance()
project.read(QGIS_PROJECT)

# --- Charger la sélection JSON ---
with open(SE_FILE, "r", encoding="utf-8") as f:
    se_data = json.load(f)

# --- Appliquer la sélection sur la couche "IDSE Layer" ---
layer_name = "IDSE Layer"  # Nom exact de ta couche QGIS
layers = QgsProject.instance().mapLayersByName(layer_name)

if layers:
    layer = layers[0]
    expr = f'"idse_new" = \'{se_data["idse_new"]}\''
    layer.selectByExpression(expr)
    print(f"Selection applied: {se_data['idse_new']}")
else:
    print(f"Couche {layer_name} introuvable")

# --- Sauvegarder le projet si besoin ---
project.write()
