from telegram.ext import ConversationHandler

# Defining conversation states as a range of integers
(
    # States for Payment
    AWAITING_AMOUNT,
    AWAITING_RECEIPT,

    # States for Purchase Flow
    SELECTING_CATEGORY,
    SELECTING_PLAN,
    CONFIRMING_PURCHASE,
    SELECTING_PAYMENT_METHOD,

    # States for Gift Card (Customer)
    AWAITING_GIFT_CODE,

    # States for Gift Card Creation (Admin)
    AWAITING_GIFT_AMOUNT,
    AWAITING_GIFT_COUNT,

    # State for User Management (Admin)
    AWAITING_USER_ID_FOR_SEARCH,
    AWAITING_AMOUNT_TO_ADD,

    # State for user changing a service note
    AWAITING_SERVICE_NOTE,

    # State for service renewal
    AWAITING_RENEWAL_CONFIRMATION,

    # States for Admin Broadcast
    AWAITING_BROADCAST_MESSAGE,
    CONFIRMING_BROADCAST,

    # States for Plan Management
    PLAN_MANAGEMENT_MENU,
    AWAITING_PLAN_NAME,
    AWAITING_PLAN_CATEGORY,
    AWAITING_PLAN_DURATION,
    AWAITING_PLAN_TRAFFIC,
    AWAITING_PLAN_PRICE,
    AWAITING_PLAN_DEVICE_LIMIT,
    CONFIRMING_PLAN_CREATION,
    SELECTING_PLAN_TO_MANAGE,
    SELECTING_FIELD_TO_EDIT,
    AWAITING_NEW_PLAN_VALUE,
    CONFIRMING_PLAN_DELETION,


    # State for Service Cancellation
    AWAITING_CANCELLATION_CONFIRMATION,

    # States for Panel Management
    PANEL_MANAGEMENT_MENU,
    AWAITING_PANEL_NAME,
    AWAITING_PANEL_URL,
    AWAITING_PANEL_USERNAME,
    AWAITING_PANEL_PASSWORD,
    CONFIRMING_PANEL_CREATION,
    SELECTING_PANEL_TO_MANAGE,
    SELECTING_FIELD_TO_EDIT_PANEL,
    AWAITING_NEW_PANEL_VALUE,
    CONFIRMING_PANEL_DELETION,


) = range(40) # Increased the range

# A constant to end the conversation from anywhere
END_CONVERSION = ConversationHandler.END