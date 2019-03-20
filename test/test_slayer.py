import sys, os

CURRENT_TEST_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(CURRENT_TEST_DIR + "/../src")

import numpy as np
import matplotlib.pyplot as plt
from slayer import spikeLayer
from data_reader import SlayerParams
import torch

net_params = SlayerParams(CURRENT_TEST_DIR + "/test_files/parameters.yaml")

Ns = int(net_params['simulation']['tSample'] / net_params['simulation']['Ts'])
spikeData = np.zeros((2, Ns))
spikeData[0, 100] = 1/net_params['simulation']['Ts']
spikeData[0, 120] = 1/net_params['simulation']['Ts']
spikeData[0, 870] = 1/net_params['simulation']['Ts']
spikeData[1, 153] = 1/net_params['simulation']['Ts']
spikeData[1, 680] = 1/net_params['simulation']['Ts']

spike = torch.FloatTensor(spikeData.reshape((1, 1, 1, 2, Ns))).to(torch.device('cuda'))

slayer = spikeLayer(net_params['neuron'], net_params['simulation'])

a = slayer.applySrmKernel(spike)

print('neuron type: ', slayer.neuron['type'])
print('Ts         : ', slayer.simulation['Ts'])
print('Device     : ', slayer.device)
print('spikeData  : ', spikeData.shape)
print('spike      : ', spike.shape)
print('psp        : ', a.shape)


###############################################################################
# testing dense layer #########################################################

# fcLayer1 = slayer.dense(512, 10)
# fcLayer2 = slayer.dense((34, 34), 10)
# fcLayer3 = slayer.dense((34, 34, 2), 10)
# print(fcLayer1.weight.shape)
# print(fcLayer2.weight.shape)
# print(fcLayer3.weight.shape)

Nbin = 100
Nin  = (34, 24, 2)
Nout = 30
NinProd = int(np.product(Nin))
input   = np.random.normal(size = (NinProd, Nbin)) 
fcLayer = slayer.dense(Nin, Nout)
# basic groundtruth calculation
weightMatrix = fcLayer.weight.cpu().data.numpy().reshape(Nout, NinProd)
output = np.dot(weightMatrix, input)
# pytorch calculation
inputTorch = torch.from_numpy(input).reshape((1, Nin[2], Nin[1], Nin[0], Nbin)).float()
outputTorch = fcLayer(inputTorch)
error = np.linalg.norm(output - outputTorch.reshape((Nout, Nbin)).cpu().data.numpy())
print('Error = ', error)



plt.figure(1)
plt.plot(np.arange(0, slayer.srmKernel.shape[0]) * slayer.simulation['Ts'], slayer.srmKernel.cpu().data.numpy(), label = 'srmKernel')
plt.plot(np.arange(0, slayer.refKernel.shape[0]) * slayer.simulation['Ts'], slayer.refKernel.cpu().data.numpy(), label = 'refKernel')
plt.legend()
plt.xlabel('Time')

plt.figure(2)
print(spike.shape[-1])
print(spike.shape[0])
plt.plot(np.arange(0, spike.shape[-1]) * slayer.simulation['Ts'], spike.cpu().data.numpy().reshape(2, Ns).transpose(), label = 'spike')
plt.gca().set_prop_cycle(None)
plt.plot(np.arange(0, spike.shape[-1]) * slayer.simulation['Ts'],     a.cpu().data.numpy().reshape(2, Ns).transpose(), label = 'psp')
plt.xlabel('Time')

plt.show()