from typing import List, Optional


class DiscordEmbedField(object):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def as_data_struct(self):
        return {'name': self.name, 'value': self.value}

    def as_text(self) -> str:
        return f"{self.name}: {self.value}"


class DiscordEmbed(object):
    title: Optional[str]
    description: Optional[str]
    thumbnail: Optional[str]
    fields: List[DiscordEmbedField]

    def __init__(self):
        self.title = None
        self.description = None
        self.thumbnail = None
        self.fields = []

    def set_title(self, title: str):
        self.title = title

    def set_description(self, description: str):
        self.description = description

    def set_thumbnail(self, thumbnail: str):
        self.thumbnail = thumbnail

    def add_field(self, field: DiscordEmbedField):
        self.fields.append(field)

    def as_data_struct(self):
        struct = {}
        if self.title is not None:
            struct['title'] = self.title
        if self.description is not None:
            struct['description'] = self.description
        if self.thumbnail is not None:
            struct['thumbnail'] = self.thumbnail
        if len(self.fields) > 0:
            struct['fields'] = [field.as_data_struct() for field in self.fields]
        return struct

    def as_text(self) -> str:
        parts = []
        if self.title is not None:
            parts.append(self.title)
        if self.description is not None:
            parts.append(self.description)
        for field in self.fields:
            parts.append(field.as_text())
        return "\n".join(parts)
