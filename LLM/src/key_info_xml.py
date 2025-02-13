import logging
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def prettify_xml(elem):
    """Formate le XML de manière lisible."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def json_to_xml():
    try:
        # Chemins des fichiers
        project_root = str(Path(__file__).parent.parent.parent)
        json_file = os.path.join(project_root, "LLM", "outputs", "kid.json")
        
        # Lire le JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Créer la structure XML
        root = ET.Element("key-information")
        
        # Product
        product = ET.SubElement(root, "product")
        product.set("name", data["product"]["name"])
        product.set("type", data["document"]["type"])
        product.set("isin", data["product"]["isin"])
        product.set("currency", data["product"]["currency"])
        
        # Risk
        risk = ET.SubElement(root, "risk")
        risk.set("level", str(data["risk"]["level"]))
        warnings = ET.SubElement(risk, "warnings")
        for warning in data["risk"]["warnings"]:
            warning_elem = ET.SubElement(warnings, "warning")
            warning_elem.text = warning
        
        # Dates
        dates = ET.SubElement(root, "dates")
        dates.set("issue", data["dates"]["issue"])
        dates.set("redemption", data["dates"]["redemption"])
        dates.set("valuation", data["dates"]["redemption_valuation"])
        
        # Performance
        performance = ET.SubElement(root, "performance")
        for scenario_type in ["favorable", "moderate", "unfavorable", "stress"]:
            scenario = ET.SubElement(performance, "scenario")
            scenario.set("type", scenario_type)
            scenario_data = data["performance"]["scenarios"][scenario_type]
            scenario.set("initial", str(scenario_data["initial"]))
            scenario.set("final", str(scenario_data["final"]))
            scenario.set("change", str(scenario_data["percentage_change"]))
        
        # Costs
        costs = ET.SubElement(root, "costs")
        total = ET.SubElement(costs, "total")
        total.set("one_off", str(data["performance"]["costs"]["total"]["one_off"]))
        if data["performance"]["costs"]["total"]["ongoing"]:
            total.set("ongoing", str(data["performance"]["costs"]["total"]["ongoing"]))
        impact = ET.SubElement(costs, "impact_on_return")
        impact.set("one_off", str(data["performance"]["costs"]["impact_on_return"]["one_off"]))
        if data["performance"]["costs"]["impact_on_return"]["ongoing"]:
            impact.set("ongoing", str(data["performance"]["costs"]["impact_on_return"]["ongoing"]))
        
        # Générer le XML formaté
        xml_string = prettify_xml(root)
        
        # Sauvegarder le XML
        output_file = os.path.join(project_root, "LLM", "outputs", "key-info.xml")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        logger.info(f"XML sauvegardé dans {output_file}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement : {str(e)}")
        raise

if __name__ == "__main__":
    json_to_xml()
