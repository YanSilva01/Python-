#Entrada de dados

custof=float (input("Digite o valor do custof:"))
distri=float((custof*28)/100)
imposto=float((custof*45)/100)

#Processamento de dados

custo=float(custof+distri+imposto)
print(f"O preço do carro é: {custo:.2f}")


