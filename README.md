# sample_thrift_app
Thrift is a marshalling technique to allow clients and servers to communicate

### Prerequisite

This application assumes you're running in Ubuntu and have python 3.x installed with PIP

perform this before proceeding further

`pip install thrift`

# Generate python (Optional)

if on ubuntu

`sudo apt install thrift`

then in this project directory

`thrift --gen py tutorial.thrift`

# Testing your setup (Required)

In one terminal do the following: 

```
cd <project_root>/servers/python_server
sh start_server.sh
```

In a second terminal do the following:

```
cd <project_root>/clientss/python_client
sh start_client.sh
```

You should see the following in each terminal :

Terminal 1:
```
% sh start_server.sh
.../sample_thrift_app/servers/python_server:.../sample_thrift_app/servers/python_server/gen_py:
Starting the server...
ping()
add(1,1)
calculate(1, Work(num1=1, num2=0, op=4, comment=None))
calculate(1, Work(num1=15, num2=10, op=2, comment=None))
getStruct(1)
```

Terminal 2:
```
% sh start_client.sh 
.../sample_thrift_app/clients/python_client:.../sample_thrift_app/clients/python_client/gen_py:
ping()
1+1=2
InvalidOperation: InvalidOperation(whatOp=4, why='Cannot divide by 0')
15-10=5
Check log: 5
```

You have now successfully connected your python client and your python server.

### Troubleshooting

If, while starting the server, you see this error

```
OSError: [Errno 48] Address already in use
```
You likely already have a Thrift server running, OR the port you are trying to use is already taken.  Feel free to modify the port in the server until it starts.  Do not forget to update the client code as well.
