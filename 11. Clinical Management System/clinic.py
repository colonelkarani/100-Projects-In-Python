from lab import *


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
            else:
                return "The blood test is there but the haemoglobin is not sampled" 
        else:
            return "There is no blood test to analyze"
    def __str__(self):
        return f"Patient: {self.name}, Age: {self.age}, Labs: {self.labs}"      
    



# john = Patient("John Doe", 30)
# john_blood_test = BloodTest()
# john_urine_test = UrineTest()   
# john_electrolyte_test = ElectrolyteTest()
# john_electrolyte_test.add_result( "Sodium (mmol/L)", 138)
# john_urine_test.add_result("Color", "Pale Yellow")
# john_urine_test.add_result("Appearance", "Clear")
# john_blood_test.add_result("Hemoglobin (g/dL)", 15.5)
# john_blood_test.add_result("White Blood Cells (thousand/uL)", 7.2)
# john.add_lab(john_blood_test)
# john.add_lab(john_urine_test)
# john.add_lab(john_electrolyte_test)
# print(john)

# labs = john.get_labs()

    
patients = [""]*3
for i in range(len(patients)):
    patient_name = input("Add patient name\n")
    age = int(input("Enter patient age: \n"))  
    patients[i] =Patient(patient_name, age)
    print(f"Patient added: \n name :{patients[i].name}\n age {patients[i].age}")

