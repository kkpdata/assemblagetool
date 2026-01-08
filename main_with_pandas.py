from pathlib import Path
from assemblage_functions import bepaal_N_vak, combin_seriesysteem
import pandas as pd
import numpy as np

def read_input_data(input_file: str, tabblad_componenten: str, tabblad_faalmechanismen: str):
    # Read componenten data
    componenten_df = pd.read_excel(input_file, sheet_name=tabblad_componenten)
    # Read faalmechanismen data
    faalmechanismen_df = pd.read_excel(input_file, sheet_name=tabblad_faalmechanismen)
    # merge delta_L and type_assemblage_tussen_vakken from faalmechanismen to componenten
    componenten_df = componenten_df.merge(faalmechanismen_df[['id', 'delta_L', 'type_assemblage_tussen_vakken']], left_on='id_initieel_mechanisme', right_on='id', how='left')
    return componenten_df


if __name__ == "__main__":
    # Set the working directory to the workspace folder within the current directory
    wd = Path.cwd().joinpath("workspace")
    # set the input and output file paths
    INPUT_FILE = "input/input_stph.xlsx"
    TABBLAD_COMPONENTEN = "componenten"
    TABBLAD_FAALMECHANISMEN = "faalmechanismen"
    OUTPUT_FOLDER = "output"
    OUTPUT_FILE_VAKKANSEN = "output/Vakkansen_voorbeeld.xlsx"
    
    # Read input data
    componenten_df = read_input_data(str(Path(wd, INPUT_FILE)), TABBLAD_COMPONENTEN, TABBLAD_FAALMECHANISMEN)
    # Calculate N_vak for each row in the dataframe
    componenten_df['N_vak'] = np.vectorize(bepaal_N_vak)(
        componenten_df['lengte'],
        componenten_df['a'],
        componenten_df['delta_L']
    )
    # Calcuate vakkansen
    componenten_df['pf_vak'] = componenten_df['pf_dsn'] * componenten_df['N_vak']
    # Save vakkansen to excel
    componenten_df.to_excel(str(Path(wd, OUTPUT_FILE_VAKKANSEN)), index=False)
    # Calculate onder en bovengrenzen voor seriesysteem
    # bovengrens gaat uit van volledig onafhankelijke componenten (SOM)
    # ondergrens gaat uit van volledig afhankelijke componenten (MAX)
    pfs = componenten_df['pf_vak'].to_numpy()
    pf_ondergrens, pf_bovengrens = combin_seriesysteem(pfs)
    print(f"Ondergrens systeemkans: {pf_ondergrens} met een terugkeertijd van {1/pf_ondergrens:.0f} jaar")
    print(f"Bovengrens systeemkans: {pf_bovengrens} met een terugkeertijd van {1/pf_bovengrens:.0f} jaar")
    