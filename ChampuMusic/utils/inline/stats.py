from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def stats_buttons(_, status):
    not_sudo = [
        InlineKeyboardButton(
            text=f"📊 Top Overall",
            callback_data="TopOverall",
        )
    ]
    sudo = [
        InlineKeyboardButton(
            text=f"🎛 System Stats",
            callback_data="bot_stats_sudo",
        ),
        InlineKeyboardButton(
            text=f"📊 Top Overall",
            callback_data="TopOverall",
        ),
    ]
    upl = InlineKeyboardMarkup(
        [
            sudo if status else not_sudo,
            [
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ],
        ]
    )
    return upl


def back_stats_buttons(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="stats_back",
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ],
        ]
    )
    return upl
