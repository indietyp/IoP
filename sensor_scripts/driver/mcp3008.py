import spidev


class mcp3008():
    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(self, adcnum):
        spi = spidev.SpiDev()
        spi.open(0, 1)

        if ((adcnum > 3) or (adcnum < 0)):
            return -1
        r = spi.xfer2([1, (2 + adcnum) << 6, 0])
        adcout = ((r[1] & 3) << 8) + r[2]
        return adcout

    def read_pct(self, adcnum):
        r = self.readadc(adcnum)
        return int(round((r / 1023.0) * 100))

    def read_3v3(self, adcnum):
        r = self.readadc(adcnum)
        v = (r / 1023.0) * 3.3
        return v

    def readadc_avg(self, adcnum):
        r = []
        for i in range(0, 10):
            r.append(self.readadc(adcnum))
        return sum(r) / 10.0
