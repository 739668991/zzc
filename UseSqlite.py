# Reference: Dusty Phillips.  Python 3 Objected-oriented Programming Second Edition. Pages 326-328.
# Copyright (C) 2019 Hui Lan

import sqlite3

class Sqlite3Template:
    def __init__(self, db_fname):
        self.db_fname = db_fname
        
    def connect(self, db_fname):
        self.conn = sqlite3.connect(self.db_fname)
    
    def instructions(self, query_statement):
        raise NotImplementedError()
    
    def operate(self):
        self.results = self.conn.execute(self.query) # self.query is to be given in the child classes
        self.conn.commit()
        
    def format_results(self):
        raise NotImplementedError()  
    
    def do(self):
        self.connect(self.db_fname)
        self.instructions(self.query)
        self.operate()
        
        
class InsertQuery(Sqlite3Template):
    def instructions(self, query):
        self.query = query
        

class RecordQuery(Sqlite3Template):
    def instructions(self, query):
        self.query = query

    def format_results(self):
        output = []
        for row in self.results.fetchall():
            output.append(', '.join([str(i) for i in row]))
        return '\n\n'.join(output)    


if __name__ == '__main__':
    
    #iq = InsertQuery('RiskDB.db')
    #iq.instructions("INSERT INTO inspection Values ('FoodSupplies', 'RI2019051301', '2019-05-13', '{}')")
    #iq.do()
    #iq.instructions("INSERT INTO inspection Values ('CarSupplies', 'RI2019051302', '2019-05-13', '{[{\"risk_name\":\"elevator\"}]}')")
    #iq.do()
    
    rq = RecordQuery('RiskDB.db')
    rq.instructions("SELECT * FROM inspection WHERE inspection_serial_number LIKE 'RI20190513%'")
    rq.do()
    print(rq.format_results())
