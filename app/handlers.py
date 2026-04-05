from aiogram.filters import CommandStart
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
import app.keyboards as kb
from redis.asyncio import Redis
from tables.crud import (user_state, save_user_state, get_contestants,
                          add_vote, has_voted, del_vote, get_cont_name)


router = Router()
r = Redis(host="localhost", port=6379, decode_responses=True)

@router.message(CommandStart())
async def cmd_start(message: Message):
    
    user_id = message.from_user.id
    throttle_key = f"limit:{user_id}"
    if await r.get(throttle_key):
        await message.answer("⏳ Слишком часто, подождите секунду")
        return
    await r.set(throttle_key, "1", ex=1)
    
    await message.answer(
        f"👋 Здравствуйте, <b>{message.from_user.first_name}</b>\n"
        "Добро пожаловать в бота для выбора <b>лучшего</b> кандидата",
        reply_markup=kb.start,
        parse_mode="HTML")
        

@router.message(Command("vote"))
async def cmd_vote(message: Message):
    
    user_id = message.from_user.id
    throttle_key = f"limit:{user_id}"
    if await r.get(throttle_key):
        await message.answer("⏳ Слишком часто, подождите секунду")
        return
    await r.set(throttle_key, "1", ex=1)
    
    contestants = await get_contestants()
    if not await has_voted(user_id):
        if not contestants:

            await message.answer(
            "❌ Список участниц пуст! Обратитесь к администратору"    
            )

        c = contestants[0]
        
        await message.answer_photo(
            photo=c["photo"],
            caption=f"<b>{c['name']}</b>\n{c['description']}",
            reply_markup=kb.voting,
            parse_mode="HTML")
    else:
        
        await message.answer("Вы уже голосовали!",
                             reply_markup=kb.cancel_vote)
        

@router.message(Command("del_vote"))
async def cmd_delvote(message: Message):
    
    user_id = message.from_user.id
    throttle_key = f"limit:{user_id}"
    if await r.get(throttle_key):
        await message.answer("⏳ Слишком часто, подождите секунду")
        return
    await r.set(throttle_key, "1", ex=1)
    
    if await has_voted(user_id):

        contestant = await get_cont_name(user_id)
        await message.answer(
            f"😦 Вы уверены, что хотите отменить голос за участника <b>{contestant}</b>?",
            reply_markup=kb.sure,
            parse_mode="HTML")
    else:

        await message.answer("🫸 Вы еще не голосовали!",
                                      reply_markup=kb.start)
        

@router.callback_query(F.data == "start voting")
async def start_voting(callback: CallbackQuery):  

    await callback.answer()

    user_id = callback.from_user.id
    if not await has_voted(user_id):

        contestants = await get_contestants()
        if not contestants:

            await callback.message.delete()
            await callback.message.answer(
            "❌ Список участниц пуст! Обратитесь к администратору")    
            return

        await save_user_state(user_id, 0)
        c = contestants[0]
        
        await callback.message.edit_media(
            media=InputMediaPhoto(
            media=c["photo"],
            caption=f"<b>{c['name']}</b>\n{c['description']}",
            parse_mode="HTML"),
            reply_markup=kb.voting,
            )
        
    else:
        await callback.message.edit_text(
            "❌ Вы уже голосовали!\n",
            reply_markup=kb.cancel_vote
        )
    


