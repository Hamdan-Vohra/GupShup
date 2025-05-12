# Project StartUp Logic

## Basic Info

This branch contains the main logic for my chat app, that is implemented using socket programming in python
It includes two files mainly, one for server and another for client that could be run from different client.

## Handling Multiple Clients

To hanlde the multiple clients, I used threading from server side where each client will be handed over to each thread,as we are working on single machine,multi core but single CPU, so we can't initiate the logic for parallel programming, it would be on large scale.

### Variables

In this way, the variable online_users and friends_list will be local for each thread / client.

## Handling Sockets

I used my knowledge gained from university lectures, and also explore the documentation for sockets in python to make use of sockets.

## Migration from Simple Sockets to Web Sockets

Then, I transform my backend logic for web sockets and also used sockets for frontend(client/browser) to backend(server) communication.

Flask for backend
Simple JS,HTML and CSS for frontend
Mongodb for DataBase
