# প্রয়োজনীয় লাইব্রেরি ইম্পোর্ট করুন
import logging
import requests
import os # এই লাইনটি 'os' মডিউল ইম্পোর্ট করার জন্য

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# লগিং সেটআপ করুন যাতে আপনি বটের কার্যকলাপ দেখতে পারেন
# এটি বটের কার্যকলাপ এবং সম্ভাব্য সমস্যাগুলো ট্র্যাক করতে সাহায্য করে।
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# আপনার টেলিগ্রাম বট টোকেন এনভায়রনমেন্ট ভেরিয়েবল থেকে নিন।
# Render.com-এ যখন ডিপ্লয় করবেন, তখন এই 'joy banhla'নামে এনভায়রনমেন্ট ভেরিয়েবল সেট করবেন।
# লোকালি পরীক্ষা করার সময়, আপনি আপনার সিস্টেমের এনভায়রনমেন্ট ভেরিয়েবল হিসেবে এটি সেট করতে পারেন।
TELEGRAM_BOT_TOKEN = os.environ.get("7940124369:AAHsl3z8awdJ7L651zSBUNbLeNO80eTTKdg")
if not TELEGRAM_BOT_TOKEN:
    # যদি টোকেন না পাওয়া যায়, তাহলে এরর লগ করুন এবং প্রোগ্রাম বন্ধ করুন।
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set. Exiting.")
    exit(1)
