from datetime import time
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
                                user_management, broadcast, plan_management,
                                backup_handlers, panel_management, settings_handlers)
from bot.states.conversation_states import *
from bot.jobs import check_and_renew_services

logger = get_logger(__name__)

def main() -> None:
    """The main function to run the bot."""
    logger.info("Starting bot...")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # --- Job Scheduling for Auto-Renewal ---
    job_queue = application.job_queue
    job_queue.run_daily(check_and_renew_services, time=time(hour=1, minute=0), name='daily_renewal_check')

    admin_filter = filters.User(user_id=ADMIN_ID)

    # --- Conversation Handler Definitions ---
    
    # This handler is now defined inside payment_handlers.py
    # online_payment_conv = ...

    wallet_charge_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(payment_handlers.ask_for_payment_method, pattern='^increase_balance$')],
        states={
            AWAITING_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_handlers.receive_charge_amount)]
        },
        fallbacks=[CommandHandler('cancel', payment_handlers.cancel_payment)],
        map_to_parent={END_CONVERSION: SELECTING_PAYMENT_METHOD} # Go back to payment method selection
    )

    card_to_card_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(payment_handlers.card_to_card_start, pattern='^pay_card_to_card$')
        ],
        states={
            AWAITING_RECEIPT: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, payment_handlers.receipt_handler)]
        },
        fallbacks=[CommandHandler('cancel', payment_handlers.cancel_payment)],
        map_to_parent={END_CONVERSION: END_CONVERSION}
    )
    
    online_payment_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(payment_handlers.start_online_payment, pattern='^pay_online$')],
        states={
            AWAITING_ONLINE_PAYMENT_VERIFICATION: [CallbackQueryHandler(payment_handlers.verify_online_payment, pattern='^verify_payment_')]
        },
        fallbacks=[CommandHandler('cancel', payment_handlers.cancel_payment)],
        map_to_parent={END_CONVERSION: END_CONVERSION}
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
                card_to_card_conv_handler,
                online_payment_conv_handler
            ]
        },
        fallbacks=[CallbackQueryHandler(purchase_flow.cancel_purchase, pattern='^cancel_purchase$')],
    )

    change_note_conv_handler = service_management.change_note_conv_handler
    renew_service_conv_handler = service_management.renew_service_conv_handler
    cancel_service_conv_handler = service_management.cancel_service_conv_handler
    gift_card_conv_handler = gift_card_handler.gift_card_conv_handler
    new_gift_conv_handler = gift_card_management.new_gift_conv_handler
    user_search_conv_handler = user_management.user_search_conv_handler
    add_balance_conv_handler = user_management.add_balance_conv_handler
    broadcast_conv_handler = broadcast.broadcast_conv_handler

    # --- Admin Settings Nested Conversation Handlers ---
    add_plan_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(plan_management.start_add_plan, pattern='^add_plan$')],
        states={
            AWAITING_PLAN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_management.receive_plan_name)],
            AWAITING_PLAN_CATEGORY: [CallbackQueryHandler(plan_management.receive_plan_category, pattern='^plan_cat_')],
            AWAITING_PLAN_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_management.receive_plan_duration)],
            AWAITING_PLAN_TRAFFIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_management.receive_plan_traffic)],
            AWAITING_PLAN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_management.receive_plan_price)],
            AWAITING_PLAN_DEVICE_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_management.receive_plan_device_limit)],
            CONFIRMING_PLAN_CREATION: [CallbackQueryHandler(plan_management.confirm_create_plan, pattern='^confirm_create_plan$')]
        },
        fallbacks=[CallbackQueryHandler(plan_management.cancel_plan_creation, pattern='^cancel_create_plan$')]
    )

    edit_plan_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(plan_management.start_edit_plan, pattern='^edit_plan$')],
        states={
            AWAITING_NEW_PLAN_VALUE: [
                 CallbackQueryHandler(plan_management.select_field_to_edit, pattern='^edit_field_'),
                 MessageHandler(filters.TEXT & ~filters.COMMAND, plan_management.receive_new_plan_value)
            ]
        },
        fallbacks=[CallbackQueryHandler(plan_management.show_plan_management_menu, pattern='^back_to_plan_manage_menu_')]
    )
    
    add_panel_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(panel_management.start_add_panel, pattern='^add_panel$')],
        states={
            AWAITING_PANEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, panel_management.receive_panel_name)],
            AWAITING_PANEL_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, panel_management.receive_panel_url)],
            AWAITING_PANEL_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, panel_management.receive_panel_username)],
            AWAITING_PANEL_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, panel_management.receive_panel_password)],
            CONFIRMING_PANEL_CREATION: [CallbackQueryHandler(panel_management.confirm_create_panel, pattern='^confirm_create_panel$')]
        },
        fallbacks=[CallbackQueryHandler(panel_management.cancel_panel_creation, pattern='^cancel_create_panel$')]
    )

    edit_panel_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(panel_management.start_edit_panel, pattern='^edit_panel$')],
        states={
            AWAITING_NEW_PANEL_VALUE: [
                CallbackQueryHandler(panel_management.select_field_to_edit_panel, pattern='^edit_panel_field_'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, panel_management.receive_new_panel_value)
            ]
        },
        fallbacks=[CallbackQueryHandler(panel_management.show_panel_management_menu, pattern='^back_to_panel_manage_menu_')]
    )
    
    edit_texts_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{_('buttons.admin_settings.edit_texts')}$"), settings_handlers.start_text_edit)],
        states={
            EDIT_TEXTS_NAVIGATE: [
                CallbackQueryHandler(settings_handlers.navigate_text_keys, pattern='^navigate_'),
                CallbackQueryHandler(settings_handlers.prompt_for_new_value, pattern='^edit_value_'),
                CallbackQueryHandler(settings_handlers.back_to_top_level, pattern='^back_to_top_level$'),
            ],
            AWAITING_NEW_TEXT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings_handlers.receive_new_value)]
        },
        fallbacks=[CallbackQueryHandler(settings_handlers.back_to_settings, pattern='^back_to_settings$')],
        map_to_parent={ ConversationHandler.END: ADMIN_SETTINGS_MENU }
    )

    # Main Admin Settings Conversation Handlers
    plan_management_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_settings.plan_management')}$"), plan_management.start_plan_management)],
        states={
            SELECTING_PLAN_TO_MANAGE: [
                CallbackQueryHandler(plan_management.show_plan_management_menu, pattern='^manage_plan_'),
                add_plan_conv_handler,
            ],
            SELECTING_FIELD_TO_EDIT: [
                edit_plan_conv_handler,
                CallbackQueryHandler(plan_management.start_delete_plan, pattern='^delete_plan'),
                CallbackQueryHandler(plan_management.start_plan_management, pattern='^back_to_plan_list$')
            ],
            CONFIRMING_PLAN_DELETION: [
                CallbackQueryHandler(plan_management.confirm_delete_plan, pattern='^confirm_delete_'),
                CallbackQueryHandler(plan_management.show_plan_management_menu, pattern='^back_to_plan_manage_menu')
            ]
        },
        fallbacks=[CallbackQueryHandler(settings_handlers.show_settings_menu, pattern='^back_to_settings_menu$')],
        map_to_parent={ ConversationHandler.END: ADMIN_SETTINGS_MENU }
    )

    panel_management_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_settings.panel_management')}$"), panel_management.start_panel_management)],
        states={
            SELECTING_PANEL_TO_MANAGE: [
                CallbackQueryHandler(panel_management.show_panel_management_menu, pattern='^manage_panel_'),
                add_panel_conv_handler,
            ],
            SELECTING_FIELD_TO_EDIT_PANEL: [
                edit_panel_conv_handler,
                CallbackQueryHandler(panel_management.start_delete_panel, pattern='^delete_panel'),
                CallbackQueryHandler(panel_management.start_panel_management, pattern='^back_to_panel_list$')
            ],
            CONFIRMING_PANEL_DELETION: [
                CallbackQueryHandler(panel_management.confirm_delete_panel, pattern='^confirm_delete_panel_'),
                CallbackQueryHandler(panel_management.show_panel_management_menu, pattern='^back_to_panel_manage_menu_')
            ]
        },
        fallbacks=[CallbackQueryHandler(settings_handlers.show_settings_menu, pattern='^back_to_settings_menu$')],
        map_to_parent={ ConversationHandler.END: ADMIN_SETTINGS_MENU }
    )
    
    admin_settings_conv = ConversationHandler(
        entry_points=[MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_panel.settings')}$"), settings_handlers.show_settings_menu)],
        states={
            ADMIN_SETTINGS_MENU: [
                plan_management_conv_handler,
                panel_management_conv_handler,
                edit_texts_conv,
            ]
        },
        fallbacks=[MessageHandler(filters.Regex(f"^{_('buttons.admin_panel.back_to_main')}$"), panel.admin_panel_entry)],
    )

    # ------------------- Handler Registration -------------------
    application.add_handler(purchase_conv_handler)
    application.add_handler(wallet_charge_conv_handler)
    application.add_handler(change_note_conv_handler)
    application.add_handler(renew_service_conv_handler)
    application.add_handler(cancel_service_conv_handler)
    application.add_handler(gift_card_conv_handler)
    application.add_handler(new_gift_conv_handler)
    application.add_handler(user_search_conv_handler)
    application.add_handler(add_balance_conv_handler)
    application.add_handler(broadcast_conv_handler)
    application.add_handler(admin_settings_conv)

    application.add_handler(CommandHandler("admin", panel.admin_panel_entry, filters=admin_filter))
    application.add_handler(MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_panel.dashboard')}$"), panel.show_dashboard))
    application.add_handler(MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_panel.backup')}$"), backup_handlers.backup_database))
    application.add_handler(MessageHandler(admin_filter & filters.Regex(f"^{_('buttons.admin_panel.exit')}$"), panel.exit_admin_panel))

    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.account_info')}$"), info_handlers.account_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.support')}$"), info_handlers.support_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.applications')}$"), info_handlers.applications_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.wallet')}$"), wallet_handlers.wallet_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.test_account')}$"), test_account_handler.get_test_account))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.manage_service')}$"), service_management.list_services))
    
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.marketer_panel')}$"), marketer_handlers.marketer_panel_entry))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.invite_link')}$"), marketer_handlers.get_invite_link))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.stats')}$"), marketer_handlers.show_stats))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.request_payout')}$"), marketer_handlers.request_payout))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.marketer_panel.back_to_main')}$"), marketer_handlers.back_to_main_menu_from_marketer))
    
    application.add_handler(CallbackQueryHandler(wallet_handlers.transaction_history, pattern='^transaction_history$'))
    application.add_handler(CallbackQueryHandler(payment_handlers.back_to_wallet, pattern='^back_to_wallet$'))
    application.add_handler(CallbackQueryHandler(financial_handlers.handle_receipt_confirmation, pattern='^(confirm_receipt_|reject_receipt_)'))
    
    application.add_handler(CallbackQueryHandler(service_management.show_service_menu, pattern='^manage_service_'))
    application.add_handler(CallbackQueryHandler(service_management.get_subscription_link, pattern='^get_sub_'))
    application.add_handler(CallbackQueryHandler(service_management.get_qr_code, pattern='^get_qr_'))
    application.add_handler(CallbackQueryHandler(service_management.get_active_connections, pattern='^get_connections_'))
    application.add_handler(CallbackQueryHandler(service_management.regenerate_uuid, pattern='^regen_uuid_'))
    application.add_handler(CallbackQueryHandler(service_management.toggle_auto_renew_handler, pattern='^toggle_renew_'))
    application.add_handler(CallbackQueryHandler(service_management.update_servers_handler, pattern='^update_servers_'))
    application.add_handler(CallbackQueryHandler(service_management.back_to_main_menu_from_services, pattern='^back_to_main_menu$'))
    
    application.add_handler(CallbackQueryHandler(user_management.view_user_services, pattern='^admin_view_services_'))

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical("Bot stopped due to a critical error: %s", e, exc_info=True)