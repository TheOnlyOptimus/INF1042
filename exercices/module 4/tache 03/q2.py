import math

def distance_origine(point):
    x, y = point
    return math.sqrt(x**2 + y**2)

# Test
print(distance_origine((3, 4)))  # 5.0