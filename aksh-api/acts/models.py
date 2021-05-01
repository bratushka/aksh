from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models import DatedModel

# noinspection SpellCheckingInspection
ACT_ISSUERS = (
    ('Vinnytsia', 'Вінниця'),
    ('Lutsk', 'Луцьк'),
    ('Dnipro', 'Дніпро'),
    ('Kramatorsk', 'Краматорськ'),
    ('Zhytomyr', 'Житомир'),
    ('Uzhhorod', 'Ужгород'),
    ('Zaporizhia', 'Запоріжжя'),
    ('Ivano-Frankivsk', 'Івано-Франківськ'),
    ('Kropyvnytskyi', 'Кропивницький'),
    ('Sievierodonetsk', 'Сєвєродонецьк'),
    ('Lviv', 'Львів'),
    ('Kyiv', 'Київ'),
    ('Sevastopol', 'Севастополь'),
    ('Mykolaiv', 'Миколаїв'),
    ('Odessa', 'Одеса'),
    ('Poltava', 'Полтава'),
    ('Rivne', 'Рівне'),
    ('Sumy', 'Суми'),
    ('Ternopil', 'Тернопіль'),
    ('Kharkiv', 'Харків'),
    ('Kherson', 'Херсон'),
    ('Khmelnytskyi', 'Хмельницький'),
    ('Cherkasy', 'Черкаси'),
    ('Chernivtsi', 'Чернівці'),
    ('Chernihiv', 'Чернігів'),
)


def _document__file__upload_to(document: 'Document', filename: str) -> str:
    return f'acts/{document.act.issuer}/{filename}'


class Act(DatedModel):
    class Meta:
        unique_together = (('issuer', 'act_id'),)

    issuer = models.TextField(choices=ACT_ISSUERS)
    act_id = models.TextField()
    title = models.TextField()

    # Whether the data was successfully forwarded to interes.shtab.net
    forwarded = models.BooleanField(default=False)

    removed_from_source = models.BooleanField(default=False)
    needs_inspection = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.get_issuer_display()}: {self.act_id}: {self.title}'


class Document(DatedModel):
    act = models.ForeignKey(Act, models.CASCADE, related_name='documents')
    order = models.PositiveSmallIntegerField()
    url = models.TextField()
    file = models.FileField(
        max_length=1000,
        null=True,
        blank=True,
        upload_to=_document__file__upload_to,
    )
    last_modified = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.url
