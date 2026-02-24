import math
from datetime import date
import random
from datetime import datetime, timedelta

# 1.
print(math.pi)

# 2. 
print(random.randint(1, 100))

# 3. 
print(date.today())

# 4.
maintenant = datetime.now()
dans_100_heures = maintenant + timedelta(hours=100)
print(dans_100_heures)

# 5.
def aire_cercle(diametre):
    rayon = diametre / 2
    return math.pi * rayon ** 2

