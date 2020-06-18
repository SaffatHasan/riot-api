import secrets
import requests

API_KEY = secrets.RIOT_API_KEY


class RiotApi:
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        self.base = "https://na1.api.riotgames.com"

    def get_live_game_info_by_summoner(self, summoner_name):
        summoner_id = self.get_summoner(summoner_name)['id']
        url = f"/lol/spectator/v4/active-games/by-summoner/{summoner_id}"
        return self.perform_request(url)

    def get_kills_and_assists_by_summoner(self, summoner_name):
        participant_id = self.get_most_recent_match_participant_id(summoner_name)
        match_timeline = self.get_most_recent_match_timeline(summoner_name)
        events = []
        for frame in match_timeline['frames']:
            for event in frame['events']:
                if event['type'] == 'CHAMPION_KILL':
                    if event['killerId'] == participant_id or participant_id in event['assistingParticipantIds']:
                        events.append(event)
        return events

    def get_most_recent_match_timeline(self, summoner_name):
        # TODO null case check
        game_id = self.get_most_recent_match_id(summoner_name)
        return self.perform_request(f"/lol/match/v4/timelines/by-match/{game_id}")

    def get_most_recent_match_participant_id(self, summoner_name):
        game_id = self.get_most_recent_match_id(summoner_name)
        url = f"/lol/match/v4/matches/{game_id}"
        result = self.perform_request_by_summoner_name(summoner_name, url)
        participants = result["participantIdentities"]

        for participant in participants:
            if participant["player"]["summonerName"] == summoner_name:
                return participant["participantId"]
        raise ValueError("Could not find summoner in that game")

    def get_most_recent_match_id(self, summoner_name):
        return self.get_most_recent_match(summoner_name)['gameId']

    def get_most_recent_match(self, summoner_name):
        return self.get_summoner_games(summoner_name)['matches'][0]

    def get_summoner_games(self, summoner_name):
        url = "/lol/match/v4/matchlists/by-account/{}"
        return self.perform_request_by_summoner_name(summoner_name, url)

    def perform_request_by_summoner_name(self, summoner_name, url):
        account_id = self.get_account_id(summoner_name)
        return self.perform_request(url.format(account_id))

    def get_account_id(self, summoner_name):
        return self.get_summoner(summoner_name)['accountId']

    def get_summoner(self, summoner_name):
        url = f"/lol/summoner/v4/summoners/by-name/{summoner_name}"
        return self.perform_request(url)

    def perform_request(self, url, data={}):
        data['api_key'] = self.API_KEY
        req = requests.get(self.base + url, data)
        return req.json()


def main():
    api = RiotApi(API_KEY)
    summoner_name = "Fidoz"
    print(api.get_summoner(summoner_name))
    print(api.get_most_recent_match(summoner_name))
    print(api.get_most_recent_match_participant_id(summoner_name))
    print(api.get_most_recent_match_timeline(summoner_name))
    print(api.get_kills_and_assists_by_summoner(summoner_name))
    print(api.get_live_game_info_by_summoner(summoner_name))


if __name__ == "__main__":
    main()
