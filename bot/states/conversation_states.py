from telegram.ext import ConversationHandler

# Defining conversation states as a range of integers for different conversation flows.
(
    # --- Customer Flows ---
    AWAITING_AMOUNT,                    # For wallet charge
    AWAITING_RECEIPT,                   # For card-to-card payment
    SELECTING_CATEGORY,                 # Purchase flow
    SELECTING_PLAN,                     # Purchase flow
    CONFIRMING_PURCHASE,                # Purchase flow
    SELECTING_PAYMENT_METHOD,           # Purchase flow
    AWAITING_GIFT_CODE,                 # Gift card redemption
    AWAITING_SERVICE_NOTE,              # Editing service note
    AWAITING_RENEWAL_CONFIRMATION,      # Renewing a service
    AWAITING_CANCELLATION_CONFIRMATION, # Cancelling a service
    AWAITING_ONLINE_PAYMENT_VERIFICATION, # Online payment

    # --- Admin Flows ---
    AWAITING_GIFT_AMOUNT,               # Creating gift cards
    AWAITING_GIFT_COUNT,                # Creating gift cards
    AWAITING_USER_ID_FOR_SEARCH,        # User management
    AWAITING_AMOUNT_TO_ADD,             # User management: add balance
    AWAITING_ROLE_SELECTION,            # User management: change role (NEW)
    AWAITING_BROADCAST_MESSAGE,         # Broadcast
    CONFIRMING_BROADCAST,               # Broadcast

    # --- Admin Settings Sub-flows ---
    ADMIN_SETTINGS_MENU,                # Main settings menu state

    # Plan Management (Add, Edit, Delete)
    PLAN_MANAGEMENT_MENU,               # Main plan management
    AWAITING_PLAN_NAME,
    AWAITING_PLAN_CATEGORY,
    AWAITING_PLAN_DURATION,
    AWAITING_PLAN_TRAFFIC,
    AWAITING_PLAN_PRICE,
    AWAITING_PLAN_DEVICE_LIMIT,
    CONFIRMING_PLAN_CREATION,
    CONFIRMING_PLAN_DELETION,
    SELECTING_FIELD_TO_EDIT_PLAN,       # Editing a plan (NEW)
    AWAITING_NEW_PLAN_VALUE,            # Editing a plan (NEW)

    # Panel Management
    SELECTING_PANEL_TO_MANAGE,
    MANAGING_SPECIFIC_PANEL,
    CONFIRMING_PANEL_DELETION,
    AWAITING_PANEL_NAME,
    AWAITING_PANEL_URL,
    AWAITING_PANEL_USERNAME,
    AWAITING_PANEL_PASSWORD,
    CONFIRMING_PANEL_CREATION,
    SELECTING_FIELD_TO_EDIT_PANEL,
    AWAITING_NEW_PANEL_VALUE,

    # Text Editing
    EDIT_TEXTS_NAVIGATE,
    AWAITING_NEW_TEXT_VALUE,

    # General & Payment Settings
    PAYMENT_SETTINGS_MENU,
    GENERAL_SETTINGS_MENU,
    AWAITING_NEW_SETTING_VALUE,

    # Commission Settings
    COMMISSION_SETTINGS_MENU,
    AWAITING_COMMISSION_THRESHOLD,
    AWAITING_COMMISSION_RATE,

) = range(51) # The range is updated to cover all new states

# A constant to end the conversation from anywhere
END_CONVERSION = ConversationHandler.END