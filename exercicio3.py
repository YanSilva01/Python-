from __future__ import barry_as_FLUFL
import math
while True:
    tintas=float(input("Informe a quantidade de metro quadrado pintado?"))
    litros=tintas/3
    lata= math.ceil(litros/18)
    preco= lata *80

    print("o preço é:",preco)

    print(f"você tera de comprar",lata,"de tintas!")

    cont=str(input("deseja continuar a operação?\ny-sim n-não\n"))
    if(cont=="y"):
        print("Proxima operação")
        print("........")
                
            
    elif(cont=="n"):
         print("Fechar o programa")
    break









