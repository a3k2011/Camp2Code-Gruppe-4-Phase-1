import PiCar

def main():
    '''
        Main-Programm: Manuelles Ansteuern der implementierten Fahrparcours 1-6

        Args[Klassen]:
                        PiCar.BaseCar()
                        PiCar.Sonic()
                        PiCar.SensorCar()
        Funktionen der Klassen:
                        fp1() - fp6()
        Args[Fahrparcour]:
                        v (int): Geschwindigkeit. Default 50
    '''
    myCar = PiCar.SensorCar()

    #myCar.fp1(v=50)

    #myCar.fp2(v=50)

    #myCar.fp3(v=50)

    #myCar.fp4(v=50)

    myCar.fp5(v=50)


if __name__ == "__main__":
    main()