from pathlib import Path
from assemblage_classes import KansElement, Element, Faalmechanisme, Systeemkans


def main():
    for element in elementen:
        print(
            f"Element ID: {element.id}, Length: {element.L}, Faalmechanisme: {element.faalmechanisme.naam}, "
            f"Pf_dsn: {element.Pf_dsn.pof}, Pf_vak: {element.Pf_vak.pof}, Beta_dsn: {element.Pf_dsn.beta}")
    print("\nSysteemkans berekening:")
    print(f"Faalmechanisme: {systeemkans.faalmechanisme.naam}, Pf systeem: {systeemkans.systeemkans.pof}, "
          f"Beta systeem: {systeemkans.systeemkans.beta}")
    


if __name__ == "__main__":
    # Set the working directory to the workspace folder
    Path.cwd().joinpath("workspace").mkdir(parents=True, exist_ok=True)
    # set the input and output file paths
    INPUT_FILE = "input/input_voorbeeld.xlsx"
    OUTPUT_FOLDER = "output"
    OUTPUT_FILE = "output/Systeemkans_voorbeeld.xlsx"
    
    # define faalmechanismen
    overtopping = Faalmechanisme(
        id=1, 
        naam="Overtopping",
        beschrijving="Overtopping door hoge waterstand",
        dL=99000.0,
        wijze_van_opschaling=["MAX"]
    )

    # define elements
    el1 = Element(id=1, M_van=0.0, M_tot=100.0, a = 1.0,
                  faalmechanisme=overtopping,
                  Pf_dsn=KansElement(pof=0.001),
                  invloedsfactor_belasting=0.95,
                 )
    
    el2 = Element(id=2, M_van=100.0, M_tot=200.0, a = 1.0,
                  faalmechanisme=overtopping,
                  Pf_dsn=KansElement(pof=0.002),
                  invloedsfactor_belasting=0.95,
                 )
    
    elementen = [el1, el2]

    # calculate systeemkans
    systeemkans = Systeemkans(faalmechanisme=overtopping, elementen=elementen)
        
    main()
