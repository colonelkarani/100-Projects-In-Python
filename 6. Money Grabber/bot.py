class Bird():
    def __init__(self, name):
        self.name = name

    is_hungry = True
    health = 50


    def feed_birds(self, food):
        self.health +=20
        if (self.is_hungry == True):
            self.is_hungry = False
        print(f"Feeding birds with {food}\n Is the bird hungry? {self.is_hungry}")

    def check_stomach(self):
        print(f"Is the bird hungry? {self.is_hungry}")

    def check_health(self):
        print(f"The health of {self.name} is {self.health}")

    def shoot_bird(self):
        print("pu pu "*4)
        print(f"the {self.name} has been shot😟")
        self.health = 0

parrot = Bird("Parrot")
parrot.check_health()
print("")
parrot.feed_birds("Biscuit")

print("")
parrot.feed_birds("Banana")
print("")

parrot.check_health()
print("")
parrot.shoot_bird()
print("")
parrot.check_health()
