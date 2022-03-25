import sys
import time
import basecar_tim as BC
import soniccar_tim as SC
import fahrparcour_tim as fp


def testeSpeed(bc):
    print("+"*20 + "Starte Test Speed:" + "+"*20)
    print("Speed 1:", bc.speed)
    bc.speed = 55
    time.sleep(2)
    print("Speed 2:", bc.speed)
    bc.stop()
    print("Speed 3:", bc.speed)

def testeSteeringAngle(bc):
    print("+"*20 + "Starte Test Steering Angle:" + "+"*20)
    print("Steering Angle 1:", bc.steering_angle)
    bc.steering_angle = 45
    time.sleep(1)
    print("Steering Angle 2:", bc.steering_angle)
    bc.steering_angle = 135
    time.sleep(1)
    print("Steering Angle 3:", bc.steering_angle)
    bc.steering_angle = 90
    print("Steering Angle 4:", bc.steering_angle)

def testeDirection(bc):
    print("+"*20 + "Starte Test Direction:" + "+"*20)
    print("Direction 1:", bc.direction)
    testeSpeed(bc)
    time.sleep(1)
    bc.direction = 2
    print("Direction 2:", bc.direction)
    testeSpeed(bc)
    time.sleep(1)
    bc.direction = -1
    print("Direction 3:", bc.direction)
    testeSpeed(bc)
    time.sleep(1)
    bc.direction = 0
    print("Direction 4:", bc.direction)
    testeSpeed(bc)


def main():

    # Cars erstellen
    #bc = BC.BaseCar()
    sc = SC.SonicCar()

    # Test Manuell
    #bc.speed = 30
    #time.sleep(3)
    #bc.direction = -1
    #time.sleep(3)
    #bc.direction = 0
    #time.sleep(3)
    #bc.stop()

    # Teste Drive Funktion
    #bc.drive(80, 1)
    #time.sleep(2)
    #bc.drive(30, -1)
    #time.sleep(2)
    #bc.drive(100, 0)
    #time.sleep(2)
    #bc.stop()

    # Test Speed
    #testeSpeed(bc)
    #testeSpeed(sc)

    # Test Steering Angle
    #testeSteeringAngle(bc)
    #testeSteeringAngle(sc)

    # Test Direction
    #testeDirection(bc)
    #testeDirection(sc)

    # Test Fahrparcour1
    #fp.fahrparcour1(bc, 50)
    #fp.fahrparcour1(sc, 50)

    # Test Fahrparcour2
    #fp.fahrparcour2(bc, 50)
    #fp.fahrparcour2(sc, 50)

    # Test Distanz
    #for i in range(5):
    #    print("Aktueller Abstand zum Hindernis:", sc.getDistance())
    #    time.sleep(1)

    # Teste erkundeWelt (Fahrparcour 4)
    if len(sys.argv) >= 2:
        scWelt = SC.SonicCar()
        try:
            for arg in sys.argv[1:]:
                int(arg)
            
            if len(sys.argv) == 3:
                scWelt.erkundeWelt(int(sys.argv[1]), int(sys.argv[2]))
            else:
                scWelt.erkundeWelt(int(sys.argv[1]))

        except Exception:
            print("Nur Zahlenwerte erlaubt!")


if __name__ == '__main__':
    main()