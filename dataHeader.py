class DataHeader:
    def __init__(self, seqno, gdpName, doublePrevHash, prevHash, dataHash):
        self.seqno = seqno
        self.gdpName = gdpName
        self.doublePrevHash = doublePrevHash
        self.prevHash = prevHash
        self.dataHash = dataHash