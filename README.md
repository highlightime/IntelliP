# IntelliP

## How to run
1. Install [pdm](https://pdm-project.org/en/latest/)
2. Provide [Upstage API](https://console.upstage.ai/) Key inside the `.env` file.
```
UPSTAGE_API_KEY=up_XXXXXXXXXXXXXXX
```
3. Run following script
```sh
pdm venv create
pdm sync
eval $(pdm venv activate in-project)
pdm run start
```
