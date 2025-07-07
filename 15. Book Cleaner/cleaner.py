import os 
files = os.listdir()

for f in files:
    if f.startswith("_OceanofPDF"):
        name = f
        names = name.split("_")
        filename = " ".join(names[2:])
        try:
            os.rename(f,filename)
            print(f"File renamed from \n{f} \nto\n {filename}\n")
        except Exception as e:
            print(f"Error renaming the file \n{e}")
        