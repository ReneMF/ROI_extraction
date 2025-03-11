import os
import pandas as pd

# ✅ Carpeta raíz de los datos
# DATA_FOLDER = 'Data'
DATA_FOLDER = '/Volumes/Seagate_Rene/MigrarAlemania/Postdoc_DrMed_UniZuKoeln/Proyecto_OCD-TS/Datos_OCD'

# ✅ Nombres de pacientes
PAT_NAME = ['FaCe']

# PAT_NAME = ['FaCe', 'FuHe', 'GeDr', 'GeMa', 'HeBe', 'HeKa', 'KnJo', 'KoJa',
#             'KuMa', 'LiOt', 'MiSo', 'MoEl', 'NeCa', 'RaRe', 'RoMa', 'ScDa',
#             'SpSa', 'WeBe', 'WoMu']

# ✅ Subcarpeta donde están los archivos de cada paciente
PAT_FILES = '{}/dsistudio_new'

# ✅ Archivos CSV a revisar en cada paciente
FILENAME_PATTERNS = [
    'count_MNI_ROI_2_DWI_R_dsi_new.tck_CerebrA_cg.csv',
    'count_MNI_ROI_2_DWI_L_dsi_new.tck_CerebrA_cg.csv',
    'count_STN_limbic_rh_dsi_new.tck_CerebrA_cg.csv',
    'count_STN_limbic_lh_dsi_new.tck_CerebrA_cg.csv',
    'count_1M_NAc_r_49_dsi_new.tck_CerebrA_cg.csv',
    'count_1M_NAc_l_42_dsi_new.tck_CerebrA_cg.csv'
]

# ✅ ROIs a extraer (atlas CerebrA)
# --------------------------------------------------------------------------------
# Los códigos 'A98', 'A47', etc., indican las celdas específicas en el archivo 
# .csv de entrada desde donde se extraerán los valores que formarán parte del 
# archivo de resultados. Cada código corresponde a una región anatómica de 
# interés (ROI) y representa su identificador único dentro del atlas CerebrA.
# --------------------------------------------------------------------------------
ROIs = {
    'Amygdala': {'Right': 'A98', 'Left': 'A47'},
    'Accumbens': {'Right': 'A99', 'Left': 'A48'},
    'Medial_Orbitofrontal': {'Right': 'A65', 'Left': 'A14'},
    'Lateral_Orbitofrontal': {'Right': 'A63', 'Left': 'A12'},
    'Rostral_Anterior_Cingulate': {'Right': 'A77', 'Left': 'A26'},
    'Insula': {'Right': 'A84', 'Left': 'A33'},
    'Rostral_Middle_Frontal': {'Right': 'A78', 'Left': 'A27'},
    'Pallidum': {'Right': 'A96', 'Left': 'A32'},
    'Precentral': {'Right': 'A75', 'Left': 'A24'},
    'Paracentral': {'Right': 'A68', 'Left': 'A17'},
    'Superior_Frontal': {'Right': 'A79', 'Left': 'A16'}
}

# ✅ Ruta de salida y nombre del archivo con los resultados
# OUTPUT_FOLDER = 'Dr_Med_OCD_Nac-ALIC_amSTN/OCD_ROI_data'
OUTPUT_FOLDER = '/Users/neuroclinet/Documents/Dr_Med_OCD_Nac-ALIC_amSTN/OCD_ROI_data'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)  
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, 'resultados_roi_OCD.csv')

# -------------------------------
# ✅ Funciones del pipeline
# -------------------------------

def get_patient_files(patient_folder):
    """
    Devuelve los paths completos de los archivos de tractografía para un paciente.
    """
    files = []
    for pattern in FILENAME_PATTERNS:
        full_path = os.path.join(patient_folder, pattern)
        if os.path.exists(full_path):
            files.append(full_path)
        else:
            print(f"⚠️ Archivo no encontrado: {full_path}")
    return files


def extract_roi_values(file_path, patient_name):
    """
    Extrae los valores de las ROIs especificadas desde un archivo CSV.
    """
    extracted_data = []

    try:
        # ✅ Leer CSV separado por tabulador
        df = pd.read_csv(file_path, sep='\t', header=1)
    except Exception as e:
        print(f"❌ Error leyendo el archivo {file_path}: {e}")
        return extracted_data

    # Normalizamos la columna de ROI eliminando espacios en blanco
    value_column = df.columns[0]
    roi_column = df.columns[1]
    df[roi_column] = df[roi_column].astype(str).str.strip()

    print(f"\n🔍 Procesando archivo: {os.path.basename(file_path)}")

    for roi_name, sides in ROIs.items():
        for side, code in sides.items():
            code = f"{side}_{roi_name}"

            roi_row = df[df[roi_column] == code]

            if not roi_row.empty:
                value = roi_row[value_column].values[0]
                print(f"✅ {roi_name} ({side}) - Código {code}: Valor {value}")
            else:
                value = None
                print(f"⚠️ ROI {roi_name} ({side}) con código {code} no encontrado en {file_path}")

            extracted_data.append({
                'Paciente': patient_name,
                'Archivo': os.path.basename(file_path),
                'ROI': roi_name,
                'Lado': side,
                'Codigo_ROI': code,
                'Valor': value
            })

    return extracted_data


def process_all_patients():
    """
    Procesa todos los pacientes y guarda los resultados en un archivo CSV.
    """
    all_results = []

    for patient_name in PAT_NAME:
        patient_folder = os.path.join(DATA_FOLDER, PAT_FILES.format(patient_name))

        if not os.path.isdir(patient_folder):
            print(f"❌ Carpeta no encontrada para paciente {patient_name}: {patient_folder}")
            continue

        print(f"\n🚀 Procesando paciente: {patient_name}")

        patient_files = get_patient_files(patient_folder)

        for file_path in patient_files:
            results = extract_roi_values(file_path, patient_name)
            all_results.extend(results)

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    df_resultados = pd.DataFrame(all_results)

    df_resultados.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Resultados exportados a: {OUTPUT_FILE}")


# -----------------------
# ✅ Ejecutar el script
# -----------------------
if __name__ == '__main__':
    process_all_patients()
