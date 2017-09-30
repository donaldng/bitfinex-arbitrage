# Arbitrage

The purpose of this arbitrage bot is to find arbitrage opportunity in between of pairs instead of exchanges.

Currently it can only tracks for arbitrage opportunity. Automated trading on arbitrage opportunity will be added soon.

### How to use

To start the program, execute run.py and pass in symbol paramenter. 

E.g. Symbol parameter as in IOT, OMG, etc.

```sh
$ cd arbitrage
$ python3 run.py iot 
```

### Installation

This arbitrage bot requires [Python 3.x.x](https://www.python.org/downloads/) to run.

Then you need to install required modules.

```sh
$ cd arbitrage
$ python3 -m pip install -r requirements.txt
```

### Todos
Auto trading is currenly under development, features to be implement as below:
  - Entry position - validate through orderbook 
  - Exit mechanism

License
----

This project is licensed under the MIT License - see the LICENSE.md file for details

