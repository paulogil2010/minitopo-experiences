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
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.498'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.922'}], 'netem': [(0, 0, 'loss 1.548%'), (1, 0, 'loss 4.34%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.922'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.498'}], 'netem': [(0, 0, 'loss 4.34%'), (1, 0, 'loss 1.548%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.456'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.229'}], 'netem': [(0, 0, 'loss 3.379%'), (1, 0, 'loss 2.779%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.229'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.456'}], 'netem': [(0, 0, 'loss 2.779%'), (1, 0, 'loss 3.379%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.627'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.773'}], 'netem': [(0, 0, 'loss 3.474%'), (1, 0, 'loss 0.983%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.773'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.627'}], 'netem': [(0, 0, 'loss 0.983%'), (1, 0, 'loss 3.474%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.874'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.961'}], 'netem': [(0, 0, 'loss 0.40%'), (1, 0, 'loss 4.3%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.961'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.874'}], 'netem': [(0, 0, 'loss 4.3%'), (1, 0, 'loss 0.40%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.311'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.272'}], 'netem': [(0, 0, 'loss 3.707%'), (1, 0, 'loss 1.462%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.272'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.311'}], 'netem': [(0, 0, 'loss 1.462%'), (1, 0, 'loss 3.707%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.961'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.697'}], 'netem': [(0, 0, 'loss 3.953%'), (1, 0, 'loss 0.917%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.697'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.961'}], 'netem': [(0, 0, 'loss 0.917%'), (1, 0, 'loss 3.953%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.814'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.480'}], 'netem': [(0, 0, 'loss 0.639%'), (1, 0, 'loss 0.786%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.480'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.814'}], 'netem': [(0, 0, 'loss 0.786%'), (1, 0, 'loss 0.639%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.376'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.598'}], 'netem': [(0, 0, 'loss 1.329%'), (1, 0, 'loss 2.90%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.598'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.376'}], 'netem': [(0, 0, 'loss 2.90%'), (1, 0, 'loss 1.329%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.557'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.584'}], 'netem': [(0, 0, 'loss 1.257%'), (1, 0, 'loss 1.376%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.584'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.557'}], 'netem': [(0, 0, 'loss 1.376%'), (1, 0, 'loss 1.257%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.828'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.274'}], 'netem': [(0, 0, 'loss 4.490%'), (1, 0, 'loss 2.891%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.274'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.828'}], 'netem': [(0, 0, 'loss 2.891%'), (1, 0, 'loss 4.490%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.893'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.984'}], 'netem': [(0, 0, 'loss 2.288%'), (1, 0, 'loss 4.167%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.984'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.893'}], 'netem': [(0, 0, 'loss 4.167%'), (1, 0, 'loss 2.288%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.674'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.465'}], 'netem': [(0, 0, 'loss 0.545%'), (1, 0, 'loss 3.131%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.465'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.674'}], 'netem': [(0, 0, 'loss 3.131%'), (1, 0, 'loss 0.545%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.237'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.578'}], 'netem': [(0, 0, 'loss 3.641%'), (1, 0, 'loss 2.91%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.578'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.237'}], 'netem': [(0, 0, 'loss 2.91%'), (1, 0, 'loss 3.641%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.354'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.088'}], 'netem': [(0, 0, 'loss 0.156%'), (1, 0, 'loss 3.554%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.088'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.354'}], 'netem': [(0, 0, 'loss 3.554%'), (1, 0, 'loss 0.156%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.817'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.879'}], 'netem': [(0, 0, 'loss 3.117%'), (1, 0, 'loss 3.310%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.879'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.817'}], 'netem': [(0, 0, 'loss 3.310%'), (1, 0, 'loss 3.117%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.793'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.154'}], 'netem': [(0, 0, 'loss 2.924%'), (1, 0, 'loss 2.707%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.154'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.793'}], 'netem': [(0, 0, 'loss 2.707%'), (1, 0, 'loss 2.924%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.448'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.653'}], 'netem': [(0, 0, 'loss 0.792%'), (1, 0, 'loss 1.388%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.653'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.448'}], 'netem': [(0, 0, 'loss 1.388%'), (1, 0, 'loss 0.792%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.744'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.675'}], 'netem': [(0, 0, 'loss 1.832%'), (1, 0, 'loss 2.322%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.675'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.744'}], 'netem': [(0, 0, 'loss 2.322%'), (1, 0, 'loss 1.832%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.822'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.619'}], 'netem': [(0, 0, 'loss 1.184%'), (1, 0, 'loss 3.108%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.619'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.822'}], 'netem': [(0, 0, 'loss 3.108%'), (1, 0, 'loss 1.184%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.675'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.243'}], 'netem': [(0, 0, 'loss 3.601%'), (1, 0, 'loss 3.910%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.243'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.675'}], 'netem': [(0, 0, 'loss 3.910%'), (1, 0, 'loss 3.601%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.787'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.990'}], 'netem': [(0, 0, 'loss 1.80%'), (1, 0, 'loss 2.645%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '0.990'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.787'}], 'netem': [(0, 0, 'loss 2.645%'), (1, 0, 'loss 1.80%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.420'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.677'}], 'netem': [(0, 0, 'loss 0.329%'), (1, 0, 'loss 0.157%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.677'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.420'}], 'netem': [(0, 0, 'loss 0.157%'), (1, 0, 'loss 0.329%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.114'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.774'}], 'netem': [(0, 0, 'loss 4.360%'), (1, 0, 'loss 1.937%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '2.774'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.114'}], 'netem': [(0, 0, 'loss 1.937%'), (1, 0, 'loss 4.360%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.545'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.721'}], 'netem': [(0, 0, 'loss 2.863%'), (1, 0, 'loss 1.252%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.721'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '4.545'}], 'netem': [(0, 0, 'loss 1.252%'), (1, 0, 'loss 2.863%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.270'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.160'}], 'netem': [(0, 0, 'loss 2.73%'), (1, 0, 'loss 2.722%')]},
        {'paths': [{'queuingDelay': '0', 'delay': '0', 'bandwidth': '1.160'}, {'queuingDelay': '0', 'delay': '0', 'bandwidth': '3.270'}], 'netem': [(0, 0, 'loss 2.722%'), (1, 0, 'loss 2.73%')]},
    ]


    for i in range(times):
        quicTests(mptcpTopos)

launchTests(times=2)
