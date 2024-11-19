import pyomo.environ as pyo
from pyomo.opt import SolverFactory

def solve_mps_with_glpk(mps_file):
    # Lade das MPS-Problem als ConcreteModel
    model = pyo.ConcreteModel()

    # Lade die MPS-Datei mit der pyomo.environ.read Methode
    instance = model.create_instance(mps_file)

    # Erstelle den Solver (hier verwenden wir GLPK)
    opt = SolverFactory('glpk')

    # Lösen des Modells
    results = opt.solve(instance)

    if results.solver.status == pyo.SolverStatus.ok:
        print("Das Modell wurde erfolgreich gelöst!")

        # Ausgabe der Werte der Variablen
        print("\nLösungswerte der Variablen:")
        for var in instance.component_data_objects(pyo.Var):
            print(f"Variable {var.name}: {var.value}")
        
        # Optional: Weitere Informationen zur Lösung ausgeben
        print("\nWeitere Ergebnisse:")
        print(results)

    else:
        print("Es gab ein Problem beim Lösen des Modells.")