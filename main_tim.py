import sys
import time
import basecar_tim as BC
import soniccar_tim as SC
import infraredcar_tim as IC


def main():

    # Cars erstellen
    bc = BC.BaseCar()
    sc = SC.SonicCar()
    ic = IC.InfraredCar()

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

    # Test Infrarot
    #ic.infrarot_test(50)

    # Test Fahrparcour 5
    #ic.fp5(40)

    # Test Fahrparcour 6
    ic.fp6(50)


if __name__ == '__main__':
    main()