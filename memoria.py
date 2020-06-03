import sys
#Clase de manejo de memoria con get y set properties privada.
class Memoria:
    def __init__(self):
        # address valor
        self.__values = {}

    def set_value(self, address, value):
        #print(self.__values)
        self.__values[address] = value

    def get_value(self, address):
        #print(self.__values)
        if address not in self.__values:
            #print(address)
            #print(self.__values)
            print("Error. La direccion no se encuentra en este ambiente")
            sys.exit()
        return self.__values[address]
