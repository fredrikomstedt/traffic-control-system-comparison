# A Comparison of Algorithms Used In Traffic Control Systems

## What is this?

This repository contains code for the traffic control algorithms compared in [A comparison of algorithms used in traffic control systems](http://kth.diva-portal.org/smash/record.jsf?pid=diva2%3A1214166&dswid=-3314).

## How is it used?

It was tested using **SUMO v0.32**. There seem to be issues with future versions of **SUMO** so it is recommended to use **v0.32** when running this code. It is recommended that you have some knowledge about how **SUMO** works before using the code in this repository. Information about **SUMO** can be found [here](https://sumo.dlr.de/docs/index.html).

The algorithms are defined in the `*_traffic_light.py` files. Each algorithm works differently. The `trivial` variant is purely time-based. The `deterministic` variant utilizes functions to calculate the time needed for each lane. The `learning` variant utilizes reinforcement learning to figure out the best approach. This final variant must therefore be trained before it can be properly evaluated. More information about these algorithms can be found in the paper this repository was used for (link available above).

There are several ways of testing the algorithms. Each `*_traffic_light.py` file can be run independently, and this will produce output to `stdout`. It is also possible to run the algorithms through `tester.py`, which provides command line options to choose the traffic demand and algorithm to use. This approach appends the output to the file `results.txt`. As such, the results file contains results from several tests. To speed up the process of running many tests, scripts such as `uniform_tester.sh` can therefore be used. 

To generate a new traffic demand to test on, run `generate_routefile.py` or use the `--generate_file` command with `tester.py`.

## Authors

If this work was useful to you, please consider citing it using the following BibTeX entry:
```
@thesis{Björck_Omstedt_2018, 
  title={A comparison of algorithms used in traffic control systems},
  url={http://urn.kb.se/resolve?urn=urn:nbn:se:kth:diva-229709},
  author={Björck, Erik and Omstedt, Fredrik},
  year={2018},
  type={Bachelor's Thesis}
}
```
