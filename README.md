# AKSh

## Setup

1. Get the `.data` folder with the latest data (db and media files)
1. Get the `.envs` folder with the env vars
1. Build the images with `docker-compose build`

## Run parsers

1. Run the containers with `docker-compose up`
1. From a browser console run:
    ```js
    {
        const ws = new WebSocket('ws://localhost:8001/acts/ws/');
        ws.onmessage = ({data}) => console.log(JSON.parse(data));
        ws.onopen = () => ws.send('hello');
    }
    ```
1. Check the browser console output and containers logs

## Roadmap

1. Build the frontend application to run parsers and display progress
1. Handle the errors across the application (use `try-except` where needed)
1. Write more parsers
