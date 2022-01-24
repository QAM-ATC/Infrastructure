


## Installation

We recommend to use `virtualenv` for development:

- Start by installing `virtualenv` if you don't have it
```
pip install virtualenv
```

- Once installed access the project folder
```
cd DASHBOARD
```

- Create a virtual environment
```
virtualenv env
```

- Enable the virtual environment
```
source env/bin/activate
```

- Install the python dependencies on the virtual environment
```
pip install -r requirements.txt
```

# how to run the program

- open one terminal,run the server

```
python backend.py
```

- open another separate terminal,run react app

```
npm start run
```



## TODO: 
1. support automatic weight calculation(either by human input or by automic calculation)
2. optimize the layout and makes the layout looks nice one different size of the screen
3. add loading page to the graph.(when user click the button, there is 2s delay, there should be a loading page on both graph)
4. add sharp ratio, value at risk and max drawdown
5. prevent server crash during wrong api call
6. complete the return distribution and return frontier tab.
