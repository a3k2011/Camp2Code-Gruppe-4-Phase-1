import sys
import time
import basecar_tim as BC
import soniccar_tim as SC


def main():

    # Cars erstellen
    bc = BC.BaseCar()
    sc = SC.SonicCar()

    # Test Fahrparcour 1
    #bc.fp1(50)

    # Test Fahrparcour 2
    #bc.fp2(50)

    # Test Fahrparcour 3
    #sc.fp3(50)

    # Test Fahrparcour 4
    if len(sys.argv) >= 2:
        try:
            for arg in sys.argv[1:]:
                int(arg)
            
            if len(sys.argv) == 3:
                sc.fp4(int(sys.argv[1]), int(sys.argv[2]))
            else:
                sc.fp4(int(sys.argv[1]))

        except Exception:
            print("Nur Zahlenwerte erlaubt!")


if __name__ == '__main__':
    main()