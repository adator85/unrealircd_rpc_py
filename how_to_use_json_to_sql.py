from unrealircd_rpc_py.modules.tosql.tosql import ToSql

def main():
    try:
        # PROVIDE YOUR SQL CREDENTIALS HERE
        sql = ToSql(engine_name='postgresql', # or mysql
            db_hostname='127.0.0.1',
            db_name='YOUR_DB_NAME',
            db_username='YOUR_DB_USERNAME',
            db_password='YOUR_DB_PASSWORD',
            db_port=0) # If you use default port leave the db_port to 0
        
        # IF YOU USE SQLITE, USE THE SYNTAXE BELOW
        # sql = ToSql(engine_name='sqlite')

        # PROVIDE YOUR RPC CREDENTIALS HERE
        sql.rpc_credentials.url='https://your.rpc.link:PORT/api'
        sql.rpc_credentials.username='YOUR-RPC-USER'
        sql.rpc_credentials.password='YOUR-RPC-PASSWORD'

        sql.run()
    except Exception as err:
        print(err)

if __name__ == "__main__":
    main()
