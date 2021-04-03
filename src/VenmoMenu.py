import VenmoToolbox
import getpass


class MenuOption():
        def __init__(self, optionID, optionMsg, optionCallback):
            
            self.__optionId = optionID
            self.__optionMsg = optionMsg
            self.__optionCallback = optionCallback

        def __str__(self) -> str:
            
            return  str(self.__optionId) + ") " + self.__optionMsg

        def call(self) -> None:
            
            self.__optionCallback()
       
class Menu():

    def __init__(self, name, header = ""):
        
        self.__name = name
        self.__header = header
        self.__options : list[MenuOption] = list()
        self.__menuActive = False

    def __str__(self) -> str:
        
        finalString = str()

        finalString +="\n----------------------------------\n"
        
        finalString += self.__name + "\n"
        
        finalString += self.__header + "\n"

        for option in self.__options:
        
            finalString += "\t" + str(option) + "\n"

        return finalString

    def addOption(self, optionMsg, callback) -> None:
        self.__options.append(MenuOption(len(self.__options) + 1, optionMsg, callback))

    def setHeader(self, header) -> None:
        self.__header = header

    def callOption(self, optionNumber) -> None:

        if (optionNumber > len(self.__options) or optionNumber <= 0):
        
            print("Not A Valid Option")
        
        else:
        
            self.__options[optionNumber-1].call()

    def showMenu(self):

        self.__menuActive = True

        while (self.__menuActive):

            print(self)

            choice = input("Enter selection then hit enter:\n:>")

            try:
            
                choice = int(choice)
                self.callOption(choice)

            except ValueError as e:
            
                print("Not a valid number")

                print("\n")

    def exit(self):
        self.__menuActive = False




class VenmoUser():
    def __init__(self, userInfo, toolbox : VenmoToolbox.VenmoToolbox):
        self.__userInfo = userInfo
        self.__id = int(userInfo["id"])
        self.__username = userInfo["username"]
        self.__firstName = userInfo["first_name"]
        self.__lastName = userInfo["last_name"]
        self.__friendStatus = userInfo["friend_status"]
        self.__toolbox = toolbox

    def isFriend(self) -> bool:

        status = self.__friendStatus

        if (status == "friend"):
            return True
        
        return False

    def getFriendStatus(self) -> bool:

        status = self.__friendStatus


        if (self.isFriend()):
            print("Already friends.")
            return True

        if (status == "not_friends"):
            print("Not friends.")
            return False

        if (status == "request_sent_by_you"):
            print("Friend request from you to them is pending.")
            return False

        if (status == "request_received_by_you"):
            print("Friend request from them to you is pending.")
            return False

        print("Unknown friend status: " + status)
        return False

    def sendFriendRequest(self) -> None:
        if (not self.getFriendStatus()):
            if (self.__toolbox.sendFriendRequestByUserID(self.__id)):
                print("Friend request successfully sent.")
            else:
                print("Failed to send a friend request.")
        else:
            print("Friend request not sent.")



