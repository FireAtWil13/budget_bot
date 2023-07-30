# sample-bot.py

# from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, Application,  ConversationHandler
from telegram.ext import MessageHandler, InlineQueryHandler, filters, CallbackQueryHandler
from datetime import datetime
from telegram_calendar import telegramcalendar
import sheets

# from telegram.ext.filters import BaseFilter as BaseFilter

import logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class BudgetBot():
  def __init__(self, token):
    self.token = token
    self.app = Application.builder().token(self.token).build()

    self.sheets = sheets.sheets_api()

    # пишем информацию по юзер ид
    self.entry_data = {}
    
    # список допустимых юзеров
    self.allowed_users = {114173561: "Паша", 5981533702:"Рабочий", 366756790:"Лена"}

    # self.amount = 0
    # self.income = True
    # self.entry_data[user_id]["fix_param"] = ""
    self.amnt_mess_id = {}
    self.comment_mess_id = {}
    # проверить возможность динамического обновления категорий
    self.categories = self.get_in_categories()
    self.categories.extend(self.get_out_categories())
    # print(self.categories)
    self.add_stages = ["Приход/расход", "Сумма", "Категория", "Дата", "Комментарий"]
    
    self.ADD_OR_GET, self.ADD, self.GET, self.IN, self.OUT, self.START_OVER, self.AMOUNT, self.CATEGORY, self.DATE, self.COMMENT, self.CHECK, self.UPDATE, self.FIX  = range(13)

    self.conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", self.start)],
        states={
            self.ADD_OR_GET: [CallbackQueryHandler(self.add, pattern="^Add$"),
                              CallbackQueryHandler(self.get, pattern="^Get$"),
                              CallbackQueryHandler(self.start_over, pattern="^Start_over$"),
                             ],
            self.ADD: [
             CallbackQueryHandler(self.cash_in, pattern="^In$"),
             CallbackQueryHandler(self.cash_out, pattern="^Out$"),
             # CallbackQueryHandler(self.start, pattern="^Start$"),
            
                      ],
            self.AMOUNT: [
              MessageHandler(filters.TEXT & (~filters.COMMAND), self.get_amount),
            ],
             self.CATEGORY: [
               # добавить проверку что значение в списке категнорий
             CallbackQueryHandler(self.category, pattern="^" + "|".join(self.categories) + "$")             
             ],
            self.DATE: [
              CallbackQueryHandler(self.get_today_date, pattern="^Today$"),
              CallbackQueryHandler(self.get_calendar, pattern="^OtherDate$"),
              CallbackQueryHandler(self.get_other_date)
            
            ],
          
            self.START_OVER: [
              
            ],
            self.COMMENT: [
              MessageHandler(filters.TEXT & (~filters.COMMAND), self.get_comment),
            ],
            self.CHECK: [
              CallbackQueryHandler(self.check_passed, pattern="^Ok$"),
              CallbackQueryHandler(self.check_not_passed, pattern="^Fix$")
            ],
            self.FIX: [
              CallbackQueryHandler(self.in_out_fix, pattern="^Приход/расход$"),
              CallbackQueryHandler(self.amnt_fix, pattern="^Сумма$"),
              CallbackQueryHandler(self.cat_fix, pattern="^Категория$"),
              CallbackQueryHandler(self.date_fix, pattern="^Дата$"),
              CallbackQueryHandler(self.com_fix, pattern="^Комментарий$")
              
            ]
        },
        fallbacks=[CommandHandler("start", self.start)],
    )
    # print(self.conv_handler)

    self.app.add_handler(self.conv_handler)


    # запуск прослушивания сообщений
    self.app.run_polling()
  
  # функция обработки команды '/start'
 
  async def start(self, update, context) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    user_id = user.id
    
    # self.entry_data[user_id]["fix_param"] = ""
    # Get user that sent /start and log his name
    
    print(update.message.from_user.id)

    if len(self.allowed_users) > 0 and user_id in self.allowed_users.keys():

      self.entry_data[user_id] = {}
      self.entry_data[user_id]["fix_param"] = ""
      logger.info("User %s started the conversation.", user.first_name)
      # Build InlineKeyboard where each button has a displayed text
      # and a string as callback_data
      keyboard = [
          [
              InlineKeyboardButton("Добавить запись", callback_data='Add'),
              InlineKeyboardButton("Проверить", callback_data='Get'),
          ],
          [
              InlineKeyboardButton("Таблица", url= """https://docs.google.com/spreadsheets""")
          ]
      ]
      reply_markup = InlineKeyboardMarkup(keyboard)
      # Send message with text and appended InlineKeyboard
      await update.message.reply_text("Привет! Я здесь чтобы помочь с бюджетом!\nЧто хотите сдлеать?", reply_markup=reply_markup)
      print(self.entry_data)
      # Tell ConversationHandler that we're in state `FIRST` now
      return self.ADD_OR_GET
      
    else:
      logger.info(f"User {user.first_name}, ID {user_id} do not have access to bot.")
      await update.message.reply_text(f"Привет {user.first_name}! У тебя нет доступа к этому боту.\n Запроси доступ для ID {user_id}\n Спасибо!")
      self.conv_handler.END

  async def start_over(self, update, context) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # self.entry_data[user_id]["fix_param"] = ""
    query = update.callback_query
    if query is None:
      user_id = update.message.from_user.id
    else:
      user_id = query.from_user.id
      
    self.entry_data[user_id]["fix_param"] = ""
    # query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton("Добавить запись", callback_data='Add'),
            InlineKeyboardButton("Проверить", callback_data='Get'),
        ],
        [
            InlineKeyboardButton("Таблица", url= """https://docs.google.com/spreadsheets""")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await query.edit_message_text("Привет! Я здесь чтобы помочь с бюджетом!\nЧто хотите сдлеать?", reply_markup=reply_markup)
    return self.ADD_OR_GET

  async def add(self, update, contex) -> int:
    # выбираем что хотим боавить доход/расход и переходим на ветку ADD
    """Show new choice of buttons"""
    # print(update)
    query = update.callback_query
    user_id = query.from_user.id
    # await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Доход", callback_data="In"),
            InlineKeyboardButton("Расход", callback_data="Out"),
        ],
        # [
        #     InlineKeyboardButton("В начало", callback_data="Start"),
        # ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Что нужно добавить?", reply_markup=reply_markup
    )
    # if self.entry_data[user_id]["fix_param"] != "Приход/расход":
    return self.ADD

  async def get(self, update, contex) -> int: 
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(self.ONE)),
            InlineKeyboardButton("3", callback_data=str(self.THREE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Second CallbackQueryHandler, Choose a route", reply_markup=reply_markup
    )
    return self.START_ROUTES

  async def cash_in(self, update, contex) -> int:
    """добавляем доход, ставим флаг на тип операции, запрашиваем сумму и идем дальше"""
    query = update.callback_query
    user_id = query.from_user.id
    # self.income = True
    self.entry_data[user_id]["income"] = True
    
    # await query.answer()
    await query.edit_message_text(text="Введи сумму:",)
    # записываем ид сообщения по юзер ИДу чтобы потом его удалить
    self.amnt_mess_id[user_id] = update.callback_query.message.message_id
    return self.AMOUNT

  async def cash_out(self, update, contex) -> int:
    """добавляем расход, ставим флаг на тип операции, запрашиваем сумму и идем дальше"""
    query = update.callback_query
    user_id = query.from_user.id
    self.entry_data[user_id]["income"] = False
    # query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Введи сумму:",)
    # записываем ид сообщения по юзер ИДу чтобы потом его удалить
    self.amnt_mess_id[user_id] = update.callback_query.message.message_id

    return self.AMOUNT

  async def get_amount(self, update, contex) -> int:
    """
    удаляем сообщения о запросе суммы и самой суммы, получаем сумму после cash_in/out
    получаем список категорий, в зависмости от типа операции, запрашиваем  тип операции
    в зависимости от того исправление Суммы это или начальное заполнение идем или на CHECK или на CATEGORY
    """
    # query = update.callback_query
    # user_id = query.from_user.id
    user_id = update.message.from_user.id
    query = update.callback_query
    # print(self.amnt_mess_id)
    # await query.message()
    # try:
    await self.app.bot.delete_message(update.message.chat.id, self.amnt_mess_id[user_id])
    await self.app.bot.delete_message(update.message.chat.id, update.message.message_id)
    

    user = update.message.from_user
    self.amount = update.message.text
    self.entry_data[user_id]["amount"] = update.message.text
    # print(self.entry_data)

    if self.entry_data[user_id]["fix_param"] != "Сумма":
    # Пишем в журнал биографию или рассказ пользователя
      logger.info("Пользователь %s ввел сумму: %s", user.first_name, self.amount)
      if self.entry_data[user_id]["income"]:
        self.categories = self.get_in_categories()
        keyboard = list(self.chunks(self.categories, 2))
        reply_markup = InlineKeyboardMarkup(keyboard)
      else:
        self.categories = self.get_out_categories()
        keyboard = list(self.chunks(self.categories, 2))
        reply_markup = InlineKeyboardMarkup(keyboard)
      # Send message with text and appended InlineKeyboard
      await update.message.reply_text("Выбери категорию:", reply_markup=reply_markup)
      return self.CATEGORY
    else:
      self.entry_data[user_id]["fix_param"] = ""
      await self.get_check(update, contex)
      return self.CHECK

  async def category(self, update, contex) -> int:
    """
    получаем категорию, запрашиваем сегдняшняя дата или другая
    если исправлялась категория - возвращаемя в CHEK, если нет идем дале в DATE
    """
    query = update.callback_query
    user_id = query.from_user.id
    categ = query.data
    self.entry_data[user_id]["category"] = categ
    
    if self.entry_data[user_id]["fix_param"] != "Категория":
      logger.info("Пользователь  выбрал категорию: %s",  self.entry_data[user_id]["category"])
  
      keyboard = [
          [
              InlineKeyboardButton("Сегодня", callback_data="Today"),
              InlineKeyboardButton("Другая дата", callback_data="OtherDate"),
          ],
        # [
        #       InlineKeyboardButton("В начало", callback_data="Start"),
        #   ]
      ]
      reply_markup = InlineKeyboardMarkup(keyboard)
      await query.edit_message_text(
          text="За какое число?", reply_markup=reply_markup
      )
      return self.DATE
    else:
      self.entry_data[user_id]["fix_param"]  = ""
      await self.get_check(update, contex)
      return self.CHECK

  async def get_today_date(self, update, contex) -> int:
    """
    если нужна сегодняшняя дата, то получаем дату,
    если это было исправление даты, то переходим обратно на CHECK
    если нет, то запрашиваем комментарий и идем дальше на получение
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    # query = update.callback_query
    self.entry_data[user_id]["trans_date"]  = datetime.today().strftime('%d.%m.%Y')
    # print(self.entry_data[user_id]["trans_date"] )
    if self.entry_data[user_id]["fix_param"]  != "Дата":
      await query.edit_message_text(text="Добавь комментарий:")
      self.comment_mess_id[user_id] = update.callback_query.message.message_id
      return self.COMMENT
    else:
      self.entry_data[user_id]["fix_param"] = ""
      await self.get_check(update, contex)
      return self.CHECK

  async def get_calendar(self, update, contex) -> int:
    """
    если дата другая, то вызываем календарь из telegramcalendar и идем дальше
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    # query = update.callback_query
    await query.edit_message_text(text="Выбери дату: ",  reply_markup=telegramcalendar.create_calendar())
    return self.DATE

  async def get_other_date(self, update, contex) -> int:
    """
    получаем дату из календаря
    если это было исправление даты, то переходим обратно на CHECK
    если нет, то запрашиваем комментарий и идем дальше на получение
    """
    query = update.callback_query
    user_id = query.from_user.id
    # print('get_other_date')
    # user_id = update.message.from_user.id
    # query = update.callback_query
    selected,date = telegramcalendar.process_calendar_selection(update, contex)
    self.entry_data[user_id]["trans_date"]  = date.strftime("%d.%m.%Y")
    if self.entry_data[user_id]["fix_param"]  != "Дата":
      await query.edit_message_text(text="Добавь комментарий:")
      self.comment_mess_id[user_id] = update.callback_query.message.message_id
      return self.COMMENT
    else:
      self.entry_data[user_id]["fix_param"] = ""
      await self.get_check(update, contex)
      return self.CHECK

  async def get_comment(self, update, contex) -> int:
    """
    удаляем запрос комментария из даты и сам комментарий из чата
    получаем текст комментария
    идем на проверку т.к последний шаг
    """
    user_id = update.message.from_user.id
    query = update.callback_query
    # await query.message()
    await self.app.bot.delete_message(update.message.chat.id, update.message.message_id-1)
    await self.app.bot.delete_message(update.message.chat.id, update.message.message_id)

    user = update.message.from_user
    # print(update)
    comment = update.message.text
    self.entry_data[user_id]["comment"] = comment
    # Пишем в журнал биографию или рассказ пользователя
    logger.info("Пользователь %s ввел коментарий: %s", user.first_name, self.entry_data[user_id]["comment"])
    await self.get_check(update, contex)
    # if self.entry_data[user_id]["fix_param"] != "Комментарий"
    return self.CHECK
    

  async def check_passed(self, update, contex) -> int:
    """
    если подтвердили что все корректно, то вывводим собраную информацию
    и спрашваем что нужно сделать еще, возвращаясь лио на новое добавление, 
    либо в начальное меню
    """
    
    query = update.callback_query
        # query = update.callback_query
    if query is None:
      user_id = update.message.from_user.id
    else:
      user_id = query.from_user.id
    # user_id = query.from_user.id
    # user_id = update.message.from_user.id
    print("Check")
    query = update.callback_query
    self.final_entry = {"Тип": self.trans_type, 
                        "Дата": self.entry_data[user_id]["trans_date"] , 
                        "Сумма":self.entry_data[user_id]["amount"],
                        "Категория":self.entry_data[user_id]["category"],
                        "Комметарий":self.entry_data[user_id]["comment"]}
    row_to_append = [
      self.entry_data[user_id]["trans_date"], 
      self.entry_data[user_id]["amount"], 
      self.entry_data[user_id]["comment"], 
      self.entry_data[user_id]["category"]]
    self.sheets.append_values(self.entry_data[user_id]["income"], row_to_append)
    # await query.edit_message_text(f"Спасибо! Данные приняты \n\t{self.final_entry} \nВ следующей версии они будут добавляться в таблицу, а пока остануться только здесь.")  
    await query.edit_message_text(f"Спасибо! Добавлены в таблицу.") 
    keyboard = [
        [
            InlineKeyboardButton("Добавить запись", callback_data='Add'),
            InlineKeyboardButton("В начало", callback_data='Start_over'),
        ],]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # await update.message.reply_text("Добавить еще одну запись?", reply_markup=reply_markup)
    await self.app.bot.send_message(chat_id=update.callback_query.from_user.id,
                        text="Добавить еще одну запись?",
                        reply_markup=reply_markup)

    return self.ADD_OR_GET

  async def check_not_passed(self, update, contex) -> int:
    """
    если нужно что-то исправить - запрашиваем что нужно исправить
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    # query = update.callback_query
    # self.trans_type = "Приход" if self.entry_data[user_id]["income"] else "Расход"
    new_income_type = "расход" if self.entry_data[user_id]["income"] else "приход"
    keyboard = [
        [
        InlineKeyboardButton(f"Изменить на {new_income_type}", callback_data="Приход/расход"),
        InlineKeyboardButton("Сумма", callback_data="Сумма"),
        ],
        [
        InlineKeyboardButton("Категория", callback_data="Категория"),
        InlineKeyboardButton("Дата", callback_data="Дата"),
        ],
        [
        InlineKeyboardButton("Комментарий", callback_data="Комментарий"),
        ],
        # [
        #  InlineKeyboardButton("В начало", callback_data="Start"),
        # ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Что необходимо исправить?", reply_markup=reply_markup
    )
    return self.FIX

  async def in_out_fix(self, update, contex) -> int:
    """
    исправление категории доход/расход
    ставим флаг исправления на категроию
    автоматически меняем тип (тк их всего два приход/расход)
    и запрашиваем новую категрию, т.к категории у прихода/расхода разные
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    
    # self.income = not self.income   
    self.entry_data[user_id]["income"] = not self.entry_data[user_id]["income"]
    self.entry_data[user_id]["fix_param"] = "Категория"
    # query = update.callback_query
    if self.entry_data[user_id]["income"]:
      self.categories = self.get_in_categories()
      keyboard = list(self.chunks(self.categories, 2))
      reply_markup = InlineKeyboardMarkup(keyboard)
    else:
      self.categories = self.get_out_categories()
      keyboard = list(self.chunks(self.categories, 2))
      reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await query.edit_message_text("При изменении типа нужно выбрать новую категорию:", reply_markup=reply_markup)
    return self.CATEGORY
    # await self.get_check(update, contex)
    # return self.CHECK
    
  async def amnt_fix(self, update, contex) -> int:
    """
    изменение суммы
    запрашиваем новую сумму и идем на шаг AMOUNT для обработки полученных данных
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    self.entry_data[user_id]["fix_param"] = "Сумма"
    # query = update.callback_query
    await query.edit_message_text(text="Новая сумма:",)
    return self.AMOUNT
    
  async def cat_fix(self, update, contex) -> int:
    """
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    self.entry_data[user_id]["fix_param"] = "Категория"
    # query = update.callback_query
    if self.entry_data[user_id]["income"]:
      self.categories = self.get_in_categories()
      keyboard = list(self.chunks(self.categories, 2))
      reply_markup = InlineKeyboardMarkup(keyboard)
    else:
      self.categories = self.get_out_categories()
      keyboard = list(self.chunks(self.categories, 2))
      reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await query.edit_message_text("Выбери новую категорию:", reply_markup=reply_markup)
    return self.CATEGORY
    
  async def date_fix(self, update, contex) -> int:
    """
    изменение даты
    запрашиваем какая дата и идем на шаг DATE для обработки полученных данных
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    self.entry_data[user_id]["fix_param"] = "Дата"
    # query = update.callback_query
    keyboard = [
          [
              InlineKeyboardButton("Сегодня", callback_data="Today"),
              InlineKeyboardButton("Другая дата", callback_data="OtherDate"),
          ],
        # [
        #       InlineKeyboardButton("В начало", callback_data="Start"),
        #   ]
      ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
          text="Какое новое число?", reply_markup=reply_markup
      )
    return self.DATE
   
  async def com_fix(self, update, contex) -> int:
    """
    изменение комментария
    запрашиваем новый коммент и идем на шаг COMMENT для обработки полученных данных
    """
    query = update.callback_query
    user_id = query.from_user.id
    # user_id = update.message.from_user.id
    # self.entry_data[user_id]["fix_param"] = "Комментарий"
    # query = update.callback_query
    await query.edit_message_text(text="Новый комментарий:")
    return COMMENT
  


  async def end(self, update, contex) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return self.conv_handler.END
    


  

  async def get_record_info_input(self, update, context):
    """
    !!!ВОЗМОЖНО ЛИШНЕЕ!!!
    """
    query = update.callback_query
    # await query.answer()
    # await query.edit_message_text(text="Введи сумму:")
    self.amount = update.message.text 
    text = 'Сумма:' + self.amount
    await context.bot.send_message(chat_id=update.effective_chat.id,                       text=text)  
    return self.ADD_OR_GET

  def get_out_categories(self):
    """Будет получать категории из таблицы, пока хардкод"""
    # categories = [
    #   "Продукты",
    #   "Личные расходы Лена",
    #   "Личные расходы Паша",
    #   "Транспорт",
    #   "Развлечения",
    #   "Ежемесячне расходы",
    #   "Другое",
    #   "Сбережения",
    #   "Категория 2",
    # ]
    return self.sheets.get_out_categories()

  def get_in_categories(self):
    """Будет получать категории из таблицы, пока хардкод"""
    # categories = [
    #   "Зарплата",
    #   "Другое",
    # ]
    return self.sheets.get_in_categories()

  async def get_check(self, update, context):
    """
    СПРАШИВАЕМ НУЖНО ЛИ ДОПОЛНИТЕЛЬНОЕ ИСПРАВЛЕНИЕ
    и выводим сообщение с тем, что уже собрали
    добавить форматирование?
    """
    query = update.callback_query
    if query is None:
      user_id = update.message.from_user.id
    else:
      user_id = query.from_user.id
      
    keyboard = [
        [
            InlineKeyboardButton("Все верно", callback_data="Ok"),
            InlineKeyboardButton("Нужно исправить", callback_data="Fix"),
        ],
      # [
      #       InlineKeyboardButton("В начало", callback_data="Start"),
      #   ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    self.trans_type = "Приход" if self.entry_data[user_id]["income"] else "Расход"
    check_text = f"""
        Теперь проверим:
        Тип:\t{self.trans_type}
        Дата:\t{self.entry_data[user_id]["trans_date"] }
        Сумма:\t{self.entry_data[user_id]["amount"]}
        Категория:\t{self.entry_data[user_id]["category"]}
        Комметарий:\t{self.entry_data[user_id]["comment"]}
        """
    if query is None:
      await update.message.reply_text(text=check_text, reply_markup=reply_markup)
    else:
      await query.edit_message_text(text=check_text, reply_markup=reply_markup)

  def chunks(self, lst, n):
    """
    принимает список строк и количество кнопок в ряду
    преобразует строки в кнопки с callback_data = строке(названию кнопки)
    форматирует список к нужному количеству кнопок в строке
    """
    # print(lst)
    # print(len(lst))
    btns = [InlineKeyboardButton(i, callback_data=(i)) for i in lst]
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(btns), n):
        yield btns[i:i + n]





  # async def calendar_handler(self, update, contex):
  #   await query.message.reply_text("Please select a date: ",
  #                       reply_markup=telegramcalendar.create_calendar())


  # def inline_handler(self, update, contex):
  #   selected,date = telegramcalendar.process_calendar_selection(update, contex)
  #   if selected:
  #       bot.send_message(chat_id=update.callback_query.from_user.id,
  #                       text="You selected %s" % (date.strftime("%d/%m/%Y")),
  #                       reply_markup=ReplyKeyboardRemove())

  # def get_categories(self):
  #   """Будет получать категории из таблицы, пока хардкод"""
  #   categories = [
  #   InlineKeyboardButton("Продукты"),
  #   InlineKeyboardButton("Личные расходы Лена"),
  #   InlineKeyboardButton("Личные расходы Паша"),
  #   InlineKeyboardButton("Транспорт"),
  #   InlineKeyboardButton("Развлечения"),
  #   InlineKeyboardButton("Ежемесячне расходы"),
  #   InlineKeyboardButton("Другое"),
  #   InlineKeyboardButton("Сбережения"),
  #   InlineKeyboardButton("Категория 2"),
  #   ]
  #   return categories

  #   [InlineKeyboardButton(str(i), callback_data=(i, current_list)) for i in range(1, 6)]

  # async def start(self, update, context):
  #     await context.bot.send_message(chat_id=update.effective_chat.id, 
  #                              text="I'm a bot, please talk to me!")
  
  # # функция обработки текстовых сообщений
  # async def echo(self, update, context):
  #     text = 'ECHO: ' + update.message.text 
  #     await context.bot.send_message(chat_id=update.effective_chat.id, 
  #                              text=text)    
  
  # # функция обработки команды '/caps'
  # async def caps(self, update, context):
  #     if context.args:
  #         text_caps = ' '.join(context.args).upper()
  #         await context.bot.send_message(chat_id=update.effective_chat.id, 
  #                                  text=text_caps)
  #     else:
  #         await context.bot.send_message(chat_id=update.effective_chat.id, 
  #                                  text='No command argument')
  #         await context.bot.send_message(chat_id=update.effective_chat.id, 
  #                                  text='send: /caps argument')
  
  # # функция обработки встроенного запроса
  # async def inline_caps(self, update, context):
  #     query = update.inline_query.query
  #     if not query:
  #         return
  #     results = list()
  #     results.append(
  #         InlineQueryResultArticle(
  #             id=query.upper(),
  #             title='Convert to UPPER TEXT',
  #             input_message_content=InputTextMessageContent(query.upper())
  #         )
  #     )
  #     context.bot.answer_inline_query(update.inline_query.id, results)
  
  # # функция обработки не распознных команд
  # async def unknown(self, update, context):
  #     await context.bot.send_message(chat_id=update.effective_chat.id, 
  #                              text="Sorry, I didn't understand that command.")

  # async def inline_query(self, update, context) -> None:
  #   """Handle the inline query. This is run when you type: @botusername <query>"""
  #   query = update.inline_query.query

  #   if not query:  # empty query should not be handled
  #       return

  #   results = [
  #       InlineQueryResultArticle(
  #           id=str(uuid4()),
  #           title="Caps",
  #           input_message_content=InputTextMessageContent(query.upper()),
  #       ),
  #       InlineQueryResultArticle(
  #           id=str(uuid4()),
  #           title="Bold",
  #           input_message_content=InputTextMessageContent(
  #               f"<b>{escape(query)}</b>", parse_mode=ParseMode.HTML
  #           ),
  #       ),
  #       InlineQueryResultArticle(
  #           id=str(uuid4()),
  #           title="Italic",
  #           input_message_content=InputTextMessageContent(
  #               f"<i>{escape(query)}</i>", parse_mode=ParseMode.HTML
  #           ),
  #       ),
  #   ]


      
  # categories = [
  # "Продукты",
  # "Личные расходы Лена",
  # "Личные расходы Паша",
  # "Транспорт",
  # "Развлечения",
  # "Ежемесячне расходы",
  # "Другое",
  # "Сбережения",
  # "Категория 2",
  # ]
  
  
  
  
