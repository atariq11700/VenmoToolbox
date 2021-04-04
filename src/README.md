# Documentation

## `VenmoMenu.py`
> How to use
> 1. Create an instance of the menu
> 2. Call ``login()``
> 3. Call ``run()``
>  
> Ex:
> ```python
> from VenmoMenu import VenmoMenu
> menu = VenmoMenu()
> menu.login()
> menu.run()
> ```
>  

## `VenmoToolbox.py`
```txt
Help on class VenmoToolbox in module VenmoToolbox:

class VenmoToolbox(builtins.object)
 |  VenmoToolbox(autoRevokeTokenOnDelete=True)
 |  
 |  Brief:
 |      Wrapper class for the venmo api. Exposes functionality via class methods. It is not static and an instance in required to use said functionality.
 |  
 |  Instance Variables:
 |      @var `bearerToken : str`
 |              -oauth2 auth token
 |      @var `username : str`
 |              -logged in user's username
 |      @var `userID : str`
 |              -logged in user's venmo ID
 |      @var `session : requests.Session` 
 |              -session object to persist cookies across api calls
 |      @var `deviceID : str`
 |              -current device id that venmo see's when you log in. Can be stored to remember device and not have to log in using 2FA next time.
 |      @var `autoLogOut : bool` 
 |              -boolean that dictates whether to send the request to revoke the auth token on instance destruction. By default venmo does not revoke the tokens but the default value for this variable is True.
 |      @var `loginJson : dict`
 |              -json that is returned on first login. Contains some user information
 |      @var `accJson : dict`
 |              -json containing all of the accuonts information
 |      @var `fName : str`
 |              -logged in user's first name according to the venmo account
 |      @var `endpoints : dict`
 |              -contains all the venmo api endpoints used in the toolbox
 |      @var `defaultHeaders : dict`
 |              -default headers sent in most requests. Some api requests copy and modify these headers
 |  
 |  Methods defined here:
 |  
 |  __del__(self)
 |      Brief: 
 |          Overloaded destructor. Checks the value of self.autoLogOut and bases on values will or will not send the api request to revoke the current oauth2 token.
 |      
 |      Args:
 |          N/A
 |      
 |      Returns:
 |          N/A
 |  
 |  __init__(self, autoRevokeTokenOnDelete=True)
 |      Args:
 |          @param `autoRevokeTokenOnDelete : bool`
 |                  -dictates whether to send the request to delete the token issued on login when the instance in destructed. Default value is True
 |  
 |  authenticated(self) -> bool
 |      Brief:
 |          Tells you if the current instance of the toolbox has an oauth2 token. Doesn't check the validity of the token. If the token is set via direct access to the self.bearerToken variable it could be a non valid token but this would still return true.
 |      
 |      Returns:
 |          `bool` : Does the current instance have an oauth2 token
 |  
 |  createAuthFile(self, username='', password='') -> None
 |      Brief:
 |          Creates an auth files with the passed username and password
 |          
 |      Args:
 |          @param `username : str = ""`
 |                  -account username or email
 |          @param `password : str = ""`
 |                  -account password
 |      
 |      Returns:
 |          `None`
 |  
 |  generateRandomDeviceID(self) -> str
 |      Brief:
 |          generates a random device id
 |      
 |      Returns:
 |          `str` : the generated device id
 |  
 |  get2FAOptions(self, otp_secret) -> dict
 |      Brief:  
 |          Querys the api for methods to receive a 2FA code.
 |      
 |      Args:
 |          @param `otp_secret : str `
 |                  -otp secrete header in the login request response
 |      
 |      Returns:
 |          `dict` : response json containing all the methods for receiving a 2FA code
 |  
 |  getAccountInfo(self) -> dict
 |      Brief:
 |          Query the api for the logged in user's account information
 |      
 |      Returns:
 |          `dict` : the account information json
 |  
 |  getBalance(self) -> float
 |      Brief:
 |          Returns the authenticated user's balance
 |      
 |      Returns:
 |          `float` : the user's balance
 |  
 |  getFriends(self) -> dict
 |      Brief:
 |          Gets the authenticated user's friend list
 |      
 |      Returns:
 |          `dict`: the users friends as json
 |  
 |  getPaymentMethods(self) -> dict
 |      Brief:
 |          Get the available payment menthods currently on the authenticated user's account.
 |      
 |      Returns:
 |          `dict` : json containing payment method information
 |  
 |  getUserIDByUsername(self, username) -> int
 |      Brief:
 |          Gets a user's venmo id by venmo username
 |      
 |      Args:
 |          @param `username : str  
 |                  -a venmo username
 |      
 |      Returns:
 |          `int` : the user id corresponding the the passed username if its a valid username, otherwise -1
 |  
 |  getUserInformationByID(self, userID) -> dict
 |      Brief:
 |          Gets a user's venmo information by venmo id
 |      
 |      Args:
 |          @param `userId : str`
 |                  -the desired user's venmo id
 |      
 |      Returns:
 |          `dict` : the user's venmo information in json
 |  
 |  getUserInformationByUsername(self, username) -> dict
 |      Brief:
 |          Gets a user's venmo information by venmo username
 |      
 |      Args:
 |          @param `username : str`
 |                  -the desired user's venmo username
 |      
 |      Returns:
 |          `dict` : the user's venmo information in json
 |  
 |  getUsernameByUserID(self, userID) -> str
 |      Brief:
 |          gets a user's venmo username by venmo id
 |      
 |      Args:
 |          @param `userID : int`
 |                  -a venmo user id
 |      
 |      Returns:
 |          `str` : the corresponding username if its a valid venmo id, otherwise reuturs ""
 |  
 |  getUsersFriends(self, userID) -> dict
 |      Brief:
 |          Gets a user's friend list
 |      
 |      Returns:
 |          `dict`: the users friends as json
 |  
 |  login(self, username='', password='', deviceID='') -> bool
 |      Brief:
 |          Attempts to login. Will try to use the credentials stored in the local `auth.json` file. If the files is not found, corrupted, or contains empty json fields it will create a new file using the values passed to method. It then attemps to login, handling 2FA as needed.
 |      
 |      Args:
 |          @param `username : str = ""`
 |                  -username to use when logging in if no `auth.json` exists
 |          @param `password : str = ""`
 |                  -password to use when logging in if no `auth.json` exists 
 |          @param `deviceID : str = ""~
 |                  -device id to use when logging in. If empty, it will generate a random one.
 |      
 |      Returns:
 |          `bool` : whether the login attempt was successful or not
 |  
 |  requestMoneyByUserID(self, amount, userID, msg, audienceVisibility=0) -> bool
 |      Brief:
 |          Creates a transaction to request money to a user via venmo id
 |      
 |      Args:
 |          @param `amount : float`
 |                  -The amount of money to request
 |          @param `id : int`
 |                  -The venmo id of the user to send money to
 |          @param `msg : str = ""`
 |                  -A required msg to display with the transaction
 |          @param `audienceVisibility : int = 0`
 |                  -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public
 |      
 |      Returns:    
 |          `bool` : Whether the transaction was successful or not
 |  
 |  requestMoneyByUsername(self, amount, username, msg, audienceVisibility=0) -> bool
 |      Brief:
 |          Creates a transaction to request money to a user via venmo username
 |      
 |      Args:
 |          @param `amount : float`
 |                  -The amount of money to request
 |          @param `username : str`
 |                  -The username of the user to send money to
 |          @param `msg : str = ""`
 |                  -A msg to display with the transaction
 |          @param `audienceVisibility : int = 0`
 |                  -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public
 |      
 |      Returns:    
 |          `bool` : Whether the transaction was successful or not
 |  
 |  sendFriendRequestByUserID(self, userID) -> bool
 |      Brief:  
 |          Sends a friend request to a user via venmo id
 |      
 |      Args:
 |          @param `userID : int`
 |                  -a venmo id
 |      
 |      Returns:
 |          `bool` : when the friend request was sent or not
 |  
 |  sendFriendRequestByUsername(self, username) -> bool
 |      Brief:  
 |          Sends a friend request to a user via username
 |      
 |      Args:
 |          @param `username : str`
 |                  -a venmo username
 |      
 |      Returns:
 |          `bool` : when the friend request was sent or not
 |  
 |  sendMoneyByUserID(self, amount, userID, paymentID, msg, audienceVisibility=0) -> bool
 |      Brief:
 |          Creates a transaction to send money to a user via venmo id
 |      
 |      Args:
 |          @param `amount : float`
 |                  -The amount of money to send
 |          @param `id : int`
 |                  -The venmo id of the user to send money to
 |          @param `paymentID : int`
 |                  -The payment id of the way to pay the user. Can be found data returned in self.getPaymentMethods()
 |          @param `msg : str = ""`
 |                  -A required msg to display with the transaction
 |          @param `audienceVisibility : int = 0`
 |                  -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public
 |      
 |      Returns:    
 |          `bool` : Whether the transaction was successful or not
 |  
 |  sendMoneyByUsername(self, amount, username, paymentID, msg, audienceVisibility=0) -> bool
 |      Brief:
 |          Creates a transaction to send money to a user via venmo username
 |      
 |      Args:
 |          @param `amount : float`
 |                  -The amount of money to send
 |          @param `username : str`
 |                  -The username of the user to send money to
 |          @param `paymentID : int`
 |                  -The payment id of the way to pay the user. Can be found data returned in self.getPaymentMethods()
 |          @param `msg : str = ""`
 |                  -A required msg to display with the transaction
 |          @param `audienceVisibility : int = 0`
 |                  -Dictates the visibility of the transactions. 0 -> private, 1 -> friends only, 2 -> public
 |      
 |      Returns:    
 |          `bool` : Whether the transaction was successful or not
 |  
 |  setAccountVariables(self, loginJson) -> None
 |      Brief:
 |          Sets the instance variables to the respective values  in the passed json. Also updates the default headers.
 |      
 |      Args:
 |          @param `loginJson : dict`
 |                  -Json containing the values to set the instance variables to. Usually the json returned in a login attempt.
 |      
 |      Returns:
 |          `None`
 |  
 |  updateDefaultHeaders(self) -> None
 |      Brief:
 |          Updates the values of the `device-id` and `Authorization` header values with the current values of the respective instance variables.
 |      
 |      Returns:
 |          `None`
 |  
 |  ----------------------------------------------------------------------
```