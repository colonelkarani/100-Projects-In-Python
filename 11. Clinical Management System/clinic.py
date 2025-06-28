class BloodTest:
    def __init__(self):
        self.results = {
            "Hemoglobin (g/dL)": None,
            "Hematocrit (%)": None,
            "Red Blood Cells (million/uL)": None,
            "White Blood Cells (thousand/uL)": None,
            "Platelets (thousand/uL)": None,
            "MCV (fL)": None,
            "MCH (pg)": None,
            "MCHC (g/dL)": None,
            "RDW (%)": None,
            "Neutrophils (%)": None,
            "Lymphocytes (%)": None,
            "Monocytes (%)": None,
            "Eosinophils (%)": None,
            "Basophils (%)": None,
            "Glucose (mg/dL)": None,
            "Creatinine (mg/dL)": None,
            "Urea (mg/dL)": None,
            "Sodium (mmol/L)": None,
            "Potassium (mmol/L)": None,
            "Chloride (mmol/L)": None,
            "Calcium (mg/dL)": None,
            "Total Protein (g/dL)": None,
            "Albumin (g/dL)": None,
            "ALT (U/L)": None,
            "AST (U/L)": None,
            "Alkaline Phosphatase (U/L)": None,
            "Bilirubin Total (mg/dL)": None,
            "Bilirubin Direct (mg/dL)": None,
            "Bilirubin Indirect (mg/dL)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized blood test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])


class ElectrolyteTest:
    def __init__(self):
        self.results = {
            "Sodium (mmol/L)": None,
            "Potassium (mmol/L)": None,
            "Chloride (mmol/L)": None,
            "Bicarbonate (mmol/L)": None,
            "Calcium (mg/dL)": None,
            "Phosphorus (mg/dL)": None,
            "Magnesium (mg/dL)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized electrolyte test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])  

class UrineTest:
    def __init__(self):
        self.results = {
            "Color": None,
            "Appearance": None,
            "Specific Gravity": None,
            "pH": None,
            "Protein": None,
            "Glucose": None,
            "Ketones": None,
            "Bilirubin": None,
            "Urobilinogen": None,
            "Nitrite": None,
            "Leukocyte Esterase": None,
            "Blood": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized urine test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])

class Labs:
    def __init__(self):
        self.lab_records = {}
    def add_lab(self, lab):
            lab_name = getattr(lab, 'name', lab.__class__.__name__)
            self.lab_records[lab_name] = lab
       

    def get_labs(self):
        return self.lab_records

    def __str__(self):
        if not self.lab_records:
            return "No labs recorded."
        return '; '.join([f"{name}: {lab}" for name, lab in self.lab_records.items()])
    
class Patient:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.labs = Labs()

    def add_lab(self, lab):
        self.labs.add_lab(lab)

    def get_labs(self):
        return self.labs.get_labs()
    
    def check_anaemia(self):
        blood_test = self.labs.get_labs().get('BloodTest')
        if blood_test:
            hemoglobin = blood_test.results.get("Hemoglobin (g/dL)")
            if hemoglobin is not None:
                if hemoglobin < 13.5:  
                    return "Patient is likely to be anaemic."
                else:
                    return "Patient is not anaemic." 

    def __str__(self):
        return f"Patient: {self.name}, Age: {self.age}, Labs: {self.labs}"
    

john = Patient("John Doe", 30)
john_blood_test = BloodTest()
john_urine_test = UrineTest()   
john_urine_test.add_result("Color", "Pale Yellow")
john_urine_test.add_result("Appearance", "Clear")
john_blood_test.add_result("Hemoglobin (g/dL)", 15.5)
john_blood_test.add_result("White Blood Cells (thousand/uL)", 7.2)
john.add_lab(john_blood_test)
john.add_lab(john_urine_test)
print(john)

labs = john.get_labs()