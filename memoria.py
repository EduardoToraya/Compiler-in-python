import sys
class Memoria:
    def __init__(self):
        # address valor
        self.__values = {}

    def set_value(self, address, value):
        self.__values[address] = value

    def get_value(self, address):
        if address not in self.__values:
            #print(self.__values)
            print("Error. La direccion no se encuentra en este ambiente")
            sys.exit()
        return self.__values[address]
