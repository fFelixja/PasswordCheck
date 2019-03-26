import requests
import hashlib
import signal

# Simple class to catch signals for a more gracefully shutdown.
class SignalHandler:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    # Exit.
    def exit_gracefully(self, signum, frame):
        print('\nThanks, consider to close this terminal.\nExiting script!')
        exit()

# Wrapper for hashlib sha1 function.
def sha1(rawInput):
    sha1 = hashlib.sha1(rawInput.encode('UTF-8'))
    return sha1.hexdigest().upper()

# Wrapper for request get function.
def get(path):
    url = 'https://api.pwnedpasswords.com/range/' + path
    return requests.get(url)


# Split sequence at index.
def splitAtIndex(sequence, index):
    # From start up to index (excluding).
    left = sequence[:index]
    # From index (including) to end.
    right = sequence[index:]
    return left, right
    
# Search for matches between password and request result.
def isPasswordLeaked(hashedUserPassword, requestResult):
    # Extract data from request.
    text = requestResult.text
    # Split data to array.
    dataArray = text.split('\n')
    # Search for a match.
    for data in dataArray:
        hashedPassword , occurance = data.split(':')
        if hashedPassword == hashedUserPassword:
            return True, occurance
    # No match.
    return False, 0

# User is responsible to trust this software.
def printDisclaimer():
    msg0 = "\n##############\n# DISCLAIMER #\n##############\n"
    msg  = " This SOFTWARE PRODUCT is provided by THE PROVIDER \"as is\" and \"with all faults.\" THE PROVIDER makes no representations or warranties of any kind concerning the safety, suitability, lack of viruses, inaccuracies, typographical errors, or other harmful components of this SOFTWARE PRODUCT. There are inherent dangers in the use of any software, and you are solely responsible for determining whether this SOFTWARE PRODUCT is compatible with your equipment and other software installed on your equipment. You are also solely responsible for the protection of your equipment and backup of your data, and THE PROVIDER will not be liable for any damages you may suffer in connection with using, modifying, or distributing this SOFTWARE PRODUCT."
    print(msg0)
    print(msg)
    print("\n##############")

def main():
    print('\nExit script with [Ctrl + C] or [Ctrl + D]')
    printDisclaimer()
    signalHandler = SignalHandler()
    while(True):
        try:
            # Collect user input.
            password = input('\nEnter a password: ')
        except EOFError:
            # Catch user input e.g., Ctrl + D, and exit gracefully.
            signalHandler.exit_gracefully(signal.SIGINT,None)

        # Hash the provided password.
        hashedPassword = sha1(password)
        # Split for url path and the remaining of hash.
        path, remainingOfHash = splitAtIndex(hashedPassword, 5)
        # Request result.
        requestResult = get(path)   
        # Error check from result, (200 indicate successfull request from https).
        if requestResult.status_code != 200:
            print('HTTPS request failed with ERROR', requestResult.status_code)
            signalHandler.exit_gracefully(signal.SIGINT,None)  
        
        # Check if password is leaked.
        isLeaked, times = isPasswordLeaked(remainingOfHash,requestResult)

        # Print the result to console.
        if isLeaked:
            print(password, 'was found!')
            print('Hash: {}'.format(hashedPassword))
            print("Occurences: {}".format(times))
        else:
            print('\nPassword was not found.')

if __name__ == "__main__":
    main()