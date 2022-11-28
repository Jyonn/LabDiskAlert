import datetime
import json

from SmartDjango import models, E
from django.utils.crypto import get_random_string

from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class HostError:
    NOT_FOUND = E("不存在的主机")
    DISK_NOT_FOUND = E("不存在的磁盘")
    TOKEN_ERROR = E("口令错误")
    NAME_EXISTS = E("主机名已存在")


class Host(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True,
    )

    internal_ip = models.CharField(
        max_length=20,
        unique=True,
    )

    token = models.CharField(
        max_length=32,
    )

    alert_percentage = models.IntegerField(
        default=80,
    )

    silent = models.BooleanField(
        default=False,
    )

    @classmethod
    def get_all(cls, executor: User):
        host_list = cls.objects.all()
        if not executor.is_admin:
            host_list = host_list.filter(silent=False)
        return host_list.dict(lambda host: host.d(executor))

    def d(self, executor: User = None):
        fields = ['name', 'internal_ip', 'token', 'alert_percentage', 'silent']
        if executor and executor.is_admin:
            fields.append('token')
        return self.dictify(*fields)

    @classmethod
    def get_host_by_name(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist as err:
            raise HostError.NOT_FOUND(debug_message=err)

    @classmethod
    def name_exists(cls, name):
        return cls.objects.filter(name=name).exists()

    @classmethod
    def generate_token(cls):
        return get_random_string(32)

    @classmethod
    def create(cls, name, internal_ip):
        if cls.name_exists(name):
            raise HostError.NAME_EXISTS
        return cls.objects.create(
            name=name,
            internal_ip=internal_ip,
            token=cls.generate_token(),
            alert_percentage=80,
            silent=False,
        )

    def auth(self, token):
        if self.token != token:
            raise HostError.TOKEN_ERROR
        return self

    def update_silent(self, silent):
        self.silent = silent
        self.save()
        return self

    def get_disks(self, executor: User = None):
        hostdisk_list = self.hostdisk_set.all()
        if not executor or not executor.is_admin:
            hostdisk_list = hostdisk_list.filter(listen=True)
        return hostdisk_list.dict(HostDisk.d)

    def get_users(self):
        return self.hostdisk_set.all().dict(HostDisk.d)


class HostDisk(models.Model):
    class Meta:
        unique_together = ('host', 'name')

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=20,
    )

    listen = models.BooleanField(
        default=False,
    )

    last_logging_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_logging_data = models.TextField(
        null=True,
        blank=True,
    )

    def _readable_last_logging_time(self):
        if self.last_logging_time:
            return self.last_logging_time.timestamp()

    def _readable_last_logging_data(self):
        if self.last_logging_data:
            return json.loads(self.last_logging_data)
        return {}

    def d(self, executor: User = None):
        fields = ['name', 'listen']
        if executor and executor.is_admin:
            fields.extend(['last_logging_time', 'last_logging_data'])
        return self.dictify(*fields)

    @classmethod
    def create(cls, host, name):
        if cls.host_name_exists(host, name):
            return cls.get_by_host_name(host, name)

        return cls.objects.create(
            host=host,
            name=name,
            listen=False,
        )

    def update_listen(self, listen):
        self.listen = listen
        self.save()
        return self

    @classmethod
    def get_by_host_name(cls, host, name):
        try:
            return cls.objects.get(host=host, name=name)
        except cls.DoesNotExist as err:
            raise HostError.DISK_NOT_FOUND(debug_message=err)

    @classmethod
    def host_name_exists(cls, host, name):
        return cls.objects.filter(host=host, name=name).exists()

    def logging(self, logging_data):
        self.last_logging_time = datetime.datetime.now()
        self.last_logging_data = json.dumps(logging_data, ensure_ascii=False)
        self.save()
        return self


class DiskUser(models.Model):
    class Meta:
        unique_together = ('disk', 'user')

    disk = models.ForeignKey(
        HostDisk,
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    bind = models.BooleanField(
        default=True,
    )

    alert_percentage = models.IntegerField(
        default=10,
    )

    @classmethod
    def get_by_disk_user(cls, disk, user):
        try:
            return cls.objects.get(disk=disk, user=user)
        except cls.DoesNotExist:
            return cls.objects.create(
                disk=disk,
                user=user,
                bind=True,
            )

    def d(self):
        return self.dictify('bind', 'alert_percentage')

    def update_bind(self, bind):
        self.bind = bind
        self.save()
        return self

    def update_percentage(self, percentage):
        self.alert_percentage = percentage
        self.save()
        return self


class HostP:
    name, token, internal_ip, alert_percentage, silent = Host.P('name', 'token', 'internal_ip', 'alert_percentage', 'silent')
    disk_name, disk_listen = HostDisk.P('name', 'listen')
    user_bind, user_alert_percentage = DiskUser.P('bind', 'alert_percentage')

    name_getter = name.clone().rename('name', yield_name='host').process(Host.get_host_by_name)
    disk_name = disk_name.rename('disk_name')
