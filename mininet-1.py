#!/usr/bin/python

"""
natnet.py: Example network with NATs
           h0
           |
           s0
           |
    ----------------
    |              |
   nat1           nat2
    |              |
   s1              s2
    |              |
   h1              h2
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.nodelib import NAT
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.util import irange
from time import sleep
import random.random
import math
class InternetTopo(Topo):
    "Single switch connected to n hosts."
    def __init__(self, n=100, **opts):
        Topo.__init__(self, **opts)

        # set up inet switch
        inetSwitch = self.addSwitch('s0')
        # add inet host
		for i in irange(1,8):
		    inetServer = self.addHost('svr%d' % i)
			inetServer.ip = '200.200.200.%d' % i
			inetServer.name = 'server%d' % i
			self.addLink(inetSwitch, inetServer)

        # add local nets
        for i in irange(1, n):
            inetIntf = 'nat%d-eth0' % i
            localIntf = 'nat%d-eth1' % i
            localIP = '192.168.%d.1' % i
            localSubnet = '192.168.%d.0/24' % i
            natParams = { 'ip' : '%s/24' % localIP }
            # add NAT to topology
            nat = self.addNode('nat%d' % i, cls=NAT, subnet=localSubnet,
                               inetIntf=inetIntf, localIntf=localIntf)
            switch = self.addSwitch('s%d' % i)
            # connect NAT to inet and local switches
            self.addLink(nat, inetSwitch, intfName1=inetIntf)
            self.addLink(nat, switch, intfName1=localIntf, params1=natParams)
            # add host and connect to local switch
			for j in irange(1,2):
			    host = self.addHost('h%d-%d' % (i , j),
                ip='192.168.%d.%d/24' % (i , j),
                defaultRoute='via %s' % localIP)
				self.addLink(host, switch)

def startpings( host,targetips):
    "Tell host to repeatedly ping targets"

    targetips = ' '.join( targetips )
    cmds = []
    # Simple ping loop
	pingseconds = [600,1000,1200,1800,1,2,600,3600]
	for i in irange(0,7):
	    cmds.append( 'while true; do '
            ' for ip in %s; do ' % targetips[i] +
            '  echo -n %s "->" $ip ' % host.IP() +
            '   `ping -n -w %d $ip | grep packets` ;' % pingseconds[i] 
            '  sleep 1;'
            ' done; '
            'done &' )

    while True:
	    r = math.ceil (random() * 10000 / 125 )
	    if r in range(1,9)
		print ( '*** Host %s (%s) will be pinging ips: %s' %
        ( host.name, host.IP(), targetips[r - 1] ) )
		host.cmd( cmds[r - 1] )
		sleep(pingseconds[r - 1])
def servers(hosts):
    serverips = []
    for i in irange(1,8):
	    for host in hosts:
	        if "server%d" % i in host.name.lower():
		        serverips.append(host.ip)
				hosts.remove(host)
	    
	return sorted(serverips)
def run(seconds):
    "Ping subsets of size chunksize in net of size netsize"
	    "Create network and run the CLI"
    topo = InternetTopo()
    net = Mininet(topo=topo)
    net.start(net.hosts)
	servers = servers(net.hosts)
	for host in net.hosts:
	    startpings(net.host,servers)
	endTime = time() + seconds
	while time() < endTime: pass
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run(seconds=300)