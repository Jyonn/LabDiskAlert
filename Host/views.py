from SmartDjango import Analyse, PDict, P
from django import views
from oba import Obj
from smartify import PList

from Host.models import Host, HostP, HostDisk, DiskUser
from utils.auth import Auth
from utils.disk_log import DiskLog


class HostView(views.View):
    @staticmethod
    @Auth.require_user()
    def get(r):
        """
        获取主机列表
        GET /api/host
        """
        return Host.get_all(executor=r.user)


class HostNameView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(a=[HostP.name_getter])
    def get(r):
        """
        获取主机信息
        GET /api/host/:name
        """
        return r.d.host.d(executor=r.user)

    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(a=[HostP.name], b=[HostP.internal_ip])
    def post(r):
        """
        创建主机
        POST /api/host/:name
        """
        return Host.create(**Obj.raw(r.d)).d(executor=r.user)

    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(a=[HostP.name_getter], b=[HostP.silent])
    def put(r):
        """
        修改主机静默信息
        PUT /api/host/:name
        """
        return r.d.host.update_silent(r.d.silent).d(executor=r.user)

    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(a=[HostP.name_getter])
    def delete(r):
        """
        删除主机
        DELETE /api/host/:name
        """
        r.d.host.delete()


class HostDiskView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(a=[HostP.name_getter])
    def get(r):
        """
        获取主机磁盘信息
        GET /api/host/:name/disk
        """
        return r.d.host.get_disks(executor=r.user)


class HostDiskNameView(views.View):
    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(a=[HostP.name_getter, HostP.disk_name], b=[HostP.disk_listen])
    def put(r):
        """
        修改磁盘监听信息
        PUT /api/host/:name/disk/:disk_name
        """
        disk = HostDisk.get_by_host_name(host=r.d.host, name=r.d.disk_name)
        return disk.update_listen(r.d.listen).d(executor=r.user)

    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(a=[HostP.name_getter, HostP.disk_name])
    def delete(r):
        """
        删除磁盘
        DELETE /api/host/:name/disk/:disk_name
        """
        disk = HostDisk.get_by_host_name(host=r.d.host, name=r.d.disk_name)
        disk.delete()


class HostAuthView(views.View):
    @staticmethod
    @Analyse.r(a=[HostP.name_getter], b=[HostP.token])
    def post(r):
        """
        主机认证
        POST /api/host/:name/auth
        """
        host = r.d.host.auth(r.d.token)
        return Auth.get_host_token(host)


class ReportDiskView(views.View):
    @staticmethod
    @Auth.require_host()
    def get(r):
        """
        获取主机磁盘信息
        GET /api/host/report/disk
        """
        return r.host.get_disks()

    @staticmethod
    @Auth.require_host()
    @Analyse.r(b=[PList(name='disks').set_child(HostP.disk_name)])
    def post(r):
        """
        创建磁盘
        POST /api/host/report/disk
        """
        disks = []
        for disk_name in r.d.disks:
            disks.append(HostDisk.create(host=r.host, name=disk_name))
        return list(map(lambda disk: disk.d(), disks))


class ReportDiskMemoryView(views.View):
    @staticmethod
    @Auth.require_host()
    @Analyse.r(b=[HostP.disk_name, 'disk_percentage', PDict(name='folders').set_fields('path', 'percentage')])
    def post(r):
        """
        磁盘占用预警
        POST /api/host/report/disk/memory
        """
        disk = HostDisk.get_by_host_name(host=r.host, name=r.d.disk_name)

        DiskLog(disk=disk, percentage=r.d.disk_percentage, folders=r.d.folders)


class UserDiskView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(a=[HostP.name_getter], b=[HostP.disk_name])
    def get(r):
        disk = HostDisk.get_by_host_name(host=r.d.host, name=r.d.disk_name)
        diskuser = DiskUser.get_by_disk_user(disk=disk, user=r.user)
        return diskuser.d(executor=r.user)

    @staticmethod
    @Auth.require_user()
    @Analyse.r(a=[HostP.name_getter], b=[HostP.disk_name, HostP.user_bind])
    def post(r):
        """
        修改磁盘绑定信息
        POST /api/host/:name/userdisk/bind
        """
        disk = HostDisk.get_by_host_name(host=r.d.host, name=r.d.disk_name)
        diskuser = DiskUser.get_by_disk_user(disk=disk, user=r.user)
        return diskuser.update_bind(r.d.bind).d(executor=r.user)


class UserDiskPercentageView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(a=[HostP.name_getter], b=[HostP.disk_name, HostP.user_alert_percentage])
    def post(r):
        """
        修改磁盘占用信息
        POST /api/host/:name/userdisk/percentage
        """
        disk = HostDisk.get_by_host_name(host=r.d.host, name=r.d.disk_name)
        diskuser = DiskUser.get_by_disk_user(disk=disk, user=r.user)
        return diskuser.update_percentage(r.d.alert_percentage).d(executor=r.user)

