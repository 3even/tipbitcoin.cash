# Setup instructions

In Terminal:

```
> sudo apt update
> sudo apt upgrade -y
> sudo apt install python2.7 python-pip python3-pip
> git clone https://github.com/pokkst/tipbitcoin.cash
> cd tipbitcoin.cash
> pip install -r requirements
> pip3 install -r requirements
> pip install -r requirements.txt
> pip3 install -r requirements.txt
> nano config.ini
```

## config.ini:

```
[CashTip]
streamlabs_client_id = xxx
streamlabs_client_secret = xxx
redirect_uri = (your redirect URI, the same as the URI in the Streamlabs app)
```

In Terminal:

```
> python3 db_create.py
> nano ~/.profile
```

## ~/.profile:

```
export FLASK_APP=/root/tipbitcoin.cash/run.py
```
	
In Terminal:

```
> flask run & exit
```
