def regular_expressions(line):
    line = line.replace("l0", "10")
    line = line.replace("l9", "19")
    line = line.replace("J ", "J")
    line = line.replace(":11e", ":lle")
    line = line.replace(":]le", ":lle")
    line = line.replace(" 111 ", " III ")
    line = line.replace("[V", "IV")
    line = line.replace(":]ta", ":lta")
    return line

def regular_expressions_number(line):
    line = line.replace("I", "1")
    line = line.replace("l", "1")
    line = line.replace("'1", "1")  # entry 964
    line = line.replace("]", "1")   # entry 1317
    line = line.replace("1O", "10") # 1576
    line = line.replace("S", "5")   # 1607
    line = line.replace("3O", "30") # 2042
    line = line.replace("Z", "2")   # 2132
    line = line.replace("[", "1")   # 2659
    return line

def regular_expressions_month(line):
    line = line.replace("1", "I")
    line = line.replace("l", "I")
    line = line.replace("Xll", "XII")
    line = line.replace("V111", "VIII")   # 1656
    return line