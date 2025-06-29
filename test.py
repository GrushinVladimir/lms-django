var_1 = False
var_2 = "False11"

var_1 = int(var_1)
var_1 = var_2
var_2 = str(var_2)
var_2 += str(var_1)
var_1 = str(var_1) + str(bool(var_2))
var_1 = var_2 + var_1
var_2 = bool(var_1)

print("var_1 =", var_1[0:12]) 
print("var_2 =", var_2)