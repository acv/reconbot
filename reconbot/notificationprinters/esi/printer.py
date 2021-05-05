import abc
import datetime
import yaml
import requests

from reconbot.notificationprinters.esi.formatter import Formatter


class Printer(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, eve):
        self.eve = eve

    def transform(self, notification):
        text = self.get_notification_text(notification)
        timestamp = self.timestamp_to_date(notification['timestamp'])
        ping = ':gasp:'

        notification_type = notification['type']
        if notification_type == 'StructureUnderAttack':
            ping = ':scream: @everyone '
        elif notification_type == "StructureUnderAttackByBloodRaiders":
            ping = ':scream: :blooders: '
        elif notification_type == "StructureUnderAttackByGuristas":
            ping = ':scream: :guristas: '
        elif notification_type == 'StructureFuelAlert' or notification_type == 'StructureServicesOffline':
            ping = ':fuelpump: @everyone '
        elif notification_type == 'WarDeclared':
            ping = ':scream: @everyone '
        elif notification_type == 'MoonminingExtractionFinished':
            ping = ':gasp: @Mining '

        return '%s `[%s]` %s' % (ping, timestamp, text)

    def get_notification_text(self, notification):

        types = {
            'AllWarDeclaredMsg': self.corporation_war_declared,
            'DeclareWar': self.declare_war,
            'WarDeclared': self.war_declared,
            'AllWarInvalidatedMsg': self.corporation_war_invalidated,
            'AllyJoinedWarAggressorMsg': self.aggressor_ally_joined_war,
            'CorpWarDeclaredMsg': self.corporation_war_declared,
            'EntosisCaptureStarted': self.entosis_capture_started,
            'SovCommandNodeEventStarted': self.sov_structure_command_nodes_decloaked,
            'SovStructureDestroyed': self.sov_structure_destroyed,
            'SovStructureReinforced': self.sov_structure_reinforced,
            'StructureUnderAttack': self.citadel_attacked,
            'StructureUnderAttackByBloodRaiders': self.citadel_attacked_by_blooders,
            'StructureUnderAttackByGuristas': self.citadel_attacked_by_guristas,
            'OwnershipTransferred': self.structure_transferred,
            'StructureOnline': self.citadel_onlined,
            'StructureDestroyed': self.citadel_destroyed,
            'StructureFuelAlert': self.citadel_low_fuel,
            'StructureWentLowPower': self.citadel_low_power,
            'StructureWentHighPower': self.citadel_high_power,
            'StructureAnchoring': self.citadel_anchored,
            'StructureUnanchoring': self.citadel_unanchoring,
            'StructureServicesOffline': self.citadel_out_of_fuel,
            'StructureLostShields': self.citadel_lost_shields,
            'StructureLostArmor': self.citadel_lost_armor,
            'TowerAlertMsg': self.pos_attack,
            'TowerResourceAlertMsg': self.pos_fuel_alert,
            'StationServiceEnabled': self.entosis_enabled_structure,
            'StationServiceDisabled': self.entosis_disabled_structure,
            'OrbitalReinforced': self.customs_office_reinforced,
            'OrbitalAttacked': self.customs_office_attacked,
            'SovAllClaimAquiredMsg': self.sov_claim_acquired,
            'SovStationEnteredFreeport': self.sov_structure_freeported,
            'AllAnchoringMsg': self.structure_anchoring_alert,
            'InfrastructureHubBillAboutToExpire': self.ihub_bill_about_to_expire,
            'SovAllClaimLostMsg': self.sov_claim_lost,
            'SovStructureSelfDestructRequested': self.sov_structure_started_self_destructing,
            'SovStructureSelfDestructFinished': self.sov_structure_self_destructed,
            'StationConquerMsg': self.station_conquered,
            'MoonminingExtractionStarted': self.moon_extraction_started,
            'MoonminingExtractionCancelled': self.moon_extraction_cancelled,
            'MoonminingExtractionFinished': self.moon_extraction_finished,
            'MoonminingLaserFired': self.moon_extraction_turned_into_belt,
            'MoonminingAutomaticFracture': self.moon_extraction_autofractured,
            'CorpAllBillMsg': self.corporation_bill,
            'BillPaidCorpAllMsg': self.corporation_bill_paid,
            'CharAppAcceptMsg': self.character_application_accepted,
            'CorpAppNewMsg': self.new_character_application_to_corp,
            'CharAppWithdrawMsg': self.character_application_withdrawn,
            'CharLeftCorpMsg': self.character_left_corporation,
            'CorpNewCEOMsg': self.new_corporation_ceo,
            'CorpVoteMsg': self.corporation_vote_initiated,
            'CorpVoteCEORevokedMsg': self.corporation_vote_for_ceo_revoked,
            'CorpTaxChangeMsg': self.corporation_tax_changed,
            'CorpDividendMsg': self.corporation_dividend_paid_out,
            'BountyClaimMsg': self.bounty_claimed,
            'KillReportVictim': self.kill_report_victim,
            'KillReportFinalBlow': self.kill_report_final_blow,
            'AllianceCapitalChanged': self.alliance_capital_changed,
            'WarRetractedByConcord': self.war_retracted_by_concord,

            # kept for older messages
            'notificationTypeMoonminingExtractionStarted': self.moon_extraction_started,
        }

        if notification['type'] in types:
            print("-------------")
            print(notification['text'])
            print("---")
            text = yaml.load(notification['text'], Loader=yaml.FullLoader)
            text['notification_timestamp'] = notification['timestamp']
            template = types[notification['type']]()

            rendered_notification = template.format(Formatter(self, text)) 
            return rendered_notification

        return 'Unknown notification type for printing [' + notification['type'] + ']'

    # againstID: 99008816
    # cost: 100000000
    # declaredByID: 99006941
    # delayHours: 24
    # hostileState: false
    # timeStarted: 132646817400000000
    # warHQ: <b>Osoggur - This is war HQgrad</b>
    # warHQ_IdType:
    # - 1031415482668
    # - 35832
    @staticmethod
    def war_declared():
        return 'War has been declared against {0:get_corporation_or_alliance(againstID)} by {0:get_corporation_or_alliance(declaredByID)} with War HQ {0:get_string_preserve_bold(warHQ)}'

    @staticmethod
    def corporation_war_declared():
        return 'War has been declared to {0:get_corporation_or_alliance(againstID)} by {0:get_corporation_or_alliance(declaredByID)}'

    @staticmethod
    def declare_war():
        return '{0:get_character(charID)} from {0:get_corporation_or_alliance(entityID)} has declared war to {0:get_corporation_or_alliance(defenderID)}'

    @staticmethod
    def corporation_war_invalidated():
        return 'War against {0:get_corporation_or_alliance(againstID)} has been invalidated by {0:get_corporation_or_alliance(declaredByID)}'

    @staticmethod
    def war_retracted_by_concord():
        return 'War against {0:get_corporation_or_alliance(againstID)} has been invalidated by CONCORD'

    @staticmethod
    def aggressor_ally_joined_war():
        return 'Ally {0:get_corporation_or_alliance(allyID)} joined the war to help {0:get_corporation_or_alliance(defenderID)} starting {0:eve_timestamp_to_date(startTime)}'

    @staticmethod
    def sov_claim_lost():
        return 'SOV lost in {0:get_system(solarSystemID)} by {0:get_corporation(corpID)}'

    @staticmethod
    def sov_claim_acquired():
        return 'SOV acquired in {0:get_system(solarSystemID)} by {0:get_corporation(corpID)}'

    @staticmethod
    def pos_anchoring_alert():
        return 'New POS anchored in "{0:get_moon(moonID)}" by {0:get_corporation(corpID)}'

    @staticmethod
    def pos_attack():
        return '{0:get_moon(moonID)} POS "{0:get_item(typeID)}" ({0:get_percentage(shieldValue)} shield, {0:get_percentage(armorValue)} armor, {0:get_percentage(hullValue)} hull) under attack by {0:get_character(aggressorID)}'

    @staticmethod
    def pos_fuel_alert():
        return '{0:get_moon(moonID)} POS "{0:get_item(typeID)}" is low on fuel: {0:get_pos_wants(wants)}'

    @staticmethod
    def station_conquered():
        return "Station conquered from {0:get_corporation(oldOwnerID)} by {0:get_corporation(newOwnerID)} in {0:get_system(solarSystemID)}"

    @staticmethod
    def customs_office_attacked():
        return '"{0:get_planet(planetID)}" POCO ({0:get_percentage(shieldLevel)} shields) has been attacked by {0:get_character(aggressorID)}'

    @staticmethod
    def customs_office_reinforced():
        return '"{0:get_planet(planetID)}" POCO has been reinforced by {0:get_character(aggressorID)} (comes out of reinforce on "{0:eve_timestamp_to_date(reinforceExitTime)}")'

    @staticmethod
    def structure_transferred():
        return '{0:get_item(structureTypeID)} {0:get_string(structureName)} structure in {0:get_system(solarSystemID)} has been transferred from {0:get_corporation(oldOwnerCorpID)} to {0:get_corporation(newOwnerCorpID)} by {0:get_character(charID)}'

    @staticmethod
    def entosis_capture_started():
        return 'Capturing of "{0:get_item(structureTypeID)}" in {0:get_system(solarSystemID)} has started'

    @staticmethod
    def entosis_enabled_structure(self):
        return 'Structure "{0:get_item(structureTypeID)}" in {0:get_system(solarSystemID)} has been enabled'

    @staticmethod
    def entosis_disabled_structure(self):
        return 'Structure "{0:get_item(structureTypeID)}" in {0:get_system(solarSystemID)} has been disabled'

    @staticmethod
    def sov_structure_reinforced(self):
        return 'SOV structure "{0:get_campaign_event_type(campaignEventType)}" in {0:get_system(solarSystemID)} has been reinforced, nodes will decloak "{0:eve_timestamp_to_date(decloakTime)}"'

    @staticmethod
    def sov_structure_command_nodes_decloaked(self):
        return 'Command nodes for "{0:get_campaign_event_type(campaignEventType)}" SOV structure in {0:get_system(solarSystemID)} have decloaked'

    @staticmethod
    def sov_structure_destroyed(self):
        return 'SOV structure "{0:get_item(structureTypeID)}" in {0:get_system(solarSystemID)} has been destroyed'

    @staticmethod
    def sov_structure_freeported(self):
        return 'SOV structure "{0:get_item(structureTypeID)}" in {0:get_system(solarSystemID)} has been freeported, exits freeport on "{0:eve_timestamp_to_date(freeportexittime)}"'

    @staticmethod
    def citadel_low_fuel(self):
        return 'Citadel (__**{0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}"**__) low fuel alert in {0:get_system(solarsystemID)}'

    @staticmethod
    def citadel_low_power(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") went into low power mode in {0:get_system(solarsystemID)}'

    @staticmethod
    def citadel_high_power(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") went into high power mode in {0:get_system(solarsystemID)}'

    @staticmethod
    def citadel_anchored(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") anchored in {0:get_system(solarsystemID)} by {0:get_corporation_from_link(ownerCorpLinkData)}'

    @staticmethod
    def citadel_unanchoring(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") unanchoring in {0:get_system(solarsystemID)} by {0:get_corporation_from_link(ownerCorpLinkData)}'

    @staticmethod
    def citadel_attacked(self):
        return 'Citadel (__**{0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}"**__) attacked ({0:get_percentage(shieldPercentage)} shield, {0:get_percentage(armorPercentage)} armor, {0:get_percentage(hullPercentage)} hull) in {0:get_system(solarsystemID)} by {0:get_character(charID)}'

    @staticmethod
    def citadel_attacked_by_blooders(self):
        return 'Citadel (__**{0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}"**__) attacked in {0:get_system(solarsystemID)} by Blood Raiders.'

    @staticmethod
    def citadel_attacked_by_guristas(self):
        return 'Citadel (__**{0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}"**__) attacked in {0:get_system(solarsystemID)} by Guristas.'

    @staticmethod
    def citadel_onlined(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") onlined in {0:get_system(solarsystemID)}'

    @staticmethod
    def citadel_lost_shields(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") lost shields in {0:get_system(solarsystemID)} (comes out of reinforce on "{0:eve_duration_to_date(notification_timestamp, timeLeft)}")'

    @staticmethod
    def citadel_lost_armor(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") lost armor in {0:get_system(solarsystemID)} (comes out of reinforce on "{0:eve_duration_to_date(notification_timestamp, timeLeft)}")'

    @staticmethod
    def citadel_destroyed(self):
        return 'Citadel ({0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}") destroyed in {0:get_system(solarsystemID)} owned by {0:get_corporation_from_link(ownerCorpLinkData)}'

    @staticmethod
    def citadel_out_of_fuel(self):
        return 'Citadel (__**{0:get_structure_type_from_link(structureShowInfoData)}, "{0:get_structure_name(structureID)}"**__) ran out of fuel in {0:get_system(solarsystemID)} with services "{0:get_citadel_services(listOfServiceModuleIDs)}"'

    @staticmethod
    def structure_anchoring_alert(self):
        return 'New structure ({0:get_item(typeID)}) anchored in "{0:get_moon(moonID)}" by {0:get_corporation(corpID)}'

    @staticmethod
    def ihub_bill_about_to_expire(self):
        return 'IHUB bill to {0:get_corporation(corpID)} for system {0:get_system(solarSystemID)} will expire {0:eve_timestamp_to_date(dueDate)}'

    @staticmethod
    def sov_structure_self_destructed(self):
        return 'SOV structure "{0:get_item(structureTypeID)}" has self destructed in {0:get_system(solarSystemID)}'

    @staticmethod
    def sov_structure_started_self_destructing(self):
        return 'Self-destruction of "{0:get_item(structureTypeID)}" SOV structure in {0:get_system(solarSystemID)} has been requested by {0:get_character(charID)}. Structure will self-destruct on "{0:eve_timestamp_to_date(destructTime)}"'

    @staticmethod
    def moon_extraction_started(self):
        return 'Moon extraction started by {0:get_character(startedBy)} in {0:get_system(solarSystemID)} ({0:get_moon(moonID)}, "{0:get_string(structureName)}") and will be ready on {0:eve_timestamp_to_date(readyTime)} (or will auto-explode into a belt on {0:eve_timestamp_to_date(autoTime)})'

    @staticmethod
    def moon_extraction_cancelled(self):
        return 'Moon extraction cancelled by {0:get_character(cancelledBy)} in {0:get_system(solarSystemID)} ({0:get_moon(moonID)}, "{0:get_string(structureName)}")'

    @staticmethod
    def moon_extraction_finished():
        return 'Moon extraction has finished and is ready in {0:get_system(solarSystemID)} ({0:get_moon(moonID)}, "{0:get_string(structureName)}") to be exploded into a belt (or will auto-explode into one on {0:eve_timestamp_to_date(autoTime)})'

    @staticmethod
    def moon_extraction_turned_into_belt():
        return 'Moon laser has been fired by {0:get_character(firedBy)} in {0:get_system(solarSystemID)} ({0:get_moon(moonID)}, "{0:get_string(structureName)}") and the belt is ready to be mined'

    @staticmethod
    def moon_extraction_autofractured():
        return 'Moon extraction in {0:get_system(solarSystemID)} ({0:get_moon(moonID)}, "{0:get_string(structureName)}") has autofractured into a belt and is ready to be mined'

    @staticmethod
    def corporation_bill():
        return 'Corporation bill issued to {0:get_corporation_or_alliance(debtorID)} by {0:get_corporation_or_alliance(creditorID)} for the amount of {0:get_isk(amount)} at {0:eve_timestamp_to_date(currentDate)}. Bill is due {0:eve_timestamp_to_date(dueDate)}'

    @staticmethod
    def corporation_bill_paid():
        return 'Corporation bill for {0:get_isk(amount)} was paid. Bill was due {0:eve_timestamp_to_date(dueDate)}'

    @staticmethod
    def new_character_application_to_corp():
        return 'Character {0:get_character(charID)} has applied to corporation {0:get_corporation(corpID)}. Application text:\n\n{0:get_string(applicationText)}'

    @staticmethod
    def character_application_withdrawn():
        return 'Character {0:get_character(charID)} application to corporation {0:get_corporation(corpID)} has been withdrawn'

    @staticmethod
    def character_application_accepted():
        return 'Character {0:get_character(charID)} accepted to corporation {0:get_corporation(corpID)}'

    @staticmethod
    def character_left_corporation():
        return 'Character {0:get_character(charID)} left corporation {0:get_corporation(corpID)}'

    @staticmethod
    def new_corporation_ceo():
        return '{0:get_character(newCeoID)} has replaced {0:get_character(oldCeoID)} as the new CEO of {0:get_corporation(corpID)}'

    @staticmethod
    def corporation_vote_initiated():
        return 'New corporation vote for "{0:get_string(subject)}":\n\n{0:get_string(body)}'

    @staticmethod
    def corporation_vote_for_ceo_revoked():
        return 'Corporation "{0:get_corporation(corpID)}" vote for new CEO has been revoked by {0:get_character(charID)}'

    @staticmethod
    def corporation_tax_changed():
        return 'Tax changed from {0:get_percentage(oldTaxRate)} to {0:get_percentage(newTaxRate)} for {0:get_corporation(corpID)}'

    @staticmethod
    def corporation_dividend_paid_out():
        return 'Corporation {0:get_corporation(corpID)} has paid out {0:get_isk(payout)} ISK in dividends'

    @staticmethod
    def bounty_claimed():
        return 'A bounty of {0:get_isk(amount)} has been claimed for killing {0:get_character(charID)}'

    @staticmethod
    def kill_report_victim():
        return 'Died in a(n) {0:get_item(victimShipTypeID)}: {0:get_killmail(killMailID, killMailHash)}'

    @staticmethod
    def kill_report_final_blow():
        return 'Got final blow on {0:get_item(victimShipTypeID)}: {0:get_killmail(killMailID, killMailHash)}'

    @staticmethod
    def alliance_capital_changed():
        return 'Alliance capital system of {0:get_alliance(allianceID)} has changed to {0:get_system(solarSystemID)}'

    @abc.abstractmethod
    def get_corporation(self, corporation_id):
        return

    @abc.abstractmethod
    def get_alliance(self, alliance_id):
        return

    def get_corporation_or_alliance(self, entity_id):
        try:
            return self.get_corporation(entity_id)
        except requests.RequestException:
            return self.get_alliance(entity_id)

    def get_item(self, item_id):
        item = self.eve.get_item(item_id)
        return item['name']

    @abc.abstractmethod
    def get_system(self, system_id):
        return

    def get_planet(self, planet_id):
        planet = self.eve.get_planet(planet_id)
        system = self.get_system(planet['system_id'])
        return '%s in %s' % (planet['name'], system)

    def get_moon(self, moon_id):
        moon = self.eve.get_moon(moon_id)
        return moon['name']

    @abc.abstractmethod
    def get_character(self, character_id):
        return

    @abc.abstractmethod
    def get_killmail(self, kill_id, killmail_hash):
        return

    @staticmethod
    def get_campaign_event_type(event_type):
        if event_type == 1:
            return 'TCU'
        elif event_type == 2:
            return 'IHUB'
        elif event_type == 3:
            return 'Station'
        else:
            return 'Unknown structure type "%d"' % event_type

    def get_structure_name(self, structure_id):
        structure = self.eve.get_structure(structure_id)
        if 'name' in structure:
            return structure['name']
        else:
            return "Unknown name"

    @staticmethod
    def timestamp_to_date(timestamp):
        return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def eve_timestamp_to_date(microseconds):
        """
        Convert microsoft epoch to unix epoch
        Based on: http://www.wiki.eve-id.net/APIv2_Char_NotificationTexts_XML
        """

        seconds = microseconds/10000000 - 11644473600
        return datetime.datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def eve_duration_to_date(timestamp, microseconds):
        """
        Convert microsoft epoch to unix epoch
        Based on: http://www.wiki.eve-id.net/APIv2_Char_NotificationTexts_XML
        """

        seconds = microseconds/10000000
        timedelta = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(seconds=seconds)
        return timedelta.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_percentage(value):
        if value <= 1:
            value = value * 100
        return '%.1f%%' % value

    @staticmethod
    def get_isk(isk):
        return '%.2f ISK' % isk

    @staticmethod
    def get_string(value):
        return str(value)

    @staticmethod
    def get_string_preserve_bold(value):
        return str(value).replace('<b>', '**').replace('</b>', '**')

    def get_corporation_from_link(self, show_info):
        return self.get_corporation(show_info[-1])

    def get_structure_type_from_link(self, show_info):
        return self.get_item(show_info[1])

    def get_system_from_link(self, show_info):
        return self.get_system(show_info[-1])

    def get_character_from_link(self, show_info):
        return self.get_character(show_info[-1])

    def get_pos_wants(self, wants):
        wants = map(lambda w: '%s: %d' % (self.get_item(w['typeID']), w['quantity']), wants)

        return ', '.join(wants)

    def get_citadel_services(self, modules):
        services = map(lambda item_id: self.get_item(item_id), modules)

        return ', '.join(services)
