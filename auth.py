import luogu
import datetime


def check_paste(uid, paste):
    try:
        paste = luogu.Paste(paste)
    except luogu.exceptions.NotFoundHttpException:
        return False, "剪贴板未找到"
    except luogu.exceptions.AccessDeniedHttpException:
        return False, "剪贴板未公开"
    user = paste.user
    if isinstance(uid, str) and not uid.isdigit():
        return False, "Uid 应为数字"
    uid = int(uid)
    if user.uid != uid:
        return False, "剪贴板非本人创建"
    if paste.data != f'poem snake auth: {user.uid}':
        return False, "剪贴板内容错误"
    cur = datetime.datetime.now()
    if cur - paste.time > datetime.timedelta(minutes=5):
        return False, "剪贴板过期"
    return True, None
