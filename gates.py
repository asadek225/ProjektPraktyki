def qnot(vector, target):
    vector[target] = int(not vector[target])

def cnot(vector, target, control):
    if vector[control] == 1:
        qnot(vector, target)

def Toffoli(vector, target, control1, control2):
    if vector[control1] == 1 and vector[control2] == 1:
        qnot(vector, target)

def MCT(vector, target, *controls):
    if all(vector[i] for i in controls):
        qnot(vector, target)
