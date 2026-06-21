import json
import os
import glob
from collections import Counter

def main():
    print("Iniciando análisis de vulnerabilidades...")
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    json_files = glob.glob(os.path.join(results_dir, '*.json'))
    
    if not json_files:
        print("No se encontraron archivos JSON de grype en el directorio 'results'.")
        return

    total_vulns = 0
    repo_summary = {}
    severity_counter = Counter()

    for file_path in json_files:
        repo_name = os.path.basename(file_path).replace('_vulns.json', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                matches = data.get('matches', [])
                
                repo_vulns = len(matches)
                total_vulns += repo_vulns
                repo_summary[repo_name] = repo_vulns
                
                for match in matches:
                    vuln = match.get('vulnerability', {})
                    severity = vuln.get('severity', 'Unknown')
                    severity_counter[severity] += 1
                    
        except Exception as e:
            print(f"Error leyendo {file_path}: {e}")

    # Guardar resumen en la carpeta de evidencia
    evidence_path = os.path.join(os.path.dirname(__file__), '..', 'evidence', 'reportes', 'resumen_analisis.txt')
    os.makedirs(os.path.dirname(evidence_path), exist_ok=True)
    
    with open(evidence_path, 'w', encoding='utf-8') as out_f:
        out_f.write("RESUMEN DE VULNERABILIDADES EXTRAÍDAS\n")
        out_f.write("=======================================\n\n")
        out_f.write(f"Total de vulnerabilidades encontradas: {total_vulns}\n\n")
        
        out_f.write("Vulnerabilidades por repositorio:\n")
        for repo, count in repo_summary.items():
            out_f.write(f" - {repo}: {count}\n")
            
        out_f.write("\nVulnerabilidades por severidad:\n")
        for severity, count in severity_counter.items():
            out_f.write(f" - {severity}: {count}\n")
            
    print(f"Análisis completado. Resumen guardado en: {evidence_path}")

if __name__ == "__main__":
    main()
