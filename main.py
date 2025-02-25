import s3
import route53
import ec2


try:
    while True:
        option = input("which aws service would you like to use:\n[1]s3\n[2]route53\n[3]ec2\n")
        if option == "1":
            s3.main()
        elif option == "2":
            route53.main()
        elif option == "3":
            ec2.main()
        else:
            print("you typed something wrong")

        ask_for_stop = input("would you like to use another service?: ").lower()
        if ask_for_stop != "yes":
            break

except KeyboardInterrupt:
    exit()
        