import requests
import json
from random import randint, choice
from string import ascii_uppercase




class VenmoToolbox():
    """
        Brief:
            Wrapper class for the venmo api. Exposes functionality via class methods. It is not static and an instance in required to use said functionality.

        Instance Variables:
            @var `bearerToken : str`
                    -oauth2 auth token
            @var `username : str`
                    -logged in user's username
            @var `userID : str`
                    -logged in user's venmo ID
            @var `session : requests.Session` 
                    -session object to persist cookies across api calls
            @var `deviceID : str`
                    -current device id that venmo see's when you log in. Can be stored to remember device and not have to log in using 2FA next time.
            @var `autoLogOut : bool` 
                    -boolean that dictates whether to send the request to revoke the auth token on instance destruction. By default venmo does not revoke the tokens but the default value for this variable is True.
            @var `loginJson : dict`
                    -json that is returned on first login. Contains some user information
            @var `accJson : dict`
                    -json containing all of the accuonts information
            @var `fName : str`
                    -logged in user's first name according to the venmo account
            @var `endpoints : dict`
                    -contains all the venmo api endpoints used in the toolbox
            @var `defaultHeaders : dict`
                    -default headers sent in most requests. Some api requests copy and modify these headers

        Args:
            @param `autoRevokeTokenOnDelete : bool`
                    -dictates whether to send the request to delete the token issued on login when the instance in destructed. Default value is True
    """

    def __init__(self, autoRevokeTokenOnDelete = True):

        self.bearerToken = ""
        self.username = ""
        self.userid = ""
        self.session = requests.Session()
        self.deviceID = ""
        self.autoLogOut = autoRevokeTokenOnDelete
        self.loginJson = {}
        self.accJson = {}
        self.fName = ""

        self.endpoints = {

            "base" : "https://api.venmo.com/v1",
            "oauth" : "/oauth/access_token",
            "2FAGet" : "/account/two-factor/token?client_id=1",
            "2FAPost" : "/account/two-factor/token",
            "account" : "/me",
            "userLookup" : "/users/{}",
            "usersLookup" : "/users",
            "friends" : "/users/{}/friends?limit=1337",
            "paymentMethods" : "/payment-methods",
            "friendRequest" : "/friend-requests",
            "pay" : "/payments",

        }

        self.defaultHeaders = {

                "User-Agent": "Venmo/7.44.0 (iPhone; iOS 13.0; Scale/2.0)",
                "device-id": self.deviceID,
                "Content-Type":"application/json",
                "Authorization":"Bearer " + self.bearerToken,
        }


    def updateDefaultHeaders(self) -> None:
        """
            Brief:
                Updates the values of the `device-id` and `Authorization` header values with the current values of the respective instance variables.

            Returns:
                `None`
        """
        self.defaultHeaders["device-id"] = self.deviceID
        self.defaultHeaders["Authorization"] = "Bearer " + self.bearerToken

    
    def __del__(self):
        """
            Brief: 
                Overloaded destructor. Checks the value of self.autoLogOut and bases on values will or will not send the api request to revoke the current oauth2 token.

            Args:
                N/A
            
            Returns:
                N/A
        """

        if (self.autoLogOut):

            
            logoutHeaders = self.defaultHeaders.copy()


            r = self.session.delete(self.endpoints["base"] + self.endpoints["oauth"], headers = logoutHeaders)

            print(r.text)
            print("Successfully revoked the active token")


    def login(self, username = "", password = "", deviceID="") -> bool:
        """
            Brief:
                Attempts to login. Will try to use the credentials stored in the local `auth.json` file. If the files is not found, corrupted, or contains empty json fields it will create a new file using the values passed to method. It then attemps to login, handling 2FA as needed.

            Args:
                @param `username : str = ""`
                        -username to use when logging in if no `auth.json` exists
                @param `password : str = ""`
                        -password to use when logging in if no `auth.json` exists 
                @param `deviceID : str = ""~
                        -device id to use when logging in. If empty, it will generate a random one.

            Returns:
                `bool` : whether the login attempt was successful or not
        """

        if (deviceID == ""):

            self.deviceID = self.generateRandomDeviceID()
        
        else:
        
            self.deviceID = deviceID

        authFile = None
        loginCredentials = None
        try:

            authFile = open("auth.json", mode = "r", encoding = "UTF-8")
            loginCredentials  = json.loads(authFile.read())

            if (loginCredentials.get("phone_email_or_username", "") == "" or loginCredentials.get("password", "") == ""):
                print("Incorrect auth json or empty fields.")

                raise FileNotFoundError


        
        except FileNotFoundError as e:

            if (username == "" or password == ""):
                print("No existing auth file or empty credentials entered. Unable to login.")
                return False

            self.createAuthFile(username, password)
            authFile = open("auth.json")
            loginCredentials = json.loads(authFile.read())
        

        authFile.close()
        
        self.updateDefaultHeaders()
        loginHeaders = self.defaultHeaders.copy()
        loginHeaders.pop("Authorization")


        response = self.session.post(self.endpoints["base"] + self.endpoints["oauth"], json = loginCredentials, headers = loginHeaders)


        responseJson = json.loads(response.text)


        if (responseJson.get("error", "") != ""):  #Error

            errorCode = int(responseJson["error"].get("code", 0)) 

            if (errorCode == 264):
                
                print("Incorrect Credentials.")
                return False
            
            elif (errorCode == 81109):
                
                responseJson = json.loads(self.__handle2FA(response.headers["venmo-otp-secret"]))

            else:
                
                print("Unexpected Error Logging In.")
                return False

        
        self.setAccountVariables(responseJson)
       
       
        return True

    


    def __handle2FA(self, otp_secret) -> requests.models.Response.text:
        
        self.__get2FASms(otp_secret)

        otpSMS = input("Enter the code sent to your phone via sms and hit enter.\n:>")

        response = self.__2FALogin(otp_secret, otpSMS)


        return response.text


        

    def get2FAOptions(self, otp_secret) -> dict:
        """
            Brief:  
                Querys the api for methods to receive a 2FA code.

            Args:
                @param `otp_secret : str `
                        -otp secrete header in the login request response
            
            Returns:
                `dict` : response json containing all the methods for receiving a 2FA code
        """
        
        get2FAHeaders = self.defaultHeaders.copy()
        get2FAHeaders.pop("Authorization")
        get2FAHeaders.update("venmo-otp-secret", otp_secret)

        response = self.session.get(self.endpoints["base"] + self.endpoints["2FAGet"], headers = get2FAHeaders)

        return json.loads(response.text)



    def __get2FASms(self, otp) -> None:

        
        send2FASmsHeaders = self.defaultHeaders.copy()
        send2FASmsHeaders.pop("Authorization")
        send2FASmsHeaders.update({"venmo-otp-secret" : otp})

        send2FASmsBodyJson = json.loads("{\"via\": \"sms\"} ")
        

        response = self.session.post(self.endpoints["base"] + self.endpoints["2FAPost"], headers = send2FASmsHeaders, json=send2FASmsBodyJson)
        
        responseJSON = json.loads(response.text)

        if (responseJSON.get("data", "") != ""):

            if (responseJSON["data"].get("status", "") != ""):

                if (responseJSON["data"].get("status", "") == "sent"):

                    print("SMS CODE SENT")

            else:

                print("Error sending sms code")

        else:

            print("Error sending sms code")


    def __2FALogin(self, otpHeader, otpSMS) -> requests.models.Response:

         
        login2FAHeaders = self.defaultHeaders.copy()
        login2FAHeaders.pop("Authorization")
        login2FAHeaders.update("venmo-otp-secret", otpHeader)
        login2FAHeaders.update("Venmo-Otp", otpSMS)
        

        authFile = open("auth.json")

        login2FABodyJson = json.loads(authFile.read())

        authFile.close()

        return self.session.post(self.endpoints["base"] + self.endpoints["oauth"], headers= login2FAHeaders, json=login2FABodyJson)


    def getAccountInfo(self) -> dict:
        """
            Brief:
                Query the api for the logged in user's account information

            Returns:
                `dict` : the account information json
        """
        return self.accJson


    def setAccountVariables(self, loginJson) -> None:
        """
            Brief:
                Sets the instance variables to the respective values  in the passed json. Also updates the default headers.
            
            Args:
                @param `loginJson : dict`
                        -Json containing the values to set the instance variables to. Usually the json returned in a login attempt.

            Returns:
                `None`
        """
      
        self.loginJson = loginJson
        self.bearerToken = loginJson["access_token"]
        self.username = loginJson["user"]["username"]
        self.userid = loginJson["user"]["id"]
        self.fName = loginJson["user"]

        self.updateDefaultHeaders()

        response = self.session.get(self.endpoints["base"] + self.endpoints["account"], headers = self.defaultHeaders)

        self.accJson = json.loads(response.text)

    def createAuthFile(self, username="", password="") -> None:
        """
            Brief:
                Creates an auth files with the passed username and password
                
            Args:
                @param `username : str = ""`
                        -account username or email
                @param `password : str = ""`
                        -account password

            Returns:
                `None`
        """

        loginJSON = "{{\n\t\"phone_email_or_username\": \"{a1}\",\n\t\"client_id\": \"1\",\n\t\"password\": \"{a2}\"\n}}".format(a1 = username, a2 = password)
        file = open("auth.json", mode="w+", encoding="UTF-8")
        file.write(loginJSON)
        file.close()


    def getUserInformationByID(self, userID ) -> dict:
        """
            Brief:
                Gets a user's venmo information by venmo id

            Args:
                @param `userId : str`
                        -the desired user's venmo id

            Returns:
                `dict` : the user's venmo information in json
        """

        try:

            userID = int(userID)

            response = self.session.get(self.endpoints["base"] + self.endpoints["userLookup"].format(userID), headers = self.defaultHeaders)

            return json.loads(response.text)

        except ValueError as e:

            print("Not a valid number.")
            return {}
        
    def getUserInformationByUsername(self, username ) -> dict:
        """
            Brief:
                Gets a user's venmo information by venmo username

            Args:
                @param `username : str`
                        -the desired user's venmo username

            Returns:
                `dict` : the user's venmo information in json
        """

        userId = self.getUserIDByUsername(username)

        return self.getUserInformationByID(userId)

    
    def authenticated(self) -> bool:
        """
            Brief:
                Tells you if the current instance of the toolbox has an oauth2 token. Doesn't check the validity of the token. If the token is set via direct access to the self.bearerToken variable it could be a non valid token but this would still return true.

            Returns:
                `bool` : Does the current instance have an oauth2 token
        """
        if (self.bearerToken != ""):
            return True
        else:
            return False

    def getPaymentMethods(self) -> dict:
        """
            Brief:
                Get the available payment menthods currently on the authenticated user's account.

            Returns:
                `dict` : json containing payment method information
        """ 
        
        response = self.session.get(self.endpoints["base"] + self.endpoints["paymentMethods"], headers = self.defaultHeaders)

        return json.loads(response.text)


    def getBalance(self) -> float:
        """
            Brief:
                Returns the authenticated user's balance

            Returns:
                `float` : the user's balance
        """
        return self.loginJson["balance"]
            
        
    def getFriends(self) -> dict:
        """
            Brief:
                Gets the authenticated user's friend list

            Returns:
                `dict`: the users friends as json
        """
        
        response  = self.session.get(self.endpoints["base"] + self.endpoints["friends"].format(self.userid), headers = self.defaultHeaders)


        return json.loads(response.text)



    def sendMoneyByUsername(self, amount, username , paymentID, msg, audienceVisibility = 0 ) -> bool:
        """
            Brief:
                Creates a transaction to send money to a user via venmo username

            Args:
                @param `amount : float`
                        -The amount of money to send
                @param `username : str`
                        -The username of the user to send money to
                @param `paymentID : int`
                        -The payment id of the way to pay the user. Can be found data returned in self.getPaymentMethods()
                @param `msg : str = ""`
                        -A required msg to display with the transaction
                @param `audienceVisibility : int = 0`
                        -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public

            Returns:    
                `bool` : Whether the transaction was successful or not
        """


        return self.sendMoneyByUserID(amount, self.getUserIDByUsername(username), paymentID, msg,  audienceVisibility)

        

    def requestMoneyByUsername(self, amount, username ,  msg, audienceVisibility = 0 ) -> bool:
        """
            Brief:
                Creates a transaction to request money to a user via venmo username

            Args:
                @param `amount : float`
                        -The amount of money to request
                @param `username : str`
                        -The username of the user to send money to
                @param `msg : str = ""`
                        -A msg to display with the transaction
                @param `audienceVisibility : int = 0`
                        -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public

            Returns:    
                `bool` : Whether the transaction was successful or not
        """
        return self.requestMoneyByUserID(amount, self.getUserIDByUsername(username), msg, audienceVisibility)

    def sendMoneyByUserID(self, amount, userID , paymentID, msg, audienceVisibility = 0 ) -> bool:
        """
            Brief:
                Creates a transaction to send money to a user via venmo id

            Args:
                @param `amount : float`
                        -The amount of money to send
                @param `id : int`
                        -The venmo id of the user to send money to
                @param `paymentID : int`
                        -The payment id of the way to pay the user. Can be found data returned in self.getPaymentMethods()
                @param `msg : str = ""`
                        -A required msg to display with the transaction
                @param `audienceVisibility : int = 0`
                        -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public

            Returns:    
                `bool` : Whether the transaction was successful or not
        """
        
        data = {
            "funding_source_id" : str(paymentID),
            "user_id" : str(userID),
            "amount" : str(amount),
            "note" : msg
        }


        if (audienceVisibility == 0):
            data.update({"audience": "private"})
        elif (audienceVisibility == 1):
            data.update({"audience": "friends"})
        elif (audienceVisibility == 2):
            data.update({"audience": "public"})
        else:
            print("Invalid visibility level.")
            return False

        dataJson = json.loads(json.dumps(data))

        response = self.session.post(self.endpoints["base"] + self.endpoints["pay"], headers = self.defaultHeaders, json = dataJson)


        responseJson = json.loads(response.text)

        if (responseJson.get("error", "" ) != ""):
            print("Error sending transaction. ")
            return False

        return True

    def requestMoneyByUserID(self, amount, userID ,msg,  audienceVisibility = 0 ) -> bool:
        """
            Brief:
                Creates a transaction to request money to a user via venmo id

            Args:
                @param `amount : float`
                        -The amount of money to request
                @param `id : int`
                        -The venmo id of the user to send money to
                @param `msg : str = ""`
                        -A required msg to display with the transaction
                @param `audienceVisibility : int = 0`
                        -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public

            Returns:    
                `bool` : Whether the transaction was successful or not
        """
        data = {
            "user_id" : str(userID),
            "amount" : str(-amount),
            "note" : msg
        }


        if (audienceVisibility == 0):
            data.update({"audience": "private"})
        elif (audienceVisibility == 1):
            data.update({"audience": "friends"})
        elif (audienceVisibility == 2):
            data.update({"audience": "public"})
        else:
            print("Invalid visibility level.")
            return False

        dataJson = json.loads(json.dumps(data))

        response = self.session.post(self.endpoints["base"] + self.endpoints["pay"], headers = self.defaultHeaders, json = dataJson)

        responseJson = json.loads(response.text)

        if (responseJson.get("error", "" ) != ""):
            print("Error sending transaction. ")
            return False

        return True

    def getUserIDByUsername(self,username ) -> int:
        """
            Brief:
                Gets a user's venmo id by venmo username

            Args:
                @param `username : str  
                        -a venmo username

            Returns:
                `int` : the user id corresponding the the passed username if its a valid username, otherwise -1
        """

        requestDataJson = json.loads("{{\"query\": \"{a1}\", \"limit\":\"50\",\"offset\": \"0\", \"type\":\"username\"}}".format(a1 = username))

        response = self.session.get(self.endpoints["base"] + self.endpoints["usersLookup"], headers = self.defaultHeaders, json=requestDataJson)

        responseJson = json.loads(response.text)


        for user in responseJson["data"]:
            if (user["username"].lower() == username.lower()):
                return int(user["id"])
                

        return -1

    
    def getUsernameByUserID(self, userID) -> str:
        """
            Brief:
                gets a user's venmo username by venmo id

            Args:
                @param `userID : int`
                        -a venmo user id

            Returns:
                `str` : the corresponding username if its a valid venmo id, otherwise reuturs \"\"
        """

        userInfo = self.getUserInformationByID(userID)


        if (userInfo.get("data", "")  != ""):
            return userInfo["data"]["username"]

        return ""


    def sendFriendRequestByUsername(self, username) -> bool:
        """
            Brief:  
                Sends a friend request to a user via username

            Args:
                @param `username : str`
                        -a venmo username
            
            Returns:
                `bool` : when the friend request was sent or not
        """

        userID = self.getUserIDByUsername(username)

        if (userID == -1):
            print("User not found.")
            return False

        return self.sendFriendRequestByUserID(userID)

    def sendFriendRequestByUserID(self, userID) -> bool:
        """
            Brief:  
                Sends a friend request to a user via venmo id

            Args:
                @param `userID : int`
                        -a venmo id
            
            Returns:
                `bool` : when the friend request was sent or not
        """

        if (self.getUsernameByUserID(userID) == ""):
            print("User not found.")
            return False

        body = json.loads("{{\"user_id\" : \"{a1}\"}}".format(a1 = userID))
        
        response = self.session.post(self.endpoints["base"] + self.endpoints["friendRequest"], headers = self.defaultHeaders, json = body)

        responseJson = json.loads(response.text)

        if (responseJson.get("error", "") != ""):
            if (responseJson["error"]["code"] == 2208 ):
                print("Already a pending friend request")
                return False
            else:
                print("Unknown error. Code", response["error"]["code"])

        if (responseJson.get("data", "") != ""):
            print("Friend request successfully sent to " + self.getUsernameByUserID(userID) + ".")
        

        return True


    def generateRandomDeviceID(self) -> str:
        """
            Brief:
                generates a random device id

            Returns:
                `str` : the generated device id
        """

        BASE_DEVICE_ID = "88884260-05O3-8U81-58I1-2WA76F357GR9"

        result = []
        
        for char in BASE_DEVICE_ID:

            if char.isdigit():
        
                result.append(str(randint(0, 9)))
        
            elif char == '-':
        
                result.append('-')
        
            else:
        
                result.append(choice(ascii_uppercase))

        return  "".join(result)
    


