from oba import Obj

from Host.models import HostDisk, DiskUser
from LabDiskAlert.global_settings import Global
from User.models import User
from utils.alert import alert


class DiskLog:
    def __init__(self, disk: HostDisk, percentage: int, folders):
        self.disk = disk
        self.percentage = percentage
        self.folders = Obj.raw(folders)
        self.folders = {item['path']: item['percentage'] for item in folders}

        self.logging_data = dict(
            percentage=percentage,
            folders=self.folders,
        )

        # disk level filter
        if not disk.listen:
            return

        self.disk.logging(self.logging_data)

        self.detect_user()
        user_list = self.get_alert_user_list() or []
        self.attempt_alert(user_list)

    def detect_user(self):
        for user_name in self.folders:
            if not User.name_exists(user_name):
                continue
            user = User.get_user_by_name(user_name)
            DiskUser.get_by_disk_user(self.disk, user)

    def get_alert_user_list(self):
        # host level filter
        if self.disk.host.silent:
            return
        if self.disk.host.alert_percentage > self.percentage:
            return

        # diskuser level filter
        user_list = []
        for user_name in self.folders:
            if not User.name_exists(user_name):
                continue
            user = User.get_user_by_name(user_name)
            diskuser = DiskUser.get_by_disk_user(self.disk, user)
            if diskuser.bind and diskuser.alert_percentage <= self.folders[diskuser.user.name]:
                user_list.append(diskuser)

        return user_list

    def attempt_alert(self, user_list):
        success_count = 0
        success_admin = []
        title = f'{self.disk.host.name}:{self.disk.name}磁盘空间预警'
        for diskuser in user_list:
            message = f'{diskuser.disk.host.name}({diskuser.disk.host.internal_ip})机器下的{diskuser.disk.name}磁盘' \
                      f'使用量已达{self.percentage}%，其中您的空间占有{self.folders[diskuser.user.name]}%。请及时清理！'
            alert_flag, fail_log = alert(diskuser, message, title=title)
            if alert_flag:
                success_count += 1
                if diskuser.user.is_admin:
                    success_admin.append(diskuser.user.name)

        for admin in User.get_admins():
            if admin.name in success_admin:
                continue
            message = f'{self.disk.host.name}({self.disk.host.internal_ip})机器下的{self.disk.name}磁盘' \
                      f'使用量已达{self.percentage}%。'
            if not success_count:
                message += '没有成功的报警已发送。请及时提醒。'
            email_message = message + '详细的用户占用情况如下：\n\n'
            for user_name in self.folders:
                email_message += f'{user_name}：{self.folders[user_name]}%\n'

            admin_success_flag = False
            if admin.email_activated:
                try:
                    Global.notificator.mail(admin.email, email_message, subject=title, appellation=admin.name)
                    admin_success_flag = True
                except Exception as e:
                    pass

            if admin.bark_activated:
                try:
                    Global.notificator.bark(admin.bark, message, title=title)
                    admin_success_flag = True
                except Exception as e:
                    pass

            if not admin_success_flag:
                try:
                    Global.notificator.sms(admin.phone, message)
                except Exception as e:
                    pass

