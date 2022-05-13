lista = []
for var in  [1,2,4,10]:
    lista.append(var)
    print(lista)
    print("São numeros pares")

for var in [1,3,5,7,9,11]:
    lista.append(var)
    print(lista)
    print("São números impares")
    cont=str(input("Deseja continuar?\ns-sim n-não\n"))

    if (cont == "s"):
        print("continuar operação\n")
        print(".....")

    else:
        print (cont == "n")
        print("fechar programa")
        break
    


