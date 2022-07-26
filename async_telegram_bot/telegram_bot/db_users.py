from telegram_bot.models import User, Vehicle


async def check_user(user_id):
    """Big function check, create, make admin, create wallet"""
    tg_id = user_id['id']
    user = await User.get_user_by_tg_id(tg_id)
    if user:
        return f"Вітаємо, {user.username}!", True
    else:
        return "ERROR: USER NOT FOUND", False


# For User model
async def create_user(data):
    result = await User.create_record(data)
    return result


async def find_user_by_tg_id(tg_id):
    user = await User.find_user_by_tg_id(tg_id)
    return user


async def find_vehicle_by_vin(data):
    vehicles = await Vehicle.find_vehicle_by_vin(data)
    return vehicles
