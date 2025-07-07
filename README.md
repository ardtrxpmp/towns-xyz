** TOWNS **

setup:
venv - python 3.10 - 3.12

pip install -r requirements.txt
pip install pyuseragents
pip install loguru
playwright install

private keys - ciphered format
proxies - http://user:pass@ip:port
emails - tested on outlook. format: email----pass----client id----refresh token

settings yaml

gpt key on top
change values as you like

run main.py
choose modules
login is dynamic, except for linking the wallet. i would suggest doing the fetch internal wallet login first and then funding, that way you will login with cookies afterwards