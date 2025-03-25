#include <iostream>
#include <crow.h>
#include <sqlite3.h>

int main()
{
    crow::SimpleApp app;

    CROW_ROUTE(app, "/")([](){
        return "Hello world";
    });

    app
    .port(18080)
    .run();
}