#! /usr/bin/python

from __future__ import print_function

# Doing * imports is bad :'(
from core.generate_topo import *
from core.generate_xp import *

import core.core as core
import numpy as np
import os

REMOTE_SERVER_RUNNER_HOSTNAME = ["mininet@192.168.122.15"]
REMOTE_SERVER_RUNNER_PORT = ["22"]


def getPostProcessingList(**kwargs):
    toReturn = []
    topoBasename = os.path.basename(kwargs["topoAbsPath"])
    # toReturn.append(("client.pcap",
    #                  "_".join([str(x) for x in [kwargs["testDirectory"], kwargs["xp"], kwargs["protocol"], kwargs["multipath"],
    #                                             topoBasename, "client.pcap"]])))
    # toReturn.append(("server.pcap",
    #                  "_".join([str(x) for x in [kwargs["testDirectory"], kwargs["xp"], kwargs["protocol"], kwargs["multipath"],
    #                                             topoBasename, "server.pcap"]])))
    toReturn.append(("command.log", "command.log"))
    toReturn.append(("ping.log", "ping.log"))
    if kwargs["xp"] == HTTPS:
        toReturn.append(("https_client.log", "https_client.log"))
        toReturn.append(("https_server.log", "https_server.log"))
    else:
        toReturn.append(("quic_client.log", "quic_client.log"))
        toReturn.append(("quic_server.log", "quic_server.log"))

    toReturn.append(("netstat_client_before", "netstat_client_before"))
    toReturn.append(("netstat_server_before", "netstat_server_before"))
    toReturn.append(("netstat_client_after", "netstat_client_after"))
    toReturn.append(("netstat_server_after", "netstat_server_after"))
    toReturn.append(("client_ifstat.txt", "client_ifstat.txt"))

    return toReturn


def quicTests(topos, protocol="mptcp", tmpfs="/mnt/tmpfs"):
    experienceLauncher = core.ExperienceLauncher(REMOTE_SERVER_RUNNER_HOSTNAME, REMOTE_SERVER_RUNNER_PORT)

    def testsXp(**kwargs):
        def testsMultipath(**kwargs):
            def test(**kwargs):
                xpDict = {
                    XP_TYPE: kwargs["xp"],
                    SCHEDULER_CLIENT: "default",
                    SCHEDULER_SERVER: "default",
                    CC: "olia" if kwargs["multipath"] == 1 else "cubic",
                    CLIENT_PCAP: "yes",
                    SERVER_PCAP: "yes",
                    HTTPS_FILE: "random",
                    HTTPS_RANDOM_SIZE: "20000",
                    QUIC_MULTIPATH: kwargs["multipath"],
                    RMEM: (10240, 87380, 16777216),
                }
                if int(kwargs["multipath"]) == 0:
                    kwargs["protocol"] = "tcp"

                kwargs["postProcessing"] = getPostProcessingList(**kwargs)
                core.experiment(experienceLauncher, xpDict, **kwargs)

            core.experimentFor("multipath", [0, 1], test, **kwargs)
            # core.experimentFor("multipath", [1], test, **kwargs)

        # core.experimentFor("xp", [HTTPS, QUIC], testsMultipath, **kwargs)
        core.experimentFor("xp", [QUIC], testsMultipath, **kwargs)

    core.experimentTopos(topos, "https_quic", protocol, tmpfs, testsXp)
    experienceLauncher.finish()


def generateExperimentalDesignRandomTopos(nbMptcpTopos=10, pathsPerTopo=2, bandwidth=(0.1, 100), rtt=(0, 50), queuingDelay=(0.0, 0.1), loss=(0.0, 2.5)):
    """ Assume only two paths per MPTCP topology, uniform distribution """
    mptcpTopos = []
    for nbTopo in range(nbMptcpTopos):
        mptcpTopo = {PATHS: [], NETEM: []}
        for nbPath in range(pathsPerTopo):
            bandwidthPath = "{0:.2f}".format(np.random.uniform(low=bandwidth[0], high=bandwidth[1]))
            rttPath = "{0:.0f}".format(np.random.uniform(low=rtt[0], high=rtt[1]))
            delayPath = "{0:.1f}".format(float(rttPath) / 2.0)
            lossPath = "{0:.2f}".format(np.random.uniform(low=loss[0], high=loss[1]))
            queuingDelayPath = "{0:.3f}".format(np.random.uniform(low=queuingDelay[0], high=queuingDelay[1]))
            # tcpTopos.append({PATHS: [{BANDWIDTH: bandwidthPath, DELAY: delayPath}], NETEM: [(0, 0, "loss " + str(lossPath) + "%")]})
            mptcpTopo[PATHS].append({BANDWIDTH: bandwidthPath, DELAY: delayPath, QUEUING_DELAY: queuingDelayPath})
            mptcpTopo[NETEM].append((nbPath, 0, "loss " + str(lossPath) + "%"))

        mptcpTopos.append(mptcpTopo)
        reversedMptcpTopoPaths = mptcpTopo[PATHS][::-1]
        reversedMptcpTopoNetem = []
        nbPath = 0
        for netem in mptcpTopo[NETEM][::-1]:
            reversedMptcpTopoNetem.append((nbPath, netem[1], netem[2]))
            nbPath += 1
        reversedMptcpTopo = {PATHS: reversedMptcpTopoPaths, NETEM: reversedMptcpTopoNetem}
        mptcpTopos.append(reversedMptcpTopo)

    return mptcpTopos

def launchTests(times=5):
    """ Notice that the loss must occur at time + 2 sec since the minitopo test waits for 2 seconds between launching the server and the client """
    # mptcpTopos = generateExperimentalDesignRandomTopos(nbMptcpTopos=200)
    # logging = open("topos_lowbdp_with_loss.log", 'w')
    # print(mptcpTopos, file=logging)
    # logging.close()
    mptcpTopos = [
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 15.67%'), (1, 0, 'loss 12.98%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 12.98%'), (1, 0, 'loss 15.67%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 13.53%'), (1, 0, 'loss 10.98%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 10.98%'), (1, 0, 'loss 13.53%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 13.57%'), (1, 0, 'loss 19.73%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 19.73%'), (1, 0, 'loss 13.57%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 10.64%'), (1, 0, 'loss 19.89%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 19.89%'), (1, 0, 'loss 10.64%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 19.47%'), (1, 0, 'loss 16.01%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '5'}], 'netem': [(0, 0, 'loss 16.01%'), (1, 0, 'loss 19.47%')]},
    ]


    for i in range(times):
        quicTests(mptcpTopos)

launchTests(times=1)
