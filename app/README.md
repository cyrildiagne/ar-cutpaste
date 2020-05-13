# AR Cut Paste Mobile App

An [Expo](expo.io) / [React Native](#) mobile application.
Please follow instructions from the [expo website](https://expo.io/learn) to see how to preview the app on your phone using the Expo app.

## Setup

```bash
npm install
```

Then update the IP address to point to the IP address of the computer running the local server by either:
  
  1. Using environment variable `AR_CP_SERVER_URL` or
  2. in the `serverUrl` field in [app.json](/app/app.json)

     eg `"serverUrl": "http://192.168.1.29:8080"`

## Run

If you have supplied the environment variable `AR_CP_SERVER_URL`
```bash
AR_CP_SERVER_URL="http://<ip>:<port>" npm start
```
else
```bash
npm start
```
