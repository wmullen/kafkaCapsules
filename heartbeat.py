class Heartbeat:
    def __init__(self, seqno, gdpName, headerHash, sigKey):
        self.seqno = seqno
        self.gdpName = gdpName
        self.headerHash = headerHash

        # Define new dictionary
        # Take signiture 