# আপনার ফ্রি ফায়ার প্লেয়ার ইনফো API এর বেস URL
# এই URL টি প্লেয়ারের তথ্য আনতে ব্যবহার করা হবে।
PLAYER_INFO_API_BASE_URL = "https://aditya-info-v11op.onrender.com/player-info"

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    ইউজার যখন /start কমান্ড দেয় তখন এই ফাংশনটি কাজ করে।
    ইউজারকে স্বাগতম বার্তা এবং বট ব্যবহারের নির্দেশনা দেয়।
    """
    user = update.effective_user
    # HTML ফরম্যাটে উত্তর পাঠানো হয় যাতে ইউজারনেম লিঙ্ক আকারে দেখানো যায়।
    await update.message.reply_html(
        f"হাই {user.mention_html()}! 👋\n"
        "ফ্রি ফায়ার প্লেয়ারের তথ্য জানতে, `/player_info <UID> <region>` ফর্ম্যাটে কমান্ড দিন।\n"
        "উদাহরণ: `/player_info 6681145827 bd`"
    )
    # লগ করুন কে /start কমান্ড ব্যবহার করেছে।
    logger.info(f"Start command received from {user.id}")

# /player_info কমান্ড হ্যান্ডলার
async def player_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    ইউজার যখন /player_info কমান্ড দেয় তখন এই ফাংশনটি কাজ করে।
    ইউজারের দেওয়া UID এবং region ব্যবহার করে API থেকে প্লেয়ারের তথ্য নিয়ে আসে এবং ইউজারকে দেখায়।
    """
    args = context.args # কমান্ডের পর ইউজার যা ইনপুট দিয়েছে তা গ্রহণ করুন।
    # কমান্ডের সাথে UID এবং region দেওয়া হয়েছে কিনা তা পরীক্ষা করুন।
    if not args or len(args) != 2:
        await update.message.reply_text(
            "অনুগ্রহ করে সঠিক ফর্ম্যাটে UID এবং region দিন।\n"
            "উদাহরণ: `/player_info 6681145827 bd`"
        )
        # ভুল ইনপুটের জন্য একটি সতর্কবার্তা লগ করুন।
        logger.warning(f"Invalid player_info command from {update.effective_user.id}: {update.message.text}")
        return # ফাংশনটি এখানে শেষ করুন।

    uid = args[0] # প্রথম আর্গুমেন্ট UID হিসেবে নিন।
    region = args[1].lower() # দ্বিতীয় আর্গুমেন্ট region হিসেবে নিন এবং ছোট হাতের অক্ষরে পরিবর্তন করুন।

    # API রিকোয়েস্টের জন্য সম্পূর্ণ URL তৈরি করুন।
    api_url = f"{PLAYER_INFO_API_BASE_URL}?uid={uid}&region={region}"
    # কোন API URL ব্যবহার করা হচ্ছে তা লগ করুন।
    logger.info(f"Fetching player info for UID: {uid}, Region: {region} from API: {api_url}")

    try:
        # API তে HTTP GET রিকোয়েস্ট পাঠান।
        response = requests.get(api_url)
        # যদি HTTP এরর (যেমন 404 Not Found, 500 Internal Server Error) হয়, তাহলে একটি এক্সেপশন তৈরি করুন।
        response.raise_for_status()

        # API থেকে প্রাপ্ত JSON ডেটা পার্স করুন।
        data = response.json()

        # API রেসপন্স পরীক্ষা করুন: 'status' 'success' এবং 'data' কীগুলো আছে কিনা।
        if data.get("status") == "success" and data.get("data"):
            player_data = data["data"]
            # প্লেয়ারের তথ্য সুন্দরভাবে ফরম্যাট করে একটি বার্তা তৈরি করুন।
            # এখানে MarkdownV2 ফরম্যাটিং ব্যবহার করা হয়েছে।
            message = (
                f"✨ প্লেয়ারের তথ্য ✨\n"
                f"-----------------------------------\n"
                f"🆔 **UID:** `{player_data.get('uid', 'N/A')}`\n"
                f"👤 **প্লেয়ারের নাম:** `{player_data.get('player_name', 'N/A')}`\n"
                f"🌟 **লেভেল:** `{player_data.get('level', 'N/A')}`\n"
                f"🏆 **র‍্যাঙ্ক:** `{player_data.get('rank', 'N/A')}`\n"
                f"🛡️ **গিল্ডের নাম:** `{player_data.get('guild_name', 'N/A')}`\n"
                f"🌍 **অঞ্চল:** `{player_data.get('region', 'N/A').upper()}`\n" # অঞ্চলকে বড় হাতের অক্ষরে দেখান।
                f"-----------------------------------"
            )
            # MarkdownV2 ফরম্যাটে ইউজারকে উত্তর পাঠান।
            await update.message.reply_markdown_v2(message)
            logger.info(f"Successfully sent player info for UID {uid} to {update.effective_user.id}")
        else:
            # যদি API এরর বার্তা দেয় বা তথ্য না পাওয়া যায়।
            error_message = data.get("message", "প্লেয়ারের তথ্য পাওয়া যায়নি। UID বা অঞ্চল ভুল হতে পারে।")
            await update.message.reply_text(f"দুঃখিত, তথ্য আনতে পারিনি: {error_message}")
            logger.warning(f"API returned an error for UID {uid}: {error_message}")

    except requests.exceptions.RequestException as e:
        # নেটওয়ার্ক বা API এর সাথে সংযোগের সমস্যার জন্য এরর হ্যান্ডলিং।
        await update.message.reply_text(
            "API এর সাথে সংযোগ করতে সমস্যা হচ্ছে। পরে আবার চেষ্টা করুন।"
        )
        logger.error(f"Request to API failed for UID {uid}: {e}")
    except ValueError as e:
        # JSON পার্সিং এরর হলে হ্যান্ডলিং (যদি API থেকে অ-JSON রেসপন্স আসে)।
        await update.message.reply_text(
            "API থেকে পাওয়া ডেটা প্রক্রিয়া করতে সমস্যা হয়েছে।"
        )
        logger.error(f"JSON parsing error for UID {uid}: {e}")
    except Exception as e:
        # অন্যান্য অপ্রত্যাশিত এরর হ্যান্ডলিং।
        await update.message.reply_text(
            "একটি অপ্রত্যাশিত এরর হয়েছে। অনুগ্রহ করে ডেভেলপারের সাথে যোগাযোগ করুন।"
        )
        logger.error(f"An unexpected error occurred for UID {uid}: {e}", exc_info=True)


def main() -> None:
    """
    বট শুরু করার মূল ফাংশন।
    এটি বট অ্যাপ্লিকেশন তৈরি করে, কমান্ড হ্যান্ডলার যোগ করে এবং পোলিং শুরু করে।
    """
    # Application ক্লাস ব্যবহার করে বট ইনস্ট্যান্স তৈরি করুন।
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # কমান্ড হ্যান্ডলার যোগ করুন।
    # '/start' কমান্ড এলে 'start' ফাংশনটি কল হবে।
    application.add_handler(CommandHandler("start", start))
    # '/player_info' কমান্ড এলে 'player_info' ফাংশনটি কল হবে।
    application.add_handler(CommandHandler("player_info", player_info))

    # পোলিং শুরু করুন (বট নতুন আপডেটের জন্য টেলিগ্রাম সার্ভার চেক করবে)।
    logger.info("Bot is starting polling...")
    # 'allowed_updates=Update.ALL_TYPES' মানে বট সব ধরনের আপডেট (মেসেজ, কলব্যাক, ইত্যাদি) গ্রহণ করবে।
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot has stopped polling.")


if __name__ == "__main__":
    # যখন স্ক্রিপ্টটি সরাসরি রান করা হবে, তখন main() ফাংশনটি কল হবে।
    main()
