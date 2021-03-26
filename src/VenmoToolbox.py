import requests
import json
from random import randint, choice
from string import ascii_uppercase




#df = open("../test/out.json", mode = "w+", encoding = "UTF-8")


class VenmoToolbox():

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
        self.defaultHeaders["device-id"] = self.deviceID
        self.defaultHeaders["Authorization"] = "Bearer " + self.bearerToken


    def __del__(self):

        if (self.autoLogOut):

            
            logoutHeaders = self.defaultHeaders.copy()


            r = self.session.delete(self.endpoints["base"] + self.endpoints["oauth"], headers = logoutHeaders)

            print(r.text)
            print("Successfully revoked the active token")


    def login(self, username = "", password = "", deviceID="") -> bool:

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

    


    def __handle2FA(self, otp) -> requests.models.Response.text:
        
        self.__get2FASms(otp)

        otpSMS = input("Enter the code sent to your phone via sms and hit enter.\n:>")

        response = self.__2FALogin(otp, otpSMS)


        return response.text


        

    def get2FAOptions(self, otp) -> dict:
        
        get2FAHeaders = self.defaultHeaders.copy()
        get2FAHeaders.pop("Authorization")
        get2FAHeaders.update("venmo-otp-secret", otp)

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
        return self.accJson


    def setAccountVariables(self, loginJson) -> None:
      
        self.loginJson = loginJson
        self.bearerToken = loginJson["access_token"]
        self.username = loginJson["user"]["username"]
        self.userid = loginJson["user"]["id"]
        self.fName = loginJson["user"]

        self.updateDefaultHeaders()

        response = self.session.get(self.endpoints["base"] + self.endpoints["account"], headers = self.defaultHeaders)

        self.accJson = json.loads(response.text)

    def createAuthFile(self, username="", password="") -> None:

        loginJSON = "{{\n\t\"phone_email_or_username\": \"{a1}\",\n\t\"client_id\": \"1\",\n\t\"password\": \"{a2}\"\n}}".format(a1 = username, a2 = password)
        file = open("auth.json", mode="w+", encoding="UTF-8")
        file.write(loginJSON)
        file.close()


    def getUserInformationByID(self, userID ) -> dict:

        try:

            userID = int(userID)

            response = self.session.get(self.endpoints["base"] + self.endpoints["userLookup"].format(userID), headers = self.defaultHeaders)

            return json.loads(response.text)

        except ValueError as e:

            print("Not a valid number.")
            return {}
        
    def getUserInformationByUsername(self, username ) -> dict:

        userId = self.getUserIDByUsername(username)

        return self.getUserInformationByID(userId)

    
    def authenticated(self) -> bool:
        if (self.bearerToken != ""):
            return True
        else:
            return False

    def getPaymentMethods(self) -> dict: 
        
        response = self.session.get(self.endpoints["base"] + self.endpoints["paymentMethods"], headers = self.defaultHeaders)

        return json.loads(response.text)


    def getBalance(self) -> float:
        return self.loginJson["balance"]
            
        
    def getFriends(self) -> dict:
        
        response  = self.session.get(self.endpoints["base"] + self.endpoints["friends"].format(self.userid), headers = self.defaultHeaders)


        return json.loads(response.text)



    def sendMoneyByUsername(self, amount, username , paymentID, audienceVisibility = 0 ,  msg = "") -> bool:



        #data = json.loads("{{\"funding_source_id\": \"{}\",\"user_id\": \"{}\",\"amount\": \"{}\",\"note\": \"hi gabe\",\"audience\":\"private\"}}".format(p,i,a))

        data = {
            "funding_source_id" : str(paymentID),
            "user_id" : str(self.getUserIDByUsername(username)),
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


        

    def requestMoneyByUsername(self, amount, username , paymentID, audienceVisibility = 0 ,  msg = "") -> bool:
        data = {
            "funding_source_id" : str(paymentID),
            "user_id" : str(self.getUserIDByUsername(username)),
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

    def sendMoneyByUserID(self, amount, userID , paymentID, audienceVisibility = 0 ,  msg = "") -> bool:
        
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

    def requestMoneyByUserID(self, amount, userID , paymentID, audienceVisibility = 0 ,  msg = "") -> bool:
        data = {
            "funding_source_id" : str(paymentID),
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

        requestDataJson = json.loads("{{\"query\": \"{a1}\", \"limit\":\"50\",\"offset\": \"0\", \"type\":\"username\"}}".format(a1 = username))

        response = self.session.get(self.endpoints["base"] + self.endpoints["usersLookup"], headers = self.defaultHeaders, json=requestDataJson)

        responseJson = json.loads(response.text)


        for user in responseJson["data"]:
            if (user["username"].lower() == username.lower()):
                return int(user["id"])
                

        return -1

    
    def getUsernameByUserID(self, userID) -> str:

        userInfo = self.getUserInformationByID(userID)


        if (userInfo.get("data", "")  != ""):
            return userInfo["data"]["username"]

        return ""


    def sendFriendRequestByUsername(self, username) -> bool:

        userID = self.getUserIDByUsername(username)

        if (userID == -1):
            print("User not found.")
            return False

        return self.sendFriendRequestByUserID(userID)

    def sendFriendRequestByUserID(self, userID) -> bool:

        body = json.loads("{{\"user_id\" : \"{a1}\"}}".format(a1 = userID))
        
        response = self.session.post(self.endpoints["base"] + self.endpoints["friendRequest"], headers = self.defaultHeaders, json = body)

        responseJson = json.loads(response.text)

        if (responseJson.get("error", "") != ""):
            if (responseJson["error"]["code"] == 2208 ):
                print("Already a pending friend request")
                return False

        if (responseJson.get("data", "") != ""):
            print("Friend request successfully sent to " + self.getUsernameByUserID(userID) + ".")
        

        return True


    def generateRandomDeviceID(self) -> str:

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
    