class VenmoMenu():

    def __init__(self):
        self.__toolbox = VenmoToolbox.VenmoToolbox()
        



    def login(self) -> bool:

        successfulLogin = self.__toolbox.login()

        if (successfulLogin):
            return True

        username = input("Enter your venmo username or email.\n:>")
        password = getpass.getpass("Enter you password. It will not show on screen but input is being received.\n:>")

        successfulLogin = self.__toolbox.login(username,password)

        if (not successfulLogin):
            print("Unable to login.")
            return False


        return True



    def run(self) -> None:

        if (not self.__toolbox.authenticated()):
            print("User not logged in.")
            return

        menu = Menu("Main Menu")
        menu.setHeader("Account :" + " " + self.__toolbox.username)
        menu.addOption("Send Money", self.l)
        menu.addOption("Request Money", self.l)
        menu.addOption("Show Account Information", self.__displayAccInfoHandler)
        menu.addOption("Show Account Venmo Balance", self.__getBalance)
        menu.addOption("List Friends", self.__listFriends)
        menu.addOption("Show Payment Methods", self.__getPaymentMethods)
        menu.addOption("Get A Users Id By Username", self.__getUserIDByUsername)
        menu.addOption("Get A Username By User ID", self.__getUsernameByUserID)
        menu.addOption("Get A Users Information", self.__getUserInformationHandler)
        menu.addOption("User lookup with user action menu", self.__userLookUpWithMenu)
        menu.addOption("Exit", menu.exit)
        menu.showMenu()


    def l(self):
        pass


    def __userLookUpWithMenu(self) -> None:

        try:
            id  = int(input("Enter 1 if you want to find a user by userID or 0 if by username.\n:>"))

            userInfo = {}

            if (id == 1 or id == 0):
                
                if (id):

                    userID = input("Enter the users userID.\n:>")

                    userInfo = self.__toolbox.getUserInformationByID(userID)

                else:

                    username = input("Enter the username of the user.\n:>")

                    userInfo = self.__toolbox.getUserInformationByUsername(username)

            else:

                print("Not a valid option.")


            if (userInfo.get("error", "") != ""):
                print("Failed to find user.")
                return


            userMenu  = self.__createUserMenu(userInfo["data"])
            userMenu.showMenu()


        except ValueError as e:

            print("Not a valid number.")



    def __createUserMenu(self, userData) -> Menu:

        menu = Menu("User Menu")
        user = VenmoUser(userData, self.__toolbox)
        
        menu.setHeader("Acccout:\n\tUsername: {}\n\tID: {}\n\tName: {} {}".format(userData["username"], userData["id"], userData["first_name"], userData["last_name"]))
        menu.addOption("Is Friend?", lambda : print("Friend Status: " + userData["friend_status"]))
        menu.addOption("Send Friend Request", user.sendFriendRequest)

        menu.addOption("Exit", menu.exit)

        return menu



    def __getPaymentMethods(self):

        paymentMethods = self.__toolbox.getPaymentMethods()
        print("")


        if (paymentMethods.get("data", "") == ""):
            print("Error getting payment methods data.")
            return


        for method in paymentMethods["data"]:
            print("Type: " + method["type"])
            print("Name: " + method["name"])
            print("Last-Four: " + str(method["last_four"]))
            print("ID: " + method["id"])
            print("")

    def __listFriends(self):

        friends = self.__toolbox.getFriends()

        if (friends.get("data", "") != ""):
            for friend in friends["data"]:
                print("")
                print("Name: " + friend["first_name"] + " "  + friend["last_name"])
                print("Username: " + friend["username"])
                print("ID: "  + friend["id"])
        else:
            print("Error getting friend data.")


    def __getBalance(self) -> None:
        print("\nBalance: " + str(self.__toolbox.getBalance()) )


    def __getUsernameByUserID(self) -> None:
        userID  = input("Enter the userID of the person to lookup.\n:>")

        try:
            print("\n" + self.__toolbox.getUsernameByUserID(userID))
        except ValueError as e:
            print("Not a valid number.")



    def __getUserIDByUsername(self) -> int:
        username = input("Enter the username of ther person to lookup.\n:>")

        userID  = self.__toolbox.getUserIDByUsername(username)

        if (userID == -1):
            print("Could not find that username.")
            return - 1

        print("\nUsername:", username, "UserID:", userID)
        return  userID

    def __getUserInformationHandler(self) -> None:

        try:
            id  = int(input("Enter 1 if you want to get a users information by userID or 0 if by username.\n:>"))

            userInfo = {}

            if (id == 1 or id == 0):
                
                if (id):

                    userID = input("Enter the users userID.\n:>")

                    userInfo = self.__toolbox.getUserInformationByID(userID)

                else:

                    username = input("Enter the username of the user.\n:>")

                    userInfo = self.__toolbox.getUserInformationByUsername(username)

                self.__enumerateAndPrintDict(userInfo)

            else:

                print("Not a valid option.")

        except ValueError as e:

            print("Not a valid number.")



    def __displayAccInfoHandler(self) -> None:

        level = input("Enter how much data you would like on a scale of 0-3 and hit enter, or enter 4 to see your oauth token.\n:>")

        try:
            level = int(level)
            self.__displayAccountInfo(level)

        except ValueError as e:
            print("Not a valid number.")

            
            
    def __displayAccountInfo(self, verboseLevel = 0) -> None:
        print("")
        if (verboseLevel == 0):

            print("First Name :", self.__toolbox.loginJson["user"]["first_name"])
        
            print("Username :", self.__toolbox.username)

        elif (verboseLevel == 1):

            print("First Name :", self.__toolbox.loginJson["user"]["first_name"])
            print("Username :", self.__toolbox.username)
            print("Userid :", self.__toolbox.userid)
            print("Device-ID :", self.__toolbox.deviceID)

        elif (verboseLevel == 2):

            for key in self.__toolbox.loginJson["user"]:

                print(key[0].upper() + key[1:] + " :", self.__toolbox.loginJson["user"][key])

            print("Balance :", self.__toolbox.loginJson["balance"])

        elif (verboseLevel == 3):

            self.enumerateAndPrintDict(self.__toolbox.accJson)
        
        elif (verboseLevel == 4):
        
            print("Authorization Token : " + self.__toolbox.bearerToken)
        
        else:
        
            print("Not a valid verbose level. Please enter a level 0-3, 0 being the least amount of info and 3 being the most. Enter 4 to see your oauth token.")



    def __enumerateAndPrintDict(self, object) -> None:
        
        for key in object:
        
            if (type(object[key]) == type(dict())):
        
                self.__enumerateAndPrintDict(object[key])
        
            else:
        
                print(key[0].upper() + key[1:] + " :", object[key])



