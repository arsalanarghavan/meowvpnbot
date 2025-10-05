from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          CallbackQueryHandler, ConversationHandler, filters)

from core.config import BOT_TOKEN, ADMIN_ID
from core.logger import get_logger
from core.translator import _

# ===>> Import all handlers and states <<===
from bot.handlers.customer import (start, info_handlers, wallet_handlers, payment_handlers,
                                   test_account_handler, purchase_flow, service_management, 
                                   gift_card_handler)
from bot.handlers.marketer import marketer_handlers
from bot.handlers.admin import (financial_handlers, gift_card_management, panel, 
                                user_management, broadcast_handlers)
from bot.states.conversation_states import (AWAITING_RECEIPT, SELECTING_CATEGORY, SELECTING_PLAN,
                                            CONFIRMING_PURCHASE, SELECTING_PAYMENT_METHOD, AWAITING_GIFT_CODE, AWAITING_GIFT_AMOUNT,
                                            AWAITING_GIFT_COUNT, AWAITING_USER_ID_FOR_SEARCH,
                                            AWAITING_AMOUNT_TO_ADD, AWAITING_AMOUNT, AWAITING_SERVICE_NOTE, 
                                            AWAITING_RENEWAL_CONFIRMATION, AWAITING_BROADCAST_MESSAGE,
                                            CONFIRMING_BROADCAST, END_CONVERSION)

logger = get_logger(__name__)

def main() -> None:
    """The main function to run the bot."""
    logger.info("Starting bot...")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # --- Conversation Handler Definitions ---
    wallet_charge_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(payment_handlers.ask_for_payment_method, pattern='^increase_balance$')],
        states={
            AWAITING_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_handlers.receive_charge_amount)]
        },
        fallbacks=[CommandHandler('cancel', payment_handlers.cancel_payment)],
    )

    card_to_card_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(payment_handlers.card_to_card_start, pattern='^pay_card_to_card$')
        ],
        states={
            AWAITING_RECEIPT: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, payment_handlers.receipt_handler)]
        },
        fallbacks=[CommandHandler('cancel', payment_handlers.cancel_payment)],
        map_to_parent={ END_CONVERSION: END_CONVERSION }
    )

    purchase_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.purchase_service')}$"), purchase_flow.start_purchase_flow)],
        states={
            SELECTING_CATEGORY: [CallbackQueryHandler(purchase_flow.select_category, pattern='^category_')],
            SELECTING_PLAN: [
                CallbackQueryHandler(purchase_flow.select_plan, pattern='^plan_'),
                CallbackQueryHandler(purchase_flow.start_purchase_flow, pattern='^back_to_categories$')
            ],
            CONFIRMING_PURCHASE: [
                CallbackQueryHandler(purchase_flow.show_payment_options, pattern='^confirm_purchase_'),
                CallbackQueryHandler(purchase_flow.back_to_plans, pattern='^back_to_plans$')
            ],
            SELECTING_PAYMENT_METHOD: [
                CallbackQueryHandler(purchase_flow.process_wallet_payment, pattern='^pay_wallet$'),
                CallbackQueryHandler(purchase_flow.back_to_plans, pattern='^back_to_plans$'),
                card_to_card_conv_handler
            ]
        },
        fallbacks=[CallbackQueryHandler(purchase_flow.cancel_purchase, pattern='^cancel_purchase$')],
    )
    
    change_note_conv_handler = service_management.change_note_conv_handler
    renew_service_conv_handler = service_management.renew_service_conv_handler
    gift_card_conv_handler = gift_card_handler.gift_card_conv_handler
    new_gift_conv_handler = gift_card_management.new_gift_conv_handler
    user_search_conv_handler = user_management.user_search_conv_handler
    add_balance_conv_handler = user_management.add_balance_conv_handler
    broadcast_conv_handler = broadcast_handlers.broadcast_conv_handler

    # ------------------- Handler Registration -------------------
    application.add_handler(purchase_conv_handler)
    application.add_handler(wallet_charge_conv_handler)
    application.add_handler(card_to_card_conv_handler)
    application.add_handler(change_note_conv_handler)
    application.add_handler(renew_service_conv_handler)
    application.add_handler(gift_card_conv_handler)
    application.add_handler(new_gift_conv_handler)
    application.add_handler(user_search_conv_handler)
    application.add_handler(add_balance_conv_handler)
    application.add_handler(broadcast_conv_handler)

    # Admin Handlers
    admin_filter = filters.User(user_id=ADMIN_ID)
    application.add_handler(CommandHandler("admin", panel.admin_panel_entry, filters=admin_filter))
    application.add_handler(MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_panel.dashboard')}$"), panel.show_dashboard))
    application.add_handler(MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_panel.exit')}$"), panel.exit_admin_panel))

    # Customer & Marketer Handlers
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.account_info')}$"), info_handlers.account_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.support')}$"), info_handlers.support_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.applications')}$"), info_handlers.applications_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.wallet')}$"), wallet_handlers.wallet_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.test_account')}$"), test_account_handler.get_test_account))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.manage_service')}$"), service_management.list_services))
    
    # Marketer Panel Handlers
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.marketer_panel')}$"), marketer_handlers.marketer_panel_entry))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.invite_link')}$"), marketer_handlers.get_invite_link))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.stats')}$"), marketer_handlers.show_stats))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.request_payout')}$"), marketer_handlers.request_payout))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.back_to_main')}$"), marketer_handlers.back_to_main_menu_from_marketer))
    
    # Callback Query Handlers
    application.add_handler(CallbackQueryHandler(wallet_handlers.transaction_history, pattern='^transaction_history$'))
    application.add_handler(CallbackQueryHandler(payment_handlers.back_to_wallet, pattern='^back_to_wallet$'))
    application.add_handler(CallbackQueryHandler(financial_handlers.handle_receipt_confirmation, pattern='^(confirm_receipt_|reject_receipt_)'))
    application.add_handler(CallbackQueryHandler(service_management.show_service_menu, pattern='^manage_service_'))
    application.add_handler(CallbackQueryHandler(service_management.get_subscription_link, pattern='^get_sub_'))
    application.add_handler(CallbackQueryHandler(service_management.get_qr_code, pattern='^get_qr_'))
    application.add_handler(CallbackQueryHandler(service_management.get_active_connections, pattern='^get_connections_'))
    application.add_handler(CallbackQueryHandler(service_management.regenerate_uuid, pattern='^regen_uuid_'))
    application.add_handler(CallbackQueryHandler(service_management.back_to_main_menu_from_services, pattern='^back_to_main_menu$'))
    application.add_handler(CallbackQueryHandler(user_management.view_user_services, pattern='^admin_view_services_'))

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical("Bot stopped due to a critical error: %s", e, exc_info=True)