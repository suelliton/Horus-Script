
import pyrebase

def logar(apiKey,authDomain,databaseUrl,storageBucket,serviceAccount,email,password):
    config = {
     "apiKey": apiKey,
      "authDomain": authDomain,
      "databaseURL": databaseUrl,
      "storageBucket": storageBucket,
      "serviceAccount": serviceAccount
    }
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    user_login = auth.sign_in_with_email_and_password(email, password)
    database = firebase.database()
    storage = firebase.storage()
    return (database, storage)