@router.callback_query(F.data == "next")
async def next(callback: CallbackQuery):
    
    user_id = callback.from_user.id
    throttle_key = f"limit:{user_id}"
    if await r.get(throttle_key):
        return await callback.answer("⌛ Подождите 1 сек...", show_alert=True)
    await r.set(throttle_key, "1", ex=1)
    
    
    try:

        user_id = callback.from_user.id
        index = await user_state(user_id)
        new_index = index + 1
        contestants = await get_contestants()

        if new_index < len(contestants):
            
            await save_user_state(user_id, new_index)
            c = contestants[new_index]
            await callback.answer()

            await callback.message.edit_media(
                media=InputMediaPhoto(
                media=c["photo"],
                caption=f"<b>{c['name']}</b>\n{c['description']}",
                parse_mode="HTML"),
                reply_markup=kb.voting
                )
            return

        else:

            await callback.answer(
                "📋 Это был последний кандидат. Сделайте свой выбор!",
                show_alert=True
            )

    except Exception as e:
        print(f"Ошибка в next: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
    


@router.callback_query(F.data == "prev")
async def prev(callback: CallbackQuery):

    user_id = callback.from_user.id
    throttle_key = f"limit:{user_id}"
    if await r.get(throttle_key):
        return await callback.answer("⌛ Подождите 1 cек...", show_alert=True)
    await r.set(throttle_key, "1", ex=1)
    
    await callback.answer()

    user_id = callback.from_user.id
    index = await user_state(user_id)
    new_index = index - 1
    contestants = await get_contestants()

    if new_index >= 0:

        await save_user_state(user_id, new_index)
        c = contestants[new_index]
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=c["photo"],
                caption=f"<b>{c['name']}</b>\n{c['description']}",
                parse_mode="HTML"),
            reply_markup=kb.voting
            )
        return
        

    else:
        
        await save_user_state(user_id, 0)
        await callback.message.delete()
        await callback.message.answer(
            f"Здавствуйте, <b>{callback.from_user.first_name}</b>!\n"
            "Добро пожаловать в бота для выбора <b>лучшего</b> кандидата",
            reply_markup=kb.start,
            parse_mode="HTML"
        )


@router.callback_query(F.data == "home")
async def home(callback: CallbackQuery):  

    await callback.answer()  
    await callback.message.edit_text(
        "👋 Вы вернулись в главное меню",
        reply_markup=kb.start)


@router.callback_query(F.data == "vote")
async def vote(callback: CallbackQuery):
    
    await callback.answer()
    user_id = callback.from_user.id

    if not await has_voted(user_id):

        index = await user_state(user_id)
        contestants = await get_contestants()
        
        if not contestants or index>= len(contestants):
            await callback.message.answer(
            "⚠️ Список участников обновился. Пожалуйста, вернитесь в меню /start",
            show_alert=True
            )
            return
                
        contestant = contestants[index]
        contestant_id = contestant["id"]
        contestant_name = contestant["name"]

        if await add_vote(user_id, contestant_id):
            
            votes = contestant["votes"] + 1

            await callback.message.delete()
            await callback.message.answer(
                f"✅ Вы проголосовали за участника {contestant_name}\n"
                f"🔢 Его количество голосов: {votes}",
                reply_markup=kb.after_vote
            )
            return
        
        else: 
            await callback.message.answer(
            "❌ Произошла ошибка при сохранении голоса!"\
            "Попробуйте еще раз",
            show_alert=True)
    
    else:

        await callback.message.answer("Вы уже голосовали!",
                                      reply_markup=kb.cancel_vote)


@router.callback_query(F.data == "cancel_vote")
async def cancel_vote(callback: CallbackQuery):
    
    await callback.answer()
    user_id = callback.from_user.id
    if await has_voted(user_id):
        
        cont_name = await get_cont_name(user_id)
        await callback.message.edit_text(
            f"😦 Вы уверены, что хотите отменить голос за участника <b>{cont_name}</b>",
            reply_markup=kb.sure,
            parse_mode="HTML")
        return
    else:

        await callback.message.edit_text(
            text="🫸 Вы еще не голосовали!",
            reply_markup=kb.start)
        
        

@router.callback_query(F.data == "del")
async def delete(callback: CallbackQuery): 
 
    await callback.answer()
    user_id = callback.from_user.id
    if await del_vote(user_id):

        await callback.message.edit_text(
            text="🗑️ Ваш голос успешно отменен!\n"
            "Вы можете проголосовать заново",
            reply_markup=kb.new_vote)
        return
        
    else:

        await callback.message.edit_text(
            text="😩 Вы еще не голосовали!",
            reply_markup=kb.start)
        


@router.callback_query(F.data == "finish")
async def finish(callback: CallbackQuery):

    await callback.answer()
    user_id = callback.from_user.id
    contestant = await get_cont_name(user_id)
    await callback.message.edit_text(
        f"👌 Ваш голос за участника <b>{contestant}</b> учтен\n"
            "Дождитесь окончания конкурса!",
            parse_mode="HTML")





@router.message(F.photo)
async def get_photo(message: Message):
    photo_id = message.photo[-1].file_id
    await message.answer(photo_id)