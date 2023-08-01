import datetime


async def get_user_active_subs(sub_lst, bi) -> list:
    today = datetime.datetime.now(datetime.timezone.utc)
    res_lst = []
    for i in sub_lst:
        if i['created_at'] + datetime.timedelta(days=i['subscription_name']['day']) <= today:
            await bi.remove_pay_subscription(i['id'])
        else:
            res_lst.append(i)
    return res_lst
