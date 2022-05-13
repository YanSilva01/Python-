#Processamento de Dados 6
lista = []
valor = int(input("Qual é a Tabuada?"))

tab = 0

print('*'*10)
print("A tabuada de {}".format(valor))
print('*'*10)

for var in range(0,11):
    print("{} X {}= {}".format(tab,valor,(tab * valor)))
    tab = tab + 1

