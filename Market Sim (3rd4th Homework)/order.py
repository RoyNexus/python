import datetime as dt

class Order:

    def __init__(self, order):
        self.vector = order

    def get_symbol(self):
        return self.vector[3]
        
    def get_date(self):
        return dt.datetime(int(self.vector[0]), int(self.vector[1]), int(self.vector[2]))
        
    def get_date_16_00(self):
        return dt.datetime(int(self.vector[0]), int(self.vector[1]), int(self.vector[2]), 16, 00, 00)
        
    def get_type(self):
        return self.vector[4]
        
    def get_shares(self):
        return self.vector[5]
    
    def __str__(self):
        return str(self.vector)