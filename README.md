Reconbot for Eve Online
=======================

Reconbot is a notification relay bot for an MMO game [Eve Online](https://www.eveonline.com/signup?invc=6b509cb9-dbab-48a1-b30b-d81796f9a4df).
It fetches character notifications from the EVE API, filters irrelevant ones out and sends relevant ones to set Discord channels.
Notifications like SOV changes, SOV/POS/POCO/Citadel attacks.

# Setup

Reconbot was intended to be used as a base for further customizations, or integration with other systems, but it can be run via `run.py` as well. Check it out for an example.

## 1. EVE Developer Application

This tool is ready to be used with [Eve's ESI API](https://esi.tech.ccp.is/). You will need to register your application on [EVE Developers page](https://developers.eveonline.com/applications).

When registering your EVE Application, please pick `Authentication & API Access` connection type, and make sure your application requests these permissions:

- `esi-universe.read_structures.v1` - necessary to fetch names of any linked structures;
- `esi-characters.read_notifications.v1` - necessary to fetch character level notifications.

Reconbot does not provide a way to authenticate an account to an application, so you will need to do so via some other means. First two sections of Fuzzysteve's guide on [Using ESI with Google Sheets](https://www.fuzzwork.co.uk/2017/03/14/using-esi-google-sheets/) explain how to do that via [Postman](https://www.getpostman.com/).

When registering the application take note of the `Client ID` and `Secret Key`, as they are necessary for Reconbot to establish communication with ESI API.

## 2. Discord chat tool

__To use a Discord webhook:__

Webhooks are the easiest way to integrate Reconbot with Discord. Simply follow [this Discord guide](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks) to create a webhook for your channel.
You should now have a URL like this:
```
https://discordapp.com/api/webhooks/496014874437332490/5783au24jzyEFIaWnfTvJn0gFzh5REEEE3ee3e3eNKeFee3We2cIe_6e7e36ugUj5zEm
```

## 3. Reconbot setup

1. Clone this repository
2. Create a virtualenv environment: `virtualenv -p python3 venv`
3. Activate the virtualenv environment: `source venv/bin/activate`. This will isolate reconbot's dependencies from the rest of your system's dependencies.
4. Install Python depdendencies: `pip install -r requirements.txt`
5. Modify `reconbot.ini` with your EVE API keys, key groups and Discord accounts/channels.
6. Execute `python run.py` and wait for notifications to arrive! After the character gets a notification in-game, `reconbot` may take up to 10 minutes to detect the notification.

# Other notes

Reconbot by default will try to evenly spread out checking API keys over the cache _half_ the expiry window (which is 10 minutes for ESI), meaning that with 2 API keys in rotation an API key will be checked every ~3 minutes (with 5 keys, every minute), which can be useful to detect alliance or corporation-wide notifications more frequently than only once every 10 minutes. It will not check more than 1 API key per minute right now.

## Supported notifications

As of writing this tool there is little documentation about the types of notifications available and their contents. The following list has been assembled from working experience, is not fully complete and may be subject to change as CCP changes internals:

- AllWarDeclaredMsg
- DeclareWar
- AllWarInvalidatedMsg
- AllyJoinedWarAggressorMsg
- CorpWarDeclaredMsg
- EntosisCaptureStarted
- SovCommandNodeEventStarted
- SovStructureDestroyed
- SovStructureReinforced
- StructureUnderAttack
- OwnershipTransferred
- StructureOnline
- StructureDestroyed
- StructureFuelAlert
- StructureWentLowPower
- StructureWentHighPower
- StructureFuelAlert
- StructureAnchoring
- StructureUnanchoring
- StructureServicesOffline
- StructureLostShields
- StructureLostArmor
- TowerAlertMsg
- TowerResourceAlertMsg
- StationServiceEnabled
- StationServiceDisabled
- OrbitalReinforced
- OrbitalAttacked
- SovAllClaimAquiredMsg
- SovStationEnteredFreeport
- AllAnchoringMsg
- InfrastructureHubBillAboutToExpire
- SovAllClaimLostMsg
- SovStructureSelfDestructRequested
- SovStructureSelfDestructFinished
- StationConquerMsg
- MoonminingExtractionStarted
- MoonminingExtractionCancelled
- MoonminingExtractionFinished
- MoonminingLaserFired
- MoonminingAutomaticFracture
- CorpAllBillMsg
- BillPaidCorpAllMsg
- CharAppAcceptMsg
- CorpAppNewMsg
- CharAppWithdrawMsg
- CharLeftCorpMsg
- CorpNewCEOMsg
- CorpVoteMsg
- CorpVoteCEORevokedMsg
- CorpTaxChangeMsg
- CorpDividendMsg
- BountyClaimMsg
- KillReportVictim
- KillReportFinalBlow
- AllianceCapitalChanged

Do you have sample contents of currently unsupported notification types? Consider sharing them by creating an issue, or submit a Pull Request. Any help would be appreciated!
