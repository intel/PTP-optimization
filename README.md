# PROJECT NOT UNDER ACTIVE MANAGEMENT
This project will no longer be maintained by Intel.  
Intel has ceased development and contributions including, but not limited to, maintenance, bug fixes, new releases, or updates, to this project.  
Intel no longer accepts patches to this project.  
If you have an ongoing need to use this project, are interested in independently developing it, or would like to maintain patches for the open source software community, please create your own fork of this project.  

# Precision Time Protocol Optimization (PTP Optimization)

Precision Time Protocol (PTP) Optimization framework aims to optimize the time synchronization using the linuxptp suite by optimizing the Proportional-Integral servo’s parameters. The proposed framework automatically searches for the best variables using a Genetic Algorithm. Different evaluation functions can be used to fulfill optimization goal.

Read more: https://netdevconf.info/0x15/slides/24/netDev%200x15%20Precision%20Time%20Protocol%20optimization%20using%20genetic%20algorithm.pdf

## License

The software is copyrighted by the authors and is licensed under the GNU General Public License. See the file, COPYING, for details of the license terms.

## Hardware

PTP is implemented in PTP-aware networking hardware, that implements the IEEE 1588 standard. To succesfully run the code, an adequate Networking adapter and a proper driver must be installed in the system.

## Software

As this script uses linuxptp suite it is targeted against the linux operating system. Python3 must be installed.

### Required python packages

Use the pip to install required python packages.

```bash
pip install numpy
pip install sklearn
```

## Usage

To succesfully run the script with dedault settings run following code:

```bash
python3 main.py --i EnpXfY
```
where EpnXfY stnads for the interface name. If you want to check the interface name please run following command to print all interfaces name:

```bash
ip a
```

## Arguments

Provided script accepts a set of parameters:

| **Argument**		| **Description**								| Default |
| --------------------- | --------------------------------------------- 				| ------- |
| --pop_size		| Initial population size							| 8	  |
| --pop_size		| Number of epochs								| 10	  |
| --max_kp		| Max value of Kp								| 15	  |
| --max_kp		| Max value of Ki								| 15  	  |
| --num_random		| Number of random parents added to each epoch					| 2	  |
| --num_inherited	| Number of the best parents that are crossed to create a new generation	| 5	  |
| --num_replicated	| Number of the best parents that are replicated to create a new generation 	| 4	  |
| --mutation_coef	| Mutation coefficient								| 1	  |
| --debug_level		| Determines level of debug prints						| 1	  |
| --i			| Interface									| -	  |
| --t			| Time of a single test								| 120	  |
| --metric		| Evaluation metric (1 - MSE, 2 - RMSE, 3 - MAE)				| 1	  |
| --elite_size		| Number of elite chromosomes							| 1	  |

## Contributing

All contributions will be considered for acceptance trough pull requests. 
