
class init:
    def step(self):
        while True:
            print("Escolha qual calculo você quer fazer:\n")
            a=int(input('1soma-2subtração-3divisão-4multiplicacao\n'))

            if(a==1):self.soma()
            if(a==2):self.subtracao()
            if(a==3):self.divisao()
            if(a==4):self.multiplicacao()
            
            cont=str(input("deseja continuar a operação?\ny-sim n-não\n"))
            if(cont=="y"):
                print("Proxima operação")
                print("........")
                
            
            elif(cont=="n"):
                print("Fechar o progrrama")
                break


    def soma(self):

        soma1=float(input("Digite o valor 1"))
        soma2=float(input("Digite o valor 2\n"))
        calculo=float(soma1+soma2)
        print(f"o resultado do calculo é:\n{calculo}")


    def subtracao(self):

        subtracao1=float(input("Digite o valor 1"))
        subtracao2=float(input("Digite o valor 2\n"))
        calculo=float(subtracao1+subtracao2)
        print(f"o resultado do calculo é:\n{calculo}")

    def divisao(self):

        divisao1=float(input("Digite o valor 1"))
        divisao2=float(input("Digite o valor 2\n"))
        calculo=float(divisao1+divisao2)
        print(f"o resultado do calculo é:\n{calculo}")

    def multiplicacao(self):

        multiplicacao1=float(input("Digite o valor 1"))
        multiplicacao2=float(input("Digite o valor 2\n"))
        calculo=float(multiplicacao1+multiplicacao2)
        print(f"o resultado do calculo é:\n{calculo}")




start=init()
start.step()
     



    

    

    


  