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
    
class LipidProfile:
    def __init__(self):
        self.results = {
            "Total Cholesterol (mg/dL)": None,
            "LDL Cholesterol (mg/dL)": None,
            "HDL Cholesterol (mg/dL)": None,
            "Triglycerides (mg/dL)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized lipid profile parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class ThyroidFunctionTest:
    def __init__(self):
        self.results = {
            "TSH (mIU/L)": None,
            "Free T4 (ng/dL)": None,
            "Free T3 (pg/mL)": None,
            "Total T4 (mcg/dL)": None,
            "Total T3 (ng/dL)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized thyroid function test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    

class LiverFunctionTest:
    def __init__(self):
        self.results = {
            "ALT (U/L)": None,
            "AST (U/L)": None,
            "Alkaline Phosphatase (U/L)": None,
            "Bilirubin Total (mg/dL)": None,
            "Bilirubin Direct (mg/dL)": None,
            "Bilirubin Indirect (mg/dL)": None,
            "Albumin (g/dL)": None,
            "Total Protein (g/dL)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized liver function test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])   
    

class RenalFunctionTest:
    def __init__(self):
        self.results = {
            "Creatinine (mg/dL)": None,
            "BUN (mg/dL)": None,
            "Uric Acid (mg/dL)": None,
            "eGFR (mL/min/1.73 m²)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized renal function test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class ImagingTest:
    def __init__(self):
        self.results = {
            "X-Ray": None,
            "CT Scan": None,
            "MRI": None,
            "Ultrasound": None,
            "PET Scan": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized imaging test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class MicrobiologyTest:
    def __init__(self):
        self.results = {
            "Culture": None,
            "Sensitivity": None,
            "Gram Stain": None,
            "PCR": None,
            "Antigen Test": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized microbiology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class PathologyTest:
    def __init__(self):
        self.results = {
            "Biopsy": None,
            "Cytology": None,
            "Histology": None,
            "Immunohistochemistry": None,
            "Molecular Pathology": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized pathology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class SerologyTest:
    def __init__(self):
        self.results = {
            "HIV": None,
            "Hepatitis B": None,
            "Hepatitis C": None,
            "Syphilis": None,
            "Rheumatoid Factor": None,
            "Antinuclear Antibody (ANA)": None,
            "C-Reactive Protein (CRP)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized serology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class RheumatologyTest:
    def __init__(self):
        self.results = {
            "Anti-CCP Antibodies": None,
            "Rheumatoid Factor": None,
            "ESR (mm/hr)": None,
            "CRP (mg/L)": None,
            "ANA": None,
            "Anti-dsDNA Antibodies": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized rheumatology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class CardiologyTest:
    def __init__(self):
        self.results = {
            "ECG": None,
            "Echocardiogram": None,
            "Stress Test": None,
            "Holter Monitor": None,
            "Cardiac Biomarkers": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized cardiology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class PulmonaryFunctionTest:
    def __init__(self):
        self.results = {
            "Spirometry": None,
            "Lung Volumes": None,
            "Diffusion Capacity": None,
            "Oximetry": None,
            "Arterial Blood Gases (ABG)": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized pulmonary function test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class GastroenterologyTest:
    def __init__(self):
        self.results = {
            "Endoscopy": None,
            "Colonoscopy": None,
            "Liver Biopsy": None,
            "Stool Tests": None,
            "H. pylori Test": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized gastroenterology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class DermatologyTest:
    def __init__(self):
        self.results = {
            "Skin Biopsy": None,
            "Patch Testing": None,
            "Dermatoscopy": None,
            "Fungal Culture": None,
            "Bacterial Culture": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized dermatology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class NeurologyTest:
    def __init__(self):
        self.results = {
            "EEG": None,
            "EMG": None,
            "Nerve Conduction Studies": None,
            "Lumbar Puncture": None,
            "Cerebral Angiography": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized neurology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class OncologyTest:
    def __init__(self):
        self.results = {
            "Tumor Markers": None,
            "Genetic Testing": None,
            "Imaging Studies": None,
            "Biopsy": None,
            "Pathology Report": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized oncology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class ImmunologyTest:
    def __init__(self):
        self.results = {
            "Immunoglobulins (IgG, IgA, IgM)": None,
            "Complement Levels (C3, C4)": None,
            "Allergy Testing": None,
            "Autoantibodies": None,
            "Vaccination Titers": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized immunology test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class GeneticsTest:
    def __init__(self):
        self.results = {
            "Genetic Screening": None,
            "Carrier Testing": None,
            "Whole Exome Sequencing": None,
            "Targeted Gene Panels": None,
            "Pharmacogenomics": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized genetics test parameter.")

    def get_results(self):
        return self.results

    def __str__(self):
        return ', '.join([f"{k}: {v}" for k, v in self.results.items() if v is not None])
    
class AllergyTest:
    def __init__(self):
        self.results = {
            "Skin Prick Test": None,
            "RAST Test": None,
            "Patch Test": None,
            "Food Allergy Panel": None,
            "Environmental Allergy Panel": None
        }

    def add_result(self, test_name, value):
        if test_name in self.results:
            self.results[test_name] = value
        else:
            raise ValueError(f"{test_name} is not a recognized allergy test parameter.")

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
john_electrolyte_test = ElectrolyteTest()
john_electrolyte_test.add_result( "Sodium (mmol/L)", 138)
john_urine_test.add_result("Color", "Pale Yellow")
john_urine_test.add_result("Appearance", "Clear")
john_blood_test.add_result("Hemoglobin (g/dL)", 15.5)
john_blood_test.add_result("White Blood Cells (thousand/uL)", 7.2)
john.add_lab(john_blood_test)
john.add_lab(john_urine_test)
john.add_lab(john_electrolyte_test)
print(john)

labs = john.get_labs()