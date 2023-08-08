# spoti_disco
Lighting synced to spotify playback, powered by spotify audio analysis

## Currently supported smart light systems
- Yeelight

## Setup
### Example of config.json
Example config is included. Replace the values and **rename it to `config.json`**.
```
{
    "spotify":{
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_url": "YOUR_REDIRECT_URL"
    },
    "system" : "dirigera"
}
```