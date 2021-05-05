import yaml

from filter import Filter


class DifferentiateFobAttacks(Filter):
    def filter(self, notification):
        if notification['type'] == 'StructureUnderAttack':
            content = yaml.load(notification['text'], Loader=yaml.FullLoader)
            if 'charID' in content and content['charID'] == 1000134:
                notification['type'] = "StructureUnderAttackByBloodRaiders"
            elif 'charID' in content and content['charID'] == 1000127:
                notification['type'] = "StructureUnderAttackByGuristas"
        return notification
