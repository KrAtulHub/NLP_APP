import json 

class Database:
    
    def add_data(self, email, password):
        with open("database.json", "r") as file:
            data = json.load(file)
        
        
        if email in data:
            return False
        else:
            data[email]=[password]
            with open("database.json", "w") as file:
                json.dump(data, file, indent=4)
            return True
    
    def validate_login(self, email, password):
        with open("database.json", "r") as file:
            data = json.load(file)
        if email in data and data[email][0] == password:
            return True
        else:
            return False